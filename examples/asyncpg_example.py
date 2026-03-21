"""Example: using AsyncpgStorage with Jobify.

Install: pip install jobify-db[asyncpg]
"""

import asyncio

from jobify import Jobify

from jobify_db.postgresql.asyncpg import AsyncpgStorage

app = Jobify(
    storage=AsyncpgStorage(dsn="postgresql://user:password@localhost:5432/mydb"),
)


@app.task(cron="*/5 * * * *")
async def my_task() -> None:
    print("Running periodic task every 5 minutes")


async def main() -> None:
    async with app:
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
