import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.commons import register_user
from libs.cog_utils.pride_profiles.utils import present_info
from libs.ui.pride_profiles.pages import ProfileSearchPages, ProfileStatsPages
from libs.ui.pride_profiles.views import ConfigureView
from libs.utils.embeds import Embed
from libs.utils.view import prompt


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

    @app_commands.command(name="view")
    @app_commands.describe(name="The user's global or preferred name")
    async def view(self, interaction: discord.Interaction, name: str) -> None:
        """Look at a pride profile"""
        query = """
        SELECT user_id, views, name, pronouns, gender_identity, sexual_orientation, romantic_orientation 
        FROM profiles
        WHERE name = $1;
        """
        update_views_count = """
        UPDATE profiles
        SET views = views + 1
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

        await self.pool.execute(update_views_count, name)
        records = dict(rows)

        user = self.bot.get_user(records["user_id"]) or (
            await self.bot.fetch_user(records["user_id"])
        )

        embed = Embed(title=f"{name}'s Profile")
        embed.description = present_info(records)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Views", value=records["views"])
        embed.set_footer(text=f"User ID: {records['user_id']}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="register")
    async def register(self, interaction: discord.Interaction) -> None:
        """Register a pride profile"""
        query = """
        INSERT INTO profiles (user_id, name)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO NOTHING;
        """
        async with self.pool.acquire() as conn:
            await register_user(interaction.user.id, conn)
            status = await conn.execute(
                query, interaction.user.id, interaction.user.global_name
            )

            if status[-1] == "0":
                msg = "Sorry, but you already have an active profile!"
                await interaction.response.send_message(msg)
                return

            register_msg = "Registered your pride profile! In order to customize your profile, please use `/pride-profile configure`."
            await interaction.response.send_message(content=register_msg)

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
        SELECT user_id, name, views
        FROM profiles
        ORDER BY views DESC
        LIMIT 100;
        """
        rows = await self.pool.fetch(query)
        if rows:
            pages = ProfileStatsPages(
                entries=rows, interaction=interaction, per_page=10
            )
            await pages.start()
        else:
            await interaction.response.send_message("No names were found.")

    @app_commands.command(name="search")
    @app_commands.describe(name="The preferred name to search")
    async def search(self, interaction: discord.Interaction, name: str) -> None:
        """Searches for a pride profile using the given name"""

        query = """
        SELECT user_id, name, pronouns
        FROM profiles
        WHERE name % $1
        ORDER BY similarity(name, $1) DESC
        LIMIT 100;
        """
        rows = await self.pool.fetch(query, name)
        if rows:
            pages = ProfileSearchPages(
                entries=rows, interaction=interaction, per_page=10
            )
            await pages.start()
        else:
            await interaction.response.send_message("No names were found.")

    @app_commands.command(name="delete")
    async def delete(self, interaction: discord.Interaction) -> None:
        """Permanently deletes your pride profile"""
        msg = "Are you sure you really want to delete your profile?"
        confirm = await prompt(interaction, msg, delete_after=True)

        if confirm:
            query = "DELETE FROM profiles WHERE user_id = $1;"
            status = await self.pool.execute(query, interaction.user.id)
            if status[-1] == "0":
                await interaction.followup.send(
                    "Your pride profile doesn't exist. Please create one first.",
                    ephemeral=True,
                )
                return
            await interaction.followup.send(content="hi this works", ephemeral=True)
        elif confirm is None:
            await interaction.followup.send(
                content="Not removing your pride profile. Cancelling.", ephemeral=True
            )
        else:
            await interaction.followup.send(content="Cancelling.", ephemeral=True)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(PrideProfiles(bot))
