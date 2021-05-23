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
from pathlib import Path

import uuid
import random
import math
import logging

import copy


class IPDPS(Scheduler):
    class Solution:
        def __init__(self, allocation_array: List[str], fitness, cost, makespan):
            self.allocation_array = allocation_array
            self.fitness = fitness
            self.cost = cost
            self.makespan = makespan

    def __init__(self, loader: Loader):

        self.loader = loader

        self.execution_id = self.loader.execution_id

        self.job = self.loader.job

        self.tasks = self.job.tasks
        self.instances = self.loader.env
        self.deadline = self.loader.deadline_timedelta

        self.max_ondemand = self.loader.max_ondemand
        self.max_preemptible = self.loader.max_preemptible

        self.count_dict = {}
        self.vcpu_limits = self.loader.ec2_conf.vcpu_limits

        self.count_ondemand = 0
        self.count_preemptible = 0

        self.initial_cost = 0
        self.initial_makespan = 0

        self.d_spot = self.compute_dspot(instances=self.instances,
                                         tasks=self.tasks,
                                         max_ondemand=self.max_ondemand,
                                         deadline=self.deadline,
                                         allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

        self.ils_dspot = self.d_spot.seconds

        self.max_cost = None
        self.max_time = self.deadline.seconds
        self.alpha = self.loader.scheduler_conf.alpha
        self.burst_rate = self.loader.scheduler_conf.burstable_factor
        self.max_iteration = self.loader.scheduler_conf.max_iteration

        self.on_demand_instances: List[InstanceType] = []
        self.preemptible_instances: List[InstanceType] = []
        self.burstable_instances: List[InstanceType] = []
        self.tasks_list: List[Task] = []

        self.selected_instances: Dict[str, (InstanceType, str)] = {}

        self.rr_list = None

        self.__prepare_scheduler()
        # determine max cost
        #
        # logging.info("ILS alpha = {} D_spot: {} Deadline: {} ".format(
        #     self.alpha, self.d_spot, deadline
        # ))

    def __prepare_scheduler(self):

        # create listS with the instances ON_DEMAND  and PREEMPTIBLE
        for key, instance in self.instances.items():
            if instance.burstable:
                self.burstable_instances.append(instance)
            else:
                if instance.market_ondemand:
                    self.on_demand_instances.append(instance)
                if instance.market_preemptible:
                    self.preemptible_instances.append(instance)

        max_rank = max(self.preemptible_instances, key=lambda item: item.rank)
        min_rank = min(self.preemptible_instances, key=lambda item: item.rank)

        # build round round robin list
        self.rr_list = self.build_roundrobin_list(max_rank.rank, min_rank.rank, self.preemptible_instances)

        # Create a list of tasks
        for key, task in self.tasks.items():
            self.tasks_list.append(task)
        self.tasks_list.sort(key=lambda x: x.memory, reverse=True)

        # Sort on_demand instance by price in ascendant order (Heuristic Execution)
        self.on_demand_instances.sort(key=lambda x: x.price_ondemand)

    def __allocation_array_to_queues(self, allocation_array):

        queues: Dict[str, Queue] = {}
        queues_list: List[Queue] = []

        for task_id in range(len(allocation_array)):
            instance_id = allocation_array[task_id]

            task = self.tasks[str(task_id)]

            if instance_id in queues:
                queue = queues[instance_id]
            else:
                instance, market = self.selected_instances[instance_id]

                queue = Queue(instance_id=instance_id,
                              instance_type=instance,
                              market=market,
                              allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

                queues[queue.instance_id] = queue
                queues_list.append(queue)

            queue.insert(task)

        return queues_list

    # receive: list of tasks, on_demand VMs, preemptible_vms and round_robin selection if rr == True
    # return: allocation_array, queues_dict
    def __static_scheduler(self, tasks: List[Task], preemptible_instances: List[InstanceType], rr_list, rr=True):

        self.count_dict = {}
        self.count_ondemand = 0
        self.count_preemptible = 0

        self.selected_instances: Dict[str, (InstanceType, str)] = {}

        allocation_array: List[str] = [None] * self.job.num_tasks

        queues = []

        # START SCHEDULING, To each Task do
        for task in tasks:

            allocated = False

            queues.sort(key=lambda x: x.makespan_seconds)

            # try to a locate tasks on an already selected instance
            for queue in queues:

                EFT = timedelta(seconds=queue.get_prospects(task))

                if (queue.market == CloudManager.PREEMPTIBLE and EFT < self.d_spot) or \
                    (queue.market == CloudManager.ON_DEMAND and EFT < self.deadline):
                    # If the instance is Preemptible check the d_spot limit
                    # Otherwise check the deadline
                    # allocate task to instance
                    queue.insert(task)

                    # UPDATE allocation_array
                    allocation_array[task.task_id] = queue.instance_id

                    allocated = True
                    break

            if not allocated:
                for instance in preemptible_instances:
                    # try to allocate the task on a  new Preempetible VM

                    if rr:
                        instance: InstanceType = rr_list()

                    # check the limit of instances and if migration restriction will be respected
                    queue = Queue(instance_id=uuid.uuid4(),
                                  instance_type=instance,
                                  market=CloudManager.PREEMPTIBLE,
                                  allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)

                    EFT = timedelta(seconds=queue.get_prospects(task))
                    # check instance allocated limits and EFT Limits

                    if instance.type not in self.count_dict:
                        self.count_dict[instance.type] = 0

                    if self.count_preemptible < self.max_preemptible and self.count_dict[instance.type] < \
                        instance.limits_preemptible and EFT < self.d_spot:
                        # allocate Task
                        queue.insert(task)

                        self.selected_instances[queue.instance_id] = instance, queue.market

                        # update queues and count_dict
                        queues.append(queue)
                        self.count_dict[queue.instance_type.type] += 1
                        self.count_preemptible += 1

                        # update allocation_array
                        allocation_array[task.task_id] = queue.instance_id

                        allocated = True
                        break

            # THERE IS NO SOLUTION BEFORE DE DEADLINE TO THIS APPLICATION!
            if not allocated:
                raise Exception("THERE IS NO SOLUTION WITH THAT DEADLINE TO JOB '{}' !".format(self.loader.job.job_id))

        return allocation_array

    def __compute_fitness(self, solution: Solution):

        # cost, makespan = self.get_cost_and_makespan(self.__allocation_array_to_queues(allocation_array))

        queues = self.__allocation_array_to_queues(solution.allocation_array)

        cost = 0.0
        makespan = 0.0
        real_mkp = 0.0
        total_vcpu = 0

        # GET COST AND MAKESPAN
        for queue in queues:
            total_vcpu += queue.instance_type.vcpu
            # Deadline RULE!
            if queue.market == CloudManager.PREEMPTIBLE and queue.makespan_seconds > self.ils_dspot or total_vcpu > self.vcpu_limits:
                makespan = float("inf")
                # logging.info("D SPOT RULE Violated! Makespan: {}".format(makespan))

            if makespan < queue.makespan_seconds:
                makespan = queue.makespan_seconds

            if real_mkp < queue.makespan_seconds:
                real_mkp = queue.makespan_seconds

            cost += queue.expected_cost

        makespan_norm = makespan / self.ils_dspot

        # logging.info("COST: {} Makespan : {}".format(cost, makespan_norm))
        solution.fitness = (self.alpha * cost) + ((1 - self.alpha) * makespan_norm)
        solution.cost = cost
        solution.makespan = real_mkp

        return solution

    def __local_search_n1(self, solution_s0: Solution):
        solution = copy.deepcopy(solution_s0)

        #  DO LOCAL SEARCH
        p1 = random.randint(0, self.job.num_tasks - 1)
        p2 = random.randint(0, self.job.num_tasks - 1)

        temp = solution.allocation_array[p1]
        solution.allocation_array[p1] = solution.allocation_array[p2]
        solution.allocation_array[p2] = temp

        solution = self.__compute_fitness(solution)

        if solution.fitness < solution_s0.fitness:
            return solution

        else:
            return solution_s0

    def __local_search_n2(self, solution_s0: Solution):
        solution = copy.deepcopy(solution_s0)

        #  DO LOCAL SEARCH

        instance_id = random.choice(list(self.selected_instances.keys()))

        p1 = random.randint(0, self.job.num_tasks - 1)
        p2 = random.randint(0, self.job.num_tasks - 1)

        solution.allocation_array[p1] = instance_id
        solution.allocation_array[p2] = instance_id

        solution = self.__compute_fitness(solution)

        if solution.fitness < solution_s0.fitness:
            return solution

        else:
            return solution_s0

    def __local_search_n5(self, solution_s0: Solution, rate=0.1):
        solution = copy.deepcopy(solution_s0)

        #  DO LOCAL SEARCH

        instance_id = random.choice(list(self.selected_instances.keys()))

        n_tasks = math.floor(rate * self.job.num_tasks)

        for i in range(n_tasks):
            p1 = random.randint(0, self.job.num_tasks - 1)

            solution.allocation_array[p1] = instance_id

            solution = self.__compute_fitness(solution)

            if solution.fitness < solution_s0.fitness:
                return solution

        return solution_s0

    def __swap_vm(self, solution_s0, market):
        solution = copy.deepcopy(solution_s0)
        instance = random.choice(list(self.instances.values()))
        id = uuid.uuid4()

        can_go = False

        if not instance.burstable:

            if instance.type not in self.count_dict:
                self.count_dict[instance.type] = 0

            self.count_dict[instance.type] += 1

            if market == CloudManager.PREEMPTIBLE and self.count_preemptible < self.max_preemptible:
                if self.count_dict[instance.type] < instance.limits_preemptible:
                    self.count_preemptible += 1
                    can_go = True

            if market == CloudManager.ON_DEMAND and self.count_ondemand < self.max_ondemand:
                if self.count_dict[instance.type] < instance.limits_ondemand:
                    self.count_ondemand += 1
                    can_go = True

        if can_go:
            self.selected_instances[id] = instance, market

            p1 = random.randint(0, self.job.num_tasks - 1)
            p2 = random.randint(0, self.job.num_tasks - 1)

            solution.allocation_array[p1] = id
            solution.allocation_array[p2] = id

            solution = self.__compute_fitness(solution)

        if solution.fitness < solution_s0.fitness:
            return solution
        else:
            return solution_s0

    def __pertubation(self, solution_s0: Solution, last_best_iteration, iteration):

        solution = self.__swap_vm(solution_s0, market=CloudManager.PREEMPTIBLE)
        # solution = self.__swap_vm(solution, market=CloudManager.ON_DEMAND)

        if (iteration - last_best_iteration) > 20:
            self.ils_dspot += self.ils_dspot * 0.25
            logging.info("###########################  relaxed D_spot: {}".format(self.ils_dspot))

        return solution

    def __local_search(self, solution: Solution, max_attempts):
        count = 0

        while count < max_attempts:
            solution = self.__local_search_n1(solution)
            solution = self.__local_search_n2(solution)
            solution = self.__local_search_n5(solution)

            count = count + 1

        return solution

    def __iterated_search(self, max_attempts=100, max_iterations=100):

        allocation_array = self.__static_scheduler(tasks=self.tasks_list,
                                                   preemptible_instances=self.preemptible_instances,
                                                   rr_list=self.rr_list,
                                                   rr=True)
        solution = IPDPS.Solution(allocation_array=allocation_array,
                                  fitness=0.0,
                                  cost=0.0,
                                  makespan=0.0)

        solution = self.__compute_fitness(solution)

        logging.info("INITIAL SOLUTION  Fitness: {} Cost: {} Makespan: {} ".format(solution.fitness,
                                                                                   solution.cost,
                                                                                   solution.makespan))

        # solution = self.__local_search(solution, max_attempts)
        best_solution: IPDPS.Solution = copy.deepcopy(solution)
        global_best: IPDPS.Solution = copy.deepcopy(solution)
        iteration = 0

        last_best_iteration = 0
        while iteration < max_iterations:
            solution = self.__pertubation(solution, last_best_iteration, iteration)
            solution = self.__local_search(solution, max_attempts=max_attempts)

            if solution.fitness < best_solution.fitness:
                best_solution = copy.deepcopy(solution)

                logging.info("Iteration: {} Fitness: {} Cost: {} Makespan: {} ".format(iteration,
                                                                                       best_solution.fitness,
                                                                                       best_solution.cost,
                                                                                       best_solution.makespan))
                last_best_iteration = iteration

                real_fitness = (self.alpha * best_solution.cost) + (
                    (1 - self.alpha) * best_solution.makespan / self.d_spot.seconds)

                if real_fitness < global_best.fitness:
                    global_best = copy.deepcopy(best_solution)

            iteration += 1

        return global_best

    def __burstable_allocation(self, solution: Solution):
        queues: List[Queue] = self.__allocation_array_to_queues(solution.allocation_array)

        logging.info("Burstable Alloccation")
        # restart count_dict and selected instances
        self.count_dict = {}
        self.count_ondemand = 0
        self.count_preemptible = 0

        violating_tasks = []
        for queue in queues:

            print(queue.instance_id)

            # getting violating tasks
            if queue.makespan_seconds > self.d_spot.seconds:
                while queue.makespan_seconds > self.d_spot.seconds:
                    logging.info("ENTROU D_SPOT VIOLATION")
                    print("Makespan antes: {}".format(queue.makespan_seconds))
                    task = queue.pop()
                    print("Makespan depois: {}".format(queue.makespan_seconds))
                    violating_tasks.append(task)

            # Update count dict
            if queue.instance_type.type not in self.count_dict:
                self.count_dict[queue.instance_type.type] = 0
            self.count_dict[queue.instance_type.type] += 1

            if queue.market == CloudManager.ON_DEMAND:
                self.count_ondemand += 1
            else:
                self.count_preemptible += 1

        # Create a list of queues with burstable VMs type.
        burst_queues: List[Queue] = []
        n_burst = math.ceil(self.burst_rate * len(queues))
        logging.info("Inserting burstables n_burst : {}".format(n_burst))
        while len(burst_queues) < n_burst:

            inserted = False
            for instance in self.burstable_instances:
                print(instance)
                if instance.type not in self.count_dict:
                    self.count_dict[instance.type] = 0

                if self.count_dict[instance.type] < instance.limits_ondemand:
                    burst_queues.append(Queue(
                        instance_id=uuid.uuid4(),
                        instance_type=instance,
                        market=CloudManager.ON_DEMAND,
                        allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution
                    ))
                    self.count_dict[instance.type] += 1
                    self.count_ondemand += 1

                    inserted = True
                    break

            if not inserted:
                logging.info("##################### Not fullfill N_burst: {} ###################### ".format(n_burst))
                break

            if self.count_ondemand > self.max_ondemand:
                raise Exception("Burstable insert error: On-demand limits reached!")

        # scheduling violating tasks

        logging.info("Scheduling Violating TAsks size: {}".format(len(violating_tasks)))
        while len(violating_tasks) > 0:

            task = violating_tasks.pop()
            allocated = False
            for queue in burst_queues[:]:
                queue.insert(task, baseline=True)
                burst_queues.remove(queue)
                queues.append(queue)
                allocated = True

            if not allocated:

                for instance in self.burstable_instances:
                    if instance.type not in self.count_dict:
                        self.count_dict[instance.type] = 0

                    if self.count_dict[
                        instance.type] < instance.limits_ondemand and self.count_ondemand < self.max_ondemand:
                        queue = Queue(instance_id=uuid.uuid4(),
                                      instance_type=instance,
                                      market=CloudManager.ON_DEMAND,
                                      allow_parallel_execution=self.loader.scheduler_conf.allow_parallel_execution)
                        queue.insert(task)
                        queues.append(queue)
                        self.count_dict[instance.type] += 1
                        self.count_ondemand += 1

                        allocated = True

            if not allocated:
                raise Exception("VIolating TAsks BURST ALLOCATION ERROR!")

        logging.info("Remove IDLE burstable VMS.")
        # find task to insert o idle burstable VM.
        while len(burst_queues) > 0:
            burst_queue = burst_queues.pop()
            queues.sort(key=lambda x: x.makespan_seconds, reverse=True)

            allocated = False
            for queue in queues[:]:
                if not queue.instance_type.burstable:
                    task = queue.pop()
                    burst_queue.insert(task, baseline=True)
                    queues.append(burst_queue)
                    allocated = True
                    break

            if not allocated:
                raise Exception("Burst Allocation error: IDLE BURSTABLE Phase!")

        logging.info("remove IDLE regular VMs")
        for queue in queues[:]:
            if len(queue.tasks_list) == 0:
                queues.remove(queue)

        return queues

    def compute_makespan_and_cost(self, queues: List[Queue]):

        cost = 0.0
        makespan = 0

        for queue in queues:
            queue.expected_cost += cost
            if makespan < queue.makespan_seconds:
                makespan = queue.makespan_seconds

        return cost, makespan

    def create_primary_map(self):
        solution = self.__iterated_search(max_iterations=self.max_iteration)

        queues_on_demand = self.__allocation_array_to_queues(solution.allocation_array)

        queues_burst = self.__burstable_allocation(solution)

        counting = {}
        on_demand_counting = 0
        preemptible_counting = 0
        total_tasks = 0
        vcpu_total = 0

        for queue in queues_burst:
            total_tasks += len(queue.tasks_list)
            vcpu_total += queue.instance_type.vcpu

            if queue.market == CloudManager.ON_DEMAND:
                on_demand_counting += 1

            else:
                preemptible_counting += 1

            if queue.instance_type.type not in counting:
                counting[queue.instance_type.type] = 1
            else:
                counting[queue.instance_type.type] += 1

        for key, value in counting.items():
            print("Key: {}  #: {} ".format(key, value))

        logging.info("# VMs on-demand: {} # preemptible: {} # vCPU: {}. Total tasks: {}".format(on_demand_counting,
                                                                                                preemptible_counting,
                                                                                                vcpu_total,
                                                                                                total_tasks))

        cost_on_demand_real = cost_on_demand = 0
        makespan_on_demand = 0

        for queue in queues_on_demand:
            queue.market = CloudManager.ON_DEMAND
            queue.update()

            cost_on_demand += queue.expected_cost_ondemand
            cost_on_demand_real += queue.expected_cost

            if makespan_on_demand < queue.makespan_seconds:
                makespan_on_demand = queue.makespan_seconds

        logging.info("########### ON-DEMAND ONLY - Cost: {} Makespan: {} Cost_Real: {} ################".format(
            cost_on_demand_real,
            makespan_on_demand,
            cost_on_demand))

        Scheduler.write_json(queues=queues_burst,
                             job_id=self.job.job_id,
                             job_name=self.job.job_name,
                             expected_makespan_seconds=solution.makespan,
                             expected_cost=solution.cost,
                             deadline_seconds=self.deadline.seconds,
                             file_output=self.loader.map_file,
                             scheduler_name=self.name)

        Scheduler.write_json(queues=queues_on_demand,
                             job_id=self.job.job_id,
                             job_name=self.job.job_name,
                             expected_makespan_seconds=solution.makespan,
                             expected_cost=solution.cost,
                             deadline_seconds=self.deadline.seconds,
                             file_output=self.loader.map_file + "_ondemand",
                             scheduler_name=self.name)

    # WARNING: THAT FUNCTION ALWAYS HAVE TO BE CALLING INSIDE A SEMAPHORE AREA
    def migrate(self, affected_tasks: List[Task], fault_dispatcher: Dispatcher,
                instances: List[InstanceType], deadline_timestamp: datetime,
                fault_time_timestamp: datetime, count_list: Dict[str, int],
                idle_dispatchers: List[Dispatcher], working_dispatchers: List[Dispatcher]):

        used_idle = {}

        leftover: List[Task] = []

        # Try to migrate tasks to burstable VMs
        for task in affected_tasks:
            allocated = False

            # Trying to migrate the  task to a idle bustable VM
            if len(idle_dispatchers) > 0:

                for dispatcher in idle_dispatchers:

                    if dispatcher.vm.burstable:

                        end = dispatcher.queue.get_prospects(task)
                        # TODO DEBUG
                        EFT = datetime.now() + timedelta(seconds=end)

                        runtime_min = math.floor(task.get_runtime(dispatcher.vm.instance_type.type) / 60.0)
                        cpu_credits = dispatcher.vm.get_cpu_credits()

                        if EFT < deadline_timestamp and cpu_credits >= runtime_min and dispatcher.list_of_tasks.size < dispatcher.vm.instance_type.vcpu:

                            task.allocated_cpu_credits = runtime_min
                            task.burst_mode = True
                            dispatcher.vm.reserve_credits(task.allocated_cpu_credits)

                            dispatcher.add_task(task)

                            if dispatcher.vm.instance_id not in used_idle:
                                used_idle[dispatcher.vm.instance_id] = dispatcher

                            logging.info("Migrate task '{}' to idle BURST resource '{}' - CPU Credits: '{}'".format(
                                task.task_id,
                                dispatcher.vm.instance_id,
                                dispatcher.vm.get_cpu_credits()
                            ))

                            break

            if not allocated:
                leftover.append(task)

        # update affected tasks with leftovers
        affected_tasks = leftover
        # reset leftovers lits
        leftover: List[Task] = []

        # Try to migrate task to a NOT burstable VMs
        for task in affected_tasks:
            allocated = False

            # Migrating tasks to idle resources (NOT BURSTABLE)
            if len(idle_dispatchers) > 0:  # check if there is idle VMs

                # Sort idle dispatcher to ...
                idle_dispatchers.sort(key=lambda x: x.queue.market, reverse=True)

                for dispatcher in idle_dispatchers:

                    if dispatcher.vm.state == CloudManager.RUNNING and not dispatcher.vm.burstable:

                        end = dispatcher.queue.get_prospects(task)

                        # TODO DEBUG
                        EFT = datetime.now() + timedelta(seconds=end)
                        diff = deadline_timestamp - EFT

                        # if it is a spot VM, we have to check hypothesis 2
                        # otherwise if instance is on-demand check only the deadline
                        if (
                            dispatcher.vm.market == CloudManager.PREEMPTIBLE and diff < dispatcher.task_max_timedelta) \
                            or (dispatcher.vm.market == CloudManager.ON_DEMAND and EFT < deadline_timestamp):

                            dispatcher.add_task(task)

                            logging.info("Migrate task '{}' to idle resource '{}' - '{}'".format(
                                task.task_id,
                                dispatcher.vm.instance_id,
                                dispatcher.vm.market
                            ))

                            if dispatcher.vm.instance_id not in used_idle:
                                used_idle[dispatcher.vm.instance_id] = dispatcher

                            break

            # Migrating tasks to work resources
            if not allocated and len(working_dispatchers) > 0:
                # Sort work dispatcher to ...
                working_dispatchers.sort(key=lambda x: x.queue.market, reverse=True)

                # check if there are working dispatchers available
                for dispatcher in working_dispatchers:

                    if dispatcher is not fault_dispatcher and dispatcher.working and not dispatcher.vm.burstable:

                        end = dispatcher.queue.get_prospects(task)

                        EFT = dispatcher.vm.start_time + dispatcher.vm.hibernation_duration + timedelta(
                            seconds=end)

                        # if dispatcher is spot VM check hypotheses 2
                        # otherwise check deadline
                        if (
                            dispatcher.vm.market == CloudManager.PREEMPTIBLE and deadline_timestamp - EFT < dispatcher.task_max_timedelta) \
                            or (dispatcher.vm.market == CloudManager.ON_DEMAND and EFT < deadline_timestamp):
                            dispatcher.add_task(task)

                            logging.info("Migrate task '{}' to working resource '{}'".format(
                                task.task_id,
                                dispatcher.vm.instance_id
                            ))

                            break

            if not allocated:
                leftover.append(task)

        # update affected tasks
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
                loader=self.loader
            )

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

                    if instance.burstable:
                        continue

                    # self, instance, market, deadline):
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
        return "ipdps"
