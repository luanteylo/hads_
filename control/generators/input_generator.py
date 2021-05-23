import csv
import json


from control.managers.ec2_manager import EC2Manager

from control.repository.postgres_repo import PostgresRepo

from math import ceil

import random


# class InputGenerator:
#
#     @staticmethod
#     def generate_env_file(csv_file, output_file):
#
#         dict = {
#             "instances": {},
#             "slot_time": 3600,
#             "global_limits": {
#                 "spot": 20,
#                 "on-demand": 20
#             }
#         }
#
#
#         with open(csv_file) as fp:
#             reader = csv.DictReader(fp)
#
#             for row in reader:
#                 instance_type = row['API Name']
#                 memory = float(row['Memory'].split()[0])
#                 vcpus = int(row['vCPUs'].split()[0])
#                 price_ondemand = float(row['Linux On Demand cost'].split()[0].replace('$', ''))
#                 # TODO CHANGE IT
#                 price_spot = EC2Manager.get_spot_price(instance_type, 'us-west-1c')[0][1]
#
#                 dict['instances'][instance_type] = {
#                     "memory": memory,
#                     "vcpu": vcpus,
#                     "prices": {
#                         "on-demand": price_ondemand,
#                         "spot": price_spot,
#                     },
#                     "restrictions": {
#                         "markets": {
#                             "on-demand": "allowed",
#                             "spot": "allowed"
#                         },
#                         "limits": {
#                             "on-demand": 5,
#                             "spot": 5
#                         }
#
#                     }
#
#                 }
#
#             # create json file
#             with open(output_file, 'w') as fp:
#                 json.dump(dict, indent=4, fp=fp)
#
#     @staticmethod
#     def generate_job_file(number_of_task, job_id, job_name, description, output_file,
#                           based_jobs):
#
#         dict_root = {
#             "job_id": job_id,
#             "job_name": job_name,
#             "description": description,
#             "tasks": {
#
#             }
#
#         }
#
#         repo = PostgresRepo()
#
#         for i in range(number_of_task):
#             # select a base job
#             base_job = random.choice(based_jobs)
#
#             info = repo.get_tasks_average_runtime(base_job)
#
#             # print(info)
#
#             dict_root['tasks'][str(i)] = {
#
#                 "memory": info['memory'],
#                 "io": 0.0,
#                 "command": info['cmd'],
#                 "runtime": {
#                     "c3.xlarge": ceil(info["c3.xlarge"]),
#                     "c3.large": ceil(info["c3.large"]),
#                     "c4.large": ceil(info["c4.large"]),
#                     "c4.xlarge": ceil(info["c4.xlarge"]),
#                 }
#
#             }
#
#         # create json file
#         with open(output_file, 'w') as fp:
#             json.dump(dict_root, indent=4, fp=fp, default=str)
#
#     @staticmethod
#     def generate_job_file_static(number_of_task, job_id, job_name, description, output_file, size, runtime):
#
#         dict_root = {
#             "job_id": job_id,
#             "job_name": job_name,
#             "description": description,
#             "tasks": {
#
#             }
#
#         }
#
#         for i in range(number_of_task):
#             # select a base job
#
#             # memory_footprint = (((size * size * 4) / 1024.0) + 20600) / 1024.0
#             memory_footprint = 3.75
#
#             basetime = runtime * (1 + random.uniform(0.0, 0.03))
#             # print(info)
#
#             dict_root['tasks'][str(i)] = {
#
#                 "memory": memory_footprint,
#                 "io": 0.0,
#                 "command": "sh exec.sh {} {}".format(size, runtime),
#                 "runtime": {
#                     "c3.xlarge": 0.977 * basetime,
#                     "c3.large": 0.979 * basetime,
#                     "c4.large": basetime,
#                     "c4.xlarge": 0.997 * basetime,
#                     "c5.large": 0.997 * basetime,
#                     "c5.xlarge": 0.997 * basetime
#                 }
#
#             }
#
#         # create json file
#         with open(output_file, 'w') as fp:
#             json.dump(dict_root, indent=4, fp=fp, default=str)
