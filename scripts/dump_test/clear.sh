docker stop $1
docker rm $1
(cd $HOME/s3/test/0/data/; rm *.txt)
(cd $HOME/s3/test/0/backup; rm -rf checkpoint0)
