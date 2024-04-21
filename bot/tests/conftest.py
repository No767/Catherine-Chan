import glob
import os

import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest
import pytest_asyncio

TESTING_EXTENSIONS = [
    "cogs.dictionary",
    "cogs.fun",
    "cogs.hrt",
    "cogs.pride_profiles",
    "cogs.pronouns",
    "cogs.tonetags",
]


class TestBot(commands.Bot):
    def __init__(self, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        for extension in TESTING_EXTENSIONS:
            await self.load_extension(extension)


@pytest_asyncio.fixture
async def bot():
    # Setup
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = TestBot(intents=intents)
    dpytest.configure(b)

    yield b

    # Teardown
    await dpytest.empty_queue()  # empty the global message queue as test teardown


def pytest_sessionfinish(session, exitstatus):
    """Code to execute after all tests."""

    # dat files are created when using attachements
    file_list = glob.glob("./dpytest_*.dat")
    for file_path in file_list:
        try:
            os.remove(file_path)
        except Exception:
            print("Error while deleting file : ", file_path)
