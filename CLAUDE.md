# CLAUDE.md

## Project overview

**jobify-db** is a Python library providing database storage backends for the [Jobify](https://github.com/theseriff/jobify) scheduling framework. It implements the `Storage` protocol from jobify with support for PostgreSQL, MongoDB, and MySQL.

## Architecture

```
src/jobify_db/
  _internal/           # Private implementation (not part of public API)
    common/
      consts.py        # DEFAULT_TABLE_NAME, DEFAULT_COLLECTION_NAME, DEFAULT_DATABASE_NAME
      errors.py        # StorageConfigurationError, StorageNotInitializedError, StorageError
    postgresql/
      queries.py       # Shared PostgreSQL DDL/DML
      asyncpg/         # asyncpg driver
      psycopg/         # psycopg3 driver
    mongodb/
      motor/           # motor driver
    mysql/
      queries.py       # Shared MySQL DDL/DML
      aiomysql/        # aiomysql driver
  postgresql/          # Public subpackage: asyncpg.py, psycopg.py (re-exports)
  mongodb/             # Public subpackage: motor.py (re-export)
  mysql/               # Public subpackage: aiomysql.py (re-export)
  __init__.py          # Exports only error classes
```

### Key patterns

- **Public imports** via subpackages: `from jobify_db.postgresql.asyncpg import AsyncpgStorage` (no lazy `__getattr__` imports)
- **Pool/client ownership**: `_owns_pool`/`_owns_client` flag — only close resources the storage created itself
- **Property access** to pool/client/collection guarded by `StorageNotInitializedError`
- **Storage protocol**: `startup()`, `shutdown()`, `get_schedules()`, `add_schedule()`, `delete_schedule()`, `delete_schedule_many()`
- **ScheduledJob** is a NamedTuple: `job_id`, `name`, `message` (bytes), `status` (JobStatus enum), `next_run_at` (datetime)

### Driver differences

| Feature | asyncpg | psycopg | motor | aiomysql |
|---------|---------|---------|-------|----------|
| Params | `$1, $2` | `%s` | N/A | `%s` |
| Upsert | `ON CONFLICT DO UPDATE` | `ON CONFLICT DO UPDATE` | `find_one_and_update` | `ON DUPLICATE KEY UPDATE ... AS new` |
| Transactions | explicit `async with pool.acquire() as conn, conn.transaction()` | explicit `async with conn.transaction()` | none (single-doc ops are atomic) | manual `conn.commit()` |
| Delete many | `ANY($1::TEXT[])` | `ANY(%s::TEXT[])` | `delete_many({"job_id": {"$in": ...}})` | `executemany` with single DELETE |

## Commands

```sh
just lint              # ruff format + ruff check + codespell
just mypy              # type checking
just semgrep           # semgrep scan
just bandit            # security linting
just pre-commit-all    # all pre-commit hooks
just static-analysis   # mypy + bandit + semgrep

# Tests
uv run --active --frozen pytest tests/                    # all tests (requires Docker)
uv run --active --frozen pytest tests/unit/               # unit tests only (no Docker)
uv run --active --frozen pytest tests/integration/        # integration tests (requires Docker)
```

## Code conventions

- Python 3.10+ — no `from __future__ import annotations`
- Type hints: use `Final[str]`, `TypeAlias` for complex generics
- Configs are split: `ruff.toml`, `mypy.ini`, `pytest.ini` (not in `pyproject.toml`)
- `ruff.toml` takes precedence over `pyproject.toml` for ruff settings
- Strict mypy with `strict_bytes = True`
- All async code, no sync wrappers
- No docstrings enforced (D1xx rules disabled in ruff)
- Test factories in `tests/factories.py` — mock factories and `make_job()` helper
- Integration tests use `testcontainers` (requires Docker daemon)
- `detect-secrets` excludes `examples/` and `README.md` via `.pre-commit-config.yaml`

## Installation extras

```sh
pip install jobify-db[asyncpg]    # PostgreSQL via asyncpg
pip install jobify-db[psycopg]    # PostgreSQL via psycopg3
pip install jobify-db[motor]      # MongoDB via motor
pip install jobify-db[aiomysql]   # MySQL via aiomysql
```
