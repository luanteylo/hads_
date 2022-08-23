MSG='''
\n\n
\t###########################################################################################################################################\n
\t\n\n
\t INSTALL POSTGRES
\t\n\n
\t###########################################################################################################################################\n
'''

echo $MSG


mkdir -p $HOME/docker/volumes/postgres

docker run -e POSTGRES_PASSWORD=luan1110 -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data --name pg-docker postgres -N 1500  -B 4096MB

echo "Note: Before the control execution, to create the database, execute client.py recreate_db "

