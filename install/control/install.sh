#!/usr/bin/env bash

# full path to the framework code
SOURCE_PATH=~/Devel/hads_

# access ID and pwd generate in AWS
AWS_ACCESS_ID=
AWS_ACCESS_PWD=

# full path to the directory where the setup file is
#SETUP_PATH=$SOURCE_PATH
#SETUP_FILE=setup.cfg
#NOTIFY_PWD=luanteylo@gmail.com

# database password 
db_pwd=luan1110


#uid=1000
#gid=1000


# install dependencies
sudo apt -y update

sudo apt install -y build-essential
sudo apt install -y libssl-dev
sudo apt install -y libffi-dev
sudo apt install -y python-dev
sudo apt install -y libpq-dev
sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y postgresql-client
sudo apt install -y docker


# install python requirements
pip3 install -r $SOURCE_PATH/requirements.txt

# install database
mkdir -p ~/docker/volumes/postgres
docker run -e POSTGRES_PASSWORD=$db_pwd -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data --name pg-docker test -N 1500  -B 4096MB
#cat $SOURCE_PATH/install/control/clean_db.sql | docker exec -i pg-docker psql -U postgres


# creating aws config file
mkdir -p ~/.aws/

echo "[default]
region = us-east-1
output = json" | tee -a ~/.aws/config

echo "[default]
aws_access_key_id = $AWS_ACCESS_ID
aws_secret_access_key = $AWS_ACCESS_PWD
" | tee -a ~/.aws/credentials

