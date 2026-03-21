# AGENTS.md

This file provides context for AI coding agents (GitHub Copilot, Cursor, Windsurf, etc.) working on this project.

## Project

**jobify-db** — database storage backends for the [Jobify](https://github.com/theseriff/jobify) scheduling framework.

Implements `Storage` protocol with drivers: asyncpg, psycopg (PostgreSQL), motor (MongoDB), aiomysql (MySQL).

## Structure

- `src/jobify_db/_internal/` — private implementations, not public API
- `src/jobify_db/{db}/{driver}.py` — public re-exports (e.g. `from jobify_db.postgresql.asyncpg import AsyncpgStorage`)
- `tests/unit/` — mocked unit tests, no external dependencies
- `tests/integration/` — real database tests via testcontainers (Docker required)
- `tests/factories.py` — shared test helpers: `make_job()`, `make_aiomysql_mock_pool()`, `make_psycopg_mock_pool()`, `make_motor_mock_client()`
- `examples/` — usage examples for each driver

## Rules

- Python 3.10+ syntax. Do NOT use `from __future__ import annotations`.
- No lazy `__getattr__` imports — use explicit re-exports in public subpackages.
- Strict mypy (`mypy.ini`), strict ruff (`ruff.toml`), strict bytes.
- Configs are in separate files: `ruff.toml`, `mypy.ini`, `pytest.ini` — not in `pyproject.toml`.
- Use `just lint` to run linting, `just mypy` for type checking.
- Run `uv run --active --frozen pytest tests/unit/` for quick feedback (no Docker).
- All storage classes follow the same pattern: `__init__` (validate + store config), `startup()` (create pool + DDL), `shutdown()` (close owned resources), CRUD methods.
- Pool/client ownership pattern: if the user passes an external pool/client, the storage must NOT close it on shutdown.
- Each driver has its own query files under `_internal/{db}/{driver}/queries.py`.

## Adding a new storage backend

1. Create `src/jobify_db/_internal/{db}/{driver}/` with `__init__.py`, `storage.py`, `queries.py`
2. Create shared queries in `src/jobify_db/_internal/{db}/queries.py` if needed (DDL/SELECT)
3. Create public re-export: `src/jobify_db/{db}/{driver}.py`
4. Add optional dependency in `pyproject.toml` under `[project.optional-dependencies]`
5. Add unit tests in `tests/unit/test_{driver}_storage.py`
6. Integration tests are parametrized in `tests/integration/test_storage.py` — add fixture in `conftest.py` and append to `storage`/`storage_from_external` fixture params
7. Add example files in `examples/`
8. Update `README.md` and `noxfile.py`
