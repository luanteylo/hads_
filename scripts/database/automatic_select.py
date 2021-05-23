import psycopg2


def generate_output(job_id, execution_id):
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="luan1110",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="controldb")
        cursor = connection.cursor()
        query = "SELECT M1.job_id, M1.execution_id, M1.task_id, M3.command, M1.type, " \
                "EXTRACT(EPOCH FROM (M2.timestamp - M1.timestamp)) as timest, M2.avg_memory " \
                "FROM  (SELECT job_id, execution_id, task_id, type, instance_id, status, timestamp " \
                "FROM (SELECT job_id, execution_id, task_id, instance_id, timestamp, status " \
                "FROM execution  WHERE status ='executing') as T1, " \
                "(SELECT id, type FROM instance) as T2 WHERE T1.instance_id = T2.id) as M1, " \
                "(SELECT job_id, execution_id, task_id, type, instance_id, status, timestamp, avg_memory " \
                "FROM (SELECT job_id, execution_id, task_id, instance_id, timestamp, status, avg_memory " \
                "FROM execution WHERE status ='finished') as T1, " \
                "(SELECT id, type FROM instance) as T2 WHERE T1.instance_id = T2.id) as M2, " \
                "(SELECT * FROM task) as M3 " \
                "WHERE  M1.job_id = M2.job_id and M1.execution_id = M2.execution_id " \
                "and M1.task_id = M2.task_id and M1.instance_id = M2.instance_id " \
                "and M1.task_id = M3.task_id and M1.job_id = M3.job_id " \
                "and M1.job_id={0} and M1.execution_id={1} ORDER by M1.task_id, M1.timestamp".format(job_id,
                                                                                                     execution_id)

        SQL_for_file_output = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

        file_csv = "/home/luan/csv_output/output_{}_{}.csv".format(job_id, execution_id)
        with open(file_csv, 'w') as f_output:
            cursor.copy_expert(SQL_for_file_output, f_output)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


job_id = 551
execution_id = [0,1, 3]

for id in execution_id:
    generate_output(job_id=job_id, execution_id=id)
