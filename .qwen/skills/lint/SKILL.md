---
name: lint
description: Run all linting checks (ruff format, ruff check, codespell)
tags: ["quality", "linting"]
---

Run the project linter suite:

```sh
just lint
```

This executes:
1. `ruff format` — auto-format code
2. `ruff check --exit-non-zero-on-fix` — lint with auto-fix
3. `codespell` — spell checking

Configuration: `ruff.toml` (not pyproject.toml).
