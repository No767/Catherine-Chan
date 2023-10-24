import logging
import signal
from pathlib import Path
from typing import Dict, Optional

import asyncpg
import discord
from aiohttp import ClientSession
from cogs import EXTENSIONS, VERSION
from discord.ext import commands, ipcx
from libs.cog_utils.prometheus_metrics import (
    Metrics,
    create_gauges,
    create_guild_gauges,
    fill_gauges,
)
from libs.ui.pronouns import ApprovePronounsExampleView
from libs.utils import CatherineCommandTree, load_blacklist
from prometheus_async.aio.web import start_http_server

# Some weird import logic to ensure that watchfiles is there
_fsw = True
try:
    from watchfiles import awatch
except ImportError:
    _fsw = False


class Catherine(commands.Bot):
    def __init__(
        self,
        config: Dict[str, Optional[str]],
        ipc_secret_key: str,
        ipc_host: str,
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
            command_prefix=commands.when_mentioned,
            help_command=None,
            intents=intents,
            owner_id=454357482102587393,
            tree_cls=CatherineCommandTree,
            *args,
            **kwargs,
        )
        self.dev_mode = dev_mode
        self.logger: logging.Logger = logging.getLogger("catherine")
        self.ipc = ipcx.Server(self, host=ipc_host, secret_key=ipc_secret_key)
        self.metrics: Metrics = create_gauges()
        self._ipc_host = ipc_host
        self._metrics_port = 6789
        self._blacklist_cache: Dict[int, bool] = {}
        self._config = config
        self._session = session
        self._pool = pool

    @property
    def blacklist_cache(self) -> Dict[int, bool]:
        """Global blacklist cache

        The main blacklist is stored on PostgreSQL, and is always a 1:1 mapping of the cache.
        R. Danny loads it from a JSON file, but I call that json as a db.

        Returns:
            Dict[int, bool]: Cached version of all globally blacklisted users.
        """
        return self._blacklist_cache

    @property
    def config(self) -> Dict[str, Optional[str]]:
        """Global configuration dictionary read from .env files

        This is used to access API keys, and many others from the bot.

        Returns:
            Dict[str, str]: A dictionary of configuration values
        """
        return self._config

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

    # Basically silence all prefixed errors
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        return

    def add_to_blacklist_cache(self, id: int) -> None:
        self._blacklist_cache[id] = True

    def update_blacklist_cache(self, id: int, status: bool) -> None:
        self._blacklist_cache.update({id: status})

    def remove_from_blacklist_cache(self, id: int) -> None:
        self._blacklist_cache.pop(id)

    def replace_blacklist_cache(self, new_cache: Dict[int, bool]) -> None:
        self._blacklist_cache = new_cache

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

        self._blacklist_cache = await load_blacklist(self.pool)
        self.add_view(ApprovePronounsExampleView("", 0, 10, self.pool))
        self.logger.info("Loaded blacklist cache")

        for cog in EXTENSIONS:
            self.logger.debug(f"Loaded extension: {cog}")
            await self.load_extension(cog)

        await self.ipc.start()
        await start_http_server(addr=self._ipc_host, port=6789)
        self.logger.info(
            "Prometheus Server started on %s:%s", self._ipc_host, self._metrics_port
        )

        fill_gauges(self)

        if self.dev_mode is True and _fsw is True:
            self.logger.info("Dev mode is enabled. Loading Jishaku and FSWatcher")
            await self.load_extension("jishaku")
            self.loop.create_task(self.fs_watcher())

    async def on_ready(self):
        if not hasattr(self, "uptime") and not hasattr(self, "guild_metrics_created"):
            self.uptime = discord.utils.utcnow()
            self.guild_metrics_created = create_guild_gauges(self)

        curr_user = None if self.user is None else self.user.name
        self.logger.info(f"{curr_user} is fully ready!")

    async def on_ipc_ready(self):
        self.logger.info(
            "Standard IPC Server started on %s:%s", self.ipc.host, self.ipc.port
        )
        self.logger.info(
            "Multicast IPC server started on %s:%s",
            self.ipc.host,
            self.ipc.multicast_port,
        )
