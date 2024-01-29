from typing import Optional

import discord
import orjson
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.ui.dictionary.pages import (
    InclusivePages,
    NounPages,
    PronounsPages,
    TermsPages,
)
from libs.ui.dictionary.structs import (
    InclusiveContent,
    InclusiveEntity,
    NounContent,
    NounEntity,
    PronounsEntity,
    PronounsMorphemes,
    TermAssets,
    TermEntity,
)
from libs.ui.dictionary.utils import format_pronouns_info, split_flags
from libs.utils import Embed
from yarl import URL


class Dictionary(commands.GroupCog, name="dictionary"):
    """The to-go LGBTQ+ dictionary"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.session = self.bot.session

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
            data = await r.json(loads=orjson.loads)
            if len(data) == 0:
                await interaction.followup.send("No terms were found")
                return
            converted = [
                TermEntity(
                    term=term["term"],
                    original=term["original"] if len(term["original"]) > 0 else None,
                    definition=term["definition"],
                    key=term["key"],
                    assets=TermAssets(
                        flags=split_flags(term["flags"]),
                        images=term["images"] if len(term["images"]) > 0 else None,
                    ),
                    category=term["category"].split(","),
                    author=term["author"],
                )
                for term in data
            ]
            pages = TermsPages(entries=converted, interaction=interaction)
            await pages.start()

    @app_commands.command(name="nouns")
    @app_commands.describe(query="The noun to look for")
    async def nouns(
        self, interaction: discord.Interaction, query: Optional[str] = None
    ) -> None:
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
                    neutral=NounContent(
                        regular=entry["neutr"], plural=entry["neutrPl"]
                    ),
                    author=entry["author"],
                )
                for entry in data
            ]
            pages = NounPages(entries=converted, interaction=interaction)
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
                        possessive_determiner=data["morphemes"][
                            "possessive_determiner"
                        ],
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
                embed.add_field(
                    name="Aliases", value=", ".join(pronouns_entry.aliases).rstrip(",")
                )
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
                            possessive_determiner=entry["morphemes"][
                                "possessive_determiner"
                            ],
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
