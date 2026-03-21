"""Example: using MotorStorage with Jobify (MongoDB).

Requires a MongoDB replica set for transaction support.

Install: pip install jobify-db[motor]
"""

import asyncio

from jobify import Jobify

from jobify_db.mongodb.motor import MotorStorage

app = Jobify(
    storage=MotorStorage(
        uri="mongodb://localhost:27017",
        database_name="my_app",
        collection_name="scheduled_jobs",
    ),
)


@app.task(cron="0 9 * * 1")
async def weekly_report() -> None:
    print("Generating weekly report every Monday at 9 AM")


async def main() -> None:
    async with app:
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
