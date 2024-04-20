from typing import List

import discord
from libs.utils.pages import CatherinePages, SimplePageSource

from .structs import SimpleProfileEntry, SimpleViewsEntry
from .utils import SimpleProfilesPageEntry, ViewsProfilePageEntry


class ProfileSearchPages(CatherinePages):
    def __init__(
        self,
        entries: List[SimpleProfileEntry],
        *,
        interaction: discord.Interaction,
        per_page=1,
    ):
        converted = [SimpleProfilesPageEntry(entry) for entry in entries]
        super().__init__(
            SimplePageSource(converted, per_page=per_page),
            interaction=interaction,
            compact=True,
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(217, 156, 255))


class ProfileStatsPages(CatherinePages):
    def __init__(
        self,
        entries: List[SimpleViewsEntry],
        *,
        interaction: discord.Interaction,
        per_page=1,
    ):
        converted = [ViewsProfilePageEntry(entry) for entry in entries]
        super().__init__(
            SimplePageSource(converted, per_page=per_page),
            interaction=interaction,
            compact=True,
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(217, 156, 255))
