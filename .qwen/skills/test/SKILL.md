---
name: test
description: Run project tests (unit, integration, or all)
tags: ["testing", "pytest"]
---

## Unit tests (no Docker)

```sh
uv run --active --frozen pytest tests/unit/ -v
```

## Integration tests (requires Docker)

```sh
uv run --active --frozen pytest tests/integration/ -v
```

## All tests

```sh
uv run --active --frozen pytest tests/ -v
```

## Multi-version matrix

```sh
uv run --active --frozen nox
```

Test factories are in `tests/factories.py`. Integration tests are parametrized across all storage backends in `tests/integration/test_storage.py`.
