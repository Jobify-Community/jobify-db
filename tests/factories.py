from datetime import datetime, timezone

from jobify._internal.common.constants import JobStatus
from jobify._internal.storage.base import ScheduledJob


def make_job(
    job_id: str = "job-1",
    name: str = "test_job",
    message: bytes = b'{"key": "value"}',
    status: JobStatus = JobStatus.PENDING,
    next_run_at: datetime = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
) -> ScheduledJob:
    return ScheduledJob(
        job_id=job_id,
        name=name,
        message=message,
        status=status,
        next_run_at=next_run_at,
    )
