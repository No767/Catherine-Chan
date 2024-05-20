import asyncio
import logging
from pathlib import Path

import asyncpg
from asyncpg_trek import Direction, execute, plan
from asyncpg_trek.asyncpg import AsyncpgBackend

from bot.libs.utils.config import CatherineConfig

MIGRATIONS_DIR = Path(__file__).parent / "migrations-trek"

config_path = Path(__file__).parent / "bot" / "config.yml"
config = CatherineConfig(config_path)

POSTGRES_URI = config["postgres"]["uri"]
TARGET_REVISION = config["postgres"]["revision"]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Migrations] %(levelname)s\t%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
)


async def migrate(
    conn: asyncpg.Connection,
    target_revision: str,
) -> None:
    backend = AsyncpgBackend(conn)
    async with backend.connect():
        planned = await plan(
            backend,
            MIGRATIONS_DIR,
            target_revision=target_revision,
            direction=Direction.up,
        )
        await execute(backend, planned)


async def main():
    conn = await asyncpg.connect(dsn=POSTGRES_URI)
    await migrate(conn, TARGET_REVISION)
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
