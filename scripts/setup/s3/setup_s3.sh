
MSG='''
\n\n
\t###########################################################################################################################################\n
\t\n\n 
\t SETUP S3
\n\n
\t###########################################################################################################################################\n
'''

echo $MSG

sudo apt install -y awscli
sudo apt install -y automake autotools-dev fuse g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config


# prepare s3 setup
#git clone https://github.com/s3fs-fuse/s3fs-fuse.git
(cd s3fs-fuse; ./autogen.sh; ./configure --prefix=/usr --with-openssl; make; sudo make install)

# configuring access key
echo "Access key ID: "
read key
echo "Secret access Key: "
read pwd

echo "$key:$pwd"| sudo tee -a /etc/passwd-s3fs > /dev/null
sudo chmod 640 /etc/passwd-s3fs

echo 'Setup s3fs'
echo "user_allow_other" | sudo tee -a /etc/fuse.conf > /dev/null
