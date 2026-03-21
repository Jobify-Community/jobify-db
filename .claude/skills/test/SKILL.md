---
name: test
description: Run project tests (unit or all)
user-invocable: true
argument-hint: "[unit|integration|all]"
allowed-tools: Bash(uv run *)
---

Run tests based on the argument:

- `unit` or no argument: `uv run --active --frozen pytest tests/unit/ -v`
- `integration`: `uv run --active --frozen pytest tests/integration/ -v` (Docker required)
- `all`: `uv run --active --frozen pytest tests/ -v` (Docker required)

Test factories are in `tests/factories.py`. Integration tests are parametrized across all storage backends in `tests/integration/test_storage.py`.

Report failures with file paths and line numbers.
