from typing import List

import discord
from libs.cog_utils.tonetags import ExactAndSimilarTonetags
from libs.utils.pages import CatherinePages, EmbedListSource, SimplePages

from .embed_entries import (
    BareToneTagPageEntry,
    ESTonetagsPageEntry,
    SimpleToneTagPageEntry,
    StatsBareToneTagPageEntry,
    ToneTagInfoPageEntry,
)
from .structs import BareToneTag, SimpleToneTag, StatsBareToneTag, ToneTagInfo


class ToneTagPages(CatherinePages):
    def __init__(
        self,
        entries: List[ToneTagInfo],
        *,
        interaction: discord.Interaction,
        per_page: int = 1,
    ):
        converted = [ToneTagInfoPageEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class ESToneTagsPages(CatherinePages):
    def __init__(
        self,
        entries: List[ExactAndSimilarTonetags],
        *,
        interaction: discord.Interaction,
    ):
        converted = [ESTonetagsPageEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=1), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class SimpleToneTagsPages(SimplePages):
    def __init__(
        self,
        entries: List[SimpleToneTag],
        *,
        interaction: discord.Interaction,
        per_page: int = 12,
    ):
        converted = [SimpleToneTagPageEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page, interaction=interaction)


class BareToneTagsPages(SimplePages):
    def __init__(
        self,
        entries: List[BareToneTag],
        *,
        interaction: discord.Interaction,
        per_page: int = 12,
    ):
        converted = [BareToneTagPageEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page, interaction=interaction)


class StatsBareToneTagsPages(SimplePages):
    def __init__(
        self,
        entries: List[StatsBareToneTag],
        *,
        interaction: discord.Interaction,
        per_page: int = 10,
    ):
        converted = [StatsBareToneTagPageEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page, interaction=interaction)
