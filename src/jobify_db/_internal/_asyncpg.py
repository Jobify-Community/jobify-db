from collections.abc import Sequence
from typing import Final
from zoneinfo import ZoneInfo

import asyncpg
from jobify._internal.common.constants import JobStatus
from jobify._internal.storage.base import (
    ScheduledJob,
    Storage,
    validate_table_name,
)
from typing_extensions import override

from jobify_db._internal._exceptions import (
    StorageConfigurationError,
    StorageNotInitializedError,
)
from jobify_db._internal._queries import (
    CREATE_SCHEDULED_TABLE_QUERY,
    DELETE_SCHEDULE_MANY_QUERY,
    DELETE_SCHEDULE_QUERY,
    INSERT_SCHEDULE_QUERY,
    SELECT_SCHEDULES_QUERY,
)


class AsyncpgStorage(Storage):
    def __init__(
        self,
        dsn: str | None = None,
        *,
        pool: asyncpg.Pool | None = None,
        table_name: str = "jobify_schedules",
        min_size: int = 1,
        max_size: int = 10,
    ) -> None:
        if dsn is None and pool is None:
            msg = "Either 'dsn' or 'pool' must be provided."
            raise StorageConfigurationError(msg)

        validate_table_name(table_name)

        self._dsn: Final[str | None] = dsn
        self._pool: asyncpg.Pool | None = pool
        self._owns_pool: bool = pool is None
        self._table_name: Final[str] = table_name
        self._min_size: Final[int] = min_size
        self._max_size: Final[int] = max_size
        self._tz: Final[ZoneInfo] = ZoneInfo("UTC")

        self._create_query: Final[str] = CREATE_SCHEDULED_TABLE_QUERY.format(
            table_name=table_name,
        )
        self._select_query: Final[str] = SELECT_SCHEDULES_QUERY.format(
            table_name=table_name,
        )
        self._insert_query: Final[str] = INSERT_SCHEDULE_QUERY.format(
            table_name=table_name,
        )
        self._delete_query: Final[str] = DELETE_SCHEDULE_QUERY.format(
            table_name=table_name,
        )
        self._delete_many_query: Final[str] = DELETE_SCHEDULE_MANY_QUERY.format(
            table_name=table_name,
        )

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise StorageNotInitializedError
        return self._pool

    @override
    async def startup(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
            )

        await self.pool.execute(self._create_query)

    @override
    async def shutdown(self) -> None:
        if self._pool is not None and self._owns_pool:
            await self._pool.close()
            self._pool = None

    @override
    async def get_schedules(self) -> list[ScheduledJob]:
        rows = await self.pool.fetch(self._select_query)
        return [
            ScheduledJob(
                job_id=row["job_id"],
                name=row["name"],
                message=bytes(row["message"]),
                status=JobStatus(row["status"]),
                next_run_at=row["next_run_at"].astimezone(self._tz),
            )
            for row in rows
        ]

    @override
    async def add_schedule(self, *scheduled: ScheduledJob) -> None:
        async with self.pool.acquire() as conn, conn.transaction():
            for sch in scheduled:
                await conn.execute(
                    self._insert_query,
                    sch.job_id,
                    sch.name,
                    sch.message,
                    sch.status,
                    sch.next_run_at,
                )

    @override
    async def delete_schedule(self, job_id: str) -> None:
        await self.pool.execute(self._delete_query, job_id)

    @override
    async def delete_schedule_many(self, job_ids: Sequence[str]) -> None:
        if not job_ids:
            return

        await self.pool.execute(self._delete_many_query, list(job_ids))
