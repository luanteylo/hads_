
# DUMP
docker exec -t pg-docker pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql

# RECOVERY

cat your_dump.sql | docker exec -i pg-docker psql -U postgres
