from jobify_db._internal.common.errors.storage import StorageError


class StorageNotInitializedError(StorageError):
    def __init__(self) -> None:
        super().__init__("Storage not initialized. Call startup() first.")
