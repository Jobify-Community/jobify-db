"""Example: using AiomysqlStorage with Jobify.

Install: pip install jobify-db[aiomysql]
"""

import asyncio

from jobify import Jobify

from jobify_db.mysql.aiomysql import AiomysqlStorage

app = Jobify(
    storage=AiomysqlStorage(
        host="localhost",
        port=3306,
        user="root",
        password="password",
        db="mydb",
    ),
)


@app.task(cron="*/5 * * * *")
async def my_task() -> None:
    print("Running periodic task every 5 minutes")


async def main() -> None:
    async with app:
        await app.wait_all()


if __name__ == "__main__":
    asyncio.run(main())
