from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from libs.utils import Embed
from yarl import URL

if TYPE_CHECKING:
    from catherinecore import Catherine


class Fun(commands.Cog):
    """Fun commands!"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot

    @app_commands.command(name="ship")
    @app_commands.describe(
        first_user="The first user to ship", second_user="The second user to ship"
    )
    async def ship(
        self,
        interaction: discord.Interaction,
        first_user: discord.Member,
        second_user: discord.Member,
    ) -> None:
        """Ship two of your love dovey friends"""
        params = {
            "user1": first_user.display_avatar.url,
            "user2": second_user.display_avatar.url,
        }
        url = URL("https://api.popcat.xyz/ship") % params
        embed = Embed(title="Aww! We ship it!")
        embed.set_image(url=str(url))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="who-would-win")
    @app_commands.describe(user="The user to place your bets against")
    async def who_would_win(self, interaction: discord.Interaction, user: discord.Member) -> None:
        """Who would win template with friends!"""
        params = {
            "image1": interaction.user.display_avatar.url,
            "image2": user.display_avatar.url,
        }
        url = URL("https://api.popcat.xyz/whowouldwin") % params
        embed = Embed(title="Place your bets!!")
        embed.set_image(url=str(url))
        await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Fun(bot))
