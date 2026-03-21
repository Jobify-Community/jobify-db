from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

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


def make_aiomysql_mock_pool() -> MagicMock:
    mock_cursor = AsyncMock()

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__aexit__ = AsyncMock(return_value=False)
    mock_conn.commit = AsyncMock()

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    mock_pool.close = MagicMock()
    mock_pool.wait_closed = AsyncMock()
    return mock_pool


def make_psycopg_mock_pool() -> MagicMock:
    mock_conn = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_conn

    mock_pool = MagicMock()
    mock_pool.closed = False
    mock_pool.connection.return_value = mock_cm
    mock_pool.open = AsyncMock()
    mock_pool.close = AsyncMock()
    return mock_pool


def make_motor_mock_client() -> tuple[MagicMock, MagicMock, AsyncMock]:
    mock_collection = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    return mock_client, mock_db, mock_collection
