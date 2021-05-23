#!/usr/bin/env python


from control.managers.ec2_manager import EC2Manager

from control.config.application_config import ApplicationConfig
from control.config.checkpoint_config import CheckPointConfig
from control.config.communication_config import CommunicationConfig
from control.config.database_config import DataBaseConfig
from control.config.debug_config import DebugConfig
from control.config.docker_config import DockerConfig
from control.config.ec2_config import EC2Config
from control.config.file_system_config import FileSystemConfig
from control.config.input_config import InputConfig
from control.config.logging_config import LoggingConfig
from control.config.notify_config import NotifyConfig
from control.config.scheduler_config import SchedulerConfig
from control.config.simulation_config import SimulationConfig

from control.domain.instance_type import InstanceType
from control.domain.job import Job

from control.repository.postgres_repo import PostgresRepo

from datetime import timedelta

from typing import Dict

import logging
import json
import os

from pathlib import Path


class Loader:
    HADS_VERSION = '1.0.4'

    env: Dict[str, InstanceType]
    job: Job

    def __init__(self, args):

        """Command line args"""
        # input files parameters
        self.input_path = args.input_path
        self.job_file = args.job_file
        self.env_file = args.env_file
        self.map_file = args.map_file

        # deadline in seconds parameter
        self.deadline_seconds = args.deadline_seconds
        # ac size in seconds
        self.ac_size_seconds = args.ac_size_seconds
        # log file name
        self.log_file = args.log_file
        # simulation parameters
        self.resume_rate = args.resume_rate
        self.revocation_rate = args.revocation_rate
        # name of the scheduler
        self.scheduler_name = args.scheduler_name
        # notify end of execution by email
        self.notify = args.notify
        # Client command
        self.client_command = args.command

        self.deadline_timedelta = None

        # instances able to be used
        self.instances_list = []

        # limits Parameters
        # global on-demand count_list
        self.count_list = {}
        self.max_preemptible = None
        self.max_ondemand = None
        # used to attend the cloud limits

        # Load config Classes
        self.application_conf = ApplicationConfig()
        self.checkpoint_conf = CheckPointConfig()
        self.communication_conf = CommunicationConfig()
        self.database_conf = DataBaseConfig()
        self.debug_conf = DebugConfig()
        self.docker_conf = DockerConfig()
        self.ec2_conf = EC2Config()
        self.filesys_conf = FileSystemConfig()
        self.input_conf = InputConfig()
        self.logging_conf = LoggingConfig()
        self.notify_conf = NotifyConfig()
        self.scheduler_conf = SchedulerConfig()
        self.simulation_conf = SimulationConfig()

        # local path where the daemon file is
        self.daemon_file = None

        '''
        Parameters of the execution
        The execution_id is defined according with the database last execution_id
        '''
        self.execution_id = None  # ID of the current execution

        '''
        Dictionary with the domain.instance_type that can be used in the execution
        Read from env.json
        '''
        self.env = None

        '''
        Class domain.job contains all tasks that will be executed
        and the information  about the job
        '''
        self.job: Job = None

        self.__prepare_logging()
        self.__load_input_parameters()

        self.__load_job()
        self.__load_env()

        self.__get_execution_id()

        self.__update_prices()

    def __prepare_logging(self):
        """
        Set up the log format, level and the file where it will be recorded.
        """
        if self.log_file is None:
            self.log_file = Path(self.logging_conf.path, self.logging_conf.log_file)
        else:
            self.log_file = Path(self.logging_conf.path, self.log_file)

        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()
        root_logger.setLevel(self.logging_conf.level)

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

    def __load_input_parameters(self):
        """
        Merging command line arguments with arguments from setup.cfg
        """

        if self.input_path is None:
            self.input_path = self.input_conf.path

        if self.job_file is None:
            self.job_file = os.path.join(self.input_path, self.input_conf.job_file)
        else:
            self.job_file = os.path.join(self.input_path, self.job_file)

        if self.env_file is None:
            self.env_file = os.path.join(self.input_path, self.input_conf.env_file)
        else:
            self.env_file = os.path.join(self.input_path, self.env_file)

        if self.map_file is None:
            self.map_file = os.path.join(self.input_path, self.input_conf.map_file)
        else:
            self.map_file = os.path.join(self.input_path, self.map_file)

        if self.scheduler_name is None:
            self.scheduler_name = SchedulerConfig().name

        self.daemon_file = os.path.join(self.application_conf.daemon_path, self.application_conf.daemon_file)

        if self.deadline_seconds is None:
            self.deadline_seconds = self.input_conf.deadline_seconds

        self.deadline_timedelta = timedelta(seconds=self.deadline_seconds)

        if self.ac_size_seconds is None:
            self.ac_size_seconds = self.input_conf.ac_size_seconds

        if self.revocation_rate is None:
            self.revocation_rate = self.simulation_conf.revocation_rate
        if self.resume_rate is None:
            self.resume_rate = self.simulation_conf.resume_rate

    def __load_job(self):
        """
        Read the file job_file and create the class Job
        """

        try:
            with open(self.job_file) as f:
                job_json = json.load(f)
        except Exception as e:
            logging.error("<Loader>: Error file {} ".format(self.job_file))
            raise Exception(e)

        self.job = Job.from_dict(job_json)

    def __load_env(self):
        """
        Read the file env_file and create a dictionary with all available instances
        """

        try:
            with open(self.env_file) as f:
                env_json = json.load(f)
        except Exception as e:
            logging.error("<Loader>: Error file {} ".format(self.env_file))
            raise Exception(e)

        # get limits max_vms
        self.max_preemptible = env_json['global_limits']['ec2']['preemptible']
        self.max_ondemand = env_json['global_limits']['ec2']['on-demand']

        self.env = {}

        for instance in InstanceType.from_dict(env_json):
            # start global count list
            self.count_list[instance.type] = 0

            self.env[instance.type] = instance

            self.instances_list.append(instance)

    def __get_execution_id(self):
        """
        Read the database to get the next execution_id
        """

        repo = PostgresRepo()
        row = repo.get_execution(filter={'job_id': self.job.job_id, 'limit': 1, 'order': 'desc'})
        if len(row) == 0:
            self.execution_id = 0
        else:
            # get least execution ID
            self.execution_id = row[0].execution_id + 1

    def __update_prices(self):
        """
        get current instances prices on EC2 and update the env dictionary and also the env.json input file
        """

        zone = self.ec2_conf.zone
        region = self.ec2_conf.region

        for instance in self.env.values():

            if instance.market_ondemand:
                instance.setup_ondemand_price(
                    price=EC2Manager.get_ondemand_price(instance_type=instance.type, region=region),
                    region=region
                )

            if instance.market_preemptible:
                instance.setup_preemptible_price(
                    price=EC2Manager.get_preemptible_price(instance_type=instance.type, zone=zone)[0][1],
                    region=region,
                    zone=zone
                )

        # Update env file
        with open(self.env_file, "r") as jsonFile:
            data = json.load(jsonFile)

        # updating prices on env_file
        tmp = data["instances"]
        for type in tmp:
            tmp[type]['prices']['on-demand'] = self.env[type].price_ondemand
            tmp[type]['prices']['preemptible'] = self.env[type].price_preemptible

        data["instances"] = tmp

        with open(self.env_file, "w") as jsonFile:
            json.dump(data, jsonFile, sort_keys=False, indent=4, default=str)

    def print_execution_info(self):
        logging.info("\n")

        header_msg = 50 * "#" + "\tHADS {}\t".format(Loader.HADS_VERSION) + 50 * "#"
        logging.info(header_msg)
        logging.info("")

        logging.info("\tExecuting type: '{}' Scheduler: '{}'".format(self.client_command, self.scheduler_name))
        logging.info("")
        logging.info("\tInput Files:")
        logging.info("\tJob: {}".format(self.job_file))
        logging.info("\tEnv: {}".format(self.env_file))
        logging.info("\tMap: {}".format(self.map_file))
        logging.info("\tLog File: {}".format(self.log_file))
        logging.info("\tAPP Local Path: {}".format(self.application_conf.app_local_path))
        logging.info("\tDaemon: {}".format(self.daemon_file))
        logging.info("")
        logging.info("")
        logging.info("\t" + 30 * "*")
        logging.info("\tJob id: {} Execution id: {}".format(self.job.job_id, self.execution_id))
        logging.info("\tDeadline: {} AC: {}".format(self.deadline_seconds,
                                                    self.ac_size_seconds))
        logging.info("\t" + 30 * "*")

        logging.info("")
        logging.info("\tWITH SIMULATION: {}".format(self.simulation_conf.with_simulation))
        if self.simulation_conf.with_simulation:
            logging.info("\tRevocation Rate: {]  Resume Rate: {}".format(self.simulation_conf.revocation_rate,
                                                                         self.simulation_conf.resume_rate))
        logging.info("\tWITH CHECKPOINT: {}".format(self.checkpoint_conf.with_checkpoint))
        logging.info("\tDEBUG MODE: {}".format(self.debug_conf.debug_mode))
        logging.info("")

        logging.info(120 * "#")
        logging.info("\n\n")
