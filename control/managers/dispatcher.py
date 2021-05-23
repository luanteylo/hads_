from control.managers.cloud_manager import CloudManager
from control.managers.virtual_machine import VirtualMachine

from control.domain.task import Task

from control.scheduler.queue import Queue

from control.util.linked_list import LinkedList
from control.util.event import Event
from control.util.loader import Loader

from control.daemon.daemon_manager import Daemon
from control.daemon.communicator import Communicator

from control.repository.postgres_repo import PostgresRepo
from control.repository.postgres_objects import Execution as ExecutionRepo
from control.repository.postgres_objects import Instance as InstanceRepo
from control.repository.postgres_objects import InstanceStatus as InstanceStatusRepo
from control.repository.postgres_objects import InstanceStatistic as InstanceStatisticRepo
from control.repository.postgres_objects import TaskStatistic as TaskStatisticRepo

from typing import List
import threading
import time
import logging
import os
import math

from datetime import datetime, timedelta

from zope.event import notify


class Executor:

    def __init__(self, task: Task, vm: VirtualMachine, loader: Loader):

        self.loader = loader

        self.task = task
        self.vm = vm

        self.repo = None
        # Execution Status
        self.status = Task.WAITING

        # socket.communicator
        # used to send commands to the ec2 instance
        self.communicator = Communicator(host=self.vm.instance_ip, port=self.loader.communication_conf.socket_port)

        """Track INFO """
        # used to abort the execution loop
        self.stop_signal = False
        # checkpoint tracker
        self.next_checkpoint_datetime = None

        self.thread = threading.Thread(target=self.__run, daemon=True)

    def update_status_table(self):
        """
        Update Execution Table
        Call if task status change
        """
        # Update Execution Status Table
        self.repo.add_execution(
            ExecutionRepo(
                execution_id=self.loader.execution_id,
                job_id=self.loader.job.job_id,
                task_id=self.task.task_id,
                instance_id=self.vm.instance_id,
                timestamp=datetime.now(),
                status=self.status
            )
        )

        # repo.close_session()

    def __run(self):
        # START task execution

        self.repo = PostgresRepo()

        action = Daemon.START

        if self.task.has_checkpoint:
            action = Daemon.RESTART
        try:
            self.communicator.send(action=action, value=self.dict_info)
        except Exception as e:
            logging.error(e)
            self.__stopped(Task.ERROR)
            return

        # if task was started with success
        # start execution loop
        # print(self.communicator.response)
        if self.communicator.response['status'] == 'success':

            logging.info("<Executor {}-{}>:  Start Task Return: {}".format(self.vm.instance_id,
                                                                           self.task.task_id,
                                                                           self.communicator.response['value']))

            if action == Daemon.START:
                self.status = Task.EXECUTING
            else:
                self.status = Task.RESTARTED

            self.update_status_table()

            # start task execution Loop
            while (self.status == Task.EXECUTING or self.status == Task.RESTARTED) and not self.stop_signal:

                try:
                    docker_status, exit_code = self.__get_task_status()
                    usage = self.__get_task_usage()

                    if self.loader.checkpoint_conf.with_checkpoint \
                        and self.vm.market == CloudManager.PREEMPTIBLE and self.task.do_checkpoint:
                        self.__checkpoint_task()

                except Exception as e:
                    logging.error(e)
                    self.__stopped(Task.ERROR)
                    return

                # update memory usage
                if usage is not None and 'memory' in usage:
                    current_mem = self.__to_megabyte(usage['memory'])
                    current_cpu_str = usage['cpu']

                    current_cpu = 0.0

                    if current_cpu_str.find("%") != -1:
                        current_cpu = float(current_cpu_str.replace('%', ''))

                    # repo = PostgresRepo()
                    self.repo.add_task_statistic(TaskStatisticRepo(
                        execution_id=self.loader.execution_id,
                        job_id=self.loader.job.job_id,
                        task_id=self.task.task_id,
                        timestamp=datetime.now(),
                        cpu_usage=current_cpu,
                        memory_usage=current_mem
                    ))
                    # repo.close_session()

                if docker_status is not None and docker_status == 'exited':

                    status = Task.FINISHED

                    if exit_code != '0':
                        status = Task.RUNTIME_ERROR

                    self.__stopped(status)
                    return

                if docker_status is not None and docker_status == 'not found':
                    status = Task.RUNTIME_ERROR
                    self.__stopped(status)
                    return

                time.sleep(1)

        # if kill signal than checkpoint task (SIMULATION)
        if self.stop_signal:
            # check is task is running
            try:
                docker_status, exit_code = self.__get_task_status()
                if docker_status is not None and docker_status == 'running':
                    self.__checkpoint(stop_task=True)  # Checkpoint and stop task
                    self.__stopped(Task.HIBERNATED)
                else:
                    self.__stopped(Task.FINISHED)

            except Exception as e:
                logging.error(e)
                self.__stopped(Task.STOP_SIGNAL)

            return

        self.__stopped(Task.ERROR)

    def __stopped(self, status):
        # update execution time

        # if task had Migrated, not to do
        if self.status == Task.MIGRATED:
            self.repo.close_session()
            return

        self.status = status

        self.update_status_table()
        # close repo
        self.repo.close_session()

        # Check if condition is true to checkpoint the task

    def __checkpoint_task(self):

        if self.next_checkpoint_datetime is None:
            # compute next_checkpoint datetime
            self.next_checkpoint_datetime = datetime.now() + timedelta(seconds=self.task.checkpoint_interval)

        elif datetime.now() > self.next_checkpoint_datetime:

            self.__checkpoint()
            self.next_checkpoint_datetime = datetime.now() + timedelta(seconds=self.task.checkpoint_interval)

    def __checkpoint(self, stop_task=False):

        for i in range(3):
            try:

                action = Daemon.CHECKPOINT_STOP if stop_task else Daemon.CHECKPOINT

                logging.info("<Executor {}-{}>: Checkpointing task...".format(self.task.task_id,
                                                                              self.vm.instance_id))

                start_ckp = datetime.now()
                self.communicator.send(action, value=self.dict_info)

                if self.communicator.response['status'] == 'success':
                    end_ckp = datetime.now()

                    logging.info("<Executor {}-{}>: Checkpointed with success. Time: {}".format(self.task.task_id,
                                                                                                self.vm.instance_id,
                                                                                                end_ckp - start_ckp))
                    self.task.has_checkpoint = True
                    self.task.update_task_time()

                return
            except:
                pass

        raise Exception("<Executor {}-{}>: Checkpoint error".format(self.task.task_id, self.vm.instance_id))

    def __get_task_status(self):

        for i in range(3):

            try:

                self.communicator.send(action=Daemon.STATUS,
                                       value=self.dict_info)

                result = self.communicator.response

                docker_status = None
                exit_code = None

                if result['status'] == 'success':
                    docker_status = result['value']['status']
                    exit_code = result['value']['exit_code']

                return docker_status, exit_code
            except:
                logging.error("<Executor {}-{}>: Get task Status {}/3".format(self.task.task_id,
                                                                              self.vm.instance_id,
                                                                              i + 1))
                time.sleep(1)

        raise Exception("<Executor {}-{}>: Get task status error".format(self.task.task_id, self.vm.instance_id))

    def __get_task_usage(self):
        for i in range(3):
            try:
                self.communicator.send(action=Daemon.TASK_USAGE,
                                       value=self.dict_info)

                result = self.communicator.response

                usage = None

                if result['status'] == 'success':
                    usage = result['value']

                return usage
            except:
                logging.error(
                    "<Executor {}-{}>: Get task Usage {}/3".format(self.task.task_id, self.vm.instance_id, i + 1))
                time.sleep(1)

        raise Exception("<Executor {}-{}>: Get task usage error".format(self.task.task_id, self.vm.instance_id))

    def __to_megabyte(self, str):

        pos = str.find('MiB')

        if pos == -1:
            pos = str.find('GiB')
        if pos == -1:
            pos = str.find('KiB')
        if pos == -1:
            pos = str.find('B')

        memory = float(str[:pos])
        index = str[pos:]

        to_megabyte = {
            "GiB": 1073.742,
            "MiB": 1.049,
            "B": 1e+6,
            "KiB": 976.562
        }

        return to_megabyte[index] * memory

    @property
    def dict_info(self):

        quota = self.vm.cpu_quota

        if self.task.burst_mode:
            quota = -1

        info = {
            "task_id": self.task.task_id,
            "command": self.task.command,
            'cpu_quota': quota
        }

        return info


class Dispatcher:
    error_tasks: List[Task]
    finished_tasks: List[Task]
    hibernated_tasks: List[Task]
    waiting_tasks: List[Task]
    running_tasks: List[Task]

    running_executors: List[Executor]
    finished_executors: List[Executor]

    def __init__(self, vm: VirtualMachine, queue: Queue, loader: Loader):
        self.loader = loader

        self.vm: VirtualMachine = vm  # Class that control a Virtual machine on the cloud
        self.queue = queue  # Class with the scheduling plan

        # Control Flags
        self.working = False
        # flag to indicate that the instance is ready to execute
        self.ready = False
        # indicate that VM resume
        self.resume = False
        # indicate that VM hibernates
        self.hibernated = False

        # debug flag indicates that the dispatcher should wait for the shutdown command
        self.debug_wait_command = self.loader.debug_conf.debug_mode

        # migration count
        self.migration_count = 0

        '''
        List that determine the execution order of the
        tasks that will be executed in that dispatcher
        '''
        self.list_of_tasks = LinkedList()

        # current tasks status
        self.waiting_tasks = []
        self.finished_tasks = []
        self.error_tasks = []
        self.hibernated_tasks = []
        self.running_tasks = []

        # current executor status
        self.running_executors = []
        self.finished_executors = []

        # threading event to waiting for tasks to execute
        self.waiting_work = threading.Event()
        self.semaphore = threading.Semaphore()

        self.main_thread = threading.Thread(target=self.__execution_loop, daemon=True)

        self.repo = PostgresRepo()
        self.least_status = None
        self.timestamp_status_update = None

        # self.stop_period = None
        self.expected_makespan_timestamp = None

        self.__create_ordered_list()

    def __get_instance_usage(self):
        memory = 0
        cpu = 0

        communicator = Communicator(self.vm.instance_ip,
                                    self.loader.communication_conf.socket_port)

        info = {
            "task_id": 0,
            "command": '',
            'cpu_quota': 0
        }

        max_attempt = 1

        for i in range(max_attempt):
            try:
                communicator.send(action=Daemon.INSTANCE_USAGE, value=info)

                result = communicator.response

                if result['status'] == 'success':
                    memory = float(result['value']['memory'])
                    cpu = float(result['value']['cpu'])
            except:
                logging.error("<Dispatcher {}>: Get Instance Usage {}/{}".format(self.vm.instance_id,
                                                                                 i + 1,
                                                                                 max_attempt))

        return cpu, memory

    def __update_instance_status_table(self, state=None):
        """
        Update Instance Status table
        """
        if state is None:
            state = self.vm.state

        # Check if the update have to be done due to the time

        time_diff = None
        if self.timestamp_status_update is not None:
            time_diff = datetime.now() - self.timestamp_status_update

        if self.least_status is None or self.least_status != state or \
            time_diff > timedelta(seconds=self.loader.scheduler_conf.status_update_time):
            cpu = 0.0
            memory = 0.0
            # cpu, memory = self.__get_instance_usage()
            # Update Instance_status Table
            self.repo.add_instance_status(InstanceStatusRepo(instance_id=self.vm.instance_id,
                                                             timestamp=datetime.now(),
                                                             status=state,
                                                             memory_footprint=memory,
                                                             cpu_usage=cpu,
                                                             cpu_credit=self.vm.get_cpu_credits()))

            self.timestamp_status_update = datetime.now()
            self.least_status = self.vm.state

    def __update_instance_statistics_table(self):

        self.repo.add_instance_status(InstanceStatisticRepo(instance_id=self.vm.instance_id,
                                                            deploy_overhead=self.vm.deploy_overhead.seconds,
                                                            termination_overhead=self.vm.terminate_overhead.seconds,
                                                            uptime=self.vm.uptime.seconds))

    def __update_waiting_tasks(self):
        for task in self.waiting_tasks:
            # Update Execution Status Table
            self.repo.add_execution(ExecutionRepo(execution_id=self.loader.execution_id,
                                                  job_id=self.loader.job.job_id,
                                                  task_id=task.task_id,
                                                  instance_id=self.vm.instance_id,
                                                  timestamp=datetime.now(),
                                                  status=Task.WAITING))

    def __create_ordered_list(self):

        # logging.info('Loading dispatcher queue to instance type: "{}" Logical ID: {}'.format(
        #     self.queue.instance_type.type,
        #     self.queue.instance_id
        # ))

        self.semaphore.acquire()

        # Create the list of tasks that will be executed
        for vcpu_key, item in self.queue.cores.items():
            aux = item.head

            while aux is not None:
                task: Task = aux.data.task

                self.list_of_tasks.add_ordered(
                    task
                )

                self.waiting_tasks.append(task)

                aux = aux.next

        self.semaphore.release()

    def add_task(self, task: Task):

        start, end = self.queue.insert(task)

        task.expected_start = start
        task.expected_end = end

        self.list_of_tasks.add_ordered(task)
        self.waiting_tasks.append(task)

        self.repo.add_execution(ExecutionRepo(execution_id=self.loader.execution_id,
                                              job_id=self.loader.job.job_id,
                                              task_id=task.task_id,
                                              instance_id=self.vm.instance_id,
                                              timestamp=datetime.now(),
                                              status=Task.WAITING))

        # update makespan
        self.expected_makespan_timestamp = self.vm.start_time + timedelta(seconds=self.queue.makespan_seconds)

    def add_tasks(self, tasks: List[Task]):

        for task in tasks:
            self.add_task(task)

    def get_possible_to_be_stolen(self, check_next_period=True):

        aux = self.list_of_tasks.head

        possible_stolen: List[Task] = []

        if self.ready:

            while aux is not None:
                task = aux.data

                if check_next_period:

                    task_size = task.expected_end - task.expected_start
                    datetime_end = self.vm.start_time + timedelta(seconds=task.expected_start) + timedelta(
                        seconds=task_size)

                    if datetime_end >= self.next_period_end:
                        possible_stolen.append(task)
                else:

                    possible_stolen.append(task)

                aux = aux.next

        return possible_stolen

    def remove_task(self, task: Task):
        self.waiting_tasks.remove(task)
        self.queue.remove(task)
        self.list_of_tasks.remove([task])

        self.repo.add_execution(ExecutionRepo(execution_id=self.loader.execution_id,
                                              job_id=self.loader.job.job_id,
                                              task_id=task.task_id,
                                              instance_id=self.vm.instance_id,
                                              timestamp=datetime.now(),
                                              status=Task.STOLEN))

    def remove_tasks(self, tasks: List[Task]):

        # remove from waiting _task
        for task in tasks:
            self.remove_task(task)

    def __notify(self, value):

        kwargs = {'instance_id': self.vm.instance_id,
                  'dispatcher': self,
                  'running': self.running_tasks,
                  'finished': self.finished_tasks,
                  'waiting': self.waiting_tasks,
                  'hibernated': self.hibernated_tasks}

        notify(
            Event(
                event_type=Event.INSTANCE_EVENT,
                value=value,
                **kwargs
            )
        )

    def __can_execute(self, task: Task):
        can_execute = True

        for executor in self.running_executors:
            r_task = executor.task

            if r_task.expected_end <= task.expected_start:
                can_execute = False

        return can_execute

    def __update_running_executors(self):

        new_list_executors = []
        new_list_tasks = []

        for r in self.running_executors:

            if r.status == Task.EXECUTING or r.status == Task.WAITING or r.status == Task.RESTARTED:
                new_list_executors.append(r)
                new_list_tasks.append(r.task)
            else:
                if r.status == Task.FINISHED:
                    self.finished_tasks.append(r.task)

                    if self.vm.burstable and r.task.burst_mode:
                        self.vm.release_credits(r.task.allocated_cpu_credits)

                elif r.status == Task.ERROR:
                    self.error_tasks.append(r.task)

                    if self.vm.burstable and r.task.burst_mode:
                        self.vm.release_credits(r.task.allocated_cpu_credits)

                elif r.status == Task.HIBERNATED:
                    self.hibernated_tasks.append(r.task)

                self.finished_executors.append(r)

        self.running_tasks = new_list_tasks
        self.running_executors = new_list_executors

    def __prepare_daemon(self):
        attempt = 1
        while True:
            time.sleep(self.loader.communication_conf.retry_interval)

            try:
                communicator = Communicator(host=self.vm.instance_ip, port=self.loader.communication_conf.socket_port)
                communicator.send(action=Daemon.TEST, value={'task_id': None, 'command': None})

                if communicator.response['status'] == 'success':
                    return True

            except Exception as e:
                if attempt > self.loader.communication_conf.repeat:
                    logging.error(e)
                    return False

            if attempt <= self.loader.communication_conf.repeat:
                logging.info('<Dispatcher {}>: Trying Daemon handshake... attempt {}/{}'
                             ''.format(self.vm.instance_id, attempt,
                                       self.loader.communication_conf.repeat))
            else:
                logging.info('<Dispatcher {}>: Daemon handshake MAX ATTEMPT ERROR'
                             ''.format(self.vm.instance_id, attempt,
                                       self.loader.communication_conf.repeat))

            attempt += 1

    # Updates
    def reset_queue_structures(self):

        self.queue = Queue(instance_id=self.queue.instance_id,
                           instance_type=self.queue.instance_type,
                           market=self.queue.market,
                           allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

        self.waiting_tasks = []
        self.finished_tasks = []
        self.error_tasks = []
        self.hibernated_tasks = []
        self.running_tasks = []

        self.running_executors = []
        self.finished_executors = []

        # self.recovered = False

        self.list_of_tasks = LinkedList()

    def update_hibernation_duration(self):
        self.vm.update_hibernation_end()
        self.vm.update_ip()

    @property
    def task_max_timedelta(self):
        task_size = timedelta(seconds=0)

        for task in self.waiting_tasks:
            if timedelta(seconds=task.get_runtime(self.vm.type)) > task_size:
                task_size = timedelta(seconds=task.get_runtime(self.vm.type))
        for task in self.running_tasks:
            if timedelta(seconds=task.get_runtime(self.vm.type)) > task_size:
                task_size = timedelta(seconds=task.get_runtime(self.vm.type))

        return task_size

    @property
    def next_period_end(self):

        duration = self.vm.uptime.total_seconds()

        slot_time = self.loader.ac_size_seconds
        number_of_periods = math.ceil(duration / slot_time)

        paid_time = number_of_periods * slot_time

        return self.vm.start_time + timedelta(seconds=paid_time) + self.vm.hibernation_duration

    def __send_task_files(self, task):

        # Send files to VM
        if task is not None and not task.has_checkpoint:

            logging.info("<Dispatcher {}>: Send Files of task: {}.".format(self.vm.instance_id, task.task_id))
            # send files
            source = os.path.join(self.loader.application_conf.app_local_path, str(task.task_id))
            target = os.path.join(self.vm.root_folder, str(task.task_id))

            try:
                # create target folder
                self.vm.ssh.execute_command('mkdir -p {}'.format(target))
                self.vm.ssh.put_dir(source, target)

            except Exception as e:
                logging.error("<Dispatcher {}>:  Error to send files of task {},".format(self.vm.instance_id,
                                                                                         task.task_id))

                task.has_files = True

    def __execution_loop(self):

        # Start the VM in the cloud
        status = self.vm.deploy()

        self.expected_makespan_timestamp = self.vm.start_time + timedelta(seconds=self.queue.makespan_seconds)

        # update instance_repo
        self.repo.add_instance(InstanceRepo(id=self.vm.instance_id,
                                            type=self.vm.instance_type.type,
                                            region=self.vm.instance_type.region,
                                            zone=self.vm.instance_type.zone,
                                            market=self.vm.market,
                                            ebs_volume=self.vm.volume_id,
                                            price=self.vm.price))

        self.__update_instance_status_table()

        if status:

            self.working = True

            try:
                self.vm.prepare_vm()
                self.__prepare_daemon()
            except Exception as e:
                logging.error(e)

                # stop working process
                self.waiting_work.clear()
                # Notify abort!
                self.__notify(CloudManager.ABORT)

            self.__update_waiting_tasks()

            # indicate that the VM is ready to execute
            self.vm.ready = self.ready = True

            while self.working:
                # waiting for work
                self.waiting_work.wait()

                self.waiting_work.clear()
                if not self.working:
                    break

                # execution loop
                self.semaphore.acquire()
                task: Task = self.list_of_tasks.pop()
                self.__send_task_files(task)
                self.semaphore.release()

                while task is not None or len(self.running_executors) > 0:

                    self.__update_instance_status_table()

                    # start Execution when instance is RUNNING
                    if self.vm.state == CloudManager.RUNNING:

                        self.semaphore.acquire()
                        # check running tasks
                        self.__update_running_executors()

                        # check if the next task can be executed
                        if task is not None and self.__can_execute(task):
                            # execute task
                            self.waiting_tasks.remove(task)
                            self.running_tasks.append(task)

                            # create a executor and start task
                            executor = Executor(
                                task=task,
                                vm=self.vm,
                                loader=self.loader
                            )
                            # start the executor loop to execute the task
                            executor.thread.start()

                            self.running_executors.append(executor)

                            # Get the next task
                            task = self.list_of_tasks.pop()
                            self.__send_task_files(task)

                        self.semaphore.release()

                    # Error: instance was not deployed or was terminated
                    elif self.vm.state in (CloudManager.ERROR, CloudManager.SHUTTING_DOWN, CloudManager.TERMINATED):
                        # VM was not created, raise a event
                        self.__notify(CloudManager.TERMINATED)

                        break

                    elif self.vm.state == CloudManager.HIBERNATED:
                        self.hibernated = True
                        self.vm.update_hibernation_start()

                        # Raise Hibernated Even

                        self.vm.hibernation_process_finished = False

                        # STOP and CHECKPOINT all tasks
                        for item in self.running_executors:
                            item.stop_signal = True

                        # waiting running tasks
                        for item in self.running_executors:
                            item.thread.join()

                        self.__update_running_executors()

                        self.vm.hibernation_process_finished = True
                        self.resume = False

                        self.__notify(CloudManager.HIBERNATED)

                        break

                # Raise IDLE EVENT
                if not self.resume:
                    if self.vm.state == CloudManager.RUNNING:
                        self.__update_instance_status_table(state=CloudManager.IDLE)
                        self.__notify(CloudManager.IDLE)
                else:
                    self.resume = False

            if self.vm.state == CloudManager.RUNNING:

                while self.debug_wait_command:
                    time.sleep(5)

                self.vm.terminate(delete_volume=self.loader.filesys_conf.ebs_delete)

            self.__update_instance_status_table()
            self.__update_instance_statistics_table()
            self.repo.close_session()

        else:
            # Error to start VM
            logging.error("<Dispatcher> Instance type: {} Was not started".format(self.vm.instance_type.type))
            self.__notify(CloudManager.ERROR)
