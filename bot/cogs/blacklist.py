import discord
from catherinecore import Catherine
from discord.ext import commands
from libs.ui.blacklist import BlacklistPages
from libs.utils import get_blacklist


class Blacklist(commands.Cog, command_attrs=dict(hidden=True)):
    """Global blacklist management cog"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.pool = self.bot.pool

    @commands.group(name="blacklist", invoke_without_command=True)
    @commands.is_owner()
    @commands.guild_only()
    async def blacklist(self, ctx: commands.Context) -> None:
        """Global blacklisting system - Without subcommand you are viewing the blacklist"""
        query = """
        SELECT id, blacklist_status
        FROM blacklist;
        """

        records = await self.pool.fetch(query)
        if len(records) == 0:
            await ctx.send("No blacklist entries found")
            return

        cache_to_list = [
            {record["id"]: record["blacklist_status"]} for record in records
        ]

        pages = BlacklistPages(entries=cache_to_list, ctx=ctx)
        await pages.start()

    @blacklist.command(name="add")
    async def add(self, ctx: commands.Context, id: discord.Object):
        """Adds an ID to the global blacklist"""
        given_id = id.id
        query = """
        INSERT INTO blacklist (id, blacklist_status)
        VALUES ($1, $2) ON CONFLICT (id) DO NOTHING;
        """
        await self.pool.execute(query, given_id, True)
        get_blacklist.cache_invalidate(given_id, self.pool)
        self.bot.metrics.blacklisted_users.inc()
        await ctx.send(f"Done. Added ID {given_id} to the blacklist")

    @blacklist.command(name="remove")
    async def remove(self, ctx: commands.Context, id: discord.Object):
        """Removes an ID from the global blacklist"""
        given_id = id.id
        query = """
        DELETE FROM blacklist
        WHERE id = $1;
        """
        await self.pool.execute(query, given_id)
        get_blacklist.cache_invalidate(given_id, self.pool)
        self.bot.metrics.blacklisted_users.dec()
        await ctx.send(f"Done. Removed ID {given_id} from the blacklist")


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Blacklist(bot))
