#!/usr/bin/env bash
MSG='''
\n\n
\t###########################################################################################################################################\n
\t\n\n
\t INSTALL CONTROL
\n\n
\t###########################################################################################################################################\n
'''

echo $MSG

mkdir -p $HOME/app

sudo apt -y update

sudo apt install -y libpq-dev
sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y postgresql-client

# configuring access key
echo "Access key ID: "
read key
echo "Secret access Key: "
read pwd

echo "Notify email : "
read pwd_mail

echo "Bucket name"
read bucket


uid=1000
gid=1000



export AWS_ACCESS_ID=$key
export AWS_ACCESS_PWD=$pwd

export SETUP_PATH=$HOME/Devel/control/
export SETUP_FILE=setup.cfg

export NOTIFY_PWD=$pwd_mail


echo "export AWS_ACCESS_ID=$key
export AWS_ACCESS_PWD=$pwd

export SETUP_PATH=$HOME/Devel/control/
export SETUP_FILE=setup.cfg

export NOTIFY_PWD=$pwd_mail

alias db='psql -h localhost -U postgres -d controldb'
" | tee -a $HOME/.bashrc


echo "[default]
region = us-east-1
output = json" | tee -a $HOME/.aws/config

echo "[default]
aws_access_key_id = $key
aws_secret_access_key = $pwd
" | tee -a $HOME/.aws/credentials




alias db='psql -h localhost -U postgres -d controldb'


echo "Mounting S3"
# mount the bucket
sudo s3fs $bucket -o use_cache=/tmp -o allow_other -o uid=$uid -o gid=$gid -o mp_umask=002 -o multireq_max=5 ~/storage

echo "starting postgres"

docker start pg-docker


(cd $HOME/Devel/control/; pip3 install -r requirements.txt)


echo "Don't forget to send the .pem!!!"
echo "Don't foget to send the update version of synthetic!!!!!"
echo "Don't forget to define app folder!!!"

echo "Don't forget fix DB pwd"

# cat $HOME/Devel/control/scripts/setup/ami/clean_dump.sql | docker exec -i pg-docker psql -U postgres
