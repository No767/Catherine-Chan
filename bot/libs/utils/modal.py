from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from .embeds import FullErrorEmbed

if TYPE_CHECKING:
    from catherinecore import Catherine

NO_CONTROL_MSG = "This modal cannot be controlled by you, sorry!"


class CatherineModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interaction = interaction
        self.bot: Catherine = interaction.client  # type: ignore

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, /
    ) -> None:
        self.bot.logger.exception(
            "Ignoring modal exception from %s: ",
            self.__class__.__name__,
            exc_info=error,
        )
        await interaction.response.send_message(
            embed=FullErrorEmbed(error), ephemeral=True
        )
        self.stop()
