---
name: typecheck
description: Run mypy strict type checking
tags: ["quality", "typing"]
---

```sh
just mypy
```

Configuration: `mypy.ini` (strict mode, Python 3.10, strict_bytes=True).

Key rules:
- All functions must be typed
- No implicit optional
- No untyped decorators
- `ignore_missing_imports = True` for third-party libs
- Use `Final` for immutable attributes
- Use `TypeAlias` for complex generic types (e.g., Motor client/collection)
