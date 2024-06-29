import glob
import os
from pathlib import Path

import aiohttp
import asyncpg
import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest
import pytest_asyncio
from libs.utils.config import CatherineConfig

TESTING_EXTENSIONS = [
    "cogs.dictionary",
    "cogs.hrt",
    "cogs.pride_profiles",
    "cogs.pronouns",
]

CONFIG_PATH = Path(__file__).parents[1] / "config.yml"


def load_postgres_uri() -> str:
    config = CatherineConfig(CONFIG_PATH)
    ideal_conf = config.postgres.get("uri")
    if ideal_conf is None:
        return os.environ["POSTGRES_URI"]
    return ideal_conf


class TestBot(commands.Bot):
    pool: asyncpg.Pool
    session: aiohttp.ClientSession

    def __init__(self, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents)

    async def close(self) -> None:
        await self.session.close()
        await self.pool.close()

    async def setup_hook(self) -> None:
        self.pool = await asyncpg.create_pool(dsn=load_postgres_uri())  # type: ignore
        self.session = aiohttp.ClientSession()

        for extension in TESTING_EXTENSIONS:
            await self.load_extension(extension, package="..cogs")


@pytest_asyncio.fixture
async def bot():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = TestBot(intents=intents)
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
        except Exception:
            print("Error while deleting file : ", file_path)
