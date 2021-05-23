/* Get status of the used instances */

    SELECT T1.instance_id, type, market, status, timestamp
    FROM instance, instance_status, (SELECT DISTINCT instance_id
                    FROM execution
                    WHERE job_id=12 and execution_id=2
                    ) as T1
    WHERE T1.instance_id = instance.id and T1.instance_id = instance_status.instance_id
    ORDER BY timestamp;


/* get instances up time */
SELECT T1.instance_id, T2.type, T2.market,  EXTRACT(EPOCH FROM (M2.timestamp - M1.timestamp)) as uptime
FROM
    -- Get instance IDs
    (SELECT DISTINCT instance_id, job_id, execution_id FROM execution) as T1,

    -- Get instance type
    (SELECT id, type, market FROM instance) as T2,

    -- get start timestamp
    (SELECT instance_id, timestamp FROM instance_status where status='running') as M1,


    --get end timestamp
    (SELECT instance_id, timestamp FROM instance_status where status='terminated') as M2

WHERE T1.instance_id = T2.id
and M1.instance_id = T2.id
and M2.instance_id = T2.id
and T1.job_id = 101 and T1.execution_id  = 0;



/*Get number of finished tasks*/
SELECT COUNT(*)
FROM execution
WHERE job_id=551 and execution_id=0 and status='finished';

/* GEt test info */
SELECT on_demand, spot, elapsed, cost, hibernations, work_stealing, hibernation_recovery, working_migration, idle_migration, hibernation_timeout, completed_tasks
FROM TEST
WHERE job_id=551 and execution_id=0;




/*GET tasks memory*/
SELECT min(avg_memory)
FROM execution
WHERE job_id=551 and execution_id=0 and status='finished';


/* GET TASK EXECUTION WITH instances
 */

    SELECT T2.task_id, T2.instance_id, T1.type, T2.status, T2.avg_memory
    FROM instance as T1,
         (SELECT task_id, instance_id, status, avg_memory, timestamp
          FROM execution
          WHERE execution_id=0 and job_id=551 and status='finished') as T2
    WHERE T1.id = T2.instance_id order by T1.type;

/* COPY SELECT to csv file*/
-- \copy (Select * From job) To '/home/luan/test.csv' With csv;

/*get task execution time*/

SELECT M1.job_id, M1.execution_id, M1.task_id, M3.command, M1.type, EXTRACT(EPOCH FROM (M2.timestamp - M1.timestamp)) as timest
FROM
    -- get tasks with executing status
    (SELECT job_id, execution_id, task_id, type, instance_id, status, timestamp
    FROM (SELECT job_id, execution_id, task_id, instance_id, timestamp, status
    FROM execution
    WHERE status ='executing') as T1,
          (SELECT id, type FROM instance) as T2
          WHERE T1.instance_id = T2.id) as M1,

    -- get tasks with finished status
    (SELECT job_id, execution_id, task_id, type, instance_id, status, timestamp
    FROM (SELECT job_id, execution_id, task_id, instance_id, timestamp, status
          FROM execution
          WHERE status ='finished') as T1,
          (SELECT id, type FROM instance) as T2
    WHERE T1.instance_id = T2.id) as M2,

    -- get tasks parameters
    (SELECT * FROM task) as M3

WHERE  M1.job_id = M2.job_id and M1.execution_id = M2.execution_id
 and M1.task_id = M2.task_id and M1.instance_id = M2.instance_id
 and M1.task_id = M3.task_id and M1.job_id = M3.job_id
 and M1.job_id=1 and M1.execution_id=1 ORDER by M1.task_id, M1.timestamp;




-- Get tasks runtime


SELECT T1.job_id, T1.execution_id, T1.task_id, T1.timestamp, T2.timestamp, EXTRACT(EPOCH FROM (T2.timestamp - T1.timestamp)) as timest
FROM
     -- get tasks with executing status
    (SELECT job_id, execution_id, task_id, instance_id, timestamp, status
    FROM execution
    WHERE status ='executing') as T1,

    -- get tasks with finished status
    (SELECT job_id, execution_id, task_id, instance_id, timestamp, status
    FROM execution
    WHERE status ='finished') as T2
WHERE T1.job_id = T2.job_id and T1.execution_id = T2.execution_id
and   T1.task_id = T2.task_id and T1.job_id=1 and T1.execution_id = 2;


-- Get average runtime by task
SELECT AVG(timest)
FROM
    (SELECT T1.job_id as job_id, T1.task_id as task_id, T1.execution_id, T1.instance_id as instance_id, EXTRACT(EPOCH FROM (T2.timestamp - T1.timestamp)) as timest
    FROM
         -- get tasks with executing status
        (SELECT job_id, execution_id, task_id, instance_id, timestamp, status
        FROM execution
        WHERE status ='executing') as T1,

        -- get tasks with finished status
        (SELECT job_id, execution_id, task_id, instance_id, timestamp, status
        FROM execution
        WHERE status ='finished') as T2,


     WHERE T1.job_id = T2.job_id and T1.execution_id = T2.execution_id) as T4
WHERE  job_id=1 and task_id=0;
