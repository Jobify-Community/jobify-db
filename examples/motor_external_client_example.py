"""Example: using MotorStorage with an externally managed client.

Useful when you already have a Motor client for other parts
of your application and want to reuse it for job scheduling.

Install: pip install jobify-db[motor]
"""

import asyncio
from typing import Any

from jobify import Jobify
from motor.motor_asyncio import AsyncIOMotorClient

from jobify_db.mongodb.motor import MotorStorage

URI = "mongodb://localhost:27017"


async def main() -> None:
    client: AsyncIOMotorClient[dict[str, Any]] = AsyncIOMotorClient(URI)

    app = Jobify(
        storage=MotorStorage(
            client=client,
            database_name="my_app",
        ),
    )

    @app.task(cron="*/30 * * * *")
    async def cache_warmup() -> None:
        print("Warming up cache every 30 minutes")

    async with app:
        await app.wait_all()


if __name__ == "__main__":
    asyncio.run(main())
