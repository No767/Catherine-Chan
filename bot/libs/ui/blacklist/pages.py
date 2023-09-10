from typing import Dict, List

import discord
from libs.utils.pages import CatherinePages, SimplePageSource

from .page_entries import BlacklistPageEntry


class BaseBlacklistPages(CatherinePages):
    def __init__(
        self, entries, *, interaction: discord.Interaction, per_page: int = 10
    ):
        super().__init__(
            SimplePageSource(entries, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(
            title="Blacklist List", colour=discord.Colour.from_rgb(255, 176, 241)
        )


class BlacklistPages(BaseBlacklistPages):
    def __init__(
        self,
        entries: List[Dict[int, bool]],
        *,
        interaction: discord.Interaction,
        per_page: int = 10
    ):
        converted = [BlacklistPageEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page, interaction=interaction)
