from jobify._internal.exceptions import BaseJobifyError


class StorageError(BaseJobifyError):
    pass


class StorageNotInitializedError(StorageError):
    def __init__(self) -> None:
        super().__init__("Storage not initialized. Call startup() first.")


class StorageConfigurationError(StorageError):
    pass
