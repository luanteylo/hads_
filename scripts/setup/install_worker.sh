MSG='''
\n\n
\t###########################################################################################################################################\n
\t\n\n 
\t SETUP WORKER
\n\n
\t###########################################################################################################################################\n
'''

# Install python  and libdev

sudo apt install -y python3-pip
sudo apt install -y libpq-dev

# Install static-heuristic requirements

sudo apt install -y g++
sudo apt install -y libboost-all-dev


mkdir -p $HOME/.aws/
mkdir -p $HOME/storage


echo "installing  docker"

(cd docker; sh setup_docker.sh)

echo "installing  S3"

(cd s3; sh setup_s3.sh)

echo "Setup setup_hibernation"
(cd ami; sh setup_hibernation.sh)





