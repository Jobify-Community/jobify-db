Run the project test suite. First try unit tests (fast, no Docker):

```sh
uv run --active --frozen pytest tests/unit/ -v
```

If the user wants full tests (requires Docker):

```sh
uv run --active --frozen pytest tests/ -v
```

Report failures with file paths and line numbers. Test factories are in `tests/factories.py`.
