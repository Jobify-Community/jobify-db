---
name: add-storage
description: Step-by-step guide for adding a new storage backend
tags: ["architecture", "implementation"]
---

## Steps to add a new storage backend

1. Create implementation directory:
   ```
   src/jobify_db/_internal/{db}/{driver}/__init__.py
   src/jobify_db/_internal/{db}/{driver}/storage.py
   src/jobify_db/_internal/{db}/{driver}/queries.py
   ```

2. Create shared queries if needed:
   ```
   src/jobify_db/_internal/{db}/queries.py  # DDL (CREATE TABLE), SELECT
   ```

3. Create public re-export:
   ```python
   # src/jobify_db/{db}/{driver}.py
   from jobify_db._internal.{db}.{driver}.storage import {Driver}Storage
   __all__ = ["{Driver}Storage"]
   ```

4. Add empty `__init__.py` for public subpackage `src/jobify_db/{db}/__init__.py`

5. Add optional dependency in `pyproject.toml` under `[project.optional-dependencies]`

6. Storage class requirements:
   - Inherit from `Storage`, use `@override` on all protocol methods
   - Accept connection params OR external pool/client in `__init__`
   - Set `_owns_pool = pool is None` to track ownership
   - `pool`/`client` property raises `StorageNotInitializedError` if None
   - `startup()` creates pool if needed + runs DDL
   - `shutdown()` closes pool ONLY if `_owns_pool is True`
   - All queries must be parameterized

7. Add mock factory to `tests/factories.py` if the driver has complex mock setup

8. Add unit tests: `tests/unit/test_{driver}_storage.py`

9. Add fixtures to `tests/integration/conftest.py`, append fixture names to `storage`/`storage_from_external` params in `tests/integration/test_storage.py`

10. Add examples: `examples/{driver}_example.py`, `examples/{driver}_external_pool_example.py`

11. Update: `README.md`, `noxfile.py`, `CLAUDE.md`, `AGENTS.md`, `QWEN.md`

12. Verify: `just lint && just mypy && uv run --active --frozen pytest tests/unit/ -q`
