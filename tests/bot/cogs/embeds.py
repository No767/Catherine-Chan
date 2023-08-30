import sys
from pathlib import Path

from discord.ext import commands

path = Path(__file__).parents[3].joinpath("bot")
sys.path.append(str(path))


from libs.cog_utils.pronouns import build_approve_embed
from libs.utils import ConfirmEmbed, Embed, ErrorEmbed, SuccessEmbed


class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="e")
    async def e(self, ctx):
        await ctx.send(embed=Embed())

    @commands.command(name="ce")
    async def ce(self, ctx):
        await ctx.send(embed=ConfirmEmbed())

    @commands.command(name="se")
    async def se(self, ctx):
        await ctx.send(embed=SuccessEmbed())

    @commands.command(name="ee")
    async def ee(self, ctx):
        await ctx.send(embed=ErrorEmbed())

    @commands.command(name="approve")
    async def approve(self, ctx):
        e = build_approve_embed("Hey", "Hey", ctx.author)
        await ctx.send(embed=e)
