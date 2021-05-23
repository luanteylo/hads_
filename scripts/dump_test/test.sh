# usage: sh start <name> <size> <sleep_seconds>


docker create --name $1 -v /home/ubuntu/s3/test/0/data/:/home/control/ -w /home/control/ synthetic sh exec.sh $2

docker start $1

sleep $3

docker container stats $1 --no-stream

time docker checkpoint create --checkpoint-dir=/home/ubuntu/s3/test/0/backup/ --leave-running=true $1 checkpoint0


sh clear.sh $1
