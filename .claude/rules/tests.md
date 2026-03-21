---
paths:
  - "tests/**/*.py"
---

# Test rules

- Use `@pytest.mark.asyncio()` with parentheses (flake8-pytest-style)
- Shared test helpers go in `tests/factories.py`, not inline in test files
- Integration tests are parametrized in `tests/integration/test_storage.py` — add new backends by appending fixture names to `storage`/`storage_from_external` params
- Unit tests use mocks — never connect to real databases
- Each storage-specific shutdown assertion stays as a separate test in `TestExternalShutdown`
- Use `MagicMock` (not `AsyncMock`) for pool/conn objects that use sync context managers (e.g., aiomysql `pool.acquire()`)
