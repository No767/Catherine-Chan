from typing import Optional

import discord
import orjson
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.ui.dictionary import (
    InclusivePages,
    NounPages,
    TermsPages,
    split_flags,
)
from libs.ui.dictionary.structs import (
    InclusiveContent,
    InclusiveEntity,
    NounContent,
    NounEntity,
    TermAssets,
    TermEntity,
)
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
        url = URL("https://en.pronouns.page/api/terms")
        if query:
            url = url / "search" / query
        async with self.session.get(url) as r:
            data = await r.json(loads=orjson.loads)
            if len(data) == 0:
                await interaction.response.send_message("No terms were found")
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
        url = URL("https://en.pronouns.page/api/nouns")
        if query:
            url = url / "search" / query
        async with self.session.get(url) as r:
            # If people start using this for pronouns, then a generator shows up
            # so that's in case this happens
            if r.content_type == "text/html":
                await interaction.response.send_message("Uhhhhhhhhhhhh what mate")
                return
            data = await r.json(loads=orjson.loads)
            if len(data) == 0:
                await interaction.response.send_message("No nouns were found")
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
        url = URL("https://en.pronouns.page/api/inclusive")
        if term:
            url = url / "search" / term
        async with self.session.get(url) as r:
            data = await r.json(loads=orjson.loads)
            if len(data) == 0:
                await interaction.response.send_message("No inclusive terms were found")
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

    # TODO: Complete the rewrite for this
    @app_commands.command(name="lookup")
    @app_commands.describe(
        pronouns="The pronouns to look up. These are actual pronouns, such as she/her, and they/them. "
    )
    async def lookup(self, interaction: discord.Interaction, pronouns: str) -> None:
        """Lookup info about the given pronouns

        Pronouns include she/her, they/them and many others. Singular pronouns (eg 'she') also work.
        """
        url = URL("https://en.pronouns.page/api/pronouns/")
        banner_url = URL("https://en.pronouns.page/api/banner/")
        full_url = url / pronouns
        full_banner_url = banner_url / f"{pronouns}.png"
        async with self.session.get(full_url) as r:
            data = await r.json(loads=orjson.loads)
            if data is None:
                await interaction.response.send_message(
                    "The pronouns requested were not found"
                )
                return

            desc = f"""
            {data['description']}
            
            **Info**
            Aliases: {data['aliases']}
            Pronounceable: {data['pronounceable']}
            Normative: {data['normative']}\n
            """
            if len(data["morphemes"]) != 0:
                desc += "\n**Morphemes**\n"
                for k, v in data["morphemes"].items():
                    desc += f"{k.replace('_', ' ').title()}: {v}\n"

            if len(data["pronunciations"]) != 0:
                desc += "\n**Pronunciations**\n"
                for k, v in data["pronunciations"].items():
                    desc += f"{k.replace('_', ' ').title()}: {v}\n"
            embed = Embed()
            embed.title = data["name"]
            embed.description = desc
            embed.add_field(name="Examples", value="\n".join(data["examples"]))
            embed.add_field(
                name="Forms",
                value=f"Third Form: {data['thirdForm']}\nSmall Form: {data['smallForm']}",
            )
            embed.add_field(
                name="Plural?",
                value=f"Plural: {data['plural']}\nHonorific: {data['pluralHonorific']}",
            )
            embed.set_image(url=str(full_banner_url))
            await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Dictionary(bot))
