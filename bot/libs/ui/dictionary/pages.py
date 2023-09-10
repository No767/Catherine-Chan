from typing import List

import discord
from libs.utils.pages import CatherinePages, EmbedListSource

from .embed_entries import (
    DictInclusiveEmbedEntry,
    DictNounsEmbedEntry,
    DictPPEntry,
    DictTermsEmbedEntry,
)
from .structs import (
    DictInclusiveEntry,
    DictNounsEntry,
    DictPronounsPageEntry,
    DictTermsEntry,
)


class SimpleItemPages(CatherinePages):
    def __init__(self, entries, *, interaction: discord.Interaction, per_page: int = 1):
        super().__init__(
            EmbedListSource(entries, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.og_blurple())


class DictTermsPages(CatherinePages):
    def __init__(
        self,
        entries: List[DictTermsEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [DictTermsEmbedEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class DictInclusivePages(CatherinePages):
    def __init__(
        self,
        entries: List[DictInclusiveEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [DictInclusiveEmbedEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class DictNounsPages(CatherinePages):
    def __init__(
        self,
        entries: List[DictNounsEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [DictNounsEmbedEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class DictPPPages(SimpleItemPages):
    def __init__(
        self,
        entries: List[DictPronounsPageEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [DictPPEntry(entry).to_dict() for entry in entries]
        super().__init__(converted, per_page=per_page, interaction=interaction)
