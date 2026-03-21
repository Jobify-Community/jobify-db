# GitHub Copilot Instructions

## Project: jobify-db

Database storage backends for the Jobify scheduling framework. Drivers: asyncpg, psycopg (PostgreSQL), motor (MongoDB), aiomysql (MySQL).

## Rules

- Python 3.10+. Do NOT use `from __future__ import annotations`.
- No lazy `__getattr__` imports — use explicit re-exports.
- All async code, strict mypy, strict ruff.
- Configs in separate files: `ruff.toml`, `mypy.ini`, `pytest.ini`.
- Pool/client ownership: external resources must NOT be closed on shutdown.
- Use `Final` for immutable attributes, `TypeAlias` for complex generics.
- Test factories in `tests/factories.py`.

## Structure

- Private implementations: `src/jobify_db/_internal/{db}/{driver}/storage.py`
- Public re-exports: `src/jobify_db/{db}/{driver}.py`
- Shared queries: `src/jobify_db/_internal/{db}/queries.py`
- Integration tests parametrized in `tests/integration/test_storage.py`

## Storage interface

```python
class Storage:
    async def startup(self) -> None: ...
    async def shutdown(self) -> None: ...
    async def get_schedules(self) -> list[ScheduledJob]: ...
    async def add_schedule(self, *scheduled: ScheduledJob) -> None: ...
    async def delete_schedule(self, job_id: str) -> None: ...
    async def delete_schedule_many(self, job_ids: Sequence[str]) -> None: ...
```
