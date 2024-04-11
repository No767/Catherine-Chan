import logging
from pathlib import Path

import asyncpg
import discord
from aiohttp import ClientSession
from cogs import EXTENSIONS, VERSION
from discord.ext import commands
from libs.cog_utils.prometheus_metrics import (
    Metrics,
    create_gauges,
    create_guild_gauges,
    fill_gauges,
)
from libs.ui.pronouns import ApprovePronounsExampleView
from libs.utils.config import CatherineConfig
from libs.utils.reloader import Reloader
from libs.utils.tree import CatherineCommandTree
from prometheus_async.aio.web import start_http_server


class Catherine(commands.Bot):
    def __init__(
        self,
        config: CatherineConfig,
        intents: discord.Intents,
        session: ClientSession,
        pool: asyncpg.Pool,
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
        self.logger: logging.Logger = logging.getLogger("catherine")
        self.metrics: Metrics = create_gauges()
        self.session = session
        self.pool = pool
        self.version = str(VERSION)
        self._dev_mode = config.bot.get("dev_mode", False)
        self._reloader = Reloader(self, Path(__file__).parent)
        self._prometheus = config.bot.get("prometheus", {})
        self._prometheus_enabled = self._prometheus.get("enabled", False)

    # Basically silence all prefixed errors
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        return

    async def setup_hook(self) -> None:
        self.add_view(ApprovePronounsExampleView("", 0, 10, self.pool))

        for cog in EXTENSIONS:
            self.logger.debug(f"Loaded extension: {cog}")
            await self.load_extension(cog)

        await self.load_extension("jishaku")

        if self._prometheus_enabled:
            prom_host = self._prometheus.get("host", "127.0.0.1")
            prom_port = self._prometheus.get("port", 6789)

            await start_http_server(addr=prom_host, port=prom_port)
            self.logger.info("Prometheus Server started on %s:%s", prom_host, prom_port)

            fill_gauges(self)

        if self._dev_mode:
            self._reloader.start()

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = discord.utils.utcnow()
        elif self._prometheus_enabled and not hasattr(self, "guild_metrics_created"):
            self.guild_metrics_created = create_guild_gauges(self)

        curr_user = None if self.user is None else self.user.name
        self.logger.info(f"{curr_user} is fully ready!")

    async def on_reloader_ready(self):
        self.logger.info("Dev mode is enabled. Loaded Reloader")
