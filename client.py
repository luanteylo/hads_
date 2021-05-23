#!/usr/bin/env python
from control.scheduler.schedulers import Scheduler
from control.scheduler.CCScheduler import CCScheduler
from control.scheduler.IPDPS import IPDPS

from control.util.loader import Loader
from control.util.mail_me import MailMe

from control.managers.schedule_manager import ScheduleManager

from distutils.util import strtobool

from control.util.recreate_database import RecreateDatabase

import logging
import traceback
import argparse
import datetime


# TODO move notification to loader class
def __notification(status, loader: Loader):
    # Sending email

    try:
        # mail me
        mail = MailMe(user=loader.notify_conf.src_mail,
                      pwd=loader.notify_conf.pwd_mail)

        subject = "Control Execution Status: {}".format(status)
        msg = "Status: {}\n" \
              "JOB: {}\n" \
              "Map: {}\n" \
              "Env: {}\n" \
              "Finish time: {}".format(status, loader.job_file, loader.map_file, loader.env_file,
                                       datetime.datetime.now())

        mail.send_email(recipient=loader.notify_conf.dest_mail, subject=subject, body=msg)
        logging.info("<Client>: Notification send with success to {}".format(loader.notify_conf.dest_mail))
    except Exception as e:
        logging.error("<Client>: Notification Error...")
        logging.error(e)


def __call_control(loader: Loader):
    try:
        loader.print_execution_info()

        manager = ScheduleManager(loader=loader)

        manager.start_execution()

        status = "SUCCESS"

    except Exception as e:
        logging.error(e)
        status = "ERROR"

    # check if the user want be notified at the end of the execution
    if loader.notify:
        __notification(status=status, loader=loader)

    # if loader.dump:
    #     logging.info("Backup Database..")
    #     dump.dump_db()
    #     logging.info("Backup finished...")


def __call_primary_scheduling(loader: Loader):
    loader.print_execution_info()
    # load scheduler
    scheduler = None
    if loader.scheduler_name.upper() == Scheduler.CC:
        scheduler = CCScheduler(loader=loader)

    elif loader.scheduler_name.upper() == Scheduler.IPDPS:
        scheduler = IPDPS(loader=loader)

    if scheduler is None:
        logging.error("<Loader>: ERROR - Scheduler {} not found".format(loader.scheduler_name))
        Exception("<Loader>: ERROR - Scheduler {} not found".format(loader.scheduler_name))

    scheduler.create_primary_map()


def __call_recreate_database(loader: Loader):
    logging.info("Are you sure that you want to recreate the database  {}? (yes or no):"
                 "".format(loader.database_conf.database_name))
    answer = input()

    try:

        if strtobool(answer):
            RecreateDatabase.execute()
            logging.info("Database was recreated with success")
        else:
            logging.info("Database WAS NOT recreated.")
    except Exception as e:
        logging.error(e)


def main():
    parser = argparse.ArgumentParser(description='Hibernation Aware Dynamic Scheduler - HADS 1.0.1')

    parser.add_argument('--input_path', help="the path where there are all input files", type=str, default=None)
    parser.add_argument('--job_file', help="job file name", type=str, default=None)
    parser.add_argument('--env_file', help="env file name", type=str, default=None)
    parser.add_argument('--map_file', help="map file name", type=str, default=None)
    parser.add_argument('--deadline_seconds', help="deadline (seconds)", type=int, default=None)
    parser.add_argument('--ac_size_seconds', help="Define the size of the Logical Allocation Cycle (seconds)", type=int,
                        default=None)

    parser.add_argument('--log_file', help="log file name", type=str, default=None)

    parser.add_argument('--resume_rate', help="Resume rate of the spot VMs [0.0 - 1.0] (simulation-only parameter)",
                        type=float, default=None)
    parser.add_argument('--revocation_rate',
                        help="Revocation rate of the spot VMs [0.0 - 1.0] (simulation-only parameter)", type=float,
                        default=None)

    parser.add_argument('--scheduler_name',
                        help="Scheduler name - Currently supported Schedulers are: " + ", ".join(
                            Scheduler.scheduler_names),
                        type=str, default=None)

    parser.add_argument('--notify', help='Send an email to notify the end of the execution (control mode)',
                        action='store_true', default=False)

    options_map = {
        'control': __call_control,
        'map': __call_primary_scheduling,
        'recreate_db': __call_recreate_database,
    }
    parser.add_argument('command', choices=options_map.keys())

    loader = Loader(args=parser.parse_args())

    func = options_map[loader.client_command]

    func(loader=loader)


if __name__ == "__main__":
    main()
