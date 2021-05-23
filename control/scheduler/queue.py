from typing import Dict

from control.domain.instance_type import InstanceType
from control.domain.task import Task
from control.domain.job import Job

from control.managers.cloud_manager import CloudManager

from control.util.linked_list import LinkedList, Node

import copy


class CoreData:
    task: Task

    def __init__(self, task, start, end):
        """
        :param task:Task
        :param start: Float
        :param end: Float
        """

        self.task = task
        self.start = start
        self.end = end
        self.core_id = None

    def __lt__(self, other):
        return self.end <= other.start

    def __str__(self):
        return "<CoreData({}-({},{} - {}))>".format(self.task.task_id, self.start, self.end, self.task.memory)


class Queue:
    cores: Dict[int, LinkedList]

    def __init__(self, instance_id, instance_type: InstanceType, market, allow_parallel_execution):
        """
        :type instance: InstanceType
        """

        self.instance_id = instance_id
        self.instance_type = instance_type
        self.market = market
        # start core struct
        self.cores = {}

        self.makespan_seconds = 0.0
        self.expected_cost = 0.0
        self.expected_cost_ondemand = 0.0

        self.tasks_list = []
        if allow_parallel_execution:
            for i in range(self.instance_type.vcpu):
                self.cores[i] = LinkedList()
        else:
            self.cores[0] = LinkedList()

    def __check_memory(self, selected_core, start, end, task):
        """
        :param selected_core: int
        :param qtask:QTask
        :return:
        """

        shared_memory = 0.0

        for i in self.cores:

            if i != selected_core:

                aux = self.cores[i].head

                max_mem = 0.0

                while aux is not None:
                    if aux.data.start <= start and start < aux.data.end or \
                        aux.data.start < end and end < aux.data.end:

                        if max_mem < aux.data.task.memory:
                            max_mem = aux.data.task.memory

                    aux = aux.next

                shared_memory += max_mem

                if shared_memory + task.memory > self.instance_type.memory:
                    return False

        return True

    def __found_position(self, task, baseline):
        """
        :param task: Task
        """
        if baseline:
            runtime = int(task.get_runtime(self.instance_type.type) * (self.instance_type.baseline / 10.0))
        else:
            runtime = task.get_runtime(self.instance_type.type)

        data = CoreData(task, None, None)

        # look for the best place to put the task
        for core_i in self.cores:
            aux_i: Node = self.cores[core_i].tail

            # if there isn't tasks in that core
            if aux_i is None:
                baseline = start_time = 0.0
            else:
                baseline = start_time = aux_i.data.end

            end_time = start_time + runtime

            if (data.core_id is None or end_time < data.end) and self.__check_memory(core_i, start_time, end_time,
                                                                                     task):
                data.core_id = core_i
                data.start = start_time
                data.end = end_time

            # alignment analyses
            for core_j in self.cores:

                if core_j != core_i:
                    aux_j: Node = self.cores[core_j].head

                    while aux_j is not None:

                        if baseline < aux_j.data.end:

                            start_time = aux_j.data.end
                            end_time = start_time + runtime

                            if (data.end is None or end_time < data.end) and self.__check_memory(core_i, start_time,
                                                                                                 end_time,
                                                                                                 task):
                                data.core_id = core_i
                                data.start = start_time
                                data.end = end_time

                        aux_j = aux_j.next

        return data

    def insert(self, task, baseline=False):

        """
        :param task: Task
        :return: boolean
        """

        data = self.__found_position(task, baseline)

        self.cores[data.core_id].add_ordered(data)

        # update makespan
        if self.makespan_seconds < data.end:
            self.makespan_seconds = data.end

            # update cost
        price = self.instance_type.price_ondemand if self.market == CloudManager.ON_DEMAND \
            else self.instance_type.price_preemptible

        self.expected_cost = (price / 3600) * self.makespan_seconds  # converte price to seconds
        self.expected_cost_ondemand = (self.instance_type.price_ondemand / 3600) * self.makespan_seconds

        # Update task info

        task.expected_start = data.start
        task.expected_end = data.end
        self.tasks_list.append(task)

        # TODO return boolean
        return data.start, data.end

    def get_prospects(self, task, baseline=False):
        """
        Return the makespan and the cost generated with the insertion of the task
        :param task: Task
        :param baseline: Boolean
        :return: float
        """

        data = self.__found_position(task, baseline)

        return data.end

    def to_dict(self):
        dict = {}
        for core_id, linked_list in self.cores.items():

            key = "vcpu_{}".format(core_id)
            dict[key] = {}

            aux = linked_list.head

            while aux is not None:
                dict[key][str(aux.data.task.task_id)] = {
                    "start": aux.data.start,
                    "end": aux.data.end
                }
                aux = aux.next
        return dict

    def print_queue(self):
        print(self.instance_type)
        print(self.market)
        for i in self.cores:
            aux = self.cores[i].head
            print(i, ": ", end="")
            while aux is not None:
                print(aux.data, end=", ")
                aux = aux.next
            print("")

    def build_queue_from_dict(self, job: Job, adict):

        for vcpu, item in adict.items():

            core_i = int(vcpu.split("_")[-1])

            for id, info in item.items():
                start = float(info['start'])
                end = float(info['end'])

                task = copy.copy(job.tasks[id])

                task.expected_start = start
                task.expected_end = end

                # update expect start and end of task
                # task.update_expected_execution_time(start, end)

                self.tasks_list.append(task)
                self.cores[core_i].add_ordered(CoreData(task, start, end))

                # update makespan
                if self.makespan_seconds < end:
                    self.makespan_seconds = end

    def get_parallel_tasks_at_time(self, start, end):
        # which tasks will be running at time p ?

        parallel_tasks = []

        for key, core in self.cores.items():
            aux = core.head

            while aux is not None:
                # check if task is parallel
                if start <= aux.data.start <= end or start <= aux.data.end <= end \
                    or aux.data.start <= start <= aux.data.end:
                    parallel_tasks.append(aux.data.task)
                aux = aux.next

        return parallel_tasks

    def pop(self):
        if len(self.tasks_list) > 0:
            task = self.tasks_list.pop()
            self.remove(task)
            return task
        else:
            raise Exception("Queue Exception: Queue Pop Error")

    def remove(self, task):
        if task in self.tasks_list:
            self.tasks_list.remove(task)

        to_remove = None
        to_remove_core = None
        for i in self.cores:
            aux = self.cores[i].head
            while aux is not None:
                if aux.data.task.task_id == task.task_id:
                    to_remove = aux.data
                    to_remove_core = i

                aux = aux.next

        if to_remove is not None:
            self.cores[to_remove_core].remove([to_remove])

        self.update()

    def update(self):

        self.makespan_seconds = 0.0

        # UPDATE MAKESPAN
        for i in self.cores:
            aux = self.cores[i].head
            while aux is not None:
                if self.makespan_seconds is None or self.makespan_seconds < aux.data.end:
                    self.makespan_seconds = aux.data.end

                aux = aux.next

        # update cost
        price = self.instance_type.price_ondemand if self.market == CloudManager.ON_DEMAND \
            else self.instance_type.price_preemptible

        self.expected_cost = (price / 3600) * self.makespan_seconds  # converte price to seconds
        self.expected_cost_ondemand = (self.instance_type.price_ondemand / 3600) * self.makespan_seconds
