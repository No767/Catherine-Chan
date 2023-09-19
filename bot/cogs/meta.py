import datetime
import itertools
import platform

import discord
import psutil
import pygit2
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt, oauth_url
from libs.utils import Embed, human_timedelta


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
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(
            datetime.timedelta(minutes=commit.commit_time_offset)
        )
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(
            commit_tz
        )

        # [`hash`](url) message (offset)
        offset = format_dt(commit_time.astimezone(datetime.timezone.utc), "R")
        return f"[`{short_sha2}`](https://github.com/No767/Catherine-Chan/commit/{commit.hex}) {short} ({offset})"

    def get_last_commits(self, count: int = 5):
        repo = pygit2.Repository(".git")
        commits = list(
            itertools.islice(
                repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count
            )
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

        for guild in self.bot.guilds:
            total_members += guild.member_count or 0

        # For Kumiko, it's done differently
        # R. Danny's way of doing it is probably close enough anyways
        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()

        revisions = self.get_last_commits()
        embed = Embed()
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)  # type: ignore
        embed.title = "Support Server Invite"
        embed.url = "https://discord.gg/ns3e74frqn"
        embed.description = f"Latest Changes (Stable):\n {revisions}"
        embed.set_footer(
            text=f"Made with discord.py v{discord.__version__}",
            icon_url="https://cdn.discordapp.com/emojis/596577034537402378.png?size=128",
        )
        embed.add_field(name="Servers Count", value=len(self.bot.guilds))
        embed.add_field(name="User Count", value=f"{total_members} total")
        embed.add_field(
            name="Process", value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU"
        )
        embed.add_field(name="Python verson", value=platform.python_version())
        embed.add_field(name="Catherine-Chan Version", value=str(self.bot.version))
        embed.add_field(name="Uptime", value=self.get_bot_uptime(brief=True))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite")
    async def invite(self, interaction: discord.Interaction) -> None:
        """Get Catherine-Chan's invite link"""
        # This should be filled in by the time the bot is fully ready
        if self.bot.application is None:
            return
        invite_url = oauth_url(client_id=self.bot.application.id)
        await interaction.response.send_message(
            f"Invite Catherine-Chan using this link: {invite_url}"
        )


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Meta(bot))
