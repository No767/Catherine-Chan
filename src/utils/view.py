from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

import discord

from .embeds import FullErrorEmbed

if TYPE_CHECKING:
    from core import Catherine

NO_CONTROL_MSG = "This view cannot be controlled by you, sorry!"


async def prompt(
    interaction: discord.Interaction,
    message: str,
    *,
    timeout: float = 60.0,  # noqa: ASYNC109
    ephemeral: bool = True,
    delete_after: bool = False,
) -> Optional[bool]:
    view = ConfirmationView(interaction, timeout, delete_after)
    await interaction.response.send_message(message, view=view, ephemeral=ephemeral)
    view.response = await interaction.original_response()
    await view.wait()
    return view.value


class TimeoutEmbed(discord.Embed):
    """Timed out embed"""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", discord.Color.from_rgb(214, 6, 6))
        kwargs.setdefault("title", "\U00002757 Timed Out")
        kwargs.setdefault(
            "description", "Timed out waiting for a response. Cancelling action."
        )
        super().__init__(**kwargs)


class CatherineView(discord.ui.View):
    def __init__(
        self, interaction: discord.Interaction, *, timeout: Optional[float] = 180.0
    ):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.original_response: Optional[discord.InteractionMessage]
        self.triggered = asyncio.Event()
        self.bot: Catherine = interaction.client  # type: ignore

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
        self.bot.logger.exception(
            "Ignoring view exception from %s: ", self.__class__.__name__, exc_info=error
        )
        await interaction.response.send_message(
            embed=FullErrorEmbed(error), ephemeral=True
        )
        self.stop()


class ConfirmationView(CatherineView):
    def __init__(
        self,
        interaction: discord.Interaction,
        timeout: float = 180.0,
        *,
        delete_after: bool = True,
    ):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.value: Optional[bool] = None
        self.delete_after = delete_after
        self.response: Optional[discord.InteractionMessage] = None

    async def on_timeout(self) -> None:
        if self.delete_after and self.response:
            await self.response.delete()
        elif self.response:
            await self.response.edit(view=None)

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        self.value = True
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()

        self.stop()

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
