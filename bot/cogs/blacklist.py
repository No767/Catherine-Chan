from typing import Any, AsyncIterator, TypeVar, Union

import discord
from catherinecore import Catherine
from discord.ext import commands, menus
from libs.utils.pages.context_paginator import CatherineContextPages

_T = TypeVar("_T")


class BlacklistPageSource(menus.AsyncIteratorPageSource):
    def __init__(self, entries: dict[str, Union[_T, Any]]):
        super().__init__(self.blacklist_iterator(entries), per_page=20)

    async def blacklist_iterator(
        self, entries: dict[str, Union[_T, Any]]
    ) -> AsyncIterator[str]:
        for key, entry in entries.items():
            yield f"{key}: {entry}"

    async def format_page(self, menu, entries: list[str]) -> discord.Embed:
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(f"{index + 1}. {entry}")

        menu.embed.description = "\n".join(pages)
        return menu.embed


class BlacklistPages(CatherineContextPages):
    def __init__(self, entries: dict[str, Union[_T, Any]], *, ctx: commands.Context):
        super().__init__(BlacklistPageSource(entries), ctx=ctx, compact=True)
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(200, 168, 255))


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
        entries = self.bot.blacklist.all()
        if len(entries) == 0:
            await ctx.send("No blacklist entries found")
            return

        pages = BlacklistPages(entries, ctx=ctx)
        await pages.start()

    @blacklist.command(name="add")
    async def add(self, ctx: commands.Context, id: discord.Object):
        """Adds an ID to the global blacklist"""
        given_id = id.id
        await self.bot.add_to_blacklist(given_id)
        self.bot.metrics.blacklist.users.inc()
        await ctx.send(f"Done. Added ID {given_id} to the blacklist")

    @blacklist.command(name="remove")
    async def remove(self, ctx: commands.Context, id: discord.Object):
        """Removes an ID from the global blacklist"""
        given_id = id.id
        await self.bot.remove_from_blacklist(given_id)
        self.bot.metrics.blacklist.users.dec()
        await ctx.send(f"Done. Removed ID {given_id} from the blacklist")


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Blacklist(bot))
