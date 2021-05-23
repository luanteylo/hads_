from control.scheduler.schedulers import Scheduler
from control.scheduler.queue import Queue

from control.domain.instance_type import InstanceType
from control.domain.task import Task

from control.managers.cloud_manager import CloudManager
from control.managers.dispatcher import Dispatcher
from control.managers.virtual_machine import VirtualMachine

from control.util.loader import Loader

from datetime import timedelta
from datetime import datetime

from typing import List, Dict

import uuid
from pathlib import Path

import logging


class CCScheduler(Scheduler):

    def __init__(self, loader: Loader):

        self.loader = loader

        self.execution_id = loader.execution_id

        self.job = loader.job

        self.tasks = self.job.tasks
        self.instances = loader.env
        self.deadline = loader.deadline_timedelta

        self.max_ondemand = loader.max_ondemand
        self.max_preemptible = loader.max_preemptible

        self.expected_makespan_seconds = 0.0
        self.expected_cost = 0.0
        self.expected_cost_ondemand = 0.0
        self.queues: List[Queue] = []

        self.d_spot = self.compute_dspot(instances=loader.env,
                                         tasks=self.tasks,
                                         max_ondemand=self.max_ondemand,
                                         deadline=self.deadline,
                                         allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

    def create_primary_map(self):

        count_dict = {}
        ondemand_instances = []
        preemptible_instances = []

        tasks_list = []

        logging.info("Scheduling D_spot: {}".format(self.d_spot))

        # create a list with the instances and start the count_dict
        for key, instance in self.instances.items():
            if instance.market_ondemand and not instance.burstable:
                ondemand_instances.append(instance)

            if instance.market_preemptible and not instance.burstable:
                preemptible_instances.append(instance)

            count_dict[key] = 0

        max_rank = max(preemptible_instances, key=lambda item: item.rank)
        min_rank = min(preemptible_instances, key=lambda item: item.rank)

        ondemand_instances.sort(key=lambda x: x.price_ondemand)

        # build round round robin list
        rr_list = self.build_roundrobin_list(max_rank.rank, min_rank.rank, preemptible_instances)

        # Create a list of tasks
        for key, task in self.tasks.items():
            tasks_list.append(task)

        tasks_list.sort(key=lambda x: x.memory, reverse=True)

        # START SCHEDULING, To each Task do
        for task in tasks_list:

            allocated = False

            self.queues.sort(key=lambda x: x.makespan_seconds)

            # try to a locate tasks on an already selected instance
            for queue in self.queues:

                EFT = timedelta(seconds=queue.get_prospects(task))

                if (queue.market == CloudManager.PREEMPTIBLE and EFT < self.d_spot) or \
                    (queue.market == CloudManager.ON_DEMAND and EFT < self.deadline):
                    # If the instance is Preemptible check the d_spot limit
                    # Otherwise check the deadline
                    # allocate task to instance
                    queue.insert(task)
                    allocated = True
                    break

            if not allocated:
                for i in range(len(preemptible_instances)):
                    # try to allocate the task on a  new Preempetible VM
                    instance: InstanceType = rr_list()

                    # check the limit of instances and if migration restriction will be respected

                    queue = Queue(instance_id=uuid.uuid4(),
                                  instance_type=instance,
                                  market=CloudManager.PREEMPTIBLE,
                                  allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

                    EFT = timedelta(seconds=queue.get_prospects(task))
                    # check instance allocated limits and EFT Limits
                    if count_dict[instance.type] < instance.limits_preemptible and EFT < self.d_spot:
                        queue.insert(task)
                        # update queues and count_dict
                        self.queues.append(queue)
                        count_dict[queue.instance_type.type] += 1

                        allocated = True
                        break

            if not allocated:
                # Try to allocate the tasks on a new on-demand VM
                for instance in ondemand_instances:
                    queue = Queue(instance_id=uuid.uuid4(),
                                  instance_type=instance,
                                  market=CloudManager.ON_DEMAND,
                                  allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

                    EFT = timedelta(seconds=queue.get_prospects(task))

                    if count_dict[instance.type] < instance.limits_ondemand and EFT < self.deadline:
                        queue.insert(task)
                        self.queues.append(queue)
                        count_dict[queue.instance_type.type] += 1

                        allocated = True
                        break

            # THERE IS NO SOLUTION BEFORE DE DEADLINE TO THIS APPLICATION!
            if not allocated:
                raise Exception("THERE IS NO SOLUTION WITH THAT DEADLINE TO JOB '{}' !".format(self.loader.job.job_id))

        # GET COST AND MAKESPAN
        for queue in self.queues:
            if self.expected_makespan_seconds < queue.makespan_seconds:
                self.expected_makespan_seconds = queue.makespan_seconds

            self.expected_cost += queue.expected_cost
            self.expected_cost_ondemand += queue.expected_cost_ondemand

        Scheduler.write_json(queues=self.queues,
                             job_id=self.job.job_id,
                             job_name=self.job.job_name,
                             expected_makespan_seconds=self.expected_makespan_seconds,
                             expected_cost=self.expected_cost,
                             deadline_seconds=self.deadline.seconds,
                             file_output=self.loader.map_file,
                             scheduler_name="CC")

    def migrate(self, affected_tasks: List[Task], fault_dispatcher: Dispatcher,
                instances: List[InstanceType], deadline_timestamp: datetime,
                fault_time_timestamp: datetime, count_list: Dict[str, int],
                idle_dispatchers: List[Dispatcher], working_dispatchers: List[Dispatcher]):

        # WARNING: THAT FUNCTION ALWAYS HAVE TO BE CALLING INSIDE A SEMAPHORE AREA

        # Migrating tasks to idle resources
        used_idle = {}
        if len(idle_dispatchers) > 0:  # check if there is idle VMs
            leftover: List[Task] = []

            # Sort idle dispatcher to ...
            idle_dispatchers.sort(key=lambda x: x.queue.market, reverse=True)
            for task in affected_tasks:
                allocated = False

                for dispatcher in idle_dispatchers:

                    if dispatcher.vm.state == CloudManager.RUNNING and not dispatcher.hibernated:

                        end = dispatcher.queue.get_prospects(task)

                        # TODO DEBUG
                        EFT = datetime.now() + timedelta(seconds=end)

                        # if it is a spot VM, we have to check hypothesis 2
                        # otherwise if instance is on-demand check only the deadline
                        if (
                            dispatcher.vm.market == CloudManager.PREEMPTIBLE and
                            deadline_timestamp - EFT < dispatcher.task_max_timedelta) \
                            or (dispatcher.vm.market == CloudManager.ON_DEMAND and EFT < deadline_timestamp):

                            dispatcher.add_task(task)
                            allocated = True
                            logging.info("Migrate task '{}' to idle resource '{}' - '{}'".format(
                                task.task_id,
                                dispatcher.vm.instance_id,
                                dispatcher.vm.market
                            ))

                            if dispatcher.vm.instance_id not in used_idle:
                                used_idle[dispatcher.vm.instance_id] = dispatcher

                            break

                if not allocated:
                    leftover.append(task)

            affected_tasks = leftover

        # Migrating tasks to work resources
        if len(working_dispatchers) > 0:  # check if there are working dispatchers available
            leftover = []

            # Sort work dispatcher to ...
            working_dispatchers.sort(key=lambda x: x.queue.market, reverse=True)
            for task in affected_tasks:

                allocated = False

                for dispatcher in working_dispatchers:

                    if dispatcher is not fault_dispatcher and dispatcher.working and not dispatcher.hibernated:
                        end = dispatcher.queue.get_prospects(task)

                        EFT = dispatcher.vm.start_time + dispatcher.vm.hibernation_duration + timedelta(seconds=end)

                        # if dispatcher is spot VM check hypotheses 2
                        # otherwise check deadline
                        if (dispatcher.vm.market == CloudManager.PREEMPTIBLE
                            and deadline_timestamp - EFT < dispatcher.task_max_timedelta) \
                            or (dispatcher.vm.market == CloudManager.ON_DEMAND and EFT < deadline_timestamp):
                            dispatcher.add_task(task)
                            allocated = True

                            logging.info("Migrate task '{}' to working resource '{}'".format(
                                task.task_id,
                                dispatcher.vm.instance_id
                            ))

                            break

                if not allocated:
                    leftover.append(task)

            affected_tasks = leftover

        # MIGRATING TO NEW INSTANCES
        # Finally, try to scheduling to new Instances
        makespan_datetime: datetime
        queues, makespan_datetime, count_list = self.backup_heuristic(affected_tasks=affected_tasks,
                                                                      instances=instances,
                                                                      deadline_datetime=deadline_timestamp,
                                                                      fault_time_datetime=fault_time_timestamp,
                                                                      count_list=count_list)  # TODO CHECK MAKESPAN
        # WRITE BACKUP JSON FILE
        backup_file = Path(self.loader.input_conf.path,
                           "{}_{}_{}_backup.json".format(self.execution_id,
                                                         fault_dispatcher.vm.instance_id,
                                                         fault_dispatcher.migration_count))

        fault_dispatcher.migration_count += 1

        Scheduler.write_json_backup(queues=queues,
                                    deadline=deadline_timestamp,
                                    makespan=makespan_datetime,
                                    backup_file=backup_file)

        '''
        UPDATE List of Dispatchers
        '''

        # UPDATE THE IDLE_LIST
        for key, dispatcher in used_idle.items():
            idle_dispatchers.remove(dispatcher)
            dispatcher.waiting_work.set()
            working_dispatchers.append(dispatcher)

        for queue in queues:
            # define the manager

            new_dispatcher = Dispatcher(
                vm=VirtualMachine(
                    instance_type=queue.instance_type,
                    market=queue.market,
                    loader=self.loader
                ),
                queue=queue,
                loader=self.loader)

            # update list of instances
            working_dispatchers.append(new_dispatcher)

            new_dispatcher.main_thread.start()
            new_dispatcher.waiting_work.set()

    def backup_heuristic(self, affected_tasks: List[Task],
                         instances: List[InstanceType],
                         deadline_datetime: datetime,
                         fault_time_datetime: datetime,
                         count_list: Dict[str, int] = None):

        self.queues = []

        # sort by on-demand price
        instances.sort(key=lambda x: x.price_ondemand)

        if count_list is None:
            count_list = {}
            for instance in instances:
                count_list[instance.type] = 0

        for task in affected_tasks:

            allocated = False

            # try to allocate in an already selected on-demand VM

            self.queues.sort(key=lambda x: x.makespan_seconds)
            for queue in self.queues:
                end = queue.get_prospects(task)

                # TODO DEBUG
                EFT = fault_time_datetime + timedelta(seconds=end) + timedelta(
                    seconds=queue.instance_type.boot_overhead_seconds)

                if EFT < deadline_datetime:
                    # allocate task to instance
                    queue.insert(task)
                    allocated = True
                    break

            if not allocated:

                # get new Instances
                for instance in instances:
                    # self, instance, market, deadline):
                    if instance.burstable:
                        continue

                    instance_id = uuid.uuid4()
                    queue = Queue(instance_id=instance_id,
                                  instance_type=instance,
                                  market=CloudManager.ON_DEMAND,
                                  allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

                    end = queue.get_prospects(task)

                    aux_time_datetime = fault_time_datetime + timedelta(seconds=end) + timedelta(
                        seconds=instance.boot_overhead_seconds)
                    if aux_time_datetime < deadline_datetime and count_list[instance.type] < instance.limits_ondemand:
                        # allocate task to instance
                        queue.insert(task)
                        # Update Queue
                        self.queues.append(queue)
                        # update count list
                        count_list[instance.type] += 1
                        allocated = True
                        break

            # THERE IS NO SOLUTION BEFORE DE DEADLINE TO THIS TASK! Try to allocate task on a new on-demand VM
            if not allocated:
                for instance in instances:
                    if instance.burstable:
                        continue
                    instance_id = uuid.uuid4()
                    queue = Queue(instance_id=instance_id,
                                  instance_type=instance,
                                  market=CloudManager.ON_DEMAND,
                                  allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

                    if count_list[instance.type] < instance.limits_ondemand:
                        queue.insert(task)
                        self.queues.append(queue)
                        count_list[instance.type] += 1
                        break

        # GET Timedelta MAKESPAN
        aux = 0.0
        maximum_overhead_time = 0.0
        for queue in self.queues:
            if aux < queue.makespan_seconds:
                aux = queue.makespan_seconds

            if maximum_overhead_time < queue.instance_type.boot_overhead_seconds:
                maximum_overhead_time = queue.instance_type.boot_overhead_seconds

        makespan_datetime = fault_time_datetime + timedelta(seconds=aux) + timedelta(seconds=maximum_overhead_time)

        return self.queues, makespan_datetime, count_list

    @property
    def name(self):
        return "CC"
