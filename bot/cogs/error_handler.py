import traceback
from typing import List

import discord
from catherinecore import Catherine
from discord.app_commands import (
    AppCommandError,
    BotMissingPermissions,
    MissingPermissions,
    NoPrivateMessage,
)
from discord.ext import commands
from discord.utils import utcnow
from libs.utils import ErrorEmbed


class ErrorHandler(commands.Cog):
    """Error Handler cog - meant for global errors"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot

    def build_error_embed(self, error: AppCommandError) -> ErrorEmbed:
        error_traceback = "\n".join(traceback.format_exception_only(type(error), error))
        embed = ErrorEmbed()
        embed.description = f"""
        Uh oh! It seems like the command ran into an issue! For support, please visit [Catherine-Chan's Support Server](https://discord.gg/ns3e74frqn) to get help!
        
        **Error**:
        ```
        {error_traceback}
        ```
        """
        embed.set_footer(text="Happened At")
        embed.timestamp = utcnow()
        return embed

    def build_premade_embed(self, title: str, description: str) -> ErrorEmbed:
        embed = ErrorEmbed()
        embed.title = title
        embed.description = description
        return embed

    def build_missing_perm_embed(
        self, missing_perms: List[str], is_bot: bool = True
    ) -> ErrorEmbed:
        title = (
            "Catherine-Chan is missing some permissions!"
            if is_bot is True
            else "Missing Permissions"
        )
        desc = f"""
        It looks like you are missing the following permissions in order to run the command:
        {','.join(missing_perms).rstrip(',')}
        """
        if is_bot:
            desc = f"""
            It looks like Catherine-Chan is missing these permissions:
            {','.join(missing_perms).rstrip(',')}
            """

        embed = ErrorEmbed()
        embed.title = title
        embed.description = desc
        embed.set_footer(text="Happened At")
        embed.timestamp = utcnow()
        return embed

    async def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_app_command_error

    async def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        return

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ) -> None:
        if isinstance(error, MissingPermissions):
            await interaction.response.send_message(
                embed=self.build_missing_perm_embed(error.missing_permissions, False)
            )
        elif isinstance(error, BotMissingPermissions):
            await interaction.response.send_message(
                embed=self.build_missing_perm_embed(error.missing_permissions, True)
            )
        elif isinstance(error, NoPrivateMessage):
            await interaction.response.send_message(
                embed=self.build_premade_embed(
                    "DMs don't work",
                    "The command you are trying to run does not work in DMs.",
                )
            )
        else:
            await interaction.response.send_message(embed=self.build_error_embed(error))


async def setup(bot: Catherine) -> None:
    await bot.add_cog(ErrorHandler(bot))
