from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jobify_db import StorageConfigurationError, StorageNotInitializedError
from jobify_db.postgresql.asyncpg import AsyncpgStorage


class TestAsyncpgStorageInit:
    def test_raises_when_no_dsn_and_no_pool(self) -> None:
        with pytest.raises(StorageConfigurationError):
            AsyncpgStorage()

    def test_raises_on_invalid_table_name(self) -> None:
        with pytest.raises(ValueError, match="Invalid table name"):
            AsyncpgStorage(dsn="postgresql://localhost/test", table_name="DROP TABLE;")

    def test_creates_with_dsn_pool_not_ready(self) -> None:
        storage = AsyncpgStorage(dsn="postgresql://localhost/test")
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool

    def test_creates_with_pool(self) -> None:
        mock_pool = MagicMock()
        storage = AsyncpgStorage(pool=mock_pool)
        assert storage.pool is mock_pool


class TestAsyncpgStoragePool:
    def test_pool_raises_when_not_initialized(self) -> None:
        storage = AsyncpgStorage(dsn="postgresql://localhost/test")
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool


class TestAsyncpgStorageStartup:
    @pytest.mark.asyncio()
    async def test_startup_creates_pool_from_dsn(self) -> None:
        mock_pool = AsyncMock()
        storage = AsyncpgStorage(dsn="postgresql://localhost/test")

        with patch(
            "jobify_db._internal.postgresql.asyncpg.storage.asyncpg.create_pool",
            new_callable=AsyncMock,
            return_value=mock_pool,
        ) as create:
            await storage.startup()
            create.assert_awaited_once_with(
                dsn="postgresql://localhost/test", min_size=1, max_size=10
            )

        mock_pool.execute.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_startup_skips_pool_creation_when_pool_provided(self) -> None:
        mock_pool = AsyncMock()
        storage = AsyncpgStorage(pool=mock_pool)

        with patch(
            "jobify_db._internal.postgresql.asyncpg.storage.asyncpg.create_pool",
            new_callable=AsyncMock,
        ) as create:
            await storage.startup()
            create.assert_not_awaited()

        mock_pool.execute.assert_awaited_once()


class TestAsyncpgStorageShutdown:
    @pytest.mark.asyncio()
    async def test_shutdown_closes_owned_pool(self) -> None:
        mock_pool = AsyncMock()
        storage = AsyncpgStorage(dsn="postgresql://localhost/test")

        with patch(
            "jobify_db._internal.postgresql.asyncpg.storage.asyncpg.create_pool",
            new_callable=AsyncMock,
            return_value=mock_pool,
        ):
            await storage.startup()

        await storage.shutdown()

        mock_pool.close.assert_awaited_once()
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool

    @pytest.mark.asyncio()
    async def test_shutdown_does_not_close_external_pool(self) -> None:
        mock_pool = AsyncMock()
        storage = AsyncpgStorage(pool=mock_pool)

        await storage.shutdown()

        mock_pool.close.assert_not_awaited()
        assert storage.pool is mock_pool

    @pytest.mark.asyncio()
    async def test_shutdown_noop_when_no_pool(self) -> None:
        storage = AsyncpgStorage(dsn="postgresql://localhost/test")
        await storage.shutdown()


class TestAsyncpgStorageDeleteScheduleMany:
    @pytest.mark.asyncio()
    async def test_delete_many_noop_for_empty_list(self) -> None:
        mock_pool = AsyncMock()
        storage = AsyncpgStorage(pool=mock_pool)

        await storage.delete_schedule_many([])

        mock_pool.execute.assert_not_awaited()
