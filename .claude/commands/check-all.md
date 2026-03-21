Run all quality checks in sequence:

1. Linting:
```sh
just lint
```

2. Type checking:
```sh
just mypy
```

3. Security:
```sh
just bandit
```

4. Unit tests:
```sh
uv run --active --frozen pytest tests/unit/ -q
```

Report a summary of results for each step. Stop on first failure and report it.
