from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jobify_db import StorageConfigurationError, StorageNotInitializedError
from jobify_db.mysql.aiomysql import AiomysqlStorage
from tests.factories import make_aiomysql_mock_pool


class TestAiomysqlStorageInit:
    def test_raises_when_no_host_and_no_pool(self) -> None:
        with pytest.raises(StorageConfigurationError):
            AiomysqlStorage()

    def test_raises_on_invalid_table_name(self) -> None:
        with pytest.raises(ValueError, match="Invalid table name"):
            AiomysqlStorage(host="localhost", table_name="DROP TABLE;")

    def test_creates_with_host_pool_not_ready(self) -> None:
        storage = AiomysqlStorage(host="localhost")
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool

    def test_creates_with_pool(self) -> None:
        mock_pool = MagicMock()
        storage = AiomysqlStorage(pool=mock_pool)
        assert storage.pool is mock_pool


class TestAiomysqlStoragePool:
    def test_pool_raises_when_not_initialized(self) -> None:
        storage = AiomysqlStorage(host="localhost")
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool


class TestAiomysqlStorageStartup:
    @pytest.mark.asyncio()
    async def test_startup_creates_pool_from_host(self) -> None:
        mock_pool = make_aiomysql_mock_pool()
        storage = AiomysqlStorage(
            host="localhost", user="root", password="pass", db="testdb"
        )

        with patch(
            "jobify_db._internal.mysql.aiomysql.storage.aiomysql.create_pool",
            new_callable=AsyncMock,
            return_value=mock_pool,
        ) as create:
            await storage.startup()
            create.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_startup_skips_pool_creation_when_pool_provided(
        self,
    ) -> None:
        mock_pool = make_aiomysql_mock_pool()
        storage = AiomysqlStorage(pool=mock_pool)

        with patch(
            "jobify_db._internal.mysql.aiomysql.storage.aiomysql.create_pool",
            new_callable=AsyncMock,
        ) as create:
            await storage.startup()
            create.assert_not_awaited()


class TestAiomysqlStorageShutdown:
    @pytest.mark.asyncio()
    async def test_shutdown_closes_owned_pool(self) -> None:
        mock_pool = make_aiomysql_mock_pool()
        storage = AiomysqlStorage(host="localhost")

        with patch(
            "jobify_db._internal.mysql.aiomysql.storage.aiomysql.create_pool",
            new_callable=AsyncMock,
            return_value=mock_pool,
        ):
            await storage.startup()

        await storage.shutdown()

        mock_pool.close.assert_called_once()
        mock_pool.wait_closed.assert_awaited_once()
        with pytest.raises(StorageNotInitializedError):
            _ = storage.pool

    @pytest.mark.asyncio()
    async def test_shutdown_does_not_close_external_pool(self) -> None:
        mock_pool = MagicMock()
        storage = AiomysqlStorage(pool=mock_pool)

        await storage.shutdown()

        mock_pool.close.assert_not_called()
        assert storage.pool is mock_pool

    @pytest.mark.asyncio()
    async def test_shutdown_noop_when_no_pool(self) -> None:
        storage = AiomysqlStorage(host="localhost")
        await storage.shutdown()


class TestAiomysqlStorageDeleteScheduleMany:
    @pytest.mark.asyncio()
    async def test_delete_many_noop_for_empty_list(self) -> None:
        mock_pool = MagicMock()
        storage = AiomysqlStorage(pool=mock_pool)

        await storage.delete_schedule_many([])

        mock_pool.acquire.assert_not_called()
