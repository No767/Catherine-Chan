import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.blacklist import is_owner
from libs.ui.blacklist import BlacklistPages
from libs.utils import get_or_fetch_full_blacklist

ID_DESCRIPTION = "User or Guild ID to add"
HANGOUT_GUILD_ID = discord.Object(id=1145897416160194590)


class Blacklist(commands.GroupCog, name="blacklist"):
    """Global blacklist management cog"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.pool = self.bot.pool
        self.id_description = "User or Guild ID to add"
        self.done_msg = "Done."
        super().__init__()

    @is_owner()
    @app_commands.guild_only()
    @app_commands.command(name="view")
    @app_commands.guilds(HANGOUT_GUILD_ID)
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
    @app_commands.guild_only()
    @app_commands.command(name="add")
    @app_commands.guilds(HANGOUT_GUILD_ID)
    @app_commands.describe(id=ID_DESCRIPTION)
    async def add(self, interaction: discord.Interaction, id: str):
        """Add to global blacklist"""
        d_obj = discord.Object(id=int(id))
        query = """
        INSERT INTO blacklist (id, blacklist_status)
        VALUES ($1, $2) ON CONFLICT (id) DO NOTHING;
        """
        await self.pool.execute(query, d_obj.id, True)
        if d_obj.id not in self.bot.blacklist_cache:
            self.bot.add_to_blacklist_cache(d_obj.id)
        await interaction.response.send_message(self.done_msg, ephemeral=True)

    @is_owner()
    @app_commands.guild_only()
    @app_commands.command(name="remove")
    @app_commands.guilds(HANGOUT_GUILD_ID)
    @app_commands.describe(id=ID_DESCRIPTION)
    async def remove(self, interaction: discord.Interaction, id: str):
        """Remove from global blacklist"""
        di_obj = discord.Object(id=int(id))
        query = """
        DELETE FROM blacklist
        WHERE id = $1;
        """
        await self.pool.execute(query, di_obj.id)
        if di_obj.id in self.bot.blacklist_cache:
            self.bot.remove_from_blacklist_cache(di_obj.id)

        await interaction.response.send_message(self.done_msg, ephemeral=True)

    @is_owner()
    @app_commands.guild_only()
    @app_commands.command(name="status")
    @app_commands.guilds(HANGOUT_GUILD_ID)
    @app_commands.describe(id=ID_DESCRIPTION, status="New status")
    async def status(self, interaction: discord.Interaction, id: int, status: bool):
        """Update from global blacklist"""
        dis_obj = discord.Object(id=int(id))
        query = """
        UPDATE blacklist
        SET status = $2
        WHERE id = $1;
        """
        await self.pool.execute(query, dis_obj.id, status)
        if id in self.bot.blacklist_cache:
            self.bot.update_blacklist_cache(dis_obj.id, status)

        await interaction.response.send_message(self.done_msg, ephemeral=True)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Blacklist(bot))
