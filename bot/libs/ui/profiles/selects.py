import asyncpg
import discord

from .modals import EditProfileModal


class SelectPrideCategory(discord.ui.Select):
    def __init__(self, pool: asyncpg.Pool) -> None:
        options = [
            discord.SelectOption(label="Name", value="name"),
            discord.SelectOption(label="Pronouns", value="pronouns"),
            discord.SelectOption(label="Gender Identity", value="gender_identity"),
            discord.SelectOption(
                label="Sexual Orientation", value="sexual_orientation"
            ),
            discord.SelectOption(
                label="Romantic Orientation", value="romantic_orientation"
            ),
        ]
        super().__init__(placeholder="Select a category", options=options, row=0)
        self.pool = pool

    async def callback(self, interaction: discord.Interaction) -> None:
        value = self.values[0]
        edit_modal = EditProfileModal(value, self.pool)
        await interaction.response.send_modal(edit_modal)
        return
