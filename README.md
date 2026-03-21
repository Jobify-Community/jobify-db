# Database storage backends for Jobify

[![Downloads](https://static.pepy.tech/personalized-badge/jobify-db?period=month&units=international_system&left_color=grey&right_color=green&left_text=downloads/month)](https://www.pepy.tech/projects/jobify-db)
[![Package version](https://img.shields.io/pypi/v/jobify-db?label=PyPI)](https://pypi.org/project/jobify-db)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/jobify-db.svg)](https://pypi.org/project/jobify-db)

*jobify-db* provides database storage backends for the [Jobify](https://github.com/theseriff/jobify) framework. It features:

* **PostgreSQL** support via `asyncpg` and `psycopg` drivers
* **MongoDB** support via `motor` driver
* Accepts either a connection string or an externally managed pool/client
* Automatic table/collection creation on startup

## Installation

Install with the driver you need:

```sh
pip install jobify-db[asyncpg]
pip install jobify-db[psycopg]
pip install jobify-db[motor]
```

Or with `uv`:

```sh
uv add "jobify-db[asyncpg]"
uv add "jobify-db[psycopg]"
uv add "jobify-db[motor]"
```

## How to use

### PostgreSQL with asyncpg

```python
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
        await app.wait_all()


if __name__ == "__main__":
    asyncio.run(main())
```

### PostgreSQL with psycopg

```python
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
        await app.wait_all()


if __name__ == "__main__":
    asyncio.run(main())
```

### MongoDB with motor

```python
import asyncio

from jobify import Jobify

from jobify_db.mongodb.motor import MotorStorage

app = Jobify(
    storage=MotorStorage(
        uri="mongodb://localhost:27017",
        database_name="my_app",
    ),
)


@app.task(cron="0 9 * * 1")
async def weekly_report() -> None:
    print("Generating weekly report every Monday at 9 AM")


async def main() -> None:
    async with app:
        await app.wait_all()


if __name__ == "__main__":
    asyncio.run(main())
```

### Using an external pool/client

You can pass an externally managed pool or client instead of a connection string. This is useful when you want to share the pool across multiple components.

```python
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
```

The same pattern works for `PsycopgStorage(pool=pool)` and `MotorStorage(client=client)`.
