"""Example: using PsycopgStorage with Jobify.

Install: pip install jobify-db[psycopg]
"""

import asyncio

from jobify import Jobify

from jobify_db.postgresql.psycopg import PsycopgStorage

app = Jobify(
    storage=PsycopgStorage(
        conninfo="postgresql://user:password@localhost:5432/mydb",
    ),
)


@app.task(cron="*/1 * * * *")
async def health_check() -> None:
    print("Health check passed")


async def main() -> None:
    async with app:
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
