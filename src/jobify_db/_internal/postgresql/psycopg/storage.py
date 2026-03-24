from collections.abc import Sequence
from typing import Final
from zoneinfo import ZoneInfo

from jobify._internal.common.constants import JobStatus
from jobify._internal.storage.base import (
    ScheduledJob,
    Storage,
    validate_table_name,
)
from psycopg_pool import AsyncConnectionPool
from typing_extensions import override

from jobify_db._internal.common.consts import DEFAULT_TABLE_NAME
from jobify_db._internal.common.errors import (
    StorageConfigurationError,
    StorageNotInitializedError,
)
from jobify_db._internal.postgresql.psycopg.queries import (
    DELETE_SCHEDULE_MANY_QUERY,
    DELETE_SCHEDULE_QUERY,
    INSERT_SCHEDULE_QUERY,
)
from jobify_db._internal.postgresql.queries import (
    CREATE_SCHEDULED_TABLE_QUERY,
    SELECT_SCHEDULES_QUERY,
)


class PsycopgStorage(Storage):
    def __init__(
        self,
        conninfo: str | None = None,
        *,
        pool: AsyncConnectionPool | None = None,
        table_name: str = DEFAULT_TABLE_NAME,
        min_size: int = 1,
        max_size: int = 10,
    ) -> None:
        if conninfo is None and pool is None:
            msg = "Either 'conninfo' or 'pool' must be provided."
            raise StorageConfigurationError(msg)

        validate_table_name(table_name)

        self._conninfo: Final[str | None] = conninfo
        self._pool: AsyncConnectionPool | None = pool
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
    def pool(self) -> AsyncConnectionPool:
        if self._pool is None:
            raise StorageNotInitializedError
        return self._pool

    @override
    async def startup(self) -> None:
        if self._pool is None:
            self._pool = AsyncConnectionPool(
                conninfo=self._conninfo or "",
                min_size=self._min_size,
                max_size=self._max_size,
                open=False,
            )

        if self._pool.closed:
            await self._pool.open()

        async with self.pool.connection() as conn:
            await conn.execute(self._create_query)

    @override
    async def shutdown(self) -> None:
        if self._pool is not None and self._owns_pool:
            await self._pool.close()
            self._pool = None

    @override
    async def get_schedules(self) -> list[ScheduledJob]:
        async with self.pool.connection() as conn:
            cursor = await conn.execute(self._select_query)
            rows = await cursor.fetchall()

        return [
            ScheduledJob(
                job_id=row[0],
                name=row[1],
                message=bytes(row[2]),
                status=JobStatus(row[3]),
                next_run_at=row[4].astimezone(self._tz),
            )
            for row in rows
        ]

    @override
    async def add_schedule(self, *scheduled: ScheduledJob) -> None:
        async with self.pool.connection() as conn, conn.transaction():
            cur = conn.cursor()
            await cur.executemany(
                self._insert_query,
                [
                    (
                        sch.job_id,
                        sch.name,
                        sch.message,
                        sch.status,
                        sch.next_run_at,
                    )
                    for sch in scheduled
                ],
            )

    @override
    async def delete_schedule(self, job_id: str) -> None:
        async with self.pool.connection() as conn, conn.transaction():
            await conn.execute(self._delete_query, (job_id,))

    @override
    async def delete_schedule_many(self, job_ids: Sequence[str]) -> None:
        if not job_ids:
            return

        async with self.pool.connection() as conn, conn.transaction():
            await conn.execute(self._delete_many_query, (list(job_ids),))
