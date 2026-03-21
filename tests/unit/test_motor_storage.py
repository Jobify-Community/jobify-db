from unittest.mock import MagicMock, patch

import pytest

from jobify_db import StorageConfigurationError, StorageNotInitializedError
from jobify_db.mongodb.motor import MotorStorage
from tests.factories import make_motor_mock_client


class TestMotorStorageInit:
    def test_raises_when_no_uri_and_no_client(self) -> None:
        with pytest.raises(StorageConfigurationError):
            MotorStorage()

    def test_creates_with_uri_collection_not_ready(self) -> None:
        storage = MotorStorage(uri="mongodb://localhost:27017")
        with pytest.raises(StorageNotInitializedError):
            _ = storage.collection

    def test_creates_with_client(self) -> None:
        mock_client = MagicMock()
        storage = MotorStorage(client=mock_client)
        with pytest.raises(StorageNotInitializedError):
            _ = storage.collection


class TestMotorStorageStartup:
    @pytest.mark.asyncio()
    async def test_startup_creates_client_from_uri(self) -> None:
        mock_client, _, mock_collection = make_motor_mock_client()

        storage = MotorStorage(uri="mongodb://localhost:27017")

        with patch(
            "jobify_db._internal.mongodb.motor.storage.AsyncIOMotorClient",
            return_value=mock_client,
        ) as create:
            await storage.startup()
            create.assert_called_once_with("mongodb://localhost:27017")

        mock_collection.create_index.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_startup_uses_existing_client(self) -> None:
        mock_client, _, mock_collection = make_motor_mock_client()

        storage = MotorStorage(client=mock_client)

        with patch(
            "jobify_db._internal.mongodb.motor.storage.AsyncIOMotorClient",
        ) as create:
            await storage.startup()
            create.assert_not_called()

        mock_collection.create_index.assert_awaited_once()


class TestMotorStorageShutdown:
    @pytest.mark.asyncio()
    async def test_shutdown_closes_owned_client(self) -> None:
        mock_client, _, _ = make_motor_mock_client()

        storage = MotorStorage(uri="mongodb://localhost:27017")

        with patch(
            "jobify_db._internal.mongodb.motor.storage.AsyncIOMotorClient",
            return_value=mock_client,
        ):
            await storage.startup()

        await storage.shutdown()

        mock_client.close.assert_called_once()
        with pytest.raises(StorageNotInitializedError):
            _ = storage.collection

    @pytest.mark.asyncio()
    async def test_shutdown_does_not_close_external_client(self) -> None:
        mock_client, _, _ = make_motor_mock_client()

        storage = MotorStorage(client=mock_client)
        await storage.startup()
        await storage.shutdown()

        mock_client.close.assert_not_called()

    @pytest.mark.asyncio()
    async def test_shutdown_noop_when_no_client(self) -> None:
        storage = MotorStorage(uri="mongodb://localhost:27017")
        await storage.shutdown()


class TestMotorStorageDeleteScheduleMany:
    @pytest.mark.asyncio()
    async def test_delete_many_noop_for_empty_list(self) -> None:
        mock_client, _, mock_collection = make_motor_mock_client()

        storage = MotorStorage(client=mock_client)
        await storage.startup()

        await storage.delete_schedule_many([])

        mock_collection.delete_many.assert_not_awaited()
