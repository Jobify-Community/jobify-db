from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jobify_db import StorageConfigurationError, StorageNotInitializedError
from jobify_db.postgresql.psycopg import PsycopgStorage


class TestPsycopgStorageInit:
    def test_raises_when_no_conninfo_and_no_pool(self) -> None:
        with pytest.raises(StorageConfigurationError):
            PsycopgStorage()

    def test_raises_on_invalid_table_name(self) -> None:
        with pytest.raises(ValueError, match="Invalid table name"):
            PsycopgStorage(
                conninfo="postgresql://localhost/test", table_name="DROP TABLE;"
            )

    def test_creates_with_conninfo_pool_not_ready(self) -> None:
        storage = PsycopgStorage(conninfo="postgresql://localhost/test")
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool

    def test_creates_with_pool(self) -> None:
        mock_pool = MagicMock()
        storage = PsycopgStorage(pool=mock_pool)
        assert storage.pool is mock_pool


class TestPsycopgStoragePool:
    def test_pool_raises_when_not_initialized(self) -> None:
        storage = PsycopgStorage(conninfo="postgresql://localhost/test")
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool


class TestPsycopgStorageShutdown:
    @pytest.mark.asyncio()
    async def test_shutdown_closes_owned_pool(self) -> None:
        mock_conn = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_conn

        mock_pool = MagicMock()
        mock_pool.closed = False
        mock_pool.connection.return_value = mock_cm
        mock_pool.open = AsyncMock()
        mock_pool.close = AsyncMock()

        storage = PsycopgStorage(conninfo="postgresql://localhost/test")

        with patch(
            "jobify_db._internal.postgresql.psycopg.storage.AsyncConnectionPool",
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
        storage = PsycopgStorage(pool=mock_pool)

        await storage.shutdown()

        mock_pool.close.assert_not_awaited()
        assert storage.pool is mock_pool

    @pytest.mark.asyncio()
    async def test_shutdown_noop_when_no_pool(self) -> None:
        storage = PsycopgStorage(conninfo="postgresql://localhost/test")
        await storage.shutdown()


class TestPsycopgStorageDeleteScheduleMany:
    @pytest.mark.asyncio()
    async def test_delete_many_noop_for_empty_list(self) -> None:
        mock_pool = AsyncMock()
        storage = PsycopgStorage(pool=mock_pool)

        await storage.delete_schedule_many([])

        mock_pool.connection.assert_not_called()
