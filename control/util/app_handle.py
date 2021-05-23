from Bio import SeqIO
from pathlib import Path
import shutil
import csv
import json
import os
import math

from control.managers.ec2_manager import EC2Manager
from control.config.ec2_config import EC2Config

base_line_times = {
    "c5.2xlarge": 5.0,
    "c5.4xlarge": 3.0,
    "c5.9xlarge": 1.0,
    "c4.4xlarge": 3.0,
    "c4.8xlarge": 2.0,
    "t3.2xlarge": 10.0

}


class AppHandle:
    '''
    Set of methods to create the job file and also handle the files of execution and app folder.,
    '''

    @staticmethod
    def generate_job_file(job_id, job_name, description, csv_file, output_file):

        dict_root = {
            "job_id": job_id,
            "job_name": job_name,
            "description": description,
            "tasks": {

            }

        }

        with open(csv_file, newline='') as CSV:
            csv_reader = csv.reader(CSV)
            for row in csv_reader:
                task_id = int(row[0])
                cmd = row[1]
                n_task = int(row[2])

                dict_root['tasks'][task_id] = {
                    "memory": 0.0,
                    "io": 0.0,
                    "command": cmd,
                    "runtime": {

                        "c5.2xlarge": base_line_times["c5.2xlarge"] * n_task,
                        "c5.4xlarge": base_line_times["c5.4xlarge"] * n_task,
                        "c5.9xlarge": base_line_times["c5.9xlarge"] * n_task,
                        "c4.4xlarge": base_line_times["c4.4xlarge"] * n_task,
                        "c4.8xlarge": base_line_times["c4.8xlarge"] * n_task,
                        "t3.2xlarge": base_line_times["t3.2xlarge"] * n_task

                    }
                }

        # create json file
        with open(output_file, 'w') as fp:
            json.dump(dict_root, indent=4, fp=fp, default=str)

    @staticmethod
    def generate_env_file(csv_file, output_file):

        ec2_conf = EC2Config()

        dict = {
            "instances": {},
            "global_limits": {
                "ec2": {
                    "on-demand": 20,
                    "preemptible": 20
                }
            }
        }

        with open(csv_file) as fp:
            reader = csv.reader(fp)
            for row in reader:
                instance_type = row[0]
                vcpus = int(row[1])
                memory = float(row[2])
                price_ondemand = EC2Manager.get_ondemand_price(instance_type, region=ec2_conf.region)
                # TODO CHANGE IT
                price_preemptible = EC2Manager.get_preemptible_price(instance_type=instance_type, zone=ec2_conf.zone)

                dict['instances'][instance_type] = {
                    "gflops": 10.0,
                    "memory": memory,
                    "vcpu": vcpus,
                    "provider": 'ec2',
                    "prices": {
                        "on-demand": price_ondemand,
                        "preemptible": price_preemptible[0][1],
                    },

                    "restrictions": {
                        "limits": {
                            "on-demand": 5,
                            "preemptible": 5
                        },
                        "markets": {
                            "on-demand": "yes",
                            "preemptible": "yes"
                        },
                        "burstable": {
                            "burstable": "no",
                            "cpu_credit_rate": 0,
                            "baseline": 0
                        }
                    }

                }

            # create json file
            with open(output_file, 'w') as fp:
                json.dump(dict, indent=4, fp=fp)

    @staticmethod
    def __generate_profiling(input_path, job_file, map_file, env_file):
        pass

    @staticmethod
    def copytree(src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

    @staticmethod
    def __split_fasta(fasta_file, out_dir: Path):
        '''
        Extract multiple sequence fasta file and write each sequence in separate file
        :param fasta_file: Source file with the sequences
        :param out_dir: Directory where the separated files will be writen
        :return: Number of sequences
        '''

        print("> Split file: {}".format(fasta_file))

        file_count = 0

        with open(fasta_file) as FH:
            record = SeqIO.parse(FH, "fasta")
            for seq_rec in record:
                file_output = Path(out_dir, seq_rec.id.strip() + ".fasta")
                file_count = file_count + 1
                print("\tWriting: {}".format(file_output))
                with open(file_output, "w") as FHO:
                    SeqIO.write(seq_rec, FHO, "fasta")

        if file_count == 0:
            raise Exception("No valid sequence in fasta file")
        else:
            print("\n> {} Files created with success.".format(file_count))

        return file_count

    @staticmethod
    def create_masa_app_structure(root_path, data_source, dest_path, clone_file, source_fasta_file, csv_out,
                                  n_super_task):
        '''

        :param root_path: Path to the file
        :param data_source: folder with all  executables (that folder will be replicated)
        :param dest_path: Dest where files will be moved
        :param clone_file: Fasta file that have to be cloned into all folders to pair files
        :param source_fasta_file: Fasta file with all sequences
        :param csv_out: CSV_file where the MASA-OpenMP parameters will be recorded
        :poram n_super_task: Number of super tasks
        :return: Path to the file with the csv file.
        '''

        root_path = Path(root_path)
        data_source = Path(data_source)
        clone_file = Path(root_path, clone_file)
        source_fasta_file = Path(root_path, source_fasta_file)
        dest_path = Path(dest_path)

        assert clone_file.is_file(), "File {} not found.".format(clone_file)
        assert source_fasta_file.is_file(), "File {} not found".format(source_fasta_file)
        assert data_source.is_dir(), "Directory {} not found".format(data_source)

        # create dest_path
        dest_path.mkdir(parents=True, exist_ok=True)

        # Split the Source sequences in different files
        n_sequences = AppHandle.__split_fasta(source_fasta_file, dest_path)

        if n_sequences < n_super_task:
            print("> ERROR: number of sequences ({}) is less than number of super tasks ({})".format(n_sequences,
                                                                                                     n_super_task))
            exit()

        spt = math.floor(n_sequences / n_super_task)
        reminder = n_sequences % n_super_task

        print("> number of sequences", n_sequences)
        print("> sequences per super tasks", spt)
        print("> reminder tasks", reminder)

        # Creating the files in different directories
        print("> Coping the files..")

        files = list(dest_path.glob('*.fasta'))
        for supert_id in range(n_super_task):
            # creating super task folder
            task_path = Path(str(dest_path) + "/{}".format(supert_id))
            task_path.mkdir(parents=True, exist_ok=True)

            # creating data path folder
            data_path = Path(str(task_path) + "/data/")
            data_path.mkdir(parents=True, exist_ok=True)

            # creating backup folder
            backup_path = Path(str(task_path) + "/backup/")
            backup_path.mkdir(parents=True, exist_ok=True)

            # creating fast_path folder
            fasta_path = Path(str(data_path) + '/fasta/')
            fasta_path.mkdir(parents=True, exist_ok=True)

            # coping data files
            AppHandle.copytree(src=data_source, dst=data_path)

            # # coping clone file
            shutil.copyfile(src=clone_file, dst=Path(fasta_path, clone_file.name))

            init = supert_id * spt
            if supert_id + 1 == n_super_task:
                end = init + spt + reminder
            else:
                end = init + spt

            print("> super task {} - number of files {}".format(supert_id, len(files[init:end])))
            files_name = []
            for file in files[init:end]:
                print("\tcopying file...", file)
                shutil.copyfile(src=str(file), dst=Path(fasta_path, file.name))

                files_name.append(file.name)

            super_task_cmd = "python3 masa_exec.py  -r {} -s {}".format(clone_file.name, " ".join(files_name))
            n_task = len(files[init:end])

            with open(csv_out, 'a') as csv_fp:
                file = csv.writer(csv_fp)
                file.writerow([supert_id, super_task_cmd, n_task])

        print("> Cleaning Files...")
        for file in files:
            os.remove(file)

root_path = '/home/luan/app/covid_files'
data_source = '/home/luan/app/masa_app'
dest_path = '/home/luan/app/masa_usa'
clone_file = 'NC_045512.2.fasta'
source_file = 'SARS-CoV-2-seqs-20202710.fasta'

n_super_task = 30
csv_parameters = 'csv_parameters.csv'


job_id = 1
csv_file = Path(dest_path, csv_parameters)
job_file = Path(dest_path, 'job.json')

AppHandle.create_masa_app_structure(root_path=root_path,
                                    data_source=data_source,
                                    dest_path=dest_path,
                                    clone_file=clone_file,
                                    source_fasta_file=source_file,
                                    csv_out=csv_file,
                                    n_super_task=n_super_task)

AppHandle.generate_job_file(job_id=job_id, job_name='', description='', csv_file=csv_file, output_file=job_file)

#
# AppHandle.generate_job_file(job_id=1, job_name='test', description='', csv_file=csv_file,
#                             output_file=Path(dest_path, 'job.json'), command='sh exec.sh ')
#
# AppHandle.generate_env_file(Path(dest_path, 'csv_env.csv'), Path(dest_path, 'env.json'))
#
#
