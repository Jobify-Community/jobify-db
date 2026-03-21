"""Example: using PsycopgStorage with an externally managed pool.

Install: pip install jobify-db[psycopg]
"""

import asyncio

from jobify import Jobify
from psycopg_pool import AsyncConnectionPool

from jobify_db.postgresql.psycopg import PsycopgStorage

CONNINFO = "postgresql://user:password@localhost:5432/mydb"


async def main() -> None:
    pool = AsyncConnectionPool(
        conninfo=CONNINFO,
        min_size=2,
        max_size=20,
        open=False,
    )
    await pool.open()

    app = Jobify(storage=PsycopgStorage(pool=pool))

    @app.task(cron="0 */6 * * *")
    async def sync_data() -> None:
        print("Syncing data every 6 hours")

    async with app:
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
