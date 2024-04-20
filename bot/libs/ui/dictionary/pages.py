from typing import List

import discord
from libs.utils.pages import CatherinePages, EmbedListSource

from .embed_entries import (
    InclusiveEntityEntry,
    NounEntityEntry,
    PronounsEntityEntry,
    TermEntityEntry,
)
from .structs import InclusiveEntity, NounEntity, PronounsEntity, TermEntity


class TermsPages(CatherinePages):
    def __init__(
        self,
        entries: List[TermEntity],
        *,
        interaction: discord.Interaction,
        per_page: int = 1,
    ):
        converted = [TermEntityEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class InclusivePages(CatherinePages):
    def __init__(
        self,
        entries: List[InclusiveEntity],
        *,
        interaction: discord.Interaction,
        per_page: int = 1,
    ):
        converted = [InclusiveEntityEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class NounPages(CatherinePages):
    def __init__(
        self,
        entries: List[NounEntity],
        *,
        interaction: discord.Interaction,
        per_page: int = 1,
    ):
        converted = [NounEntityEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class PronounsPages(CatherinePages):
    def __init__(
        self,
        entries: List[PronounsEntity],
        *,
        interaction: discord.Interaction,
        per_page: int = 1,
    ):
        converted = [PronounsEntityEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))
