from collections.abc import Sequence
from typing import Final
from zoneinfo import ZoneInfo

import aiomysql
from jobify._internal.common.constants import JobStatus
from jobify._internal.storage.base import (
    ScheduledJob,
    Storage,
    validate_table_name,
)
from typing_extensions import override

from jobify_db._internal.common.consts import DEFAULT_TABLE_NAME
from jobify_db._internal.common.errors import (
    StorageConfigurationError,
    StorageNotInitializedError,
)
from jobify_db._internal.mysql.aiomysql.queries import (
    DELETE_SCHEDULE_QUERY,
    INSERT_SCHEDULE_QUERY,
)
from jobify_db._internal.mysql.queries import (
    CREATE_SCHEDULED_TABLE_QUERY,
    SELECT_SCHEDULES_QUERY,
)


class AiomysqlStorage(Storage):
    def __init__(  # noqa: PLR0913
        self,
        host: str | None = None,
        port: int = 3306,
        user: str | None = None,
        password: str | None = None,
        db: str | None = None,
        *,
        pool: aiomysql.Pool | None = None,
        table_name: str = DEFAULT_TABLE_NAME,
        min_size: int = 1,
        max_size: int = 10,
    ) -> None:
        if pool is None and host is None:
            msg = "Either 'host' or 'pool' must be provided."
            raise StorageConfigurationError(msg)

        validate_table_name(table_name)

        self._host: Final[str | None] = host
        self._port: Final[int] = port
        self._user: Final[str | None] = user
        self._password: Final[str | None] = password
        self._db: Final[str | None] = db
        self._pool: aiomysql.Pool | None = pool
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

    @property
    def pool(self) -> aiomysql.Pool:
        if self._pool is None:
            raise StorageNotInitializedError
        return self._pool

    @override
    async def startup(self) -> None:
        if self._pool is None:
            self._pool = await aiomysql.create_pool(
                host=self._host or "localhost",
                port=self._port,
                user=self._user or "",
                password=self._password or "",
                db=self._db or "",
                minsize=self._min_size,
                maxsize=self._max_size,
            )

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SET sql_notes = 0;")
                await cur.execute(self._create_query)
                await cur.execute("SET sql_notes = 1;")
            await conn.commit()

    @override
    async def shutdown(self) -> None:
        if self._pool is not None and self._owns_pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None

    @override
    async def get_schedules(self) -> list[ScheduledJob]:
        async with self.pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(self._select_query)
            rows = await cur.fetchall()

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
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
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
            await conn.commit()

    @override
    async def delete_schedule(self, job_id: str) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(self._delete_query, (job_id,))
            await conn.commit()

    @override
    async def delete_schedule_many(self, job_ids: Sequence[str]) -> None:
        if not job_ids:
            return

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(
                    self._delete_query, [(job_id,) for job_id in job_ids]
                )
            await conn.commit()
