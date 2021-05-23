from control.domain.task import Task


class Job:

    def __init__(self, job_id, job_name, job_dict, description=""):
        self.job_id = job_id
        self.job_name = job_name
        self.description = description

        self.tasks = self.__load_tasks(job_dict)

    def __load_tasks(self, job_dict):
        tasks = {}

        for task in Task.from_dict(job_dict):
            tasks[str(task.task_id)] = task

        return tasks

    @property
    def num_tasks(self):
        return len(self.tasks)

    @classmethod
    def from_dict(cls, adict):
        return cls(
            job_id=adict['job_id'],
            job_name=adict['job_name'],
            job_dict=adict,
            description=adict['description']
        )
