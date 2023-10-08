from typing import Optional

import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.tonetags import edit_tonetag, get_tonetags, parse_tonetag
from libs.ui.tonetags import (
    BareToneTagsPages,
    CreateToneTagModal,
    DeleteToneTagViaIDView,
    DeleteToneTagView,
    EditToneTagModal,
    SimpleToneTagsPages,
    ToneTagPages,
)
from libs.utils import ConfirmEmbed

NO_TONETAGS_FOUND = "No tonetags were found"


class ToneTags(commands.GroupCog, name="tonetags"):
    """The to-go cog for tone tags"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        super().__init__()

    @app_commands.command(name="info")
    @app_commands.describe(
        indicator="The indicator to look for. If left empty, then all of the tonetags will be shown."
    )
    async def info(
        self, interaction: discord.Interaction, indicator: Optional[str] = None
    ):
        """Looks up the definition and information for a tonetag"""
        if indicator is None:
            query = """
            SELECT tonetags_lookup.indicator, tonetags.definition, tonetags.created_at, tonetags.author_id, tonetags_lookup.tonetags_id
            FROM tonetags_lookup
            INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
            LIMIT 100;
            """
            records = await self.pool.fetch(query)

            if len(records) == 0:
                await interaction.response.send_message(NO_TONETAGS_FOUND)
            pages = ToneTagPages(entries=records, interaction=interaction)
            await pages.start()
            return

        tonetags = await get_tonetags(indicator, self.pool)
        if isinstance(tonetags, str):
            await interaction.response.send_message(tonetags)
        elif tonetags is None:
            await interaction.response.send_message(NO_TONETAGS_FOUND)
        else:
            pages = ToneTagPages(entries=tonetags, interaction=interaction)  # type: ignore
            await pages.start()

    @app_commands.command(name="search")
    @app_commands.describe(query="The tonetag to search")
    async def search(self, interaction: discord.Interaction, query: str) -> None:
        """Searches for tonetags"""
        sql = """
        SELECT tonetags_lookup.indicator, tonetags.author_id, tonetags_lookup.tonetags_id
        FROM tonetags_lookup
        INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
        WHERE tonetags_lookup.indicator % $1
        ORDER BY similarity(tonetags_lookup.indicator, $1) DESC
        LIMIT 100;
        """
        parsed_query = parse_tonetag(query)
        records = await self.pool.fetch(sql, parsed_query)
        if records:
            pages = SimpleToneTagsPages(entries=records, interaction=interaction)
            await pages.start()
        else:
            await interaction.response.send_message(
                "The tonetag requested was not found"
            )

    @app_commands.command(name="list")
    @app_commands.describe(user="The user to get all owned tonetags from")
    async def list(
        self, interaction: discord.Interaction, user: Optional[discord.User] = None
    ):
        """Lists either your owned tonetags or others"""
        query = """
        SELECT tonetags_lookup.indicator, tonetags_lookup.tonetags_id
        FROM tonetags_lookup
        INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
        WHERE tonetags_lookup.author_id = $1
        LIMIT 100;
        """
        author_id = user.id if user is not None else interaction.user.id
        records = await self.pool.fetch(query, author_id)
        if records:
            pages = BareToneTagsPages(entries=records, interaction=interaction)
            await pages.start()
        else:
            await interaction.response.send_message("No tonetags found for this user")

    @app_commands.command(name="create")
    async def create(self, interaction: discord.Interaction) -> None:
        """Creates an new tonetag"""
        modal = CreateToneTagModal(self.pool)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="edit")
    @app_commands.describe(
        indicator="The indicator of the tonetag to edit",
        definition="The new definition to use. If left blank, an interactive session will open up.",
    )
    async def edit(
        self,
        interaction: discord.Interaction,
        indicator: str,
        definition: Optional[str] = None,
    ) -> None:
        """Edits a tonetag"""
        if definition is None:
            query = """
            SELECT definition
            FROM tonetags
            WHERE indicator = $1 AND author_id = $2;
            """
            old_def = await self.pool.fetchval(query, indicator, interaction.user.id)
            if old_def is None:
                await interaction.response.send_message(
                    f"The tonetag `{indicator}` was not found. Please create it first.",
                    ephemeral=True,
                )
                return
            modal = EditToneTagModal(indicator, old_def, self.pool)
            await interaction.response.send_modal(modal)
            return

        status = await edit_tonetag(
            indicator, definition, interaction.user.id, self.pool
        )
        if status[-1] != "0":
            await interaction.response.send_message(
                f"Successfully edited tonetag `{indicator}`"
            )
            return

        await interaction.response.send_message(
            "The tonetag `{self.indicator}` did not get edited"
        )

    @app_commands.command(name="delete")
    @app_commands.describe(indicator="The tonetag indicator to delete")
    async def delete(self, interaction: discord.Interaction, indicator: str) -> None:
        """Deletes a tonetag"""
        view = DeleteToneTagView(interaction, indicator, self.pool)
        embed = ConfirmEmbed()
        embed.description = (
            f"Are you sure you want to delete the tonetag `{indicator}`?"
        )
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="delete-id")
    @app_commands.describe(id="The ID of the tonetag")
    async def delete_id(self, interaction: discord.Interaction, id: int) -> None:
        """Deletes a tonetag via the ID instead"""
        view = DeleteToneTagViaIDView(interaction, id, self.pool)
        embed = ConfirmEmbed()
        embed.description = (
            f"Are you sure you want to delete the tonetag with ID `{id}`?"
        )
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(ToneTags(bot))
