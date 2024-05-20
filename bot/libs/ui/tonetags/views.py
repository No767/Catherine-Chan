from __future__ import annotations

from typing import Optional

import asyncpg
import discord
from libs.cog_utils.tonetags import parse_tonetag
from libs.utils import CatherineView, ErrorEmbed, SuccessEmbed

NO_CONTROL_MSG = "This menu cannot be controlled by you, sorry!"


class DeleteTagView(CatherineView):
    def __init__(
        self,
        interaction: discord.Interaction,
        pool: asyncpg.Pool,
        *,
        indicator: Optional[str] = None,
        indicator_id: Optional[int] = None,
    ):
        super().__init__(interaction=interaction)
        self.indicator = indicator
        self.indicator_id = indicator_id
        self.pool = pool

    async def on_timeout(self) -> None:
        if self.original_response and not self.triggered.is_set():
            await self.original_response.edit(
                embed=self.build_timeout_embed(), view=None, delete_after=15.0
            )

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        DELETE FROM tonetags
        WHERE indicator = $1 AND author_id = $2 OR id = $3;
        """

        if self.indicator:
            self.indicator = parse_tonetag(self.indicator.lower())

        status = await self.pool.execute(
            query, self.indicator, interaction.user.id, self.indicator_id
        )

        if status[-1] != "0":
            embed = SuccessEmbed()
            embed.description = f"Successfully deleted the tonetag `{self.indicator or self.indicator_id}`"
        else:
            embed = ErrorEmbed(title="Doesn't exist")
            embed.description = (
                "The tonetag that you are trying to delete doesn't exist"
            )

        if self.original_response:
            self.triggered.set()
            await self.original_response.edit(embed=embed, view=None, delete_after=15.0)

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.red,
        emoji="<:redTick:596576672149667840>",
    )
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()
