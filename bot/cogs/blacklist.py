import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.blacklist import is_owner
from libs.ui.blacklist import BlacklistPages
from libs.utils import get_or_fetch_full_blacklist

HANGOUT_GUILD_ID = 1145897416160194590
ID_DESCRIPTION = "User or Guild ID to add"
DONE_MSG = "Done."


class Blacklist(commands.Cog):
    """Global blacklist management cog"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.pool = self.bot.pool

    blacklist = app_commands.Group(
        name="blacklist",
        description="Blacklisting module",
        guild_ids=[HANGOUT_GUILD_ID],
    )

    @is_owner()
    @blacklist.command(name="view")
    async def view(self, interaction: discord.Interaction):
        """View the global blacklist"""
        blacklist = await get_or_fetch_full_blacklist(interaction.client, self.pool)
        if blacklist is None:
            await interaction.response.send_message("No blacklist entries found")
            return

        cache_to_list = [{k: v} for k, v in blacklist.items()]

        pages = BlacklistPages(entries=cache_to_list, interaction=interaction)
        await pages.start()

    @is_owner()
    @blacklist.command(name="add")
    @app_commands.describe(id=ID_DESCRIPTION)
    async def add(self, interaction: discord.Interaction, id: str):
        """Adds an ID to the global blacklist"""
        obj = discord.Object(id=int(id))
        query = """
        INSERT INTO blacklist (id, blacklist_status)
        VALUES ($1, $2) ON CONFLICT (id) DO NOTHING;
        """
        await self.pool.execute(query, obj.id, True)
        if obj.id not in self.bot.blacklist_cache:
            self.bot.add_to_blacklist_cache(obj.id)
        await interaction.response.send_message(DONE_MSG, ephemeral=True)

    @is_owner()
    @blacklist.command(name="remove")
    @app_commands.describe(id=ID_DESCRIPTION)
    async def remove(self, interaction: discord.Interaction, id: str):
        """Removes an ID from the global blacklist"""
        obj = discord.Object(id=int(id))
        query = """
        DELETE FROM blacklist
        WHERE id = $1;
        """
        await self.pool.execute(query, obj.id)
        if obj.id in self.bot.blacklist_cache:
            self.bot.remove_from_blacklist_cache(obj.id)

        await interaction.response.send_message(DONE_MSG, ephemeral=True)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Blacklist(bot))
