from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Optional

import discord
import msgspec
import orjson
from discord import app_commands
from discord.ext import commands, menus
from libs.ui.dictionary.pages import (
    InclusivePages,
    NounPages,
    PronounsPages,
)
from libs.ui.dictionary.structs import (
    InclusiveContent,
    InclusiveEntity,
    NounContent,
    NounEntity,
    PronounsEntity,
    PronounsMorphemes,
)
from libs.ui.dictionary.utils import format_pronouns_info
from libs.utils import Embed
from libs.utils.pages import CatherinePages
from yarl import URL

if TYPE_CHECKING:
    from catherinecore import Catherine


class TermInfo(msgspec.Struct, frozen=True):
    term: str
    original: str
    definition: str
    locale: str
    author: str
    category: str


class TermSource(menus.ListPageSource):
    def __init__(self, entries: list[dict[str, Any]], *, bot: Catherine, per_page: int = 1):
        super().__init__(entries=entries, per_page=per_page)
        self.cog: Dictionary = bot.get_cog("dictionary")  # type: ignore

    def determine_author(self, author: Optional[str]) -> str:
        author_base_url = URL("https://pronouns.page/")
        if author is None:
            return "Unknown"
        author_link = str(author_base_url / f"@{author}")
        return f"[{author}]({author_link})"

    def format_info(self, entry: dict[str, Any]) -> TermInfo:
        return TermInfo(
            term=", ".join(entry["term"].split("|")),
            original=self.cog.format_references(entry["original"]),
            definition=self.cog.format_references(entry["definition"]),
            locale=entry["locale"],
            author=self.determine_author(entry["author"]),
            category=", ".join(entry["category"].split(",")),
        )

    async def format_page(self, menu: "TermsPages", entries: dict[str, Any]) -> Embed:
        menu.embed.clear_fields()
        entry = self.format_info(entries)

        menu.embed.title = entry.term
        menu.embed.set_thumbnail(url=self.cog.determine_image_url(entries))
        menu.embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")

        menu.embed.description = f"{entry.original}\n\n{entry.definition}"

        # We need to swap the name value for what is in it's native locale
        menu.embed.add_field(name="Author", value=entry.author)
        menu.embed.add_field(name="Category", value=entry.category)

        return menu.embed


class TermsPages(CatherinePages):
    def __init__(self, entries: list[dict[str, Any]], *, interaction: discord.Interaction):
        self.bot: Catherine = interaction.client  # type: ignore
        self.entries = entries
        super().__init__(
            source=TermSource(entries, bot=self.bot, per_page=1),
            interaction=interaction,
            compact=False,
        )
        self.embed = Embed()


class Dictionary(commands.GroupCog, name="dictionary"):
    """The to-go LGBTQ+ dictionary"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.decoder = msgspec.json.Decoder()
        self.session = self.bot.session
        self.base_cdn = URL("https://dclu0bpcdglik.cloudfront.net/images/")
        self.base_flags = URL("https://en.pronouns.page/flags/")
        self.link_regex = re.compile(r"^(http|https)://")
        self.lang_term_codes = {
            "de": "terminologie",
            "es": "terminologia",
            "en": "terminology",
            "et": "terminoloogia",
            "fr": "terminologie",
            "it": "terminologia",
            "lad": "terminolojia",
            "nl": "erminologie",
            "no": "terminology",
            "pl": "terminologia",
            "pt": "terminologia",
            "ro": "terminologie",
            "sv": "terminologi",
            "tr": "terminoloji",
            "vi": "thuật-ngữ",
            "ar": "المصطلحات",
            "ru": "terminology",
            "ua": "terminology",
            "ja": "用語",
        }

    def split_flags(self, content: str) -> list[str]:
        regex = re.compile(r"(?<=\[).*(?=\])")
        return regex.findall(content)

    ### Term utilities

    def determine_image_url(self, entry: dict[str, Any]) -> str:
        flags = self.split_flags(entry["flags"])
        if len(flags[0]) != 0:
            flag_entity = flags[0].replace('"', "")
            return str(self.base_flags / f"{flag_entity}.png")
        elif entry["images"] and "[object Object]" not in entry["images"]:
            asset = entry["images"].split(",")
            return str(
                self.base_cdn / f"{asset[0]}-flag.png"
            )  # For general use, we'll just use the first flag shown
        return ""

    def format_inline_term_reference(self, content: str, entities: list[str], locale: str = "en"):
        if len(entities) == 0:
            return content

        url = URL.build(
            scheme="https", host=f"{locale}.pronouns.page", path=f"/{self.lang_term_codes[locale]}"
        )
        replacements = {}
        cleaned_content = re.sub(r"\{|\}", "", content)

        # The order of formatting goes like this:
        # 1. Hashtag term references
        # 2. Link references
        # 3. Pronouns references
        # 4. Anything that is automatically assumed to be english terms
        for entity in entities:
            if entity.startswith("#"):
                parts = entity[1:].partition("=")
                replacements.update(
                    {entity: f"[{parts[-1]}]({url.with_query({"filter": parts[0]})})"}
                )
            elif self.link_regex.match(entity):
                # Special case here
                if "perseus.tufts.edu" in entity:
                    keyword = entity.split("=")[-1]
                    keyword_length = len(keyword) + 1
                    reference_url = URL(entity[:-keyword_length])
                    replacements.update(
                        {
                            entity: f"[{keyword}]({reference_url.with_query({"doc": reference_url.query["doc"].replace(")", "%29").replace("(", "%28")})})"
                        }
                    )
                    continue

                link_parts = entity.partition("=")
                replacements.update({entity: f"[{link_parts[-1]}]({link_parts[0]})"})
            elif entity.startswith("/"):
                # For other languages, this is the slash for the path that would be used
                # Since we are only using english for now, this doesn't matter
                pronouns_parts = entity[1].partition("=")
                pronouns_url = URL.build(
                    scheme="https", host=f"{locale}.pronouns.page", path=f"/{pronouns_parts[0]}"
                )
                replacements.update({entity: f"[{pronouns_parts[-1]}]({pronouns_url})"})
            else:
                replacements.update({entity: f"[{entity}]({url.with_query({"filter": entity})})"})

        fmt_regex = re.compile(r"(%s)" % "|".join(map(re.escape, replacements.keys())))
        return fmt_regex.sub(lambda mo: replacements[mo.group()], cleaned_content)

    def extract_reference(self, content: str) -> list[str]:
        return re.findall(r"{(.*?)}", content)

    def format_references(self, content: str) -> str:
        return self.format_inline_term_reference(content, self.extract_reference(content))


    @app_commands.command(name="terms")
    @app_commands.describe(query="The term to look for")
    async def terms(self, interaction: discord.Interaction, query: Optional[str] = None) -> None:
        """Looks up LGBTQ+ terms up"""
        await interaction.response.defer()
        url = URL("https://en.pronouns.page/api/terms")
        if query:
            url = url / "search" / query
        async with self.session.get(url) as r:
            data = await r.json(loads=self.decoder.decode)
            if len(data) == 0:
                await interaction.followup.send("No terms were found")
                return
            pages = TermsPages(data, interaction=interaction)
            await pages.start()

    @app_commands.command(name="nouns")
    @app_commands.describe(query="The noun to look for")
    async def nouns(self, interaction: discord.Interaction, query: Optional[str] = None) -> None:
        """Looks up gender neutral nouns and language"""
        await interaction.response.defer()
        url = URL("https://en.pronouns.page/api/nouns")
        if query:
            url = url / "search" / query
        async with self.session.get(url) as r:
            # If people start using this for pronouns, then a generator shows up
            # so that's in case this happens
            if r.content_type == "text/html":
                await interaction.followup.send("Uhhhhhhhhhhhh what mate")
                return
            data = await r.json(loads=orjson.loads)
            if len(data) == 0:
                await interaction.followup.send("No nouns were found")
                return
            converted = [
                NounEntity(
                    masc=NounContent(regular=entry["masc"], plural=entry["mascPl"]),
                    fem=NounContent(regular=entry["fem"], plural=entry["femPl"]),
                    neutral=NounContent(regular=entry["neutr"], plural=entry["neutrPl"]),
                    author=entry["author"],
                )
                for entry in data
            ]
            pages = NounPages(entries=converted, interaction=interaction)
            await pages.start()

    @app_commands.command(name="inclusive")
    @app_commands.describe(term="The inclusive term to look for")
    async def inclusive(self, interaction: discord.Interaction, term: Optional[str] = None) -> None:
        """Provides inclusive terms for users to learn about"""
        await interaction.response.defer()
        url = URL("https://en.pronouns.page/api/inclusive")
        if term:
            url = url / "search" / term
        async with self.session.get(url) as r:
            data = await r.json(loads=orjson.loads)
            if len(data) == 0:
                await interaction.followup.send("No inclusive terms were found")
                return
            converted = [
                InclusiveEntity(
                    content=InclusiveContent(
                        instead_of=entry["insteadOf"],
                        say=entry["say"],
                        because=entry["because"],
                        clarification=entry["clarification"],
                    ),
                    author=entry["author"],
                )
                for entry in data
            ]
            pages = InclusivePages(entries=converted, interaction=interaction)
            await pages.start()

    @app_commands.command(name="lookup")
    @app_commands.describe(
        pronouns="The pronouns to look up. Examples include she/her, etc. Defaults to all pronouns."
    )
    async def lookup(
        self, interaction: discord.Interaction, pronouns: Optional[str] = None
    ) -> None:
        """Lookup info about the given pronouns

        Pronouns include she/her, they/them and many others. Singular pronouns (eg 'she') also work.
        """
        await interaction.response.defer()
        url = URL("https://en.pronouns.page/api/pronouns/")
        if pronouns:
            url = url / pronouns
        async with self.session.get(url) as r:
            data = await r.json(loads=orjson.loads)
            if data is None:
                await interaction.followup.send("The pronouns requested were not found")
                return

            if pronouns is not None:
                pronouns_entry = PronounsEntity(
                    name=data["name"],
                    canonical_name=data["canonicalName"],
                    description=data["description"],
                    aliases=data["aliases"],
                    normative=data["normative"],
                    morphemes=PronounsMorphemes(
                        pronoun_subject=data["morphemes"]["pronoun_subject"],
                        pronoun_object=data["morphemes"]["pronoun_object"],
                        possessive_determiner=data["morphemes"]["possessive_determiner"],
                        possessive_pronoun=data["morphemes"]["possessive_pronoun"],
                        reflexive=data["morphemes"]["reflexive"],
                    ),
                    examples=data["examples"],
                    history=data["history"],
                    sources_info=data["sourcesInfo"],
                )

                pronouns_info = format_pronouns_info(pronouns_entry)
                embed = Embed()
                embed.title = pronouns_info["title"]
                embed.description = pronouns_info["desc"]
                embed.add_field(name="Aliases", value=", ".join(pronouns_entry.aliases).rstrip(","))
                embed.add_field(name="Normative", value=pronouns_entry.normative)
                await interaction.followup.send(embed=embed)
            else:
                converted = [
                    PronounsEntity(
                        name=entry["canonicalName"],
                        canonical_name=entry["canonicalName"],
                        description=entry["description"],
                        aliases=entry["aliases"],
                        normative=entry["normative"],
                        morphemes=PronounsMorphemes(
                            pronoun_subject=entry["morphemes"]["pronoun_subject"],
                            pronoun_object=entry["morphemes"]["pronoun_object"],
                            possessive_determiner=entry["morphemes"]["possessive_determiner"],
                            possessive_pronoun=entry["morphemes"]["possessive_pronoun"],
                            reflexive=entry["morphemes"]["reflexive"],
                        ),
                        examples=entry["examples"],
                        history=entry["history"],
                        sources_info=entry["sourcesInfo"],
                    )
                    for entry in data.values()
                ]
                pages = PronounsPages(entries=converted, interaction=interaction)
                await pages.start()


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Dictionary(bot))
