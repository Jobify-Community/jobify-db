---
paths:
  - "src/jobify_db/_internal/**/storage.py"
---

# Storage implementation rules

When modifying or creating storage implementations:

- Every storage class MUST inherit from `Storage` and use `@override` on all protocol methods
- Constructor MUST call `validate_table_name(table_name)` (or equivalent for MongoDB)
- Constructor MUST accept either connection params OR an external pool/client
- Set `_owns_pool = pool is None` (or `_owns_client = client is None`) to track ownership
- `pool`/`client`/`collection` property MUST raise `StorageNotInitializedError` if resource is None
- `shutdown()` MUST only close resources when `_owns_pool`/`_owns_client` is True
- All queries MUST be parameterized — no string formatting with user input
- Use `Final` for all immutable instance attributes
- Format queries in `__init__` with `table_name` only (trusted, validated input)
