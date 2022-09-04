MSG='''
\n\n
\t###########################################################################################################################################\n
\t\n\n
\t SETUP DOCKER
\n\n
\t###########################################################################################################################################\n
'''

echo $MSG

sudo apt -y update

#wget https://deb.sipwise.com/debian/pool/main/libt/libtool/libltdl7_2.4.6-6_amd64.deb
#wget https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb
#git clone https://github.com/checkpoint-restore/criu

sudo dpkg -i deb/libltdl7_2.4.6-6_amd64.deb
sudo dpkg -i deb/docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb

sudo apt install -f -y

sudo apt install -y build-essential
sudo apt install -y gcc
sudo apt install -y libprotobuf-dev
sudo apt install -y  libprotobuf-c0-dev
sudo apt install -y protobuf-c-compiler
sudo apt install -y protobuf-compiler python-protobuf
sudo apt instlal -y libprotobuf-c-dev
sudo apt install -y pkg-config
sudo apt install -y  python-ipaddr
sudo apt install -y  iproute2
sudo apt install -y  libcap-dev
sudo apt install -y  libnl-3-dev
sudo apt install -y  libnet-dev
sudo apt install -y asciidoc
sudo apt install -y xmlto


sudo apt --fix-broken install -y

git clone https://github.com/checkpoint-restore/criu
(cd criu; make; sudo ./criu/criu check; sudo ./criu/criu –V; sudo apt-get install asciidoc  xmlto; sudo make install)
criu check


sudo groupadd docker
sudo usermod -aG docker $USER

sudo echo '{"experimental": true}'  | sudo tee -a /etc/docker/daemon.json > /dev/null

sudo service docker restart




