---
name: add-storage
description: Guided workflow for adding a new storage backend
user-invocable: true
argument-hint: "<db> <driver>"
agent: storage-architect
context: fork
---

Add a new storage backend to jobify-db.

Arguments: $ARGUMENTS (e.g., "redis aioredis" or "sqlite aiosqlite")

## Checklist

1. Create `src/jobify_db/_internal/{db}/{driver}/` with `__init__.py`, `storage.py`, `queries.py`
2. Shared DDL in `src/jobify_db/_internal/{db}/queries.py` if needed
3. Public re-export: `src/jobify_db/{db}/{driver}.py` + empty `src/jobify_db/{db}/__init__.py`
4. Optional dep in `pyproject.toml` `[project.optional-dependencies]`
5. Storage class implementing full `Storage` protocol with `@override` decorators
6. Mock factory in `tests/factories.py` if needed
7. Unit tests: `tests/unit/test_{driver}_storage.py`
8. Integration fixtures in `tests/integration/conftest.py`
9. Append to `storage`/`storage_from_external` params in `tests/integration/test_storage.py`
10. Examples: `examples/{driver}_example.py`, `examples/{driver}_external_pool_example.py`
11. Update: `README.md`, `noxfile.py`, `CLAUDE.md`, `AGENTS.md`, `QWEN.md`
12. Verify: `just lint && just mypy && uv run --active --frozen pytest tests/unit/ -q`
