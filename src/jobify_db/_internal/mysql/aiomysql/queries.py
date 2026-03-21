INSERT_SCHEDULE_QUERY = """
INSERT INTO {table_name} (job_id, name, message, status, next_run_at)
VALUES (%s, %s, %s, %s, %s) AS new
ON DUPLICATE KEY UPDATE
    name = new.name,
    message = new.message,
    status = new.status,
    next_run_at = new.next_run_at;
"""

DELETE_SCHEDULE_QUERY = """
DELETE FROM {table_name} WHERE job_id = %s;
"""
