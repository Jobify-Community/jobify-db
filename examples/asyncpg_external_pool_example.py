"""Example: using AsyncpgStorage with an externally managed pool.

Useful when you want to share the pool across multiple components,
or configure it with custom settings.

Install: pip install jobify-db[asyncpg]
"""

import asyncio

import asyncpg
from jobify import Jobify

from jobify_db.postgresql.asyncpg import AsyncpgStorage

DSN = "postgresql://user:password@localhost:5432/mydb"


async def main() -> None:
    pool = await asyncpg.create_pool(dsn=DSN, min_size=2, max_size=20)

    app = Jobify(storage=AsyncpgStorage(pool=pool))

    @app.task(cron="0 3 * * *")
    async def nightly_cleanup() -> None:
        print("Running nightly cleanup")

    async with app:
        await app.wait_all()


if __name__ == "__main__":
    asyncio.run(main())
