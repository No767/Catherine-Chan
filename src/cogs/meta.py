from __future__ import annotations

import datetime
import itertools
import platform
from typing import TYPE_CHECKING, Optional

import discord
import psutil
import pygit2
from dateutil.relativedelta import relativedelta
from discord import app_commands
from discord.ext import commands
from pygit2.enums import SortMode

from utils.embeds import Embed

if TYPE_CHECKING:
    from collections.abc import Sequence

    from core import Catherine


def human_timedelta(
    dt: datetime.datetime,
    *,
    source: Optional[datetime.datetime] = None,
    accuracy: Optional[int] = 3,
    brief: bool = False,
    suffix: bool = True,
) -> str:
    def _human_join(seq: Sequence[str], delim: str = ", ", final: str = "or") -> str:
        if not seq:
            return ""
        if len(seq) == 1:
            return seq[0]
        return f"{delim.join(seq[:-1])} {final} {seq[-1]}"

    now = source or datetime.datetime.now(datetime.UTC)

    # Merge timezone checks
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=datetime.UTC)

    # Microsecond free zone
    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    # This implementation uses relativedelta instead of the much more obvious
    # divmod approach with seconds because the seconds approach is not entirely
    # accurate once you go over 1 week in terms of accuracy since you have to
    # hardcode a month as 30 or 31 days.
    # A query like "11 months" can be interpreted as "!1 months and 6 days"
    if dt > now:
        delta = relativedelta(dt, now)
        output_suffix = ""
    else:
        delta = relativedelta(now, dt)
        output_suffix = " ago" if suffix else ""

    attrs = [
        ("year", "y"),
        ("month", "mo"),
        ("day", "d"),
        ("hour", "h"),
        ("minute", "m"),
        ("second", "s"),
    ]

    output = []

    for attr, brief_attr in attrs:
        elem = getattr(delta, attr + "s")
        if not elem:
            continue

        # Handle weeks logic inside the 'day' iteration
        if attr == "day" and delta.weeks:
            weeks = delta.weeks
            elem -= weeks * 7
            output.append(f"{weeks}w" if brief else format(Plural(weeks), "week"))

        # Skip if elem is <= 0 (specifically for days after week subtraction)
        if elem <= 0:
            continue

        # Merged formatting logic
        output.append(f"{elem}{brief_attr}" if brief else format(Plural(elem), attr))

    if accuracy is not None:
        output = output[:accuracy]

    if not output:
        return "now"

    if brief:
        return " ".join(output) + output_suffix

    return _human_join(output, final="and") + output_suffix


class Plural:
    def __init__(self, value: int):
        self.value: int = value

    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, _sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


class Meta(commands.Cog):
    """Commands for getting info about the bot"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.process = psutil.Process()

    def get_bot_uptime(self, *, brief: bool = False) -> str:
        return human_timedelta(
            self.bot.uptime, accuracy=None, brief=brief, suffix=False
        )

    def format_commit(self, commit: pygit2.Commit) -> str:
        short, _, _ = commit.message.partition("\n")
        short_sha2 = str(commit.id)[0:6]
        commit_tz = datetime.timezone(
            datetime.timedelta(minutes=commit.commit_time_offset)
        )
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(
            commit_tz
        )

        # [`hash`](url) message (offset)
        offset = discord.utils.format_dt(commit_time.astimezone(datetime.UTC), "R")
        commit_id = str(commit.id)
        return f"[`{short_sha2}`](https://github.com/No767/Catherine-Chan/commit/{commit_id}) {short} ({offset})"

    def get_last_commits(self, count: int = 5):
        repo = pygit2.Repository(".git")
        commits = list(
            itertools.islice(repo.walk(repo.head.target, SortMode.TOPOLOGICAL), count)
        )
        return "\n".join(self.format_commit(c) for c in commits)

    @app_commands.command(name="uptime")
    async def uptime(self, interaction: discord.Interaction) -> None:
        """Displays the bot's uptime"""
        uptime_message = f"Uptime: {self.get_bot_uptime()}"
        await interaction.response.send_message(uptime_message)

    @app_commands.command(name="version")
    async def version(self, interaction: discord.Interaction) -> None:
        """Displays the current build version"""
        version_message = f"Version: {self.bot.version}"
        await interaction.response.send_message(version_message)

    @app_commands.command(name="about")
    async def about(self, interaction: discord.Interaction) -> None:
        """Shows some basic info about Catherine-Chan"""
        total_members = 0
        total_unique = len(self.bot.users)

        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable:
                continue

            total_members += guild.member_count or 0

        # For Kumiko, it's done differently
        # R. Danny's way of doing it is probably close enough anyways
        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()  # type: ignore # Pyright is still complaining

        revisions = self.get_last_commits()
        embed = Embed()
        embed.set_author(
            name=self.bot.user.name,  # type: ignore
            icon_url=self.bot.user.display_avatar.url,  # type: ignore
        )
        embed.title = "Support Server Invite"
        embed.url = "https://discord.gg/ns3e74frqn"
        desc = [
            "Catherine-Chan is designed for members of the LGBTQ+ community ",
            "and serves as an informational toolkit for those who want to express themselves or learn more. "
            "Features include an pronouns tester, find LGBTQ+ terms and definitions, and many more!\n",
            f"Latest Changes:\n {revisions}",
        ]
        embed.description = "\n".join(desc)
        embed.set_footer(
            text=f"Made with discord.py v{discord.__version__}",
            icon_url="https://cdn.discordapp.com/emojis/596577034537402378.png?size=128",
        )
        embed.add_field(name="Guilds", value=guilds)
        embed.add_field(
            name="Users", value=f"{total_members} total\n{total_unique} unique"
        )
        embed.add_field(
            name="Process", value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU"
        )
        embed.add_field(name="Python Version", value=platform.python_version())
        embed.add_field(name="Catherine-Chan Version", value=str(self.bot.version))
        embed.add_field(name="Uptime", value=self.get_bot_uptime(brief=True))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite")
    async def invite(self, interaction: discord.Interaction) -> None:
        """Get Catherine-Chan's invite link"""
        # This should be filled in by the time the bot is fully ready
        if self.bot.application is None:
            return
        invite_url = discord.utils.oauth_url(client_id=self.bot.application.id)
        await interaction.response.send_message(
            f"Invite Catherine-Chan using this link: {invite_url}"
        )

    @app_commands.command(name="support")
    async def support(self, interaction: discord.Interaction):
        """Ways you can support Catherine-Chan!"""
        invite_url = discord.utils.oauth_url(client_id=self.bot.application.id)  # type: ignore # By the time the bot is ready, the app id is already there
        desc = f"""
        **Upvoting on Top.gg**: https://top.gg/bot/1142620675517984808
        **Joining the support server**: https://discord.gg/ns3e74frqn
        **Inviting Catherine-Chan to you server**: {invite_url}
        
        And there are more ways you can show your support! Check out the [support page](https://github.com/No767/Catherine-Chan#support) on how you can support the developer!
        """
        embed = Embed()
        embed.title = "Ways you can support"
        embed.description = desc
        await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Meta(bot))
