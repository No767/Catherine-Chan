from __future__ import annotations

from typing import TYPE_CHECKING

import asyncpg
import discord
from libs.cog_utils.tonetags import (
    create_tonetag,
    edit_tonetag,
    parse_tonetag,
    validate_tonetag,
)
from libs.utils import CatherineModal

if TYPE_CHECKING:
    pass


class CreateToneTagModal(CatherineModal, title="Create a ToneTag"):
    def __init__(self, interaction: discord.Interaction, pool: asyncpg.Pool):
        super().__init__(interaction)
        self.pool = pool
        self.indicator = discord.ui.TextInput(
            label="Indicator",
            placeholder="Enter the indicator name",
            style=discord.TextStyle.short,
            min_length=1,
            max_length=25,
        )
        self.definition = discord.ui.TextInput(
            label="Definition",
            placeholder="Enter the definition of the tonetag",
            style=discord.TextStyle.long,
            min_length=1,
            max_length=500,
        )
        self.add_item(self.indicator)
        self.add_item(self.definition)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        parsed_tonetag = parse_tonetag(self.indicator.value)
        if validate_tonetag(parsed_tonetag) is False:
            await interaction.response.send_message("The tonetag is invalid.")
            return

        status = await create_tonetag(
            self.indicator.value, self.definition.value, interaction.user.id, self.pool
        )
        await interaction.response.send_message(status, ephemeral=True)


class EditToneTagModal(CatherineModal, title="Edit a ToneTag"):
    def __init__(
        self,
        interaction: discord.Interaction,
        indicator: str,
        old_definition: str,
        pool: asyncpg.Pool,
    ):
        super().__init__(interaction=interaction)
        self.pool = pool
        self.indicator = indicator
        self.old_definition = old_definition
        self.definition = discord.ui.TextInput(
            label="Definition",
            placeholder="Enter the new definition of the tonetag",
            style=discord.TextStyle.long,
            min_length=1,
            max_length=500,
            default=self.old_definition,
        )
        self.add_item(self.definition)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        parsed_tonetag = parse_tonetag(self.indicator)
        status = await edit_tonetag(
            parsed_tonetag, self.definition.value, interaction.user.id, self.pool
        )
        if status[-1] != "0":
            await interaction.response.send_message(
                f"Tonetag `{self.indicator}` successfully edited"
            )
        else:
            await interaction.response.send_message(
                f"The requested tonetag `{self.indicator}` was not edited"
            )
