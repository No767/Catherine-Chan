import discord
from catherinecore import Catherine
from discord.ext import commands
from libs.ui.blacklist import BlacklistPages
from libs.utils import get_or_fetch_full_blacklist

DONE_MSG = "Done."


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
        blacklist = await get_or_fetch_full_blacklist(self.bot, self.pool)
        if blacklist is None:
            await ctx.send("No blacklist entries found")
            return

        cache_to_list = [{k: v} for k, v in blacklist.items()]

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
        if id not in self.bot.blacklist_cache:
            self.bot.add_to_blacklist_cache(given_id)
            self.bot.metrics.blacklisted_users.inc()
        await ctx.send(DONE_MSG)

    @blacklist.command(name="remove")
    async def remove(self, ctx: commands.Context, id: discord.Object):
        """Removes an ID from the global blacklist"""
        given_id = id.id
        query = """
        DELETE FROM blacklist
        WHERE id = $1;
        """
        await self.pool.execute(query, given_id)
        if given_id in self.bot.blacklist_cache:
            self.bot.remove_from_blacklist_cache(given_id)
            self.bot.metrics.blacklisted_users.dec()
        await ctx.send(DONE_MSG)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Blacklist(bot))
