from typing import NamedTuple, Optional

import discord

from .view import CatherineView


class ConfirmResponse(NamedTuple):
    value: Optional[bool]
    original_response: discord.InteractionMessage


class ConfirmationView(CatherineView):
    def __init__(
        self,
        interaction: discord.Interaction,
        timeout: float,
        delete_after: bool = True,
    ):
        super().__init__(interaction=interaction, timeout=timeout)
        self.value: Optional[bool] = None
        self.delete_after = delete_after
        self.original_response: Optional[discord.InteractionMessage] = None

    async def on_timeout(self) -> None:
        if self.delete_after and self.original_response:
            await self.original_response.delete()
        elif self.original_response:
            await self.original_response.edit(view=None)

    async def delete_response(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()
        elif self.original_response and not self.delete_after:
            await self.original_response.edit(view=None)

        self.stop()

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        self.value = True
        await self.delete_response(interaction)

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.red,
        emoji="<:redTick:596576672149667840>",
    )
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        self.value = False
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()


async def interaction_prompt(
    embed: discord.Embed,
    interaction: discord.Interaction,
    *,
    timeout: float = 60.0,
    delete_after: bool = False,
    ephemeral: bool = False
) -> ConfirmResponse:
    view = ConfirmationView(
        interaction=interaction, timeout=timeout, delete_after=delete_after
    )
    await interaction.response.send_message(embed=embed, view=view, ephemeral=ephemeral)
    view.original_response = await interaction.original_response()
    await view.wait()
    return ConfirmResponse(view.value, view.original_response)
