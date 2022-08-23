# HADS and Burst-HADS

[_TOC_]

This repository contains all files related to the Hibernation-Aware Dynamic Scheduler (HADS)

- [ ] Remove not used branches from the public repository
- [ ] Merge branches at the master one
- [ ] Write the README.rst
- [x] Write the Instalation Guide
- [x] Include the list of published papers at README

## Installation Guide

This installation guide describes a verified process for Linux environment (Ubuntu 20.04 LTS). All instructions reported here are based on this system. Number versions are provided as an indication of the versions that were tested and used in this project. 


You must have Docker installed and running as well as Python 3.

- Docker (v20.10.17)
- Python 3 (v3.9)

:warning: Currently HADS only supports the services of AWS. All the instalation steps related to the cloud is based on this provider.


#### Installing the controller

The controller is responsabel for all the management of the virtual machines in the cloud: it request machines, deploy the tasks and termina the environment. Before install the control, you need to generate a Identity and Access Management (IAM) 

1. Execute the script `install.sh`  in `install/control/`. First, update `SOURCE_PATH` variable inside it with the full path to the `hads_` project;

2. If all goes well, test if client is working in the `hads/` source repo: `python clienty.py --help`.


It is necessary to have the following AWS permissions and setup:

1. AWS CLI
2. AWS Access Key and Secret id (usually stored in ~/.aws/credentials
3. EC2 creation and deletion permissions
4. pricing:GetProducts

## Published Papers
-   Teylo, L.; Arantes, L.; Sens, P.; Drummond, L. A Hibernation Aware Dynamic Scheduler for Cloud Environments. _15th International Workshop on Scheduling and Resource Management for Parallel and Distributed Systems_, ICPP, 2019.
-   Teylo, L.; Arantes, L.; Sens, P; Drummond, L. A dynamic task scheduler tolerant to multiple hibernations in cloud environments._Cluster Computing_, v. 4, p. 1-23, 2020  (Available Online).
-   Teylo, L.; Brum, R.; Arantes, L.; Sens, P.; Drummond, L. Developing Checkpointing and Recovery Procedures with the Storage Services of Amazon Web Services.  _16th International Workshop on Scheduling and Resource Management for Parallel and Distributed Systems_, ICPP, 2020.
-   Teylo, L.; Nunes, A. L.; Melo C. M. A., A.; Boeres, C.;  Drummond, L.; Martins, N. Comparing sars-cov-2 sequences using a commercial cloud with a spot instance based dynamic scheduler.  _21th IEEE/ACM International Symposium on Cluster, Cloud and Grid Computing_, 2021.


## TODO:
- [ ] Remove not used branches from the public repository
- [ ] Merge branches at the master one
- [ ] Write the README.rst
- [x] Write the Instalation Guide
- [x] Include the list of published papers at README
