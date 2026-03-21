import pytest
from jobify._internal.common.constants import JobStatus

from jobify_db import StorageNotInitializedError
from jobify_db.mongodb.motor import MotorStorage
from tests.factories import make_job


class TestAddAndGetSchedules:
    @pytest.mark.asyncio()
    async def test_add_single_schedule(self, motor_storage: MotorStorage) -> None:
        job = make_job()
        await motor_storage.add_schedule(job)

        schedules = await motor_storage.get_schedules()

        assert len(schedules) == 1
        assert schedules[0].job_id == "job-1"
        assert schedules[0].name == "test_job"
        assert schedules[0].message == b'{"key": "value"}'
        assert schedules[0].status == JobStatus.PENDING

    @pytest.mark.asyncio()
    async def test_add_multiple_schedules(self, motor_storage: MotorStorage) -> None:
        jobs = [make_job(job_id=f"job-{i}") for i in range(5)]
        await motor_storage.add_schedule(*jobs)

        schedules = await motor_storage.get_schedules()

        assert len(schedules) == 5

    @pytest.mark.asyncio()
    async def test_upsert_updates_existing(self, motor_storage: MotorStorage) -> None:
        await motor_storage.add_schedule(make_job(status=JobStatus.PENDING))
        await motor_storage.add_schedule(make_job(status=JobStatus.RUNNING))

        schedules = await motor_storage.get_schedules()

        assert len(schedules) == 1
        assert schedules[0].status == JobStatus.RUNNING

    @pytest.mark.asyncio()
    async def test_get_schedules_empty(self, motor_storage: MotorStorage) -> None:
        schedules = await motor_storage.get_schedules()
        assert schedules == []


class TestDeleteSchedule:
    @pytest.mark.asyncio()
    async def test_delete_existing(self, motor_storage: MotorStorage) -> None:
        await motor_storage.add_schedule(make_job())
        await motor_storage.delete_schedule("job-1")

        schedules = await motor_storage.get_schedules()
        assert schedules == []

    @pytest.mark.asyncio()
    async def test_delete_nonexistent_is_noop(self, motor_storage: MotorStorage) -> None:
        await motor_storage.delete_schedule("nonexistent")

        schedules = await motor_storage.get_schedules()
        assert schedules == []


class TestDeleteScheduleMany:
    @pytest.mark.asyncio()
    async def test_delete_many(self, motor_storage: MotorStorage) -> None:
        jobs = [make_job(job_id=f"job-{i}") for i in range(5)]
        await motor_storage.add_schedule(*jobs)

        await motor_storage.delete_schedule_many(["job-0", "job-1", "job-2"])

        schedules = await motor_storage.get_schedules()
        remaining_ids = {s.job_id for s in schedules}
        assert remaining_ids == {"job-3", "job-4"}

    @pytest.mark.asyncio()
    async def test_delete_many_empty_list(self, motor_storage: MotorStorage) -> None:
        await motor_storage.add_schedule(make_job())
        await motor_storage.delete_schedule_many([])

        schedules = await motor_storage.get_schedules()
        assert len(schedules) == 1


class TestExternalClient:
    @pytest.mark.asyncio()
    async def test_crud_with_external_client(
        self, motor_storage_from_client: MotorStorage
    ) -> None:
        job = make_job()
        await motor_storage_from_client.add_schedule(job)

        schedules = await motor_storage_from_client.get_schedules()
        assert len(schedules) == 1
        assert schedules[0].job_id == "job-1"

    @pytest.mark.asyncio()
    async def test_shutdown_does_not_close_external_client(
        self, motor_storage_from_client: MotorStorage
    ) -> None:
        await motor_storage_from_client.shutdown()

        # Collection is None after shutdown, but client is still alive
        with pytest.raises(StorageNotInitializedError):
            _ = motor_storage_from_client.collection
