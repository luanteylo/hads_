import logging

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from control.repository.postgres_objects import Base, Job, Task, Instance, InstanceType, Execution, InstanceStatus

from control.config.database_config import DataBaseConfig

from statistics import mean


class PostgresRepo:
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    accepted_filters = ['job_id', 'task_id', 'instance_id', 'execution_id',
                        'memory__lt', 'memory__gt', 'memory__eq', 'cmd',
                        'instance_type', 'instance_id',
                        'region', 'zone', 'market', 'price__lt',
                        'price__gt', 'status', 'limit', 'order']

    def __init__(self):
        db_config = DataBaseConfig()

        connection_string = "postgresql+psycopg2://{}:{}@{}/{}".format(
            db_config.user,
            db_config.password,
            db_config.host,
            db_config.database_name
        )

        self.engine = create_engine(connection_string)
        Base.metadata.bind = self.engine

        self.session = sessionmaker(bind=self.engine)()

    def __add(self, obj):
        self.session.add(obj)
        self.session.commit()

        if type(obj) is Execution or type(obj) is InstanceStatus:
            logging.info("<DB_INFO>: {}".format(obj))

    def add_provenience(self, new):
        self.__add(new)

    def add_job(self, new):
        self.__add(new)

    def add_task(self, new):
        self.__add(new)

    def add_instance_type(self, new):
        self.__add(new)

    def add_instance_status(self, new):
        self.__add(new)

    def add_instance(self, new):
        self.__add(new)

    def add_execution(self, new):
        self.__add(new)

    def add_statistic(self, new):
        self.__add(new)

    def add_task_statistic(self, new):
        self.__add(new)

    def __check_filter(self, filter):
        if filter is not None:
            for key in filter:
                if key not in self.accepted_filters:
                    raise Exception('Postgres Repo ERROR:  Filter "{}" is Invalid'.format(key))

    def get_jobs(self, filter=None):

        self.__check_filter(filter)

        query = self.session.query(Job)

        if filter is None:
            return query.all()

        if 'job_id' in filter:
            query = query.filter(Job.id == filter['job_id'])

        return query.all()

    def get_tasks(self, filter=None):

        self.__check_filter(filter)

        query = self.session.query(Task)

        if filter is None:
            return query.all()

        if 'job_id' in filter:
            query = query.filter(Task.job_id == filter['job_id'])

        if 'task_id' in filter:
            query = query.filter(Task.task_id == filter['task_id'])

        if 'memory__lt' in filter:
            query = query.filter(Task.memory < filter['memory__lt'])

        if 'memory__gt' in filter:
            query = query.filter(Task.memory > filter['memory__gt'])

        if 'memory__eq' in filter:
            query = query.filter(Task.memory == filter['memory__eq'])

        if 'cmd' in filter:
            query = query.filter(Task.command == filter['cmd'])

        return query.all()

    def get_instance_type(self, filter=None):

        self.__check_filter(filter)

        session = sessionmaker(bind=self.engine)()

        query = session.query(InstanceType)

        if filter is None:
            return query.all()

        if "instance_type" in filter:
            query = query.filter(InstanceType.type == filter["instance_type"])

        return query.all()

    def get_instances(self, filter=None):
        self.__check_filter(filter)

        query = self.session.query(Instance)

        if filter is None:
            return query.all()

        if 'instance_id' in filter:
            query = query.filter(Instance.id == filter['instance_id'])

        if 'instance_type' in filter:
            query = query.filter(Instance.type == filter['instance_type'])

        if 'region' in filter:
            query = query.filter(Instance.region == filter['region'])

        if 'zone' in filter:
            query = query.filter(Instance.zone == filter['zone'])

        if 'market' in filter:
            query = query.filter(Instance.market == filter['market'])

        if 'price__lt' in filter:
            query = query.filter(Instance.price < filter['price__lt'])

        if 'price__gt' in filter:
            query = query.filter(Instance.price > filter['price__gt'])

        if 'status' in filter:
            query = query.filter(Instance.status == filter['status'])

        # TODO add time lt and gt comparation
        elements = query.all()
        return elements

    def get_execution(self, filter=None):
        self.__check_filter(filter)

        query = self.session.query(Execution)

        if filter is None:
            return query.all()

        if 'execution_id' in filter:
            query = query.filter(Execution.execution_id == filter['execution_id'])

        if 'job_id' in filter:
            query = query.filter(Execution.job_id == filter['job_id'])

        if 'task_id' in filter:
            query = query.filter(Execution.task_id == filter['task_id'])

        if 'instance_id' in filter:
            query = query.filter(Execution.instance_id == filter['instance_id'])

        if 'status' in filter:
            query = query.filter(Execution.status == filter['status'])

        if 'order' in filter:
            if filter['order'] == 'desc':
                query = query.order_by(Execution.execution_id.desc())
            else:
                query = query.order_by(Execution.execution_id.asc())

        if 'limit' in filter:
            query = query.limit(filter['limit'])

        return query.all()

    def close_session(self):
        self.session.close()

    def get_tasks_average_runtime(self, job_id):
        """
        :type job_id: int
        :return:
        """

        info = {

        }

        job = self.session.query(Job).filter_by(id=job_id).first()

        for task in job.tasks.all():

            start: Execution

            info['cmd'] = task.command

            memory = []

            for start in task.executions.filter_by(status='executing'):
                end: Execution = task.executions.filter_by(execution_id=start.execution_id, status='finished',
                                                           instance_id=start.instance_id).first()

                if end is not None:
                    time_aux = (end.timestamp - start.timestamp).total_seconds()

                    instance: Instance = self.get_instances({'instance_id': end.instance_id})[0]

                    memory.append(end.avg_memory)

                    info[instance.type] = time_aux

            info['memory'] = mean(memory)

        return info

    def get_tasks_runtime(self, job_id, execution_id):
        """
        :type job_id: int
        :return:
        """

        job = self.session.query(Job).filter_by(id=job_id).first()

        for task in job.tasks.all():

            executing = task.executions.filter_by(execution_id=execution_id, status='executing').all()

            exec: Execution
            for exec in executing:
                fin = task.executions.filter_by(execution_id=execution_id, status='finished',
                                                task_id=exec.task_id).first()

                if fin is not None:
                    print(task.task_id, task.command, fin.timestamp - exec.timestamp)

    def get_number_of_tasks_by_status(self, execution_id, job_id, status):
        execution_list = self.get_execution(filter=
        {
            'job_id': job_id,
            'execution_id': execution_id,
            'status': status
        })

        return len(execution_list)
