---
name: lint
description: Run full linting and type checking suite
user-invocable: true
allowed-tools: Bash(just *), Bash(uv run *)
---

Run the full quality check pipeline:

1. Linting:
```sh
just lint
```

2. Type checking:
```sh
just mypy
```

If there are errors, show them with file paths and line numbers. After fixing, re-run to confirm.
