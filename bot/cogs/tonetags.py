from datetime import timezone
from io import BytesIO
from typing import Optional

import discord
import orjson
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.tonetags import (
    TonetagInfo,
    edit_tonetag,
    format_similar_tonetags,
    get_exact_and_similar_tonetags,
    get_tonetag,
    get_tonetag_info,
    get_top_tonetags,
    parse_tonetag,
)
from libs.ui.tonetags import (
    BareToneTagsPages,
    CreateToneTagModal,
    DeleteToneTagViaIDView,
    DeleteToneTagView,
    EditToneTagModal,
    ESToneTagsPages,
    SimpleToneTagsPages,
    StatsBareToneTagsPages,
    ToneTagPages,
)
from libs.utils import ConfirmEmbed, Embed

NO_TONETAGS_FOUND = "No tonetags were found"
TONETAG_NOT_FOUND = "The tonetag requested was not found"
INDICATOR_DESCRIPTION = "The indicator to look for. Can be in both forms (/j or j)"


class ToneTags(commands.GroupCog, name="tonetags"):
    """The to-go cog for tone tags"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        super().__init__()

    async def _build_tonetag_info(self, tonetag: TonetagInfo) -> Embed:
        query = """SELECT (
                       SELECT COUNT(*)
                       FROM tonetags second
                       WHERE (second.uses, second.id) >= (first.uses, first.id)
                   ) AS rank
                   FROM tonetags first
                   WHERE first.id=$1
                """
        rank = await self.pool.fetchrow(query, tonetag["tonetags_id"])

        owner_id = tonetag["author_id"]
        author = self.bot.get_user(owner_id) or (await self.bot.fetch_user(owner_id))

        embed = Embed()
        embed.title = f"/{tonetag['indicator']}"
        embed.set_author(name=author.name, icon_url=author.display_avatar.url)
        embed.add_field(name="Author", value=f"<@{owner_id}>")
        embed.add_field(name="Uses", value=tonetag["uses"])
        if rank is not None:
            embed.add_field(name="Rank", value=rank["rank"])
        return embed

    def _build_tonetag_embed(self, tonetag: TonetagInfo) -> Embed:
        embed = Embed()
        embed.title = f"/{tonetag['indicator']}"
        embed.description = tonetag["definition"]
        embed.timestamp = tonetag["created_at"].replace(tzinfo=timezone.utc)
        embed.set_footer(text="Created At")
        return embed

    @app_commands.command(name="get")
    @app_commands.describe(indicator=INDICATOR_DESCRIPTION)
    async def get(self, interaction: discord.Interaction, indicator: str) -> None:
        """Gets a tonetag"""
        tonetag = await get_tonetag(indicator, self.pool)

        if isinstance(tonetag, list):
            output_str = format_similar_tonetags(tonetag)
            await interaction.response.send_message(output_str)
        elif tonetag is None:
            await interaction.response.send_message(TONETAG_NOT_FOUND)
        else:
            self.bot.metrics.successful_tonetags.inc()
            await interaction.response.send_message(
                embed=self._build_tonetag_embed(tonetag)
            )

    @app_commands.command(name="info")
    @app_commands.describe(indicator=INDICATOR_DESCRIPTION)
    async def info(self, interaction: discord.Interaction, indicator: str) -> None:
        """Provides info about the given tonetag"""

        tonetag = await get_tonetag_info(indicator, self.pool)
        if tonetag is None:
            await interaction.response.send_message(TONETAG_NOT_FOUND)
            return

        embed = await self._build_tonetag_info(tonetag)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="all")
    @app_commands.describe(json="Whether to output the tonetags in JSON format")
    async def _all(
        self, interaction: discord.Interaction, json: Optional[bool] = False
    ) -> None:
        """Displays all of the tonetags available"""
        query = """
        SELECT tonetags_lookup.indicator, tonetags.definition, tonetags.created_at, tonetags.author_id, tonetags.uses, tonetags_lookup.tonetags_id
        FROM tonetags_lookup
        INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
        ORDER BY uses DESC
        LIMIT 100;
        """
        records = await self.pool.fetch(query)

        if len(records) == 0:
            await interaction.response.send_message(NO_TONETAGS_FOUND)
            return

        if json:
            buffer = BytesIO(
                orjson.dumps([dict(row) for row in records], option=orjson.OPT_INDENT_2)
            )
            file = discord.File(fp=buffer, filename="tonetags.json")
            await interaction.response.send_message(file=file)
            return

        pages = ToneTagPages(entries=records, interaction=interaction)
        await pages.start()

    @app_commands.command(name="lookup")
    @app_commands.describe(indicator=INDICATOR_DESCRIPTION)
    async def lookup(self, interaction: discord.Interaction, indicator: str) -> None:
        """Looks for the exact and/or similar tonetags to the one given"""
        tonetags = await get_exact_and_similar_tonetags(indicator, self.pool)

        if tonetags is None:
            await interaction.response.send_message(NO_TONETAGS_FOUND)
            return

        pages = ESToneTagsPages(entries=tonetags, interaction=interaction)
        await pages.start()

    @app_commands.command(name="top")
    async def top(self, interaction: discord.Interaction) -> None:
        """Gets the top 100 tonetags by usage"""
        top_tonetags = await get_top_tonetags(self.pool)

        if len(top_tonetags) == 0:
            await interaction.response.send_message(NO_TONETAGS_FOUND)
            return

        pages = StatsBareToneTagsPages(entries=top_tonetags, interaction=interaction)
        await pages.start()

    @app_commands.command(name="search")
    @app_commands.describe(
        indicator="The indicator to search for. Can be in both forms (/j or j)"
    )
    async def search(self, interaction: discord.Interaction, indicator: str) -> None:
        """Searches for tonetags"""
        sql = """
        SELECT tonetags_lookup.indicator, tonetags.author_id, tonetags_lookup.tonetags_id
        FROM tonetags_lookup
        INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
        WHERE tonetags_lookup.indicator % $1
        ORDER BY similarity(tonetags_lookup.indicator, $1) DESC
        LIMIT 100;
        """
        parsed_indicator = parse_tonetag(indicator)
        records = await self.pool.fetch(sql, parsed_indicator)
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
            # I'm aware that this doesn't show the user's name and icon
            pages = BareToneTagsPages(entries=records, interaction=interaction)
            await pages.start()
        else:
            await interaction.response.send_message("No tonetags found for this user")

    @app_commands.command(name="create")
    async def create(self, interaction: discord.Interaction) -> None:
        """Creates an new tonetag"""
        modal = CreateToneTagModal(interaction, self.pool)
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
        indicator = parse_tonetag(indicator)
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
            modal = EditToneTagModal(interaction, indicator, old_def, self.pool)
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
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.original_response = await interaction.original_response()

    @app_commands.command(name="delete-id")
    @app_commands.describe(id="The ID of the tonetag")
    async def delete_id(self, interaction: discord.Interaction, id: int) -> None:
        """Deletes a tonetag via the ID instead"""
        view = DeleteToneTagViaIDView(interaction, id, self.pool)
        embed = ConfirmEmbed()
        embed.description = (
            f"Are you sure you want to delete the tonetag with ID `{id}`?"
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.original_response = await interaction.original_response()


async def setup(bot: Catherine) -> None:
    await bot.add_cog(ToneTags(bot))
