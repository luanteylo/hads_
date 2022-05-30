#!/usr/bin/env bash


export AWS_ACCESS_ID=AKIA5NIWKB7UTH5NCEEF
export AWS_ACCESS_PWD=nrINqPXWWyF4ral7Jh6kE+06kVONuN4+mPiJoR5U

export SETUP_PATH=$HOME/Devel/hads_/

export SETUP_FILE=setup.cfg

export NOTIFY_PWD=luanteylo@gmail.com


uid=1000
gid=1000



sudo apt -y update

sudo apt install -y libpq-dev
sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y postgresql-client


# creating aws config file

echo "[default]
region = us-east-1
output = json" | tee -a $HOME/.aws/config

echo "[default]
aws_access_key_id = $AWS_ACCESS_ID
aws_secret_access_key = $AWS_ACCESS_PWD
" | tee -a $HOME/.aws/credentials



#alias db='psql -h localhost -U postgres -d controldb'


#echo "Mounting S3"
# mount the bucket
#sudo s3fs $bucket -o use_cache=/tmp -o allow_other -o uid=$uid -o gid=$gid -o mp_umask=002 -o multireq_max=5 ~/storage

#echo "starting postgres"

#docker start pg-docker
#(cd $HOME/Devel/control/; pip3 install -r requirements.txt)


#echo "Don't forget to send the .pem!!!"
#echo "Don't foget to send the update version of synthetic!!!!!"
#echo "Don't forget to define app folder!!!"

#echo "Don't forget fix DB pwd"

# cat $HOME/Devel/control/scripts/setup/ami/clean_dump.sql | docker exec -i pg-docker psql -U postgres