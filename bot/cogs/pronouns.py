import discord
import orjson
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.pronouns import parse_pronouns
from libs.ui.pronouns import (
    PronounsProfileCircleEntry,
    PronounsProfileEntry,
    PronounsProfilePages,
    PronounsTesterModal,
    PronounsValuesEntry,
    PronounsWordsEntry,
    SuggestionView,
)
from libs.utils import Embed
from yarl import URL

APPROVAL_CHANNEL_ID = 1150575176006782976


class Pronouns(commands.GroupCog, name="pronouns"):
    """Your to-go module for pronouns!"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.session = self.bot.session
        self.pool = self.bot.pool
        super().__init__()

    @app_commands.command(name="get")
    @app_commands.describe(member="The member to lookup")
    async def get(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        """Obtains the pronouns of a Discord user from PronounDB

        This is not directly from Discord but a third party extension
        """
        params = {"platform": "discord", "ids": member.id}
        async with self.session.get(
            "https://pronoundb.org/api/v2/lookup", params=params
        ) as r:
            data = await r.json(loads=orjson.loads)
            if len(data) == 0:
                await interaction.response.send_message(
                    "No pronouns found for these user(s)."
                )
                return
            embed = Embed()
            embed.set_author(
                name=f"{member.global_name}'s pronouns",
                icon_url=member.display_avatar.url,
            )
            embed.description = "\n".join(
                [
                    f"{k}: {parse_pronouns(v)}"
                    for k, v in data[f"{member.id}"]["sets"].items()
                ]
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="test")
    @app_commands.describe(
        name="The name to use in the sentence. This could be your own name or someone else's name"
    )
    async def test(self, interaction: discord.Interaction, name: str) -> None:
        """Basically a pronouns tester command"""
        # Based off of this query: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/tags.py#L182-L191
        query = """
        SELECT sentence
        FROM pronouns_examples
        OFFSET FLOOR(RANDOM() * (
            SELECT COUNT(*)
            FROM pronouns_examples
            WHERE approved = True
        ))
        LIMIT 1;
        """
        value = await self.pool.fetchval(query)
        if value is None:
            await interaction.response.send_message("Can't find any examples")
            return
        await interaction.response.send_modal(
            PronounsTesterModal(interaction, value, name, self.bot.metrics)
        )

    @app_commands.command(name="suggest-examples")
    async def suggest_examples(self, interaction: discord.Interaction) -> None:
        """Suggest an example sentence for others to use"""
        embed = Embed()
        embed.title = "Suggestions Instructions"
        embed.description = """
        Hey there! **Make sure you read the instructions before you start!**
        
        **Once you are done, please click the finish button to finish the suggestion**
        Reference can be found [here](https://catherine-chan.readthedocs.io/en/latest/guides/user/pronoun-suggestions.html)
        
        In order to provide an example, you will need to follow the templating system used. You essentially use these as variables so when others use your sentence, it will be formatted correctly. Here is the list:
        
        - Name: `$name`
        - Subjective Pronoun: `$subjective_pronoun` (Subjective / Nominative pronouns include ones like he, she, they, it, etc)
        - Objective Pronoun: `$objective_pronoun` (Objective pronouns include them, him, her, etc)
        - Possessive Pronoun: `$possessive_pronoun` (Possessive pronouns include his, hers, theirs, etc)
        - Possessive Determiner: `$possessive_determiner` (Possessive determiners include his, her, their, etc)
        - Reflective Pronoun: `$reflective_pronoun` (Reflective pronouns include himself, herself, themselves, etc)
        
        Some examples can look like this (note that names are not fully capitalized correctly yet):
        
        - $name is really cute! $subjective_pronoun looks really good in that outfit!
        - $name is a cutiepie uwu! $subjective_pronoun looks likes $subjective_pronoun is ready to go!
        - $name is a very lovely person!
        """
        view = SuggestionView(self.bot, interaction, self.pool)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="profile")
    @app_commands.describe(
        username="The username of the user. These are not Discord usernames, but pronouns.page usernames"
    )
    async def profile(self, interaction: discord.Interaction, username: str) -> None:
        """Obtains the profile of an Pronouns.page user"""
        await interaction.response.defer()
        url = URL("https://en.pronouns.page/api/profile/get/") / username
        params = {"version": 2}
        async with self.session.get(url, params=params) as r:
            data = await r.json(loads=orjson.loads)
            if len(data["profiles"]) == 0:
                await interaction.response.send_message("The profile was not found")
                return
            curr_username = data["username"]
            avatar = data["avatar"]
            converted = {
                k: PronounsProfileEntry(
                    username=curr_username,
                    avatar=avatar,
                    locale=k,
                    names=[
                        PronounsValuesEntry(
                            value=name["value"], opinion=name["opinion"]
                        )
                        for name in v["names"]
                    ],
                    pronouns=[
                        PronounsValuesEntry(
                            value=pronoun["value"], opinion=pronoun["opinion"]
                        )
                        for pronoun in v["pronouns"]
                    ],
                    description=v["description"],
                    age=v["age"],
                    links=v["links"],
                    flags=v["flags"],
                    words=[
                        PronounsWordsEntry(
                            header=words["header"],
                            values=[
                                PronounsValuesEntry(
                                    value=value["value"], opinion=value["opinion"]
                                )
                                for value in words["values"]
                            ],
                        )
                        for words in v["words"]
                    ],
                    timezone=v["timezone"]["tz"],
                    circle=[
                        PronounsProfileCircleEntry(
                            username=member["username"],
                            avatar=member["avatar"],
                            mutual=member["circleMutual"],
                            relationship=member["relationship"],
                        )
                        for member in v["circle"]
                    ]
                    if len(v["circle"]) != 0
                    else None,
                )
                for k, v in data["profiles"].items()
            }
            pages = PronounsProfilePages(entries=converted, interaction=interaction)
            await pages.start()


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Pronouns(bot))
