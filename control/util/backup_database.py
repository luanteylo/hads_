#!/usr/bin/env python
import os
import time

from control.config.database_config import DataBaseConfig


def dump_db():

    conf = DataBaseConfig()

    backupdir = conf.dump_dir
    date = time.strftime('%Y-%m-%d')

    # GET DB NAMES
    command = "docker exec -t {} pg_dumpall -c -U {} >  {}dump_`date +%d-%m-%Y_%H_%M_%S`.sql".format(
        "pg-docker",
        conf.user,
        backupdir
    )

    print(command)

    if not os.path.exists(backupdir):
        os.mkdir(backupdir)

    os.system(command)

