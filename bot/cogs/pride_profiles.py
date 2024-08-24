from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import asyncpg
import discord
import msgspec
from discord import app_commands
from discord.ext import commands
from libs.ui.pride_profiles.views import ConfigureView
from libs.utils.embeds import Embed
from libs.utils.pages import CatherinePages, SimplePageSource
from libs.utils.view import prompt

if TYPE_CHECKING:
    from catherinecore import Catherine


class PrideProfile(msgspec.Struct, frozen=True):
    id: int
    name: str
    pronouns: Optional[str]
    gender_identity: Optional[str]
    sexual_orientation: Optional[str]
    romantic_orientation: Optional[str]
    views: int

    def to_format_dict(self):
        return {
            f: getattr(self, f)
            for f in self.__struct_fields__
            if f not in ("id", "views")
        }


class PrideProfileEmbed(Embed):
    def __init__(self, profile: PrideProfile, user: discord.User, **kwargs):
        super().__init__(**kwargs)
        self.title = f"{profile.name}'s Profile"
        self.add_field(name="Views", value=profile.views)
        self.set_thumbnail(url=user.display_avatar.url)
        self.set_footer(text=f"User ID: {profile.id}")


class IndexedPrideProfile(msgspec.Struct, frozen=True):
    id: int
    name: str
    pronouns: Optional[str] = None
    views: Optional[int] = None

    def __str__(self) -> str:
        if self.views:
            return f"{self.name} (ID: {self.id} | {self.views} view(s))"
        return f"{self.name} (ID: {self.id} | {self.pronouns or 'None'})"


class ProfileName(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str):
        lowered = value.lower()

        if len(lowered) < 3:
            raise app_commands.AppCommandError(
                "Your query must have 3 characters or more."
            )

        return value


class IndexedPrideProfilePages(CatherinePages):
    def __init__(
        self,
        entries: list[IndexedPrideProfile],
        *,
        interaction: discord.Interaction,
        per_page=1,
    ):
        super().__init__(
            SimplePageSource(entries, per_page=per_page),
            interaction=interaction,
            compact=True,
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(217, 156, 255))


class PrideProfiles(commands.GroupCog, name="pride-profiles"):
    """Create pride profiles to let others know who you are!"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        super().__init__()

    def _disambiguate(self, rows) -> str:
        if rows is None or len(rows) == 0:
            return "Profile not found."

        names = "\n".join(r["name"] for r in rows)
        return f"Profile not found. Did you mean...\n{names}"

    def format_title(self, value: str) -> str:
        return " ".join(word.capitalize() for word in value.split("_"))

    async def send_profile(
        self, interaction: discord.Interaction, profile: PrideProfile
    ) -> None:

        query = """
        UPDATE profile_profiles
        SET views = views + 1
        WHERE id = $1;
        """
        await self.pool.execute(query, profile.id)
        user = self.bot.get_user(profile.id) or (await self.bot.fetch_user(profile.id))
        profile_fmt = profile.to_format_dict()
        embed = PrideProfileEmbed(profile, user)
        embed.description = "\n".join(
            f"**{self.format_title(key)}**: {value}"
            for key, value in profile_fmt.items()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="view")
    @app_commands.describe(name="The user's global or preferred name")
    async def view(self, interaction: discord.Interaction, name: str) -> None:
        """Look at a pride profile"""
        query = """
        SELECT *
        FROM pride_profiles
        WHERE name = $1;
        """
        rows = await self.pool.fetchrow(query, name)
        if rows is None:
            query = """
            SELECT name FROM profiles
            WHERE name % $1
            ORDER BY similarity(name, $1) DESC
            LIMIT 3;
            """
            rows = await self.pool.fetch(query, name)
            await interaction.response.send_message(self._disambiguate(rows))
            return

        profile = PrideProfile(**dict(rows))
        await self.send_profile(interaction, profile)

    @app_commands.command(name="register")
    async def register(self, interaction: discord.Interaction) -> None:
        """Register a pride profile"""
        query = """
        INSERT INTO pride_profiles (id, name)
        VALUES ($1, $2);
        """
        try:
            await self.pool.execute(
                query, interaction.user.id, interaction.user.global_name
            )
        except asyncpg.UniqueViolationError:
            await interaction.response.send_message(
                "Sorry, but you already have an active profile!"
            )
            return
        else:
            await interaction.response.send_message(
                "Registered your pride profile! In order to customize your profile, please use `/pride-profile configure`."
            )

    # TODO: rewrite this
    @app_commands.command(name="configure")
    async def configure(self, interaction: discord.Interaction) -> None:
        """Configure your pride profile"""
        view = ConfigureView(interaction, self.pool)
        embed = Embed(title="Configuring your pride profile")
        embed.description = "In order to configure your pride profile, select at one of the categories listed in the drop down."
        await interaction.response.send_message(embed=embed, view=view)
        view.original_response = await interaction.original_response()

    @app_commands.command(name="top")
    async def top(self, interaction: discord.Interaction) -> None:
        """Gets the top 100 most viewed profiles globally"""
        query = """
        SELECT id, name, views
        FROM pride_profiles
        ORDER BY views DESC
        LIMIT 100;
        """
        rows = await self.pool.fetch(query)
        if not rows:
            await interaction.response.send_message("No names were found.")
            return

        pages = IndexedPrideProfilePages(
            entries=[IndexedPrideProfile(**entry) for entry in rows],
            interaction=interaction,
            per_page=10,
        )
        await pages.start()

    @app_commands.command(name="search")
    @app_commands.describe(name="The preferred name to search")
    async def search(
        self,
        interaction: discord.Interaction,
        name: app_commands.Transform[str, ProfileName],
    ) -> None:
        """Searches for a pride profile using the given name"""

        query = """
        SELECT id, name, pronouns
        FROM pride_profiles
        WHERE name % $1
        ORDER BY similarity(name, $1) DESC
        LIMIT 100;
        """
        rows = await self.pool.fetch(query, name)
        if not rows:
            await interaction.response.send_message("No names were found.")
            return

        pages = IndexedPrideProfilePages(
            entries=[IndexedPrideProfile(**entry) for entry in rows],
            interaction=interaction,
            per_page=10,
        )
        await pages.start()

    @app_commands.command(name="delete")
    async def delete(self, interaction: discord.Interaction) -> None:
        """Permanently deletes your pride profile"""
        msg = "Are you sure you really want to delete your profile?"
        confirm = await prompt(interaction, msg, delete_after=True)

        if confirm:
            query = "DELETE FROM pride_profiles WHERE id = $1;"
            status = await self.pool.execute(query, interaction.user.id)
            if status[-1] == "0":
                await interaction.followup.send(
                    "Your pride profile doesn't exist. Please create one first.",
                    ephemeral=True,
                )
                return
            await interaction.followup.send(
                content="Successfully deleted your pride profile.", ephemeral=True
            )
        elif confirm is None:
            await interaction.followup.send(
                content="Not removing your pride profile. Cancelling.", ephemeral=True
            )
        else:
            await interaction.followup.send(content="Cancelling.", ephemeral=True)

    @search.error
    async def on_search_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await interaction.response.send_message(str(error))


async def setup(bot: Catherine) -> None:
    await bot.add_cog(PrideProfiles(bot))
