# Contributing

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- [just](https://github.com/casey/just) command runner
- Docker (for integration tests)

## Setup

```sh
git clone https://github.com/C3EQUALZz/jobify-db.git
cd jobify-db
uv sync --all-extras
```

## Development workflow

### Linting and type checking

```sh
just lint              # ruff format + ruff check + codespell
just mypy              # mypy strict mode
just static-analysis   # mypy + bandit + semgrep
just pre-commit-all    # all pre-commit hooks
```

### Running tests

```sh
# Unit tests (no Docker required)
uv run --active --frozen pytest tests/unit/

# Integration tests (requires Docker)
uv run --active --frozen pytest tests/integration/

# All tests
uv run --active --frozen pytest tests/

# With coverage
uv run --active --frozen pytest tests/ --cov=jobify_db
```

### Multi-version testing

```sh
uv run --active --frozen nox
```

This runs tests across Python 3.10-3.14 and multiple jobify versions.

## Code style

- Type all functions, use `Final` for immutable attributes
- Follow existing patterns in `_internal/` for new storage backends
- Test factories go in `tests/factories.py`
- Configuration files are separate: `ruff.toml`, `mypy.ini`, `pytest.ini`

## Adding a new storage backend

See [AGENTS.md](AGENTS.md#adding-a-new-storage-backend) for the step-by-step checklist.
