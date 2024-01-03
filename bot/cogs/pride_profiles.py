import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.commons import register_user
from libs.cog_utils.pride_profiles import present_info
from libs.ui.pride_profiles import (
    ConfigureView,
    ProfileSearchPages,
    ProfileStatsPages,
)
from libs.utils.embeds import (
    ConfirmEmbed,
    Embed,
    ErrorEmbed,
    SuccessEmbed,
    TimeoutEmbed,
)
from libs.utils.prompt import interaction_prompt


class PrideProfiles(commands.GroupCog, name="pride-profiles"):
    """Create pride profiles to let others know who you are!"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        super().__init__()

    @app_commands.command(name="view")
    @app_commands.describe(user="The user to look for")
    async def view(self, interaction: discord.Interaction, user: discord.User) -> None:
        """Look at a pride profile"""
        if user.bot:
            await interaction.response.send_message(
                "You know that I am transgender, lesbian and go by she/her pronouns right?"
            )
            return

        query = """
        SELECT user_id, views, name, pronouns, gender_identity, sexual_orientation, romantic_orientation 
        FROM profiles
        WHERE user_id = $1;
        """
        update_views_count = """
        UPDATE profiles
        SET views = views + 1
        WHERE user_id = $1;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetchrow(query, user.id)
            if rows is None:
                await interaction.response.send_message(
                    "You or the user has no profile. Run `/pride-profiles register` in order to do so"
                )
                return

            await conn.execute(update_views_count, user.id)
            records = dict(rows)
            embed = Embed(title=f"{user.global_name}'s Profile")
            embed.description = present_info(records)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="User", value=f"<@{records['user_id']}>")
            embed.add_field(name="Views", value=records["views"])
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="register")
    async def register(self, interaction: discord.Interaction) -> None:
        """Register a pride profile"""
        query = """
        INSERT INTO profiles (user_id, name)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO NOTHING;
        """

        embed = ConfirmEmbed()
        embed.description = "Are you sure you want to register for a pride profile? It's very exciting and fun"

        confirm = await interaction_prompt(embed, interaction, ephemeral=True)
        if confirm.value:
            async with self.pool.acquire() as conn:
                await register_user(interaction.user.id, conn)
                status = await conn.execute(
                    query, interaction.user.id, interaction.user.global_name
                )

                embed = SuccessEmbed(description="Registered your pride profile!")

                if status[-1] == "0":
                    embed = ErrorEmbed(
                        title="Already registered",
                        description="You already have a pride profile registered!",
                    )

                await confirm.original_response.edit(embed=embed, view=None)
        elif confirm.value is None:
            embed = TimeoutEmbed()
            await confirm.original_response.edit(embed=embed, view=None)
        else:
            embed = ErrorEmbed(title="Cancelling", description="Cancelling action")
            await confirm.original_response.edit(embed=embed, view=None)

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
        embed = ConfirmEmbed()
        embed.description = "Are you sure you really want to delete your profile?"
        confirm = await interaction_prompt(embed, interaction, ephemeral=True)
        if confirm.value:
            query = """
            DELETE FROM profiles
            WHERE user_id = $1;
            """
            status = await self.pool.execute(query, interaction.user.id)

            embed = SuccessEmbed(description="Successfully deleted your pride profile")

            if status[-1] == "0":
                embed = ErrorEmbed(
                    title="Doesn't exist",
                    description="The pride profile that you are trying to delete doesn't exist",
                )
            await confirm.original_response.edit(embed=embed, view=None)
        elif confirm.value is None:
            embed = TimeoutEmbed()
            await confirm.original_response.edit(embed=embed)
        else:
            embed = ErrorEmbed(title="Cancelling", description="Cancelling action")
            await confirm.original_response.edit(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(PrideProfiles(bot))
