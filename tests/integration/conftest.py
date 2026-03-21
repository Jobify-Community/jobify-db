import re
from collections.abc import AsyncIterator, Generator
from typing import Any

import asyncpg
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from psycopg_pool import AsyncConnectionPool
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.mongodb import MongoDbContainer
from testcontainers.postgres import PostgresContainer

from jobify_db import StorageNotInitializedError
from jobify_db.mongodb.motor import MotorStorage
from jobify_db.postgresql.asyncpg import AsyncpgStorage
from jobify_db.postgresql.psycopg import PsycopgStorage


class _MongoContainer(MongoDbContainer):
    def _connect(self) -> None:
        wait_for_logs(
            self,
            LogMessageWaitStrategy(
                re.compile(r"waiting for connections", re.IGNORECASE),
            ),
        )


@pytest.fixture(scope="module")
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer("postgres:17-alpine") as container:
        yield container


@pytest.fixture(scope="module")
def postgres_dsn(postgres_container: PostgresContainer) -> str:
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    user = postgres_container.username
    password = postgres_container.password
    dbname = postgres_container.dbname
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


# --- asyncpg fixtures ---


@pytest_asyncio.fixture
async def asyncpg_storage(postgres_dsn: str) -> AsyncIterator[AsyncpgStorage]:
    s = AsyncpgStorage(dsn=postgres_dsn, table_name="jobify_asyncpg")
    await s.startup()
    try:
        yield s
    finally:
        await s.pool.execute("DELETE FROM jobify_asyncpg;")
        await s.shutdown()


@pytest_asyncio.fixture
async def asyncpg_storage_from_pool(postgres_dsn: str) -> AsyncIterator[AsyncpgStorage]:
    pool = await asyncpg.create_pool(dsn=postgres_dsn, min_size=1, max_size=5)
    assert pool is not None
    s = AsyncpgStorage(pool=pool, table_name="jobify_asyncpg_ext")
    await s.startup()
    try:
        yield s
    finally:
        await pool.execute("DELETE FROM jobify_asyncpg_ext;")
        await s.shutdown()
        await pool.close()


# --- psycopg fixtures ---


@pytest_asyncio.fixture
async def psycopg_storage(postgres_dsn: str) -> AsyncIterator[PsycopgStorage]:
    s = PsycopgStorage(conninfo=postgres_dsn, table_name="jobify_psycopg")
    await s.startup()
    try:
        yield s
    finally:
        async with s.pool.connection() as conn:
            await conn.execute("DELETE FROM jobify_psycopg;")
        await s.shutdown()


@pytest_asyncio.fixture
async def psycopg_storage_from_pool(postgres_dsn: str) -> AsyncIterator[PsycopgStorage]:
    pool = AsyncConnectionPool(conninfo=postgres_dsn, min_size=1, max_size=5, open=False)
    await pool.open()
    s = PsycopgStorage(pool=pool, table_name="jobify_psycopg_ext")
    await s.startup()
    try:
        yield s
    finally:
        async with pool.connection() as conn:
            await conn.execute("DELETE FROM jobify_psycopg_ext;")
        await s.shutdown()
        await pool.close()


# --- mongodb fixtures ---


@pytest.fixture(scope="module")
def mongo_container() -> Generator[MongoDbContainer, Any, None]:
    with _MongoContainer("mongo:7") as container:
        yield container


@pytest.fixture(scope="module")
def mongo_uri(mongo_container: MongoDbContainer) -> str:
    return str(mongo_container.get_connection_url())


@pytest_asyncio.fixture
async def motor_storage(mongo_uri: str) -> AsyncIterator[MotorStorage]:
    s = MotorStorage(uri=mongo_uri, database_name="jobify_test")
    await s.startup()
    try:
        yield s
    finally:
        await s.collection.delete_many({})
        await s.shutdown()


@pytest_asyncio.fixture
async def motor_storage_from_client(
    mongo_uri: str,
) -> AsyncIterator[MotorStorage]:
    client: AsyncIOMotorClient[dict[str, Any]] = AsyncIOMotorClient(mongo_uri)
    s = MotorStorage(client=client, database_name="jobify_test_ext")
    await s.startup()
    try:
        yield s
    finally:
        try:
            await s.collection.delete_many({})
        except StorageNotInitializedError:
            pass
        else:
            await s.shutdown()
        client.close()
