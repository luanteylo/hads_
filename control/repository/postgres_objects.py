from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Boolean, String, Float, ForeignKey, ForeignKeyConstraint, TIMESTAMP
from sqlalchemy.orm import relationship

Base = declarative_base()


class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    tasks = relationship('Task', backref='job', lazy='dynamic')

    # executions = relationship('Execution', backref='job')

    def __repr__(self):
        return "<Job(id='{}', name='{}', description={})>" \
            .format(self.id, self.name, self.description)


class Task(Base):
    __tablename__ = 'task'
    job_id = Column(Integer, ForeignKey('job.id'), primary_key=True)
    task_id = Column(Integer, primary_key=True)
    command = Column(String)
    memory = Column(Float)
    io = Column(Float)

    executions = relationship('Execution', backref='task', lazy='dynamic')

    def __repr__(self):
        return "<Task(job_id='{}', task_id='{}' command='{}', memory='{}', io='{}')>" \
            .format(self.job_id, self.task_id, self.command, self.memory, self.io)


class InstanceType(Base):
    __tablename__ = 'instance_type'
    type = Column(String, primary_key=True)
    vcpu = Column(Integer)
    memory = Column(Float)
    provider = Column(String)
    burstable = Column(Boolean, default=False)

    instances = relationship('Instance', backref='instance_type', lazy='dynamic')

    def __repr__(self):
        return "<InstanceType(type='{}', vcpu='{}' memory='{}')>" \
            .format(self.type, self.vcpu, self.memory)


class Instance(Base):
    __tablename__ = 'instance'
    id = Column(String, primary_key=True)
    type = Column(String, ForeignKey('instance_type.type'))
    region = Column(String)
    zone = Column(String)
    ebs_volume = Column(String)
    market = Column(String)
    price = Column(Float)

    # executions = relationship('Execution', backref='instance', lazy='dynamic')
    instance_status = relationship('InstanceStatus', backref='instance', lazy='dynamic')
    execution = relationship('Execution', backref='instance', lazy='dynamic')

    def __repr__(self):
        return "<Instance(instance_id='{}', type='{}' region='{}', zone='{}', market='{}', price='{}')>" \
            .format(self.id, self.type, self.region, self.zone, self.market, self.price)


class InstanceStatus(Base):
    __tablename__ = 'instance_status'
    instance_id = Column(String, ForeignKey('instance.id'), primary_key=True)
    timestamp = Column(TIMESTAMP, primary_key=True)
    memory_footprint = Column(Float, default=0.0)
    cpu_usage = Column(Float, default=0.0)
    cpu_credit = Column(Float, default=0.0)

    status = Column(String)

    def __repr__(self):
        return "InstanceStatus: <instance_id='{}', timestamp='{}' status='{}'>".format(
            self.instance_id,
            self.timestamp,
            self.status)


class Execution(Base):
    __tablename__ = 'execution'
    execution_id = Column(Integer, primary_key=True)
    job_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, primary_key=True)
    instance_id = Column(String, ForeignKey('instance.id'), primary_key=True)
    timestamp = Column(TIMESTAMP, primary_key=True)

    # task_max_memory = Column(Float, default=0.0)
    status = Column(String)

    __table_args__ = (ForeignKeyConstraint(['job_id', 'task_id'],
                                           [Task.job_id, Task.task_id]),
                      {})

    def __repr__(self):
        return "Execution: <task_id='{}', instance_id='{}', timestamp='{}', status='{}'>".format(
            self.task_id,
            self.instance_id,
            self.timestamp,
            self.status)


class TaskStatistic(Base):
    __tablename__ = 'task_statistic'
    execution_id = Column(Integer, primary_key=True)
    job_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, primary_key=True)

    memory_usage = Column(Float, default=0.0)
    cpu_usage = Column(Float, default=0.0)

    # __table_args__ = (ForeignKeyConstraint(['job_id', 'task_id', 'execution_id'],
    #                                        [Execution.job_id, Execution.task_id, Execution.execution_id]),
    #                   {})

    def __repr__(self):
        return "Execution: <task_id='{}', job_id='{}', execution_id='{} timestamp='{}', memory='{}' cpu_usage: {}>".format(
            self.task_id,
            self.job_id,
            self.execution_id,
            self.timestamp,
            self.memory_usage,
            self.cpu_usage)


class InstanceStatistic(Base):
    __tablename__ = 'instance_statistic'
    instance_id = Column(String, ForeignKey('instance.id'), primary_key=True)
    deploy_overhead = Column(Float)
    termination_overhead = Column(Float)
    uptime = Column(Float)

    def __repr__(self):
        return "InstanceStatistic: <instance_id='{}', " \
               "Deploy Overhead='{}' Termination_overhead='{}'>".format(self.instance_id,
                                                                        self.deploy_overhead,
                                                                        self.termination_overhead)


class Statistic(Base):
    __tablename__ = 'statistic'
    execution_id = Column(Integer, primary_key=True)
    job_id = Column(Integer, primary_key=True)
    start = Column(TIMESTAMP, primary_key=True)
    end = Column(TIMESTAMP)
    deadline = Column(TIMESTAMP)
    cost = Column(Float)
    status = Column(String)
