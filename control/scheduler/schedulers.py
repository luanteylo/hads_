from control.domain.instance_type import InstanceType
from control.domain.task import Task

from control.managers.dispatcher import Dispatcher
from control.managers.cloud_manager import CloudManager

from control.scheduler.queue import Queue

from datetime import datetime, timedelta

from typing import List, Dict

import json
import logging
import math
import uuid
import roundrobin


# Each Scheduler Class have to implemented the follows methods


class Scheduler:
    # Scheduler NAMES
    IPDPS = 'IPDPS'
    CC = 'CC'
    scheduler_names = [IPDPS, CC]

    MAX_RANGE = 3
    MIN_RANGE = 1

    # Create primary map
    def create_primary_map(self):
        pass

    def migrate(self, affected_tasks: List[Task],
                fault_dispatcher: Dispatcher,
                instances: List[InstanceType],
                deadline_timestamp: datetime,
                fault_time_timestamp: datetime,
                count_list: Dict[str, int],
                idle_dispatchers: List[Dispatcher],
                working_dispatchers: List[Dispatcher]):
        pass

    # SHARED Scheduler FUNCTIONS
    @staticmethod
    def build_roundrobin_list(max_rank, min_rank, instances):

        weight_list = []

        # build weithed list
        for instance in instances:
            weight = Scheduler.normalize_rank(max_rank, min_rank, instance.rank)
            # logging.info("Instance {} weight: {}".format(instance.type, weight))
            weight_list.append((instance, weight))

        # build round roubin list
        return roundrobin.weighted(weight_list)

    @staticmethod
    def normalize_rank(max, min, rank):
        range = max - min
        rank = (rank - min) / range
        range2 = Scheduler.MAX_RANGE - Scheduler.MIN_RANGE
        return int(math.ceil(rank * range2) + 1)

    @staticmethod
    def compute_dspot(instances: Dict[str, InstanceType], tasks: Dict[str, Task], max_ondemand: int,
                      allow_parallel_execution : bool, deadline: timedelta):

        # compute n
        n = math.ceil(len(tasks) / max_ondemand)

        list_of_instances = []
        for key, instance in instances.items():
            list_of_instances.append(instance)

        list_of_instances.sort(key=lambda x: x.price_ondemand)

        slowest_instance = list_of_instances[0]

        list_of_tasks = []
        for key, task in tasks.items():
            list_of_tasks.append(task)

        list_of_tasks.sort(key=lambda x: x.get_runtime(slowest_instance.type))

        queue = Queue(instance_id=uuid.uuid4(),
                      instance_type=slowest_instance,
                      market=CloudManager.ON_DEMAND,
                      allow_parallel_execution=allow_parallel_execution)

        for i in range(n):
            task = list_of_tasks[i]
            queue.insert(task)

        # print("Makespan worst case: ", timedelta(seconds=queue.makespan_seconds))

        return timedelta(seconds=max(deadline.total_seconds() - queue.makespan_seconds, 0))

    @staticmethod
    def get_cost_and_makespan(queues: List[Queue]):
        expected_makespan_seconds = 0.0
        expected_cost = 0.0

        # GET COST AND MAKESPAN
        for queue in queues:
            if expected_makespan_seconds < queue.makespan_seconds:
                expected_makespan_seconds = queue.makespan_seconds

            expected_cost += queue.expected_cost
        return expected_cost, expected_makespan_seconds

    # SHARED OUTPUT FUNCTIONS
    @staticmethod
    def write_json_backup(queues: List[Queue], deadline, makespan, backup_file):
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

    @staticmethod
    def write_json(queues: List[Queue], scheduler_name, job_id, job_name, expected_makespan_seconds, expected_cost,
                   deadline_seconds,
                   file_output):
        # build a map
        dict = {"job_id": job_id,
                "job_name": job_name,
                'scheduler': scheduler_name,
                "expected_makespan": expected_makespan_seconds,
                "expected_cost": expected_cost,
                "deadline": deadline_seconds,
                "instances": {}
                }
        logging.info("Scheduler Name: {}".format(scheduler_name))
        logging.info("Expected Makespan: {}".format(expected_makespan_seconds))
        logging.info("Expected Cost: {}".format(expected_cost))
        for queue in queues:
            if queue.market == CloudManager.PREEMPTIBLE:
                price = queue.instance_type.price_preemptible
            else:
                price = queue.instance_type.price_ondemand

            key = "id{}".format(queue.instance_id)
            dict['instances'][key] = {"type": queue.instance_type.type,
                                      "market": queue.market,
                                      "price": price,
                                      "map": queue.to_dict()}

        with open(file_output, "w") as fp:
            json.dump(dict, fp, sort_keys=True, indent=4, default=str)
