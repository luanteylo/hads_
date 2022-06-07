#!/usr/bin/env bash

# full path to the framework code
SOURCE_PATH=~/Devel/hads_


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
docker run -e POSTGRES_PASSWORD='to_change' -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data --name pg-docker postgres -N 1500  -B 4096MB
cat $SOURCE_PATH/install/control/clean_db.sql | docker exec -i pg-docker psql -U postgres


# creating aws config file
mkdir -p ~/.aws/

echo "[default]
region = us-east-1
output = json" | tee -a ~/.aws/config

echo "[default]
aws_access_key_id = ID
aws_secret_access_key = ACCESS_KEY
" | tee -a ~/.aws/credentials

