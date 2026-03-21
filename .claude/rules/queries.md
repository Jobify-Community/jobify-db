---
paths:
  - "src/jobify_db/_internal/**/queries.py"
---

# SQL/query rules

- PostgreSQL uses `$1, $2` (asyncpg) or `%s` (psycopg) parameter placeholders
- MySQL uses `%s` parameter placeholders
- MongoDB uses native PyMongo/Motor query syntax
- MySQL upsert: `INSERT ... AS new ON DUPLICATE KEY UPDATE new.column` (not deprecated `VALUES()`)
- PostgreSQL upsert: `ON CONFLICT (job_id) DO UPDATE SET ...`
- Never build SQL via string concatenation with runtime values
- Table name substitution via `.format(table_name=...)` is OK because `validate_table_name()` ensures it's safe
