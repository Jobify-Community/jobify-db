---
name: check-all
description: Run all quality checks in sequence (lint, mypy, bandit, tests)
user-invocable: true
allowed-tools: Bash(just *), Bash(uv run *)
---

Run all quality checks in order. Stop on first failure:

1. `just lint` — ruff format + check + codespell
2. `just mypy` — strict type checking
3. `just bandit` — security linting
4. `uv run --active --frozen pytest tests/unit/ -q` — unit tests

Report a summary for each step.
