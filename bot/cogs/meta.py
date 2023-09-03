import platform

import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from discord.utils import oauth_url
from libs.utils import human_timedelta


class Meta(commands.Cog):
    """Commands for getting info about the bot"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot

    def get_bot_uptime(self, *, brief: bool = False) -> str:
        return human_timedelta(
            self.bot.uptime, accuracy=None, brief=brief, suffix=False
        )

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

    @app_commands.command(name="info")
    async def info(self, interaction: discord.Interaction) -> None:
        """Shows some basic info about Catherine-Chan"""
        embed = discord.Embed()
        embed.title = f"{self.bot.user.name} Info"  # type: ignore
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)  # type: ignore
        embed.add_field(name="Server Count", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="User Count", value=len(self.bot.users), inline=True)
        embed.add_field(
            name="Python Version", value=platform.python_version(), inline=True
        )
        embed.add_field(
            name="Discord.py Version", value=discord.__version__, inline=True
        )
        embed.add_field(
            name="Catherine Build Version", value=str(self.bot.version), inline=True
        )
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
