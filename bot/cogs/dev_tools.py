from typing import Literal, Optional

import discord
from catherinecore import Catherine
from cogs import EXTENSIONS
from discord.ext import commands
from discord.ext.commands import Context, Greedy


class DevTools(commands.Cog, command_attrs=dict(hidden=True)):
    """Tools for developing Catherine-Chan (pulled from Kumiko directly)"""

    def __init__(self, bot: Catherine):
        self.bot = bot

    @commands.guild_only()
    @commands.is_owner()
    @commands.command(name="sync", hidden=True)
    async def sync(
        self,
        ctx: Context,
        guilds: Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """Performs a sync of the tree. This will sync, copy globally, or clear the tree.

        Args:
            ctx (Context): Context of the command
            guilds (Greedy[discord.Object]): Which guilds to sync to. Greedily accepts a number of guilds
            spec (Optional[Literal["~", "*", "^"], optional): Specs to sync.
        """
        await ctx.defer()
        if not guilds:
            if spec == "~":
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=ctx.guild)  # type: ignore
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await self.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await self.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.guild_only()
    @commands.is_owner()
    @commands.command(name="reload-all", hidden=True)
    async def reload_all(self, ctx: commands.Context) -> None:
        """Reloads all cogs. Used in production to not produce any downtime"""
        if not hasattr(self, "uptime"):
            await ctx.send(
                "Catherine-Chan needs to be fully loaded before anything can happen"
            )
            return

        for extension in EXTENSIONS:
            await self.bot.reload_extension(extension)
        await ctx.send("Successfully reloaded all extensions live")


async def setup(bot: Catherine):
    await bot.add_cog(DevTools(bot))
