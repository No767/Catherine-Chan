import asyncio
from typing import Any, Optional

import discord

from .embeds import FullErrorEmbed, TimeoutEmbed

NO_CONTROL_MSG = "This view cannot be controlled by you, sorry!"


class CatherineView(discord.ui.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.interaction = interaction
        self.original_response: Optional[discord.InteractionMessage]
        self.triggered = asyncio.Event()

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if self.original_response:
            await self.original_response.edit(
                embed=TimeoutEmbed(), view=None, delete_after=15.0
            )

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any],
        /,
    ) -> None:
        await interaction.response.send_message(embed=FullErrorEmbed(error))
        self.stop()
