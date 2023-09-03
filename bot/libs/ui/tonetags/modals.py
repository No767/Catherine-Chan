import asyncpg
import discord
from libs.cog_utils.tonetags import create_tonetag, edit_tonetag


class CreateToneTagModal(discord.ui.Modal, title="Create a ToneTag"):
    def __init__(self, pool: asyncpg.Pool):
        super().__init__()
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
        status = await create_tonetag(
            self.indicator.value, self.definition.value, interaction.user.id, self.pool
        )
        await interaction.response.send_message(status, ephemeral=True)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            f"An error occurred ({error.__class__.__name__})", ephemeral=True
        )


class EditToneTagModal(discord.ui.Modal, title="Edit a ToneTag"):
    def __init__(self, indicator: str, old_definition: str, pool: asyncpg.Pool):
        super().__init__()
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
        status = await edit_tonetag(
            self.indicator, self.definition.value, interaction.user.id, self.pool
        )
        if status[-1] != "0":
            await interaction.response.send_message(
                f"Tonetag `{self.indicator}` successfully editted"
            )
        else:
            await interaction.response.send_message(
                f"The requested tonetag `{self.indicator}` was not editted"
            )
