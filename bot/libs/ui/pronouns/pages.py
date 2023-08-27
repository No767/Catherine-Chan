from typing import List, Optional, TypedDict, Union

import discord
from libs.utils.pages import CatherinePages, EmbedListSource

from .embed_entries import (
    PronounsInclusiveEmbedEntry,
    PronounsNounsEmbedEntry,
    PronounsTermsEmbedEntry,
)
from .structs import PronounsInclusiveEntry, PronounsNounsEntry, PronounsTermsEntry


class PronounsTermsPages(CatherinePages):
    def __init__(
        self,
        entries: List[PronounsTermsEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [PronounsTermsEmbedEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class PronounsInclusivePages(CatherinePages):
    def __init__(
        self,
        entries: List[PronounsInclusiveEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [PronounsInclusiveEmbedEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class PronounsNounsPages(CatherinePages):
    def __init__(
        self,
        entries: List[PronounsNounsEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [PronounsNounsEmbedEntry(entry).to_dict() for entry in entries]
        super().__init__(
            EmbedListSource(converted, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))


class SimpleItemPages(CatherinePages):
    def __init__(self, entries, *, interaction: discord.Interaction, per_page: int = 1):
        super().__init__(
            EmbedListSource(entries, per_page=per_page), interaction=interaction
        )
        self.embed = discord.Embed(colour=discord.Colour.og_blurple())


class PronounsPageLaDiffEntry(TypedDict):
    term: str
    original: Union[str, None]
    definition: str
    locale: str
    approved: int
    base_id: Optional[str]
    author_id: str
    deleted: int
    flags: List[str]
    category: str
    key: str
    author: str


class PronounsPageEntry(TypedDict):
    term: str
    original: Union[str, None]
    definition: str
    locale: str
    approved: int
    base_id: Optional[str]
    author_id: str
    deleted: int
    flags: List[str]
    category: str
    key: str
    author: str
    versions: List[PronounsPageLaDiffEntry]


class PPEntry:
    def __init__(self, entry: PronounsPageEntry):
        self.dict_entry = entry

    def to_dict(self):
        data = {
            "title": self.dict_entry["term"],
            "description": self.dict_entry["definition"],
            "fields": [
                {
                    "name": "Original",
                    "value": self.dict_entry["original"],
                    "inline": True,
                },
                {"name": "Locale", "value": self.dict_entry["locale"], "inline": True},
                {
                    "name": "Category",
                    "value": self.dict_entry["category"],
                    "inline": True,
                },
            ],
        }
        return data


class PPPages(SimpleItemPages):
    def __init__(
        self,
        entries: List[PronounsPageEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1
    ):
        converted = [PPEntry(entry).to_dict() for entry in entries]
        super().__init__(converted, per_page=per_page, interaction=interaction)
