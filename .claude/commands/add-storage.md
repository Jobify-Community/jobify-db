Help the user add a new storage backend to jobify-db.

Ask for:
- Database type (e.g., redis, sqlite, clickhouse)
- Driver library name (e.g., aioredis, aiosqlite)

Then follow this checklist:

1. Create `src/jobify_db/_internal/{db}/{driver}/` with `__init__.py`, `storage.py`, `queries.py`
2. Create shared queries `src/jobify_db/_internal/{db}/queries.py` if needed (DDL, SELECT)
3. Create public re-export `src/jobify_db/{db}/{driver}.py` and empty `src/jobify_db/{db}/__init__.py`
4. Add optional dep in `pyproject.toml` `[project.optional-dependencies]`
5. Implement storage class following the pattern in existing backends:
   - `__init__()` with connection params OR external pool/client, `_owns_pool` flag
   - `pool`/`client` property guarded by `StorageNotInitializedError`
   - `startup()`, `shutdown()`, CRUD methods with `@override`
6. Add mock factory to `tests/factories.py` if needed
7. Add unit tests `tests/unit/test_{driver}_storage.py`
8. Add fixtures to `tests/integration/conftest.py`
9. Append to `storage`/`storage_from_external` params in `tests/integration/test_storage.py`
10. Add example files in `examples/`
11. Update `README.md`, `noxfile.py`
12. Run `just lint && just mypy && uv run --active --frozen pytest tests/unit/ -q`
