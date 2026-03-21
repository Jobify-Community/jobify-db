CREATE_SCHEDULED_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS {table_name} (
    job_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    message BYTEA NOT NULL,
    status TEXT NOT NULL,
    next_run_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

SELECT_SCHEDULES_QUERY = """
SELECT job_id, name, message, status, next_run_at
FROM {table_name};
"""
