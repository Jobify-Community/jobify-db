# QWEN.md

## Project

**jobify-db** — database storage backends for the [Jobify](https://github.com/theseriff/jobify) scheduling framework.

Implements `Storage` protocol: `startup()`, `shutdown()`, `get_schedules()`, `add_schedule()`, `delete_schedule()`, `delete_schedule_many()`.

Drivers: asyncpg, psycopg (PostgreSQL), motor (MongoDB), aiomysql (MySQL).

## Structure

```
src/jobify_db/
  _internal/           # Private — all implementations live here
    common/            # Shared constants and errors
    postgresql/        # asyncpg/ and psycopg/ drivers + shared queries.py
    mongodb/           # motor/ driver
    mysql/             # aiomysql/ driver + shared queries.py
  postgresql/          # Public re-exports: asyncpg.py, psycopg.py
  mongodb/             # Public re-export: motor.py
  mysql/               # Public re-export: aiomysql.py
  __init__.py          # Only error classes exported

tests/
  factories.py         # make_job(), make_aiomysql_mock_pool(), make_psycopg_mock_pool(), make_motor_mock_client()
  unit/                # Mocked tests, no Docker
  integration/         # testcontainers, parametrized across all storages
```

## Strict rules

- Python 3.10+. NEVER use `from __future__ import annotations`.
- No lazy `__getattr__` imports. Use explicit re-exports in public subpackages.
- Strict mypy (`mypy.ini`), strict ruff (`ruff.toml`). Configs are separate files, NOT in `pyproject.toml`.
- All code is async. No sync wrappers.
- Pool/client ownership: if user provides external pool/client, do NOT close it on shutdown.
- No docstrings required (D1xx disabled).

## Commands

```sh
just lint              # ruff format + check + codespell
just mypy              # type checking
just static-analysis   # mypy + bandit + semgrep
uv run --active --frozen pytest tests/unit/         # quick tests
uv run --active --frozen pytest tests/              # all tests (Docker required)
```

## Adding a new storage backend

1. `src/jobify_db/_internal/{db}/{driver}/` — `__init__.py`, `storage.py`, `queries.py`
2. Shared DDL in `src/jobify_db/_internal/{db}/queries.py` if needed
3. Public re-export: `src/jobify_db/{db}/{driver}.py`
4. Optional dep in `pyproject.toml` `[project.optional-dependencies]`
5. Unit tests: `tests/unit/test_{driver}_storage.py`
6. Integration: add fixtures to `tests/integration/conftest.py`, append to `storage`/`storage_from_external` params in `test_storage.py`
7. Examples in `examples/`
8. Update `README.md`, `noxfile.py`
