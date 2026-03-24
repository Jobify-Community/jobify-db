from collections.abc import Sequence
from typing import Any, Final, TypeAlias
from zoneinfo import ZoneInfo

from jobify._internal.common.constants import JobStatus
from jobify._internal.storage.base import ScheduledJob, Storage
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
)
from pymongo import UpdateOne
from typing_extensions import override

from jobify_db._internal.common.consts import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_DATABASE_NAME,
)
from jobify_db._internal.common.errors import (
    StorageConfigurationError,
    StorageNotInitializedError,
)

_Document: TypeAlias = dict[str, Any]
_Client: TypeAlias = AsyncIOMotorClient[_Document]
_Collection: TypeAlias = AsyncIOMotorCollection[_Document]


class MotorStorage(Storage):
    def __init__(
        self,
        uri: str | None = None,
        *,
        client: _Client | None = None,
        database_name: str = DEFAULT_DATABASE_NAME,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        if uri is None and client is None:
            msg = "Either 'uri' or 'client' must be provided."
            raise StorageConfigurationError(msg)

        self._uri: Final[str | None] = uri
        self._client: _Client | None = client
        self._owns_client: bool = client is None
        self._database_name: Final[str] = database_name
        self._collection_name: Final[str] = collection_name
        self._collection: _Collection | None = None
        self._tz: Final[ZoneInfo] = ZoneInfo("UTC")

    @property
    def client(self) -> _Client:
        if self._client is None:
            raise StorageNotInitializedError
        return self._client

    @property
    def collection(self) -> _Collection:
        if self._collection is None:
            raise StorageNotInitializedError
        return self._collection

    @override
    async def startup(self) -> None:
        if self._client is None:
            self._client = AsyncIOMotorClient(self._uri)

        db = self.client[self._database_name]
        self._collection = db[self._collection_name]

        await self._collection.create_index("job_id", unique=True)

    @override
    async def shutdown(self) -> None:
        if self._client is not None and self._owns_client:
            self._client.close()
            self._client = None
        self._collection = None

    @override
    async def get_schedules(self) -> list[ScheduledJob]:
        cursor = self.collection.find(
            {},
            {
                "_id": 0,
                "job_id": 1,
                "name": 1,
                "message": 1,
                "status": 1,
                "next_run_at": 1,
            },
        )
        return [
            ScheduledJob(
                job_id=doc["job_id"],
                name=doc["name"],
                message=doc["message"],
                status=JobStatus(doc["status"]),
                next_run_at=doc["next_run_at"].astimezone(self._tz),
            )
            async for doc in cursor
        ]

    @override
    async def add_schedule(self, *scheduled: ScheduledJob) -> None:
        operations = [
            UpdateOne(
                {"job_id": sch.job_id},
                {
                    "$set": {
                        "name": sch.name,
                        "message": sch.message,
                        "status": sch.status,
                        "next_run_at": sch.next_run_at,
                    },
                    "$setOnInsert": {"job_id": sch.job_id},
                },
                upsert=True,
            )
            for sch in scheduled
        ]
        await self.collection.bulk_write(operations)

    @override
    async def delete_schedule(self, job_id: str) -> None:
        await self.collection.delete_one({"job_id": job_id})

    @override
    async def delete_schedule_many(self, job_ids: Sequence[str]) -> None:
        if not job_ids:
            return

        await self.collection.delete_many({"job_id": {"$in": list(job_ids)}})
