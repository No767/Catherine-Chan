import sys
from pathlib import Path

from discord.ext import commands

path = Path(__file__).parents[3].joinpath("bot")
sys.path.append(str(path))


from libs.cog_utils.hrt.embeds import (
    EstrogenEmbed,
    ProgEmbed,
    ProlactinEmbed,
    TestosteroneEmbed,
)
from libs.cog_utils.pronouns import build_approve_embed
from libs.utils import (
    ConfirmEmbed,
    Embed,
    ErrorEmbed,
    SuccessEmbed,
    TimeoutEmbed,
)


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

    @commands.command(name="estrogenembed")
    async def estrogenembed(self, ctx):
        await ctx.send(embed=EstrogenEmbed())

    @commands.command(name="progestroneembed")
    async def progestroneembed(self, ctx):
        await ctx.send(embed=ProgEmbed())

    @commands.command(name="testosteroneembed")
    async def testosteroneembed(self, ctx):
        await ctx.send(embed=TestosteroneEmbed())

    @commands.command(name="prolactinembed")
    async def prolactinembed(self, ctx):
        await ctx.send(embed=ProlactinEmbed())

    @commands.command(name="timeoutembed")
    async def timeoutembed(self, ctx):
        await ctx.send(embed=TimeoutEmbed())

    @commands.command(name="approve")
    async def approve(self, ctx):
        e = build_approve_embed("Hey", "Hey", ctx.author)
        await ctx.send(embed=e)
