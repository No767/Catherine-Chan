import logging
import signal

import asyncpg
import discord
from aiohttp import ClientSession
from cogs import EXTENSIONS, VERSION
from discord.ext import commands
from libs.ui.pronouns import ApprovePronounsExampleView

# Some weird import logic to ensure that watchfiles is there
_fsw = True
try:
    from watchfiles import awatch
except ImportError:
    _fsw = False

from pathlib import Path


class Catherine(commands.Bot):
    def __init__(
        self,
        intents: discord.Intents,
        session: ClientSession,
        pool: asyncpg.Pool,
        dev_mode: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="for some eggs to hatch!"
            ),
            command_prefix="~",
            intents=intents,
            *args,
            **kwargs,
        )
        self.dev_mode = dev_mode
        self.logger: logging.Logger = logging.getLogger("discord")
        self._session = session
        self._pool = pool

    @property
    def session(self) -> ClientSession:
        """A global web session used throughout the lifetime of the bot

        Returns:
            ClientSession: AIOHTTP's ClientSession
        """
        return self._session

    @property
    def pool(self) -> asyncpg.Pool:
        """A global object managed throughout the lifetime of Kumiko

        Holds the asyncpg pool for connections

        Returns:
            asyncpg.Pool: asyncpg connection pool
        """
        return self._pool

    @property
    def version(self) -> str:
        """The version of Catherine

        Returns:
            str: The version of Catherine
        """
        return str(VERSION)

    async def fs_watcher(self) -> None:
        cogs_path = Path(__file__).parent.joinpath("cogs")
        async for changes in awatch(cogs_path):
            changes_list = list(changes)[0]
            if changes_list[0].modified == 2:
                reload_file = Path(changes_list[1])
                self.logger.info(f"Reloading extension: {reload_file.name[:-3]}")
                await self.reload_extension(f"cogs.{reload_file.name[:-3]}")

    async def setup_hook(self) -> None:
        def stop():
            self.loop.create_task(self.close())

        self.loop.add_signal_handler(signal.SIGTERM, stop)
        self.loop.add_signal_handler(signal.SIGINT, stop)

        self.add_view(ApprovePronounsExampleView("", 0, 10, self.pool))

        for cog in EXTENSIONS:
            self.logger.debug(f"Loaded extension: {cog}")
            await self.load_extension(cog)

        if self.dev_mode is True and _fsw is True:
            self.logger.info("Dev mode is enabled. Loading FSWatcher")
            self.loop.create_task(self.fs_watcher())

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = discord.utils.utcnow()
        curr_user = None if self.user is None else self.user.name
        self.logger.info(f"{curr_user} is fully ready!")
