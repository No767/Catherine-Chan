from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Optional

import aiohttp
import discord
import msgspec
from discord import app_commands
from discord.ext import commands, menus
from libs.utils import Embed
from libs.utils.pages import CatherinePages
from yarl import URL

if TYPE_CHECKING:
    from catherinecore import Catherine

BASE_URL = URL("https://pronouns.page/")
CDN_FLAGS_URL = URL("https://dclu0bpcdglik.cloudfront.net/images/")
PRONOUNS_FLAGS_URL = URL("https://en.pronouns.page/flags/")

### Structs


class TermInfo(msgspec.Struct, frozen=True):
    term: str
    original: str
    definition: str
    locale: str
    author: str
    category: str


class NounEntity(msgspec.Struct, frozen=True):
    regular: str
    plural: str


class NounInfo(msgspec.Struct, frozen=True):
    masc: str
    fem: str
    neutral: str
    author: str


class InclusiveInfo(msgspec.Struct, frozen=True):
    instead_of: str
    say: str
    because: str
    clarification: Optional[str]
    author: str


### UI components (Page Sources, Pages)
class TermSource(menus.ListPageSource):
    def __init__(
        self, entries: list[dict[str, Any]], *, bot: Catherine, per_page: int = 1
    ):
        super().__init__(entries=entries, per_page=per_page)
        self.cog: Dictionary = bot.get_cog("dictionary")  # type: ignore

    def format_info(self, entry: dict[str, Any]) -> TermInfo:
        return TermInfo(
            term=", ".join(entry["term"].split("|")),
            original=self.cog.format_references(entry["original"]),
            definition=self.cog.format_references(entry["definition"]),
            locale=entry["locale"],
            author=self.cog.determine_author(entry["author"]),
            category=", ".join(entry["category"].split(",")),
        )

    async def format_page(self, menu: "TermsPages", entries: dict[str, Any]) -> Embed:
        menu.embed.clear_fields()
        entry = self.format_info(entries)

        menu.embed.title = entry.term
        menu.embed.set_thumbnail(url=self.cog.determine_image_url(entries))
        menu.embed.set_footer(
            text=f"Page {menu.current_page + 1}/{self.get_max_pages()}"
        )

        menu.embed.description = f"{entry.original}\n\n{entry.definition}"

        # We need to swap the name value for what is in it's native locale
        menu.embed.add_field(name="Author", value=entry.author)
        menu.embed.add_field(name="Category", value=entry.category)

        return menu.embed


class TermsPages(CatherinePages):
    def __init__(
        self, entries: list[dict[str, Any]], *, interaction: discord.Interaction
    ):
        self.bot: Catherine = interaction.client  # type: ignore
        self.entries = entries
        super().__init__(
            source=TermSource(entries, bot=self.bot, per_page=1),
            interaction=interaction,
            compact=False,
        )
        self.embed = Embed()


class NounSource(menus.ListPageSource):
    def __init__(self, entries: list[dict[str, Any]], *, per_page: int = 1):
        super().__init__(entries=entries, per_page=per_page)

    def determine_author(self, author: Optional[str]) -> str:
        if author is None:
            return "Unknown"
        return author

    def format_info(self, entries: dict[str, Any]) -> NounInfo:
        def _fmt_prefix(value: str) -> str:
            if value:
                return f"- {value}"
            return value

        return NounInfo(
            masc="\n".join(
                map(_fmt_prefix, f"{entries['masc']}|{entries['mascPl']}".split("|"))
            ),
            fem="\n".join(
                map(_fmt_prefix, f"{entries['fem']}|{entries['femPl']}".split("|"))
            ),
            neutral="\n".join(
                map(_fmt_prefix, f"{entries['neutr']}|{entries['neutrPl']}".split("|"))
            ),
            author=self.determine_author(entries["author"]),
        )

    async def format_page(self, menu: "TermsPages", entries: dict[str, Any]):
        menu.embed.clear_fields()
        entry = self.format_info(entries)

        menu.embed.set_footer(
            text=f"{entry.author} | Page {menu.current_page + 1}/{self.get_max_pages()}"
        )

        menu.embed.add_field(name="Masculine", value=entry.masc)
        menu.embed.add_field(name="Feminine", value=entry.fem)
        menu.embed.add_field(name="Neutral", value=entry.neutral)
        return menu.embed


class NounPages(CatherinePages):
    def __init__(
        self, entries: list[dict[str, Any]], *, interaction: discord.Interaction
    ):
        self.bot: Catherine = interaction.client  # type: ignore
        super().__init__(
            source=NounSource(entries, per_page=1), interaction=interaction
        )
        self.embed = Embed()


class InclusiveSource(menus.ListPageSource):
    def __init__(
        self, entries: list[dict[str, Any]], *, bot: Catherine, per_page: int = 1
    ):
        super().__init__(entries=entries, per_page=per_page)
        self.cog: Dictionary = bot.get_cog("dictionary")  # type: ignore

    def format_info(self, entries: dict[str, Any]) -> InclusiveInfo:
        return InclusiveInfo(
            instead_of="\n".join(
                map(lambda value: f"- ~~{value}~~", entries["insteadOf"].split("|"))
            ),
            say="\n".join(
                map(lambda value: f"- **{value}**", entries["say"].split("|"))
            ),
            because=entries["because"],
            clarification=entries["clarification"],
            author=self.cog.determine_author(entries["author"]),
        )

    async def format_page(self, menu: "InclusivePages", entries: dict[str, Any]):
        menu.embed.clear_fields()
        entry = self.format_info(entries)

        menu.embed.description = (
            f"### Instead of \n{entry.instead_of}\n"
            f"### Better say\n{entry.say}\n"
            f"### Because\n{entry.because}\n"
        )

        if entry.clarification:
            menu.embed.description += f"### Clarification\n{entry.clarification}"

        menu.embed.set_footer(
            text=f"Page {menu.current_page + 1}/{self.get_max_pages()}"
        )

        menu.embed.add_field(name="Author", value=entry.author)
        return menu.embed


class InclusivePages(CatherinePages):
    def __init__(
        self, entries: list[dict[str, Any]], *, interaction: discord.Interaction
    ):
        self.bot: Catherine = interaction.client  # type: ignore
        super().__init__(
            source=InclusiveSource(entries, bot=self.bot, per_page=1),
            interaction=interaction,
        )
        self.embed = Embed()


class Dictionary(commands.GroupCog, name="dictionary"):
    """The to-go LGBTQ+ dictionary"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.decoder = msgspec.json.Decoder()
        self.link_regex = re.compile(r"^(http|https)://")
        self.session = self.bot.session

    ### Term utilities

    def split_flags(self, content: str) -> list[str]:
        return re.findall(r"(?<=\[).*(?=\])", content)

    def determine_image_url(self, entry: dict[str, Any]) -> str:
        flags = self.split_flags(entry["flags"])
        if len(flags[0]) != 0:
            flag_entity = flags[0].replace('"', "").split(",")
            return str(PRONOUNS_FLAGS_URL / f"{flag_entity[0]}.png")
        elif entry["images"] and "[object Object]" not in entry["images"]:
            asset = entry["images"].split(",")
            return str(
                CDN_FLAGS_URL / f"{asset[0]}-flag.png"
            )  # For general use, we'll just use the first flag shown
        return ""

    def format_inline_term_reference(self, content: str, entities: list[str]):
        if len(entities) == 0:
            return content

        url = URL.build(scheme="https", host="en.pronouns.page", path="/terminology")
        replacements = {}
        cleaned_content = re.sub(r"[\{\}]", "", content)

        # The order of formatting goes like this:
        # 1. Hashtag term references
        # 2. Link references
        # 3. Pronouns references
        # 4. Anything that is automatically assumed to be english terms
        for entity in entities:
            if entity.startswith("#"):
                parts = entity[1:].partition("=")
                replacements.update(
                    {entity: f"[{parts[-1]}]({url.with_query({'filter': parts[0]})})"}
                )
            elif self.link_regex.match(entity):
                # Special case here
                keyword = entity.split("=")[-1]
                keyword_length = len(keyword) + 1
                reference_url = URL(entity[:-keyword_length])
                if reference_url.host and reference_url.host == "www.perseus.tufts.edu":
                    replacements.update(
                        {
                            entity: f"[{keyword}]({reference_url.with_query({'doc': reference_url.query['doc'].replace(')', '%29').replace('(', '%28')})})"
                        }
                    )
                    continue

                link_parts = entity.partition("=")
                replacements.update({entity: f"[{link_parts[-1]}]({link_parts[0]})"})
            elif entity.startswith("/"):
                # For other languages, this is the slash for the path that would be used
                # Since we are only using english for now, this doesn't matter
                pronouns_parts = entity[1:].partition("=")
                pronouns_url = URL.build(
                    scheme="https",
                    host="en.pronouns.page",
                    path=f"/{pronouns_parts[0]}",
                )
                replacements.update({entity: f"[{pronouns_parts[-1]}]({pronouns_url})"})
            else:
                replacements.update(
                    {entity: f"[{entity}]({url.with_query({'filter': entity})})"}
                )

        fmt_regex = re.compile(r"(%s)" % "|".join(map(re.escape, replacements.keys())))
        return fmt_regex.sub(lambda mo: replacements[mo.group()], cleaned_content)

    def extract_reference(self, content: str) -> list[str]:
        return re.findall(r"{(.*?)}", content)

    def format_references(self, content: str) -> str:
        return self.format_inline_term_reference(
            content, self.extract_reference(content)
        )

    ### General utilities

    def determine_author(self, author: Optional[str]) -> str:
        if author is None:
            return "Unknown"
        author_link = str(BASE_URL / f"@{author}")
        return f"[{author}]({author_link})"

    async def _handle_invalid_response(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if (
            isinstance(error, app_commands.CommandInvokeError)
            and isinstance(error.original, aiohttp.ContentTypeError)
            and error.original.status == 403
        ):
            await interaction.response.send_message(
                "Unable to validate forbidden query"
            )

    @app_commands.command(name="terms")
    @app_commands.describe(query="The term to look for")
    async def terms(
        self, interaction: discord.Interaction, query: Optional[str] = None
    ) -> None:
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
    async def nouns(
        self, interaction: discord.Interaction, query: Optional[str] = None
    ) -> None:
        """Looks up gender neutral nouns and language"""
        url = URL("https://en.pronouns.page/api/nouns")
        if query:
            url = url / "search" / query
        async with self.session.get(url) as r:
            # If people start using this for pronouns, then a generator shows up
            # so that's in case this happens
            if r.status == 204:
                await interaction.response.send_message("Did you just insert pronouns?")
                return

            data = await r.json(loads=self.decoder.decode)

            if len(data) == 0:
                await interaction.response.send_message("No nouns were found")
                return

            pages = NounPages(data, interaction=interaction)
            await pages.start()

    @app_commands.command(name="inclusive")
    @app_commands.describe(term="The inclusive term to look for")
    async def inclusive(
        self, interaction: discord.Interaction, term: Optional[str] = None
    ) -> None:
        """Provides inclusive terms for users to learn about"""
        await interaction.response.defer()
        url = URL("https://en.pronouns.page/api/inclusive")
        if term:
            url = url / "search" / term
        async with self.session.get(url) as r:
            data = await r.json(loads=self.decoder.decode)
            if len(data) == 0:
                await interaction.followup.send("No inclusive terms were found")
                return
            pages = InclusivePages(entries=data, interaction=interaction)
            await pages.start()

    ### Error Handlers

    @terms.error
    async def on_terms_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await self._handle_invalid_response(interaction, error)

    @nouns.error
    async def on_nouns_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await self._handle_invalid_response(interaction, error)

    @inclusive.error
    async def on_inclusive_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await self._handle_invalid_response(interaction, error)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Dictionary(bot))
