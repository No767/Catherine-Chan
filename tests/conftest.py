import glob
import os
from pathlib import Path

from typing import AsyncGenerator, Generator, Optional

import aiohttp
import pytest
import asyncpg
import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest
import pytest_asyncio

from testcontainers.core.image import DockerImage
from testcontainers.postgres import PostgresContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from core import CatherineConfig

TESTING_EXTENSIONS = [
    "cogs.dictionary",
    "cogs.hrt",
    "cogs.pride_profiles",
    "cogs.pronouns",
]

ROOT = Path(__file__).parents[1]
DOCKER_ROOT = ROOT / "docker" / "pg"

CONFIG_PATH = ROOT / "config.yml"



def load_postgres_uri(uri: Optional[str] = None) -> str:
    try:
        config = CatherineConfig.load_from_file(CONFIG_PATH)

        if uri and isinstance(uri, str):
            config.postgres_uri = uri

        return config.postgres_uri
    except KeyError:
        return os.environ["POSTGRES_URI"]


class TestBot(commands.Bot):
    pool: asyncpg.Pool
    session: aiohttp.ClientSession

    def __init__(self, intents: discord.Intents, *, postgres: PostgresContainer):
        super().__init__(command_prefix="!", intents=intents)
        self.postgres = postgres

    async def close(self) -> None:
        await self.session.close()
        await self.pool.close()

    async def setup_hook(self) -> None:
        self.pool = await asyncpg.create_pool(dsn=load_postgres_uri(self.postgres.get_connection_url(driver=None)))
        self.session = aiohttp.ClientSession()

        for extension in TESTING_EXTENSIONS:
            await self.load_extension(extension, package="..cogs")

@pytest.fixture(scope="session")
def db_setup() -> Generator[PostgresContainer, None, None]:
    with DockerImage(path=ROOT, dockerfile_path=DOCKER_ROOT / "Dockerfile") as image:
        with PostgresContainer(str(image)) as postgres:
            postgres.waiting_for(LogMessageWaitStrategy("ready"))

            yield postgres

@pytest_asyncio.fixture(scope="function")
async def bot(db_setup: PostgresContainer) -> AsyncGenerator[TestBot, None]:
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = TestBot(intents=intents, postgres=db_setup)
    await b._async_setup_hook()
    await b.setup_hook()
    dpytest.configure(b)

    yield b

    await b.close()
    await dpytest.empty_queue()


def pytest_sessionfinish(session, exitstatus):
    """Code to execute after all tests."""

    file_list = glob.glob("./dpytest_*.dat")
    for file_path in file_list:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error ({file_path}): {e}")
