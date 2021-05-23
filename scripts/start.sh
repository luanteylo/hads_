s3fs bucket-l123 -o use_cache=/tmp -o allow_other -o uid=1000 -o gid=1000 -o mp_umask=002 -o multireq_max=5 $HOME/storage/
docker start pg-docker
