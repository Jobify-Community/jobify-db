Run the full linting suite for the project:

```sh
just lint
```

If there are ruff errors that need manual fixes, show them to the user. After fixing, re-run `just lint` to confirm.

Then run type checking:

```sh
just mypy
```

Report any issues found.
