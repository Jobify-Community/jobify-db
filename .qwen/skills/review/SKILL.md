---
name: review
description: Review code changes for quality, security, and project conventions
tags: ["code-review", "quality"]
---

## Review checklist

### Project conventions
- No `from __future__ import annotations`
- No lazy `__getattr__` imports — only explicit re-exports
- `Final` for immutable attributes, `TypeAlias` for complex generics
- Pool/client ownership: external resources must NOT be closed on shutdown
- All code is async, no sync wrappers

### Type safety
- Strict mypy compliance (`mypy.ini`)
- `strict_bytes = True`

### Security
- No SQL injection — parameterized queries only
- No hardcoded secrets
- `validate_table_name()` called in every storage `__init__`

### Tests
- Factories in `tests/factories.py`, not inline
- Integration tests parametrized in `test_storage.py`
- Use `MagicMock` for sync context managers (aiomysql pool.acquire/conn.cursor)

### Output
For each issue: file:line, severity (error/warning/suggestion), fix recommendation.
