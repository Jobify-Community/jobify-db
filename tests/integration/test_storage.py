import pytest
from jobify._internal.common.constants import JobStatus
from jobify._internal.storage.base import Storage

from jobify_db import StorageNotInitializedError
from jobify_db.mongodb.motor import MotorStorage
from jobify_db.mysql.aiomysql import AiomysqlStorage
from jobify_db.postgresql.asyncpg import AsyncpgStorage
from jobify_db.postgresql.psycopg import PsycopgStorage
from tests.factories import make_job


@pytest.fixture(
    params=[
        "asyncpg_storage",
        "psycopg_storage",
        "motor_storage",
        "aiomysql_storage",
    ],
)
def storage(request: pytest.FixtureRequest) -> Storage:
    return request.getfixturevalue(request.param)  # type: ignore[no-any-return]


@pytest.fixture(
    params=[
        "asyncpg_storage_from_pool",
        "psycopg_storage_from_pool",
        "motor_storage_from_client",
        "aiomysql_storage_from_pool",
    ],
)
def storage_from_external(request: pytest.FixtureRequest) -> Storage:
    return request.getfixturevalue(request.param)  # type: ignore[no-any-return]


class TestAddAndGetSchedules:
    @pytest.mark.asyncio()
    async def test_add_single_schedule(self, storage: Storage) -> None:
        job = make_job()
        await storage.add_schedule(job)

        schedules = await storage.get_schedules()

        assert len(schedules) == 1
        assert schedules[0].job_id == "job-1"
        assert schedules[0].name == "test_job"
        assert schedules[0].message == b'{"key": "value"}'
        assert schedules[0].status == JobStatus.PENDING

    @pytest.mark.asyncio()
    async def test_add_multiple_schedules(self, storage: Storage) -> None:
        jobs = [make_job(job_id=f"job-{i}") for i in range(5)]
        await storage.add_schedule(*jobs)

        schedules = await storage.get_schedules()

        assert len(schedules) == 5

    @pytest.mark.asyncio()
    async def test_upsert_updates_existing(self, storage: Storage) -> None:
        await storage.add_schedule(make_job(status=JobStatus.PENDING))
        await storage.add_schedule(make_job(status=JobStatus.RUNNING))

        schedules = await storage.get_schedules()

        assert len(schedules) == 1
        assert schedules[0].status == JobStatus.RUNNING

    @pytest.mark.asyncio()
    async def test_get_schedules_empty(self, storage: Storage) -> None:
        schedules = await storage.get_schedules()
        assert schedules == []


class TestDeleteSchedule:
    @pytest.mark.asyncio()
    async def test_delete_existing(self, storage: Storage) -> None:
        await storage.add_schedule(make_job())
        await storage.delete_schedule("job-1")

        schedules = await storage.get_schedules()
        assert schedules == []

    @pytest.mark.asyncio()
    async def test_delete_nonexistent_is_noop(self, storage: Storage) -> None:
        await storage.delete_schedule("nonexistent")

        schedules = await storage.get_schedules()
        assert schedules == []


class TestDeleteScheduleMany:
    @pytest.mark.asyncio()
    async def test_delete_many(self, storage: Storage) -> None:
        jobs = [make_job(job_id=f"job-{i}") for i in range(5)]
        await storage.add_schedule(*jobs)

        await storage.delete_schedule_many(["job-0", "job-1", "job-2"])

        schedules = await storage.get_schedules()
        remaining_ids = {s.job_id for s in schedules}
        assert remaining_ids == {"job-3", "job-4"}

    @pytest.mark.asyncio()
    async def test_delete_many_empty_list(self, storage: Storage) -> None:
        await storage.add_schedule(make_job())
        await storage.delete_schedule_many([])

        schedules = await storage.get_schedules()
        assert len(schedules) == 1


class TestExternalResource:
    @pytest.mark.asyncio()
    async def test_crud_with_external(self, storage_from_external: Storage) -> None:
        job = make_job()
        await storage_from_external.add_schedule(job)

        schedules = await storage_from_external.get_schedules()
        assert len(schedules) == 1
        assert schedules[0].job_id == "job-1"


class TestExternalShutdown:
    @pytest.mark.asyncio()
    async def test_asyncpg_shutdown_keeps_external_pool(
        self, asyncpg_storage_from_pool: AsyncpgStorage
    ) -> None:
        await asyncpg_storage_from_pool.shutdown()

        assert not asyncpg_storage_from_pool.pool.is_closing()

    @pytest.mark.asyncio()
    async def test_psycopg_shutdown_keeps_external_pool(
        self, psycopg_storage_from_pool: PsycopgStorage
    ) -> None:
        await psycopg_storage_from_pool.shutdown()

        assert not psycopg_storage_from_pool.pool.closed

    @pytest.mark.asyncio()
    async def test_motor_shutdown_keeps_external_client(
        self, motor_storage_from_client: MotorStorage
    ) -> None:
        await motor_storage_from_client.shutdown()

        with pytest.raises(StorageNotInitializedError):
            _ = motor_storage_from_client.collection

    @pytest.mark.asyncio()
    async def test_aiomysql_shutdown_keeps_external_pool(
        self, aiomysql_storage_from_pool: AiomysqlStorage
    ) -> None:
        await aiomysql_storage_from_pool.shutdown()

        assert aiomysql_storage_from_pool.pool is not None
