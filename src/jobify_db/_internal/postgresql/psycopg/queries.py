INSERT_SCHEDULE_QUERY = """
INSERT INTO {table_name} (job_id, name, message, status, next_run_at)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (job_id) DO UPDATE SET
    name = EXCLUDED.name,
    message = EXCLUDED.message,
    status = EXCLUDED.status,
    next_run_at = EXCLUDED.next_run_at,
    updated_at = NOW();
"""

DELETE_SCHEDULE_QUERY = """
DELETE FROM {table_name} WHERE job_id = %s;
"""

DELETE_SCHEDULE_MANY_QUERY = """
DELETE FROM {table_name} WHERE job_id = ANY(%s::TEXT[]);
"""
