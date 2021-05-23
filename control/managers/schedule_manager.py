import json

import time

from datetime import timedelta, datetime

import logging
from typing import List

from zope.event import subscribers

from control.domain.task import Task

from control.managers.virtual_machine import VirtualMachine
from control.managers.dispatcher import Dispatcher
from control.managers.cloud_manager import CloudManager
from control.managers.ec2_manager import EC2Manager

from control.simulators.status_simulator import RevocationSim
from control.simulators.status_simulator import HibernationSim
from control.simulators.status_simulator import Sim

from control.repository.postgres_repo import PostgresRepo
from control.repository.postgres_objects import Job as JobRepo
from control.repository.postgres_objects import Task as TaskRepo
from control.repository.postgres_objects import InstanceType as InstanceTypeRepo
from control.repository.postgres_objects import InstanceStatus as InstanceStatusRepo
from control.repository.postgres_objects import Statistic as StatisticRepo

from control.scheduler.schedulers import Scheduler
from control.scheduler.queue import Queue
from control.scheduler.CCScheduler import CCScheduler
from control.scheduler.IPDPS import IPDPS

from control.util.loader import Loader

import threading


class ScheduleManager:
    hibernated_dispatcher: List[Dispatcher]
    terminated_dispatcher: List[Dispatcher]
    idle_dispatchers: List[Dispatcher]
    working_dispatchers: List[Dispatcher]
    hibernating_dispatcher: List[Dispatcher]

    def __init__(self, loader: Loader):

        self.loader = loader

        # load the Scheduler that will be used
        self.scheduler: Scheduler = None
        self.__load_scheduler()

        # read expected_makespan on build_dispatcher()
        self.expected_makespan_seconds = None
        self.deadline_timestamp = None

        '''
           If the execution has simulation
           Prepare the simulation environment
        '''
        if self.loader.simulation_conf.with_simulation:
            # start simulator
            if self.loader.simulation_conf.sim_type == Sim.REVOCATION_SIM:
                self.simulator = RevocationSim(self.loader.revocation_rate)
            elif self.loader.simulation_conf.sim_type == Sim.HIBERNATION_SIM:
                self.simulator = HibernationSim(self.loader.revocation_rate, self.loader.resume_rate)
            else:
                raise Exception(
                    "Simulator {} Not Found. Check HADS setup file".format(self.loader.simulation_conf.sim_type))

        # resource pools
        self.working_dispatchers = []
        self.idle_dispatchers = []
        self.terminated_dispatcher = []
        self.hibernated_dispatcher = []
        self.hibernating_dispatcher = []

        # Keep Used EBS Volumes
        self.ebs_volumes = []

        # Vars Datetime to keep track of global execution time
        self.start_timestamp = None
        self.end_timestamp = None
        self.expected_makespan_timestamp = None
        self.elapsed_time = None

        self.repo = PostgresRepo()

        # Semaphore
        self.semaphore = threading.Semaphore()
        self.semaphore_count = threading.Semaphore()

        # TRACKERS VALUES
        self.n_work_stealing = 0
        self.n_burst_stealing = 0

        self.n_hibernations = 0
        self.n_resume = 0

        self.n_recovery = 0
        self.n_timeout = 0

        ''' ABORT FLAG'''
        self.abort = False

        '''
        Build the initial dispatchers
        The class Dispatcher is responsible to manager the execution steps
        '''
        self.__build_dispatchers()

        # Prepare the control database and the folders structure in S3
        try:
            self.__prepare_execution()
        except Exception as e:
            logging.error(e)
            raise e

    # # PRE-EXECUTION FUNCTIONS

    def __load_scheduler(self):

        if self.loader.scheduler_name.upper() == Scheduler.CC:
            self.scheduler = CCScheduler(loader=self.loader)

        elif self.loader.scheduler_name.upper() == Scheduler.IPDPS:
            self.scheduler = IPDPS(loader=self.loader)

        if self.scheduler is None:
            logging.error("<Scheduler Manager {}_{}>: "
                          "ERROR - Scheduler {} not found".format(self.loader.job.job_id,
                                                                  self.loader.execution_id,
                                                                  self.loader.scheduler_name))
            Exception("<Scheduler Manager {}_{}>:  "
                      "ERROR - Scheduler {} not found".format(self.loader.job.job_id,
                                                              self.loader.execution_id,
                                                              self.loader.scheduler_name))

    def __build_dispatchers(self):

        # Define the execution id
        # get the last execution id
        try:
            with open(self.loader.map_file) as f:
                map_json = json.load(f)

        except FileNotFoundError:
            logging.error("<Scheduler Manager {}_{}>: Error file {} ".format(self.loader.job.job_id,
                                                                             self.loader.execution_id,
                                                                             self.loader.map_file))
            raise FileNotFoundError

        except Exception:
            logging.error("<Scheduler Manager {}_{}>:  Error database not found".format(self.loader.job.job_id,
                                                                                        self.loader.execution_id))
            raise Exception

        if self.loader.deadline_seconds is None:
            self.loader.deadline_seconds = map_json['deadline']

        self.expected_makespan_seconds = float(map_json['expected_makespan'])

        for key, value in map_json['instances'].items():

            '''
            For each instance used on the pre-scheduling
            a queue of process is created accord with the 'map'
            '''
            instance_type = self.loader.env[value['type']]

            queue = Queue(instance_id=key,
                          instance_type=instance_type,
                          market=value['market'],
                          allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

            queue.build_queue_from_dict(self.loader.job, value['map'])

            # Create the Vm that will be used by the dispatcher
            vm = VirtualMachine(
                instance_type=instance_type,
                market=value['market'],
                loader=self.loader
            )

            # than a dispatcher, that will execute the tasks, is create

            dispatcher = Dispatcher(vm=vm, queue=queue, loader=self.loader)

            # check if the VM need to be register on the simulator
            if self.loader.simulation_conf.with_simulation and vm.market == CloudManager.PREEMPTIBLE:
                self.simulator.register_vm(vm)

            self.semaphore.acquire()

            self.working_dispatchers.append(dispatcher)

            self.semaphore.release()

    def __prepare_execution(self):
        """
           Prepare control database and all directories to start the execution process
        """
        # get job from control database
        jobs_repo = self.repo.get_jobs(
            filter={
                'job_id': self.loader.job.job_id
            }
        )

        # Check if Job is already in the database
        if len(jobs_repo) == 0:
            # add job to database
            self.__add_job_to_database()
        else:
            # Job is already in database
            # Check job and Instances consistency
            logging.info("<Scheduler Manager {}_{}>: - "
                         "Checking database consistency...".format(self.loader.job.job_id,
                                                                   self.loader.execution_id))

            job_repo = jobs_repo[0]

            assert job_repo.name == self.loader.job.job_name, "Consistency error (job name): {} <> {}".format(
                job_repo.name, self.loader.job.job_name)

            assert job_repo.description == self.loader.job.description, "Consistency error (job description): " \
                                                                        "{} <> {} ".format(job_repo.description,
                                                                                           self.loader.job.description)

            tasks_repo = job_repo.tasks.all()

            assert len(tasks_repo) == len(
                self.loader.job.tasks), "Consistency error (number of tasks): {} <> {} ".format(
                len(tasks_repo), len(self.loader.job.tasks)
            )

            # check tasks consistency
            for t in tasks_repo:
                assert str(t.task_id) in self.loader.job.tasks, "Consistency error (task id): {}".format(
                    t.task_id)

                task = self.loader.job.tasks[str(t.task_id)]

                assert task.memory == t.memory, "Consistency error (task {} memory): {} <> {} ".format(
                    task.task_id, t.memory, task.memory)

                assert task.command == t.command, "Consistency error (task {} command): {} <> {} ".format(
                    task.task_id, t.command, task.command)

                assert task.io == t.io, "Consistency error (task {} io):".format(task.task_id, t.io, task.io)

        # Check Instances Type
        for key, instance_type in self.loader.env.items():

            types = self.repo.get_instance_type(filter={
                'instance_type': key
            })

            if len(types) == 0:
                # add instance to control database
                self.__add_instance_type_to_database(instance_type)
            else:
                # check instance type consistency
                inst_type_repo = types[0]
                assert inst_type_repo.vcpu == instance_type.vcpu, "Consistency error (vcpu instance {}): " \
                                                                  "{} <> {} ".format(key,
                                                                                     inst_type_repo.vcpu,
                                                                                     instance_type.vcpu)

                assert inst_type_repo.memory == instance_type.memory, "Consistency error (memory instance {}):" \
                                                                      "{} <> {}".format(key,
                                                                                        inst_type_repo.memory,
                                                                                        instance_type.memory)

    def __add_job_to_database(self):
        """Record a Job and its tasks to the control database"""

        job_repo = JobRepo(
            id=self.loader.job.job_id,
            name=self.loader.job.job_name,
            description=self.loader.job.description
        )

        self.repo.add_job(job_repo)

        # add tasks
        for task_id, task in self.loader.job.tasks.items():
            self.repo.add_task(
                TaskRepo(
                    job=job_repo,
                    task_id=task.task_id,
                    command=task.command,
                    memory=task.memory,
                    io=task.io
                )
            )

    def __add_instance_type_to_database(self, instance_type):
        self.repo.add_instance_type(
            InstanceTypeRepo(
                type=instance_type.type,
                vcpu=instance_type.vcpu,
                memory=instance_type.memory,
                burstable=instance_type.burstable,
                provider=instance_type.provider
            )
        )

    '''
    ACTIONS FUNCTIONS
    '''

    def __work_stealing_burstable(self, idle_dispatcher: Dispatcher):

        stolen = False

        for work_dispatcher in self.working_dispatchers:

            if stolen:
                break

            if not work_dispatcher.vm.burstable and not stolen:
                # Get SEMAPHORE OF work Dispatcher
                work_dispatcher.semaphore.acquire()

                possible_to_be_stolen = work_dispatcher.get_possible_to_be_stolen(check_next_period=True)

                stolen = False

                # Thief loop
                for task in possible_to_be_stolen:
                    end = idle_dispatcher.queue.get_prospects(task, baseline=True)

                    EFT = datetime.now() + timedelta(seconds=end)

                    if EFT < self.deadline_timestamp and not stolen:
                        logging.info("<Scheduler Manager {}_{}>: - - WORK_STEALING_BURSTABLE "
                                     "Task '{}' was stolen by Burstable Instance:'{}' "
                                     "CPU_credits: '{}'".format(self.loader.job.job_id,
                                                                self.loader.execution_id,
                                                                task.task_id,
                                                                idle_dispatcher.vm.instance_id,
                                                                idle_dispatcher.vm.get_cpu_credits()))

                        task.burst_mode = False
                        task.allocated_cpu_credits = 0

                        work_dispatcher.remove_task(task)
                        idle_dispatcher.add_task(task)
                        # SET Burstable VM to baseline mode

                        stolen = True
                        break

                work_dispatcher.semaphore.release()

        if stolen:
            self.semaphore_count.acquire()
            self.n_burst_stealing += 1
            self.semaphore_count.release()

    def __work_stealing(self, idle_dispatcher: Dispatcher):

        # logging.info("Executing Work Stealing - instance '{}'".format(dispatcher.ec2_id))

        stolen = False

        for work_dispatcher in self.working_dispatchers:

            # Get SEMAPHORE OF work Dispatcher
            work_dispatcher.semaphore.acquire()

            possible_to_be_stolen: List[Task] = work_dispatcher.get_possible_to_be_stolen(check_next_period=True)

            # Thief loop
            for task in possible_to_be_stolen:
                end = idle_dispatcher.queue.get_prospects(task)

                EFT = datetime.now() + timedelta(seconds=end)

                if (idle_dispatcher.vm.market == CloudManager.PREEMPTIBLE and
                    EFT < self.deadline_timestamp - idle_dispatcher.task_max_timedelta) or \
                    (idle_dispatcher.queue.market == CloudManager.ON_DEMAND and EFT < self.deadline_timestamp):
                    # Stealing the task
                    logging.info(
                        "<Scheduler Manager {}_{}>: - - WORK_STEALING"
                        "Task '{}'' was stolen by Instance:'{}'".format(self.loader.job.job_id,
                                                                        self.loader.execution_id,
                                                                        task.task_id,
                                                                        idle_dispatcher.vm.instance_id))

                    work_dispatcher.remove_task(task)
                    idle_dispatcher.add_task(task)

                    stolen = True

            work_dispatcher.semaphore.release()

        if stolen:
            self.semaphore_count.acquire()
            self.n_work_stealing += 1
            self.semaphore_count.release()

    '''
    HANDLES FUNCTIONS
    '''

    def __idle_handle(self, dispatcher: Dispatcher):
        self.semaphore.acquire()

        if dispatcher in self.working_dispatchers:

            # To ensure that no one had put a new task during the IDLE EVENT
            if dispatcher.list_of_tasks.size == 0:
                self.working_dispatchers.remove(dispatcher)

                # clean queue
                dispatcher.reset_queue_structures()

                self.idle_dispatchers.append(dispatcher)

            else:
                dispatcher.waiting_work.set()

        self.semaphore.release()

    def __hibernation_handle(self, affected_tasks: List[Task], affected_dispatcher: Dispatcher):

        # Create a BACKUP PLAN

        self.semaphore.acquire()

        # Since the dispatcher had face a temporal fault we have to add it to the hibernated_pool
        self.hibernating_dispatcher.append(affected_dispatcher)
        self.working_dispatchers.remove(affected_dispatcher)

        affected_dispatcher.reset_queue_structures()

        self.semaphore.release()

        self.semaphore.acquire()

        self.scheduler.migrate(
            affected_tasks=affected_tasks,
            fault_dispatcher=affected_dispatcher,
            instances=self.loader.instances_list,
            deadline_timestamp=self.deadline_timestamp,
            fault_time_timestamp=datetime.now(),
            count_list=self.loader.count_list,
            idle_dispatchers=self.idle_dispatchers,
            working_dispatchers=self.working_dispatchers)
        # start migrate procedure

        self.hibernated_dispatcher.append(affected_dispatcher)
        self.hibernating_dispatcher.remove(affected_dispatcher)

        self.semaphore.release()

    def __fault_handle(self, event_timestamp: datetime, affected_dispatcher: Dispatcher, affected_tasks):
        # Move task to others VM
        self.semaphore.acquire()

        # migrate affected tasks
        self.scheduler.migrate(
            affected_tasks=affected_tasks,
            fault_dispatcher=affected_dispatcher,
            instances=self.loader.instances_list,
            deadline_timestamp=self.deadline_timestamp,
            fault_time_timestamp=event_timestamp,
            count_list=self.loader.count_list,
            idle_dispatchers=self.idle_dispatchers,
            working_dispatchers=self.working_dispatchers
        )

        # remove affected dispatcher from work list
        affected_dispatcher.working = False
        affected_dispatcher.waiting_work.set()
        self.working_dispatchers.remove(affected_dispatcher)
        self.terminated_dispatcher.append(affected_dispatcher)

        self.semaphore.release()

    def __error_handle(self, dispatcher: Dispatcher):
        self.semaphore.acquire()

        if dispatcher in self.working_dispatchers:

            if dispatcher.list_of_tasks.size == 0:
                self.working_dispatchers.remove(dispatcher)

                # clean queue
                # dispatcher.reset_queue_structures()

                self.terminated_dispatcher.append(dispatcher)

        else:
            dispatcher.waiting_work.set()

        self.semaphore.release()

    def __event_handle(self, event):
        event_timestamp: datetime = datetime.now()

        affected_dispatcher: Dispatcher = event.kwargs['dispatcher']

        # create lists of affected tasks
        affected_tasks: List[Task] = []  # TODO CREATE AFFECT TASKS BY STATE

        affected_tasks.extend(event.kwargs["running"])
        affected_tasks.extend(event.kwargs["waiting"])
        affected_tasks.extend(event.kwargs["hibernated"])

        logging.info("<Scheduler Manager {}_{}>: - EVENT_HANDLE "
                     "Instance: '{}', Type: '{}', Market: '{}',"
                     "Event: '{}'".format(self.loader.job.job_id,
                                          self.loader.execution_id,
                                          affected_dispatcher.vm.instance_id,
                                          affected_dispatcher.vm.type,
                                          affected_dispatcher.vm.market,
                                          event.value))

        if event.value == CloudManager.IDLE:
            logging.info("<Scheduler Manager {}_{}>: - Calling Idle Handle".format(self.loader.job.job_id,
                                                                                   self.loader.execution_id))

            self.__idle_handle(affected_dispatcher)

        elif event.value == CloudManager.HIBERNATED:
            self.semaphore_count.acquire()
            self.n_hibernations += 1
            self.semaphore_count.release()

            logging.info("<Scheduler Manager {}_{}>: - Calling Hibernation Handle".format(self.loader.job.job_id,
                                                                                          self.loader.execution_id))
            self.__hibernation_handle(affected_dispatcher=affected_dispatcher,
                                      affected_tasks=affected_tasks)

        elif event.value in [CloudManager.TERMINATED, CloudManager.ERROR]:
            logging.info("<Scheduler Manager {}_{}>: - Calling Terminate Handle".format(self.loader.job.job_id,
                                                                                        self.loader.execution_id))
            self.__fault_handle(event_timestamp=event_timestamp,
                                affected_dispatcher=affected_dispatcher,
                                affected_tasks=affected_tasks)

        # elif event.value in CloudManager.ERROR:
        #     # ERROR to initiate a new VM.
        #     logging.info("<Scheduler Manager {}_{}>: - Calling Fault Handle".format(self.loader.job.job_id,
        #                                                                             self.loader.execution_id))
        #     # self.__error_handle(affected_dispatcher)
        #     self.__fault_handle(event_timestamp=event_timestamp,
        #                         affected_dispatcher=affected_dispatcher,
        #                         affected_tasks=affected_tasks)

        # self.abort = True

        elif event.value in CloudManager.ABORT:
            self.abort = True

    '''
    CHECKERS FUNCTIONS
    '''

    def __check_idle_dispatchers(self):
        # REMOVE DISPATCHERS FROM IDLE POOL

        self.semaphore.acquire()

        work_preeptible = False

        for dispatcher in self.working_dispatchers:
            if dispatcher.vm.market == CloudManager.PREEMPTIBLE:
                work_preeptible = True

        for dispatcher in self.idle_dispatchers[:]:

            if not work_preeptible:

                dispatcher.working = False
                dispatcher.waiting_work.set()
                # update dispatcher lists
                self.idle_dispatchers.remove(dispatcher)
                self.terminated_dispatcher.append(dispatcher)

                logging.info("<Scheduler Manager {}_{}>: - IDLE HANDLE "
                             "Instance: '{}' Type: '{}' Market: '{}'. "
                             "Terminating instance. No more Preemptible Instances".format(self.loader.job.job_id,
                                                                                          self.loader.execution_id,
                                                                                          dispatcher.vm.instance_id,
                                                                                          dispatcher.vm.type,
                                                                                          dispatcher.vm.market))

            # if it is a burstable instance execute Burstable workstealing
            elif dispatcher.vm.burstable:

                # START WORKING STEALING
                self.__work_stealing_burstable(dispatcher)

            else:

                now = datetime.now()
                period_diff = dispatcher.next_period_end - now

                # check for a end of  period or termination
                if period_diff < timedelta(seconds=self.loader.input_conf.idle_slack_time) \
                    or dispatcher.vm.state == CloudManager.TERMINATED:

                    dispatcher.working = False
                    dispatcher.waiting_work.set()

                    # update dispatcher lists
                    self.idle_dispatchers.remove(dispatcher)
                    self.terminated_dispatcher.append(dispatcher)

                    # update count_list
                    self.loader.count_list[dispatcher.vm.type] -= 1

                elif dispatcher.vm.state == CloudManager.HIBERNATED:

                    self.semaphore_count.acquire()
                    self.n_hibernations += 1
                    self.semaphore_count.release()

                    # if instance hibernated while idle, then put it do hibernated_dispatcher
                    dispatcher.vm.update_hibernation_start()
                    self.idle_dispatchers.remove(dispatcher)
                    # add instance_status IDLE to database
                    self.repo.add_instance_status(

                        InstanceStatusRepo(
                            instance_id=dispatcher.vm.instance_id,
                            timestamp=datetime.now(),
                            status=EC2Manager.HIBERNATED)
                    )
                    # self.hibernations_number += 1
                    dispatcher.least_status = CloudManager.IDLE
                    self.hibernated_dispatcher.append(dispatcher)
                    dispatcher.vm.hibernation_process_finished = True

                elif dispatcher.vm.state == CloudManager.RUNNING:
                    # START WORKING STEALING
                    self.__work_stealing(dispatcher)

            if dispatcher.list_of_tasks.size > 0:
                self.idle_dispatchers.remove(dispatcher)
                self.working_dispatchers.append(dispatcher)
                dispatcher.waiting_work.set()

        self.semaphore.release()

    def __check_hibernated_dispatchers(self):
        self.semaphore.acquire()

        for dispatcher in self.hibernated_dispatcher[:]:

            # check for a return
            if dispatcher.vm.state == CloudManager.RUNNING:

                dispatcher.hibernated = False

                # TODO UPDATE END OF PERIOD
                dispatcher.update_hibernation_duration()

                logging.info("<Scheduler Manager {}_{}>: -  - Instance: '{}' Type: '{}' - Resume from hibernation."
                             "Hibernation Time: {}".format(self.loader.job.job_id,
                                                           self.loader.execution_id,
                                                           dispatcher.vm.instance_id,
                                                           dispatcher.vm.type,
                                                           dispatcher.vm.hibernation_duration
                                                           ))

                # START WORKING STEALING
                self.__work_stealing(dispatcher)

                if dispatcher.list_of_tasks.size > 0:
                    self.hibernated_dispatcher.remove(dispatcher)
                    self.working_dispatchers.append(dispatcher)

                    self.semaphore_count.acquire()
                    self.n_work_stealing += 1
                    self.semaphore_count.release()

                    dispatcher.waiting_work.set()
                else:
                    self.hibernated_dispatcher.remove(dispatcher)
                    self.idle_dispatchers.append(dispatcher)

                    self.repo.add_instance_status(
                        InstanceStatusRepo(instance_id=dispatcher.vm.instance_id,
                                           timestamp=datetime.now(),
                                           status=CloudManager.IDLE)
                    )

                    dispatcher.least_status = EC2Manager.IDLE

                self.semaphore_count.acquire()
                self.n_resume += 1
                self.semaphore_count.release()

            # check for a termination
            if dispatcher.vm.state == CloudManager.TERMINATED:
                dispatcher.update_hibernation_duration()
                self.hibernated_dispatcher.remove(dispatcher)
                self.terminated_dispatcher.append(dispatcher)

        self.semaphore.release()

    def __checkers(self):
        # Checker loop
        # Checker if all dispatchers have finished the execution
        while len(self.working_dispatchers) > 0 or len(self.hibernating_dispatcher) > 0:

            if self.abort:
                break

            # If new checkers would be created that function have to be updated
            self.__check_hibernated_dispatchers()
            self.__check_idle_dispatchers()
            time.sleep(5)

    '''
    Manager Functions
    '''

    def __start_working_dispatchers(self):
        self.semaphore.acquire()

        # Starting working dispatchers
        for dispatcher in self.working_dispatchers:
            dispatcher.main_thread.start()
            dispatcher.waiting_work.set()

        self.semaphore.release()

    def __terminate_dispatchers(self):

        if self.loader.debug_conf.debug_mode:
            logging.warning(100 * "#")
            logging.warning("\t<DEBUG MODE>: WAITING COMMAND TO TERMINATE -  PRESS ENTER")
            logging.warning(100 * "#")

            input("")

        logging.info("")
        logging.info("<Scheduler Manager {}_{}>: - Start termination process... ".format(self.loader.job.job_id,
                                                                                         self.loader.execution_id))

        # terminate simulation
        if self.loader.simulation_conf.with_simulation:
            self.simulator.stop_simulation()

        self.semaphore.acquire()

        # Terminate all HIBERNATED DISPATCHERS
        logging.info("<Scheduler Manager {}_{}>: - "
                     "Terminating working Dispatcher instances".format(self.loader.job.job_id,
                                                                       self.loader.execution_id))
        for working_dispatcher in self.working_dispatchers[:]:
            working_dispatcher.debug_wait_command = False

            working_dispatcher.working = False
            working_dispatcher.waiting_work.set()

            self.working_dispatchers.remove(working_dispatcher)
            self.terminated_dispatcher.append(working_dispatcher)

        # Terminate all HIBERNATED DISPATCHERS
        logging.info("<Scheduler Manager {}_{}>: - Terminating hibernated instances".format(self.loader.job.job_id,
                                                                                            self.loader.execution_id))
        for hibernated_dispatcher in self.hibernated_dispatcher[:]:
            hibernated_dispatcher.debug_wait_command = False

            hibernated_dispatcher.working = False
            hibernated_dispatcher.waiting_work.set()

            self.hibernated_dispatcher.remove(hibernated_dispatcher)
            self.terminated_dispatcher.append(hibernated_dispatcher)

        # Terminate all  idle_dispatchers
        logging.info("<Scheduler Manager {}_{}>: - Terminating idle instances".format(self.loader.job.job_id,
                                                                                      self.loader.execution_id))
        for idle_dispatcher in self.idle_dispatchers[:]:
            idle_dispatcher.debug_wait_command = False

            idle_dispatcher.working = False
            idle_dispatcher.waiting_work.set()

            self.idle_dispatchers.remove(idle_dispatcher)
            self.terminated_dispatcher.append(idle_dispatcher)

        # Confirm Termination
        logging.info("<Scheduler Manager {}_{}>: - Waiting Termination process...".format(self.loader.job.job_id,
                                                                                          self.loader.execution_id))
        for terminated_dispatcher in self.terminated_dispatcher[:]:
            terminated_dispatcher.debug_wait_command = False
            # waiting thread to terminate

            terminated_dispatcher.main_thread.join()

            # getting volume-id
            if self.loader.filesys_conf.type == EC2Manager.EBS:
                self.ebs_volumes.append(terminated_dispatcher.vm.volume_id)

        self.semaphore.release()

    def __end_of_execution(self):

        # end of execution
        self.end_timestamp = datetime.now()
        self.elapsed_time = (self.end_timestamp - self.start_timestamp)

        logging.info("<Scheduler Manager {}_{}>: - Waiting Termination...".format(self.loader.job.job_id,
                                                                                  self.loader.execution_id))

        cost = 0.0
        on_demand_count = 0
        preemptible_count = 0
        burstable_count = 0

        for dispatcher in self.terminated_dispatcher:
            
            if not dispatcher.vm.failed_to_created:

                if dispatcher.vm.market == CloudManager.ON_DEMAND:
                    if dispatcher.vm.burstable:
                        burstable_count += 1
                    else:
                        on_demand_count += 1
                else:
                    preemptible_count += 1

                cost += dispatcher.vm.uptime.seconds * (dispatcher.vm.price / 3600.0)  # price in seconds'

        logging.info("")

        if not self.abort:
            execution_info = "\tJob: {} Execution: {} Scheduler: {}\t".format(self.loader.job.job_id,
                                                                              self.loader.execution_id,
                                                                              self.loader.scheduler_name)
        else:
            execution_info = "\tJob: {} Execution: {} Scheduler: {}" \
                             " - EXECUTION ABORTED\t".format(self.loader.job.job_id,
                                                             self.loader.execution_id,
                                                             self.loader.scheduler_name)

        logging.info(50 * "#" + execution_info + 50 * "#")
        logging.info("")
        logging.info("\t Hibernation: {} " "Resume: {} " "Recovey: {} ""Timeout: {}".format(self.n_hibernations,
                                                                                            self.n_resume,
                                                                                            self.n_recovery,
                                                                                            self.n_timeout))

        total = on_demand_count + burstable_count + preemptible_count
        logging.info(
            "\t On-demand (not burstable): {} ""Burstable: {} Preemptible: {} Total: {}".format(on_demand_count,
                                                                                                burstable_count,
                                                                                                preemptible_count,
                                                                                                total))
        logging.info("\t Work-Stealing: {} BURST Work-Stealing: {}".format(self.n_work_stealing, self.n_burst_stealing))
        logging.info("")
        logging.info("")
        logging.info("\t Start Time: {}  End Time: {}".format(self.start_timestamp, self.end_timestamp))
        logging.info("\t Elapsed Time: {}".format(self.elapsed_time))
        logging.info("\t Deadline: {}".format(timedelta(seconds=self.loader.deadline_seconds)))
        logging.info("")
        logging.info("\t Number of Finished Tasks: {}".format(
            self.repo.get_number_of_tasks_by_status(execution_id=self.loader.execution_id,
                                                    job_id=self.loader.job.job_id, status=Task.FINISHED)))
        logging.info("\t Number of RUNTIME_ERROR Tasks: {}".format(
            self.repo.get_number_of_tasks_by_status(execution_id=self.loader.execution_id,
                                                    job_id=self.loader.job.job_id, status=Task.RUNTIME_ERROR)))

        logging.info("")
        logging.info("\t Execution Total Estimated monetary Cost: {}".format(cost))
        logging.info("")

        if self.loader.filesys_conf.type == CloudManager.EBS and not self.loader.filesys_conf.ebs_delete:
            logging.warning("The following EBS VOLUMES will note be deleted by HADS: ")
            for volume_id in self.ebs_volumes:
                logging.warning("\t-> {}".format(volume_id))

        logging.info("")
        logging.info(144 * "#")

        status = 'success'

        if self.abort:
            status = 'aborted'

        self.repo.add_statistic(
            StatisticRepo(execution_id=self.loader.execution_id,
                          job_id=self.loader.job.job_id,
                          status=status,
                          start=self.start_timestamp,
                          end=self.end_timestamp,
                          deadline=self.deadline_timestamp,
                          cost=cost)
        )


        self.repo.close_session()

        if self.abort:
            error_msg = "<Scheduler Manager {}_{}>: - " \
                        "Check all log-files. Execution Aborted".format(self.loader.job.job_id,
                                                                        self.loader.execution_id)
            logging.error(error_msg)
            raise Exception

    def start_execution(self):
        # subscriber events_handle
        subscribers.append(self.__event_handle)

        self.start_timestamp = datetime.now()
        # UPDATE DATETIME DEADLINE
        self.deadline_timestamp = self.start_timestamp + self.loader.deadline_timedelta

        self.expected_makespan_timestamp = self.start_timestamp + timedelta(seconds=self.expected_makespan_seconds)

        logging.info("<Scheduler Manager {}_{}>: - Starting Execution. "
                     "Expected Makespan: {} ."
                     "Expected Deadline: {}".format(self.loader.job.job_id,
                                                    self.loader.execution_id,
                                                    self.expected_makespan_timestamp,
                                                    self.deadline_timestamp))
        logging.info("")

        self.__start_working_dispatchers()

        # Call checkers loop
        self.__checkers()

        self.__terminate_dispatchers()

        self.__end_of_execution()
