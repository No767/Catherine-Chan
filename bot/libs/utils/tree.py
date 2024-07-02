from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands

from .embeds import FullErrorEmbed

if TYPE_CHECKING:
    from bot.catherinecore import Catherine


# This is needed for the blacklisting system
# Yes a custom CommandTree lol.
# At the very least better than Jade's on_interaction checks
# https://github.com/LilbabxJJ-1/PrideBot/blob/master/main.py#L19-L36
class CatherineCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        bot: Catherine = interaction.client  # type: ignore # Pretty much returns the subclass anyways. I checked - Noelle

        if (
            bot.owner_id == interaction.user.id
            or bot.application_id == interaction.user.id
        ):
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
                bot.logger.exception("In %s: ", interaction.command.qualified_name, exc_info=original)  # type: ignore
                await interaction.response.send_message(
                    embed=FullErrorEmbed(error), ephemeral=True
                )
        else:
            await interaction.response.send_message(embed=FullErrorEmbed(error))
