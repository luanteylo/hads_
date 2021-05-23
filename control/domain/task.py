from control.config.checkpoint_config import CheckPointConfig

from typing import Dict

import math


class Task:
    EXECUTING = 'executing'
    FINISHED = 'finished'
    WAITING = 'waiting'
    ERROR = 'error'
    RUNTIME_ERROR = 'runtime_error'
    MIGRATED = 'migrated'
    HIBERNATED = 'hibernated'
    STOLEN = 'stolen'
    STOP_SIGNAL = 'stop_signal'

    RESTARTED = 'restarted'

    def __init__(self, task_id, memory, command, io, runtime):
        self.task_id = task_id
        self.memory = memory
        self.command = command
        self.io = io
        self.runtime: Dict[str, float] = runtime

        self.expected_start = None
        self.expected_end = None
        self.task_size = None

        self.checkpoint_config = CheckPointConfig()

        self.checkpoint_factor = 0.0
        self.checkpoint_number = 0
        self.checkpoint_interval = 0.0
        self.checkpoint_dump = 0.0
        self.checkpoint_overhead = 0.0

        self.allocated_cpu_credits = 0
        self.burst_mode = False

        if self.checkpoint_config.with_checkpoint:
            self.__compute_checkpoint_values()

        self.has_checkpoint = False
        self.do_checkpoint = True

        self.__compute_checkpoint_values()

    # That function has to be call when a checkpoint is recorded
    # it updates the task runtime and the checkpoint overhead removing the periods of time that was already recorded
    def update_task_time(self):

        for key in self.runtime:
            self.runtime[key] = max(self.runtime[key] - self.checkpoint_interval, 1)

        self.checkpoint_overhead = max(self.checkpoint_overhead - self.checkpoint_dump, 0)

        if self.checkpoint_overhead == 0:
            self.do_checkpoint = False

    def __compute_checkpoint_values(self):

        # get max_runtime of the tasks
        max_runtime = max([time for time in self.runtime.values()])

        # get checkpoint factor define by the user
        self.checkpoint_factor = self.checkpoint_config.overhead_factor
        # computing checkpoint overhead
        self.checkpoint_overhead = self.checkpoint_factor * max_runtime

        # computing checkpoint dump_time
        self.checkpoint_dump = 12.99493 + 0.04 * self.memory

        # define checkpoint number
        self.checkpoint_number = int(math.floor(self.checkpoint_overhead / self.checkpoint_dump))

        # check if checkpoint number is != 0
        if self.checkpoint_number > 0:
            # define checkpoint interval
            self.checkpoint_interval = math.floor(max_runtime / self.checkpoint_number)
        else:
            # since there is no checkpoint to take (checkpoint_number = 0) the overhead is set to zero
            self.checkpoint_overhead = 0.0

    @classmethod
    def from_dict(cls, adict):
        """return a list of tasks created from a dict"""

        return [
            cls(
                task_id=int(task_id),
                memory=adict['tasks'][task_id]['memory'],
                io=adict['tasks'][task_id]['io'],
                command=adict['tasks'][task_id]['command'],
                runtime=adict['tasks'][task_id]['runtime']
            )
            for task_id in adict['tasks']
        ]

    def __str__(self):
        return "Task_id: {}, memory:{}, io:{}, command:{}, start:{}, end:{}".format(
            self.task_id,
            self.memory,
            self.io, self.command,
            self.expected_start,
            self.expected_end
        )

    def get_runtime(self, instance_type):

        if instance_type in self.runtime:
            return self.runtime[instance_type]
        else:
            return None

    def __eq__(self, other):
        return self.task_id == other.task_id

    def __lt__(self, other):
        """
        :type other: Executor
        """
        return self.expected_start < other.expected_start
