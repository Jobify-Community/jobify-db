import pytest
from jobify._internal.common.constants import JobStatus

from jobify_db.postgresql.asyncpg import AsyncpgStorage
from tests.factories import make_job


class TestAddAndGetSchedules:
    @pytest.mark.asyncio()
    async def test_add_single_schedule(self, asyncpg_storage: AsyncpgStorage) -> None:
        job = make_job()
        await asyncpg_storage.add_schedule(job)

        schedules = await asyncpg_storage.get_schedules()

        assert len(schedules) == 1
        assert schedules[0].job_id == "job-1"
        assert schedules[0].name == "test_job"
        assert schedules[0].message == b'{"key": "value"}'
        assert schedules[0].status == JobStatus.PENDING

    @pytest.mark.asyncio()
    async def test_add_multiple_schedules(self, asyncpg_storage: AsyncpgStorage) -> None:
        jobs = [make_job(job_id=f"job-{i}") for i in range(5)]
        await asyncpg_storage.add_schedule(*jobs)

        schedules = await asyncpg_storage.get_schedules()

        assert len(schedules) == 5

    @pytest.mark.asyncio()
    async def test_upsert_updates_existing(self, asyncpg_storage: AsyncpgStorage) -> None:
        await asyncpg_storage.add_schedule(make_job(status=JobStatus.PENDING))
        await asyncpg_storage.add_schedule(make_job(status=JobStatus.RUNNING))

        schedules = await asyncpg_storage.get_schedules()

        assert len(schedules) == 1
        assert schedules[0].status == JobStatus.RUNNING

    @pytest.mark.asyncio()
    async def test_get_schedules_empty(self, asyncpg_storage: AsyncpgStorage) -> None:
        schedules = await asyncpg_storage.get_schedules()
        assert schedules == []


class TestDeleteSchedule:
    @pytest.mark.asyncio()
    async def test_delete_existing(self, asyncpg_storage: AsyncpgStorage) -> None:
        await asyncpg_storage.add_schedule(make_job())
        await asyncpg_storage.delete_schedule("job-1")

        schedules = await asyncpg_storage.get_schedules()
        assert schedules == []

    @pytest.mark.asyncio()
    async def test_delete_nonexistent_is_noop(
        self, asyncpg_storage: AsyncpgStorage
    ) -> None:
        await asyncpg_storage.delete_schedule("nonexistent")

        schedules = await asyncpg_storage.get_schedules()
        assert schedules == []


class TestDeleteScheduleMany:
    @pytest.mark.asyncio()
    async def test_delete_many(self, asyncpg_storage: AsyncpgStorage) -> None:
        jobs = [make_job(job_id=f"job-{i}") for i in range(5)]
        await asyncpg_storage.add_schedule(*jobs)

        await asyncpg_storage.delete_schedule_many(["job-0", "job-1", "job-2"])

        schedules = await asyncpg_storage.get_schedules()
        remaining_ids = {s.job_id for s in schedules}
        assert remaining_ids == {"job-3", "job-4"}

    @pytest.mark.asyncio()
    async def test_delete_many_empty_list(self, asyncpg_storage: AsyncpgStorage) -> None:
        await asyncpg_storage.add_schedule(make_job())
        await asyncpg_storage.delete_schedule_many([])

        schedules = await asyncpg_storage.get_schedules()
        assert len(schedules) == 1


class TestExternalPool:
    @pytest.mark.asyncio()
    async def test_crud_with_external_pool(
        self, asyncpg_storage_from_pool: AsyncpgStorage
    ) -> None:
        job = make_job()
        await asyncpg_storage_from_pool.add_schedule(job)

        schedules = await asyncpg_storage_from_pool.get_schedules()
        assert len(schedules) == 1
        assert schedules[0].job_id == "job-1"

    @pytest.mark.asyncio()
    async def test_shutdown_does_not_close_external_pool(
        self, asyncpg_storage_from_pool: AsyncpgStorage
    ) -> None:
        await asyncpg_storage_from_pool.shutdown()

        assert not asyncpg_storage_from_pool.pool.is_closing()
