import json

from control.scheduler.queue import Queue

from control.domain.instance_type import InstanceType
from control.domain.task import Task

from control.managers.cloud_manager import CloudManager

import uuid

from typing import List, Dict

from datetime import datetime, timedelta


class BackupScheduler:

    @classmethod
    def schedule_executors(self, affected_tasks: List[Task], instances: List[InstanceType], deadline_datetime: datetime,
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
                    instance_id = uuid.uuid4()
                    queue = Queue(instance_id=instance_id,
                                  instance_type=instance,
                                  market=CloudManager.ON_DEMAND)

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
                    instance_id = uuid.uuid4()
                    queue = Queue(instance_id=instance_id,
                                  instance_type=instance,
                                  market=CloudManager.ON_DEMAND)

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

    @classmethod
    def print_map(self, queues: Dict[str, Queue]):

        for id, queue in queues.items():
            queue.print_queue()

    @classmethod
    def write_json(self, queues: List[Queue], deadline, makespan, backup_file):
        # build a map
        dict = {"expected_makespan": makespan,
                "deadline": deadline,
                "instances": {}
                }

        for queue in queues:
            key = "id{}".format(queue.instance_id)
            dict['instances'][key] = {"type": queue.instance_type.type,
                                      "market": "on-demand",
                                      "map": queue.to_dict()}

        with open(backup_file, "w") as fp:
            json.dump(dict, fp, sort_keys=True, indent=4, default=str)
