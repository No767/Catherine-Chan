from typing import Any, Dict, Optional

import discord
from discord.ext import menus
from langcodes import Language
from libs.utils.pages import CatherinePages

from .structs import PronounsProfileEntry
from .utils import determine_bold, parse_opinion, parse_words


class PronounsProfilePageSource(menus.PageSource):
    def __init__(self, locale: str):
        self.locale = locale

    def is_paginating(self) -> bool:
        return True

    def get_max_pages(self) -> Optional[int]:
        return 2

    async def get_page(self, page_number: int) -> Any:
        self.index = page_number
        return self

    async def format_page(self, menu, page):
        entry = menu.entries[self.locale]
        menu.embed.title = entry.username
        menu.embed.set_thumbnail(url=entry.avatar)
        menu.embed.set_footer(
            text="\U00002764 = Yes | \U0001f61b = Jokingly | \U0001f465 = Only if we're close | \U0001f44c = Okay | \U0001f6ab = Nope"
        )
        menu.embed.description = ""
        if self.index == 0:
            parsed_names = ", ".join(
                [
                    f"{determine_bold(value.value, value.opinion)} ({parse_opinion(value.opinion)})"
                    for value in entry.names
                ]
            )
            parsed_flags = ", ".join([flag for flag in entry.flags])
            parsed_pronouns = ", ".join(
                [
                    f"{determine_bold(value.value, value.opinion)} ({parse_opinion(value.opinion)})"
                    for value in entry.pronouns
                ]
            )
            parsed_relationships = (
                "\n".join(
                    [
                        f"{member.username} (Relationship: {member.relationship} | Mutual: {member.mutual})"
                        for member in entry.circle
                    ]
                )
                if entry.circle is not None
                else "None"
            )
            menu.embed.description += f"{entry.description}\n\n"
            menu.embed.description += (
                f"**Name(s)**: {parsed_names}\n**Pronouns**: {parsed_pronouns}\n"
            )
            menu.embed.description += f"**Flags**: {parsed_flags}\n**Age**: {entry.age or '.'}\n**Timezone**: {(entry.timezone or '.')}\n"
            menu.embed.description += f"**Relationships**:\n{parsed_relationships}\n"
        elif self.index == 1:
            parsed = parse_words(entry.words)
            menu.embed.description = parsed
        return menu.embed


class PronounsProfileLangMenu(discord.ui.Select["PronounsProfilePages"]):
    def __init__(self, entries: Dict[str, PronounsProfileEntry]):
        super().__init__(placeholder="Select a language")
        self.entries = entries
        self.__fill_options()

    def __fill_options(self):
        for entry in self.entries.keys():
            lang = Language.get(entry)
            lang_name = lang.display_name(entry)
            self.add_option(label=f"{lang_name}", value=entry)

    async def callback(self, interaction: discord.Interaction):
        if self.view is not None:
            value = self.values[0]
            if value == "en":
                await self.view.rebind(
                    PronounsProfilePageSource(locale="en"), interaction
                )
            else:
                await self.view.rebind(
                    PronounsProfilePageSource(locale=value), interaction
                )


class PronounsProfilePages(CatherinePages):
    def __init__(
        self,
        entries: Dict[str, PronounsProfileEntry],
        *,
        interaction: discord.Interaction,
        per_page: int = 1,
    ):
        self.entries = entries
        super().__init__(
            PronounsProfilePageSource(locale="en"),
            interaction=interaction,
            compact=True,
        )
        self.add_cats()

        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))

    def add_cats(self):
        self.clear_items()
        self.add_item(PronounsProfileLangMenu(self.entries))
        self.fill_items()

    async def rebind(
        self,
        source: menus.PageSource,
        interaction: discord.Interaction,
        to_page: int = 0,
    ) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)
