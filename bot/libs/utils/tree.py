from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, List, Union

import discord
from discord.app_commands import (
    AppCommandError,
    BotMissingPermissions,
    CommandTree,
    MissingPermissions,
    NoPrivateMessage,
)
from discord.utils import utcnow

from .blacklist import get_or_fetch_blacklist
from .embeds import ErrorEmbed

if TYPE_CHECKING:
    from bot.catherinecore import Catherine


def _build_error_embed(error: AppCommandError) -> ErrorEmbed:
    error_traceback = "\n".join(traceback.format_exception_only(type(error), error))
    embed = ErrorEmbed()
    embed.description = f"""
    Uh oh! It seems like the command ran into an issue! For support, please visit [Catherine-Chan's Support Server](https://discord.gg/ns3e74frqn) to get help!
    
    **Error**:
    ```{error_traceback}```
    """
    embed.set_footer(text="Happened At")
    embed.timestamp = utcnow()
    return embed


def _build_premade_embed(title: str, description: str) -> ErrorEmbed:
    embed = ErrorEmbed()
    embed.title = title
    embed.description = description
    return embed


def _build_missing_perm_embed(
    missing_perms: List[str], user: Union[discord.User, discord.Member]
) -> ErrorEmbed:
    str_user = "Catherine-Chan is" if user.bot is True else "You are"
    perms = ",".join(missing_perms).rstrip(",")
    desc = f"""
    {str_user} missing the following permissions in order to run the command:
    
    {perms}
    """
    return _build_premade_embed("Missing Permissions", desc)


# This is needed for the blacklisting system
# Yes a custom CommandTree lol.
# At the very least better than Jade's on_interaction checks
# https://github.com/LilbabxJJ-1/PrideBot/blob/master/main.py#L19-L36
class CatherineCommandTree(CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        bot: Catherine = interaction.client  # type: ignore # Pretty much returns the subclass anyways. I checked - Noelle
        bot.metrics.on_app_command_counter.inc()
        if (
            bot.owner_id == interaction.user.id
            or bot.application_id == interaction.user.id
        ):
            return True

        blacklisted_status = await get_or_fetch_blacklist(
            bot, interaction.user.id, bot.pool
        )
        if blacklisted_status is True:
            bot.metrics.attempted_commands.inc(1)
            await interaction.response.send_message(
                f"My fellow user, {interaction.user.mention}, you just got the L. You are blacklisted from using this bot. Take an \U0001f1f1, \U0001f1f1oser. [Here is your appeal form](https://media.tenor.com/K9R9beOgPR4AAAAC/fortnite-thanos.gif)"
            )
            return False
        return True

    async def on_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ) -> None:
        if isinstance(error, MissingPermissions) or isinstance(
            error, BotMissingPermissions
        ):
            await interaction.response.send_message(
                embed=_build_missing_perm_embed(
                    error.missing_permissions, interaction.user
                )
            )
        elif isinstance(error, NoPrivateMessage):
            await interaction.response.send_message(
                embed=_build_premade_embed(
                    "DMs don't work",
                    "The command you are trying to run does not work in DMs.",
                )
            )
        else:
            await interaction.response.send_message(embed=_build_error_embed(error))
