SELECT T1.instance_id, instance.type, instance.market, status, timestamp
FROM instance, instance_status, (SELECT DISTINCT instance_id
				FROM execution 
				WHERE job_id=553 and execution_id=81
				) as T1
WHERE T1.instance_id = instance.id and T1.instance_id = instance_status.instance_id and status='terminated'
ORDER BY timestamp;
