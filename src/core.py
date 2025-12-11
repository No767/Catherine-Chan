from __future__ import annotations

import asyncio
import importlib
import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union, overload

import aiohttp
import asyncpg
import discord
import msgspec
from aiohttp import ClientSession
from discord import app_commands
from discord.ext import commands

from cogs import EXTENSIONS, VERSION
from cogs.ext import prometheus
from cogs.pronouns import ApprovePronounsExampleView
from utils.embeds import FullErrorEmbed

try:
    from watchfiles import Change, awatch
except ImportError:
    _HAS_WATCHFILES = False

    raise RuntimeError("Watchfiles is not installed")
else:
    _HAS_WATCHFILES = True

if TYPE_CHECKING:
    from types import TracebackType


def find_config() -> Optional[Path]:
    path = Path("config.yml")

    if not path.exists():
        alt_location = path.parent.joinpath("src", "config.yml")

        if not alt_location.exists():
            return None

        return alt_location.resolve()

    return path.resolve()


### Application configuration


class PrometheusConfig(msgspec.Struct, frozen=True):
    enabled: bool
    host: str
    port: int


class CatherineConfig(msgspec.Struct):
    token: str
    dev_mode: bool
    approval_channel_id: int
    prometheus: PrometheusConfig
    postgres_uri: str

    @classmethod
    def load_from_file(cls, path: Optional[Path]) -> CatherineConfig:
        if not path:
            raise FileNotFoundError("Configuration file not found")

        with path.open() as f:
            return msgspec.yaml.decode(f.read(), type=CatherineConfig)


### Application development utilities


class Reloader:
    def __init__(self, bot: Catherine, root_path: Path):
        self.bot = bot
        self.loop = asyncio.get_running_loop()
        self.root_path = root_path
        self.logger = self.bot.logger
        self._cogs_path = self.root_path / "cogs"
        self._utils_path = self.root_path / "utils"

    async def reload_or_load_extension(self, module: str) -> None:
        try:
            await self.bot.reload_extension(module)
            self.logger.info("Reloaded extension: %s", module)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(module)
            self.logger.info("Loaded extension: %s", module)

    def reload_utils_modules(self, module: str) -> None:
        try:
            actual_module = sys.modules[module]
            importlib.reload(actual_module)
        except KeyError:
            self.logger.warning("Failed to reload module %s. Does it exist?", module)

    def find_modules_from_path(self, path: str) -> Optional[str]:
        root, ext = os.path.splitext(path)  # noqa: PTH122
        if ext != ".py":
            return None
        return ".".join(root.split("/")[1:])

    def find_true_module(self, module: str) -> str:
        parts = module.split(".")
        if "utils" in parts:
            utils_index = parts.index("utils")
            return ".".join(parts[utils_index:])
        cog_index = parts.index("cogs")
        return ".".join(parts[cog_index:])

    async def reload_cogs_and_utils(self, ctype: Change, true_module: str) -> None:
        if true_module.startswith("cogs"):
            if ctype in (Change.modified, Change.added):
                await self.reload_or_load_extension(true_module)
            elif ctype == Change.deleted:
                await self.bot.unload_extension(true_module)
        elif true_module.startswith("utils"):
            self.logger.info("Reloaded utils module: %s", true_module)
            self.reload_utils_modules(true_module)

    async def _watch_cogs(self):
        async for changes in awatch(self._cogs_path, self._utils_path, recursive=True):
            for ctype, cpath in changes:
                module = self.find_modules_from_path(cpath)
                if module is None:
                    continue

                true_module = self.find_true_module(module)
                await self.reload_cogs_and_utils(ctype, true_module)

    def start(self) -> None:
        if _HAS_WATCHFILES:
            self.loop.create_task(self._watch_cogs())
            self.bot.dispatch("reloader_ready")


### Application core utilities


class Blacklist[T]:
    """Internal blacklist database used by R. Danny"""

    def __init__(
        self,
        name: Path,
        *,
        load_later: bool = False,
    ):
        self.name = name
        self.encoder = msgspec.json.Encoder()
        self.loop = asyncio.get_running_loop()
        self.lock = asyncio.Lock()
        self._db: dict[str, Union[T, Any]] = {}
        if load_later:
            self.loop.create_task(self.load())
        else:
            self.load_from_file()

    def load_from_file(self):
        try:
            with self.name.open(mode="r", encoding="utf-8") as f:
                self._db = msgspec.json.decode(f.read())
        except FileNotFoundError:
            self._db = {}

    async def load(self):
        async with self.lock:
            await self.loop.run_in_executor(None, self.load_from_file)

    def _dump(self):
        temp = Path(f"{uuid.uuid4()}-{self.name}.tmp")
        with temp.open("w", encoding="utf-8") as tmp:
            encoded = msgspec.json.format(
                self.encoder.encode(self._db.copy()), indent=2
            )
            tmp.write(encoded.decode())

        # atomically move the file
        temp.replace(self.name)

    async def save(self) -> None:
        async with self.lock:
            await self.loop.run_in_executor(None, self._dump)

    @overload
    def get(self, key: Any) -> Optional[Union[T, Any]]: ...

    @overload
    def get(self, key: Any, default: Any) -> Union[T, Any]: ...

    def get(self, key: Any, default: Any = None) -> Optional[Union[T, Any]]:
        """Retrieves a config entry."""
        return self._db.get(str(key), default)

    async def put(self, key: Any, value: Union[T, Any]) -> None:
        """Edits a config entry."""
        self._db[str(key)] = value
        await self.save()

    async def remove(self, key: Any) -> None:
        """Removes a config entry."""
        del self._db[str(key)]
        await self.save()

    def __contains__(self, item: Any) -> bool:
        return str(item) in self._db

    def __getitem__(self, item: Any) -> Union[T, Any]:
        return self._db[str(item)]

    def __len__(self) -> int:
        return len(self._db)

    def all(self) -> dict[str, Union[T, Any]]:
        return self._db


class CatherineLogger:
    MAX_BYTES = 32 * 1024 * 1024  # 32 MiB

    def __init__(self) -> None:
        self._disable_watchfiles_logger()

        self.root = logging.getLogger("catherine")

    def _get_formatter(self) -> logging.Formatter:
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        return logging.Formatter(
            "[{asctime}] [{levelname}]\t\t{message}", dt_fmt, style="{"
        )

    def _disable_watchfiles_logger(self) -> None:
        watchfiles = logging.getLogger("watchfiles")

        watchfiles.propagate = False
        watchfiles.addHandler(logging.NullHandler())

    def _is_docker(self) -> bool:
        path = Path("/proc/self/cgroup")
        dockerenv_path = Path("/.dockerenv")
        return dockerenv_path.exists() or (
            path.is_file() and any("docker" in line for line in path.open())
        )

    def __enter__(self) -> None:
        discord_logger = logging.getLogger("discord")

        handler = logging.StreamHandler()
        handler.setFormatter(self._get_formatter())

        if not self._is_docker():
            file_handler = RotatingFileHandler(
                filename="catherine.log",
                encoding="utf-8",
                mode="w",
                maxBytes=self.MAX_BYTES,
                backupCount=5,
            )
            file_handler.setFormatter(self._get_formatter())

            discord_logger.addHandler(file_handler)
            self.root.addHandler(file_handler)

        discord_logger.setLevel(logging.INFO)
        discord_logger.addHandler(handler)

        self.root.setLevel(logging.INFO)
        self.root.addHandler(handler)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.root.info("Shutting down...")
        handlers = self.root.handlers[:]

        for handler in handlers:
            handler.close()
            self.root.removeHandler(handler)


class KeyboardInterruptHandler:
    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self._task: Optional[asyncio.Task] = None

    def __call__(self) -> None:
        if self._task:
            raise KeyboardInterrupt
        self._task = self.bot.loop.create_task(self.bot.close())


### Discord-specific overrides


# This is needed for the blacklisting system
# Yes a custom CommandTree lol.
# At the very least better than Jade's on_interaction checks
# https://github.com/LilbabxJJ-1/PrideBot/blob/master/main.py#L19-L36
class CatherineCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        bot: Catherine = interaction.client  # type: ignore # Pretty much returns the subclass anyways. I checked - Noelle

        if interaction.user.id in (bot.owner_id, bot.application_id):
            return True

        if interaction.user.id in bot.blacklist:
            bot.metrics.blacklist.commands.inc(1)
            msg = (
                f"My fellow user, {interaction.user.mention}, you just got the L. "
                "You are blacklisted from using this bot. Take an \U0001f1f1, \U0001f1f1oser. "
                "[Here is your appeal form](https://media.tenor.com/K9R9beOgPR4AAAAC/fortnite-thanos.gif)"
            )
            await interaction.response.send_message(msg, ephemeral=True)
            return False

        if interaction.guild and interaction.guild.id in bot.blacklist:
            bot.metrics.blacklist.commands.inc(1)
            await interaction.response.send_message(
                "This is so sad lolllllll! Your whole entire server got blacklisted!",
                ephemeral=True,
            )
            return False

        bot.metrics.commands.invocation.inc()
        if interaction.command:
            name = interaction.command.qualified_name
            bot.metrics.commands.count.labels(name).inc()

        return True

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        bot: Catherine = interaction.client  # type: ignore

        if bot._dev_mode:
            bot.logger.exception("Ignoring exception:", exc_info=error)
            return

        if isinstance(error, app_commands.NoPrivateMessage):
            await interaction.user.send(
                "This command cannot be used in private messages"
            )
        elif isinstance(error, app_commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                bot.logger.exception(
                    "In %s: ",
                    interaction.command.qualified_name,  # type: ignore
                    exc_info=original,
                )

                # Basically just ignore all content type errors for responses
                # Since we already have them printed to stderr, it makes no sense to send a response back to the user when a response is already sent.
                # In this case, it actually does more harm by giving the attackers more information than less.
                if (
                    isinstance(original, aiohttp.ContentTypeError)
                    and original.status == 0
                ):
                    return

                await interaction.response.send_message(
                    embed=FullErrorEmbed(error), ephemeral=True
                )
        else:
            await interaction.response.send_message(embed=FullErrorEmbed(error))


class Catherine(commands.Bot):
    FILE_ROOT = Path(__file__).parent

    def __init__(
        self, config: CatherineConfig, session: ClientSession, pool: asyncpg.Pool
    ) -> None:
        intents = discord.Intents.default()
        super().__init__(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="for some eggs to hatch!"
            ),
            allowed_mentions=discord.AllowedMentions(
                everyone=False, replied_user=False
            ),
            command_prefix=commands.when_mentioned,
            description="",
            help_command=None,
            intents=intents,
            owner_id=454357482102587393,
            tree_cls=CatherineCommandTree,
        )
        self.blacklist: Blacklist[bool] = Blacklist(self.FILE_ROOT / "blacklist.json")
        self.logger: logging.Logger = logging.getLogger("catherine")
        self.metrics = prometheus.MetricCollector(self)
        self.session = session
        self.pool = pool
        self.version = str(VERSION)

        self._config = config
        self._reloader = Reloader(self, self.FILE_ROOT)

        self._dev_mode = config.dev_mode
        self._prometheus = config.prometheus

    @property
    def approval_channel_id(self) -> int:
        return self._config.approval_channel_id

    async def add_to_blacklist(self, object_id: int) -> None:
        await self.blacklist.put(object_id, True)

    async def remove_from_blacklist(self, object_id: int) -> None:
        try:
            await self.blacklist.remove(object_id)
        except KeyError:
            pass

    # Basically silence all prefixed errors
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        return

    async def setup_hook(self) -> None:
        self.add_view(ApprovePronounsExampleView(self, "", 0, 10))

        for cog in EXTENSIONS:
            self.logger.debug("Loaded extension: %s", cog)
            await self.load_extension(cog)

        await self.load_extension("jishaku")

        if self._prometheus.enabled:
            await self.load_extension("cogs.ext.prometheus")
            prom_host = self._prometheus.host
            prom_port = self._prometheus.port

            await self.metrics.start(host=prom_host, port=prom_port)
            self.logger.info("Prometheus Server started on %s:%s", prom_host, prom_port)

            self.metrics.fill()

        if self._dev_mode:
            self._reloader.start()

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = discord.utils.utcnow()

        if self._prometheus.enabled and not hasattr(self, "guild_metrics_created"):
            self.guild_metrics_created = self.metrics.guilds.fill()

        user = None if self.user is None else self.user.name
        self.logger.info("%s is fully ready!", user)

    async def on_reloader_ready(self):
        self.logger.info("Dev mode is enabled. Loaded Reloader")
