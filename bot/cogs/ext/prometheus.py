from __future__ import annotations

import platform
from typing import TYPE_CHECKING, TypedDict

import discord
import msgspec
from discord import app_commands
from discord.ext import commands, tasks
from prometheus_client import Counter, Gauge, Info

if TYPE_CHECKING:
    from bot.catherinecore import Catherine


METRIC_PREFIX = "discord_"


def create_gauges(bot: Catherine) -> "Metrics":
    return Metrics(
        bot=bot,
        connection_gauge=Gauge(
            f"{METRIC_PREFIX}connected",
            "Determines if the bot is connected to Discord",
            ["shard"],
        ),
        latency_gauge=Gauge(
            f"{METRIC_PREFIX}latency",
            "latency to Discord",
            ["shard"],
        ),
        on_app_command_counter=Counter(
            f"{METRIC_PREFIX}on_app_command",
            "Amount of slash commands called by users",
        ),
        guild_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_guilds",
            "Amount of guilds this bot is in",
        ),
        text_channel_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_text_channels",
            "Amount of text channels this bot is has access to",
        ),
        voice_channel_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_voice_channels",
            "Amount of voice channels this bot is has access to",
        ),
        user_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_users", "Amount of users this bot can see"
        ),
        user_unique_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_unique_users",
            "Amount of unique users this bot can see",
        ),
        commands_gauge=Gauge(
            f"{METRIC_PREFIX}stat_app_total_commands", "Amount of commands"
        ),
        pronouns_tester_counter=Counter(
            f"{METRIC_PREFIX}pronouns_tester",
            "Amount of successful pronouns tested",
        ),
        version_info=Info(
            "version_info", "Catherine-Chan's current version and other version info"
        ),
        attempted_commands=Counter(
            f"{METRIC_PREFIX}attempted_commands",
            "Amount of attempted commands ran by blacklisted users",
        ),
        blacklisted_users=Gauge(
            f"{METRIC_PREFIX}blacklisted_users", "Number of blacklisted users"
        ),
    )


class GuildMetrics(TypedDict):
    text: int
    voice: int
    guilds: int
    total_commands: int


class MemberCounts(msgspec.Struct):
    total: int = 0
    unique: int = 0


class Metrics(msgspec.Struct, frozen=True):
    bot: Catherine
    connection_gauge: Gauge
    latency_gauge: Gauge
    on_app_command_counter: Counter
    guild_gauge: Gauge
    text_channel_gauge: Gauge
    voice_channel_gauge: Gauge
    user_gauge: Gauge
    user_unique_gauge: Gauge
    commands_gauge: Gauge
    version_info: Info
    attempted_commands: Counter
    blacklisted_users: Gauge
    pronouns_tester_counter: Counter

    def get_stats(self) -> GuildMetrics:
        # The same way R. Danny does it
        total_commands = 0
        text = 0
        voice = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable:
                continue
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1

        for cmd in self.bot.tree.walk_commands():
            if isinstance(cmd, app_commands.commands.Command):
                total_commands += 1

        return GuildMetrics(
            text=text,
            voice=voice,
            guilds=guilds,
            total_commands=total_commands,
        )

    def create_guild_gauges(self) -> None:
        stats = self.get_stats()

        self.guild_gauge.set(stats["guilds"])
        self.text_channel_gauge.set(stats["text"])
        self.voice_channel_gauge.set(stats["voice"])

    def fill_gauges(self):
        stats = self.get_stats()

        self.blacklisted_users.set(0)
        self.attempted_commands.inc(0)
        self.version_info.info(
            {
                "build_version": self.bot.version,
                "dpy_version": discord.__version__,
                "python_version": platform.python_version(),
            }
        )
        self.commands_gauge.set(stats["total_commands"])
        self.on_app_command_counter.inc(0)
        self.pronouns_tester_counter.inc(0)

        if self.bot.is_closed():
            self.connection_gauge.labels(None).set(0)
            return

        self.connection_gauge.labels(None).set(1)


class Prometheus(commands.Cog):
    """Cog which handles Prometheus metrics for Catherine-Chan"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self._prev_member_count = MemberCounts()
        self.members = self._obtain_member_count()

    def _obtain_member_count(self) -> MemberCounts:
        total_members = 0
        unique_members = len(self.bot.users)

        for guild in self.bot.guilds:
            if guild.unavailable:
                continue
            total_members += guild.member_count or 0

        return MemberCounts(total=total_members, unique=unique_members)

    def _update_member_count(self) -> None:
        members = self._obtain_member_count()
        temp = self.members

        temp.total = members.total
        temp.unique = members.unique

        self.members = temp
        self.bot.metrics.user_gauge.set(self.members.total)
        self.bot.metrics.user_unique_gauge.set(self.members.unique)

    async def cog_load(self) -> None:
        # For some reason it would only work inside here
        self.latency_loop.start()
        self.member_loop.start()

    async def cog_unload(self) -> None:
        self.latency_loop.stop()
        self.member_loop.stop()

    @tasks.loop(seconds=5)
    async def latency_loop(self) -> None:
        self.bot.metrics.latency_gauge.labels(None).set(self.bot.latency)

    @tasks.loop(seconds=10)
    async def member_loop(self) -> None:
        self._update_member_count()

    @commands.Cog.listener()
    async def on_connect(self) -> None:
        self.bot.metrics.connection_gauge.labels(None).set(1)

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        self.bot.metrics.connection_gauge.labels(None).set(1)

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        self.bot.metrics.connection_gauge.labels(None).set(0)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.bot.metrics.create_guild_gauges()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.bot.metrics.create_guild_gauges()


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Prometheus(bot))
