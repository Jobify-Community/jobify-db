"""Example: using AiomysqlStorage with an externally managed pool.

Useful when you want to share the pool across multiple components,
or configure it with custom settings.

Install: pip install jobify-db[aiomysql]
"""

import asyncio

import aiomysql
from jobify import Jobify

from jobify_db.mysql.aiomysql import AiomysqlStorage


async def main() -> None:
    pool = await aiomysql.create_pool(
        host="localhost",
        port=3306,
        user="root",
        password="password",
        db="mydb",
        minsize=2,
        maxsize=20,
    )

    app = Jobify(storage=AiomysqlStorage(pool=pool))

    @app.task(cron="0 3 * * *")
    async def nightly_cleanup() -> None:
        print("Running nightly cleanup")

    async with app:
        await app.wait_all()


if __name__ == "__main__":
    asyncio.run(main())
