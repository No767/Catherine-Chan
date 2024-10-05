from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Optional, Sequence, Union

import discord
import msgspec
import orjson
from discord import app_commands
from discord.ext import commands, menus
from libs.utils.embeds import Embed, FullErrorEmbed
from libs.utils.modal import CatherineModal
from libs.utils.pages import CatherinePages
from yarl import URL

if TYPE_CHECKING:
    from catherinecore import Catherine

NO_CONTROL_MSG = "This view cannot be controlled by you, sorry!"

### Structs


class PartialProfileInfo(msgspec.Struct, frozen=True):
    names: str
    pronouns: str
    flags: str
    circle: str


class ProfileMeta(msgspec.Struct, frozen=True):
    username: str
    locale: str
    avatar: str
    tz: Optional[str]
    age: int
    circle: list[dict[str, str]]


class ProfileInfo(msgspec.Struct, frozen=True):
    names: list[dict[str, str]]
    description: str
    pronouns: list[dict[str, str]]
    flags: list[str]
    meta: ProfileMeta
    words: Sequence[dict]  # typing may not be correct


### Embeds


class ApprovalEmbed(discord.Embed):
    def __init__(
        self,
        sentence: str,
        example: str,
        user: Union[discord.User, discord.Member],
        **kwargs,
    ):
        super().__init__(color=discord.Colour.from_rgb(255, 61, 255), **kwargs)
        self.title = "New Pronouns Example Suggestion"
        self.description = (
            f"**Sentence**: \n{sentence}\n\n**Example Sentence**: \n{example}"
        )
        self.add_field(name="Suggested By", value=user.mention)
        self.set_thumbnail(url=user.display_avatar.url)
        self.set_footer(text="Created at")
        self.timestamp = discord.utils.utcnow()


### UI components (Modals, Views, Pages, Selects)


class PronounsTesterModal(CatherineModal, title="Input the fields"):
    def __init__(
        self,
        bot: Catherine,
        interaction: discord.Interaction,
        sentence: str,
        name: str,
    ):
        super().__init__(interaction=interaction)
        self.bot = bot
        self.cog: Pronouns = bot.get_cog("pronouns")  # type: ignore
        self.sentence = sentence
        self.name = name
        self.metrics = bot.metrics
        self.sp = discord.ui.TextInput(
            label="Subjective Pronoun", placeholder="Example: They | He | She"
        )
        self.op = discord.ui.TextInput(
            label="Objective Pronoun", placeholder="Example: Them | Him | Her "
        )
        self.pd = discord.ui.TextInput(
            label="Possessive Determiner", placeholder="Example: Their | His | Her"
        )
        self.pp = discord.ui.TextInput(
            label="Possessive Pronoun", placeholder="Example: Theirs | His | Hers"
        )
        self.rp = discord.ui.TextInput(
            label="Reflective Pronoun",
            placeholder="Example: Themselves | Himself | Herself",
        )

        self.add_item(self.sp)
        self.add_item(self.op)
        self.add_item(self.pd)
        self.add_item(self.pp)
        self.add_item(self.rp)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # The new Regex-based solution to the pronouns tester command
        # Original: https://github.com/LilbabxJJ-1/PrideBot/blob/master/commands/pronouns.py#L15
        replacements = {
            "$subjective_pronoun": self.sp.value.lower(),
            "$objective_pronoun": self.op.value.lower(),
            "$possessive_pronoun": self.pp.value.lower(),
            "$possessive_determiner": self.pd.value.lower(),
            "$reflective_pronoun": self.rp.value.lower(),
            "$name": self.cog.convert_to_proper_name(self.name),
        }
        parsed_sentence = self.cog.parse_pronouns_sentence(replacements, self.sentence)
        complete_sentence = self.cog.convert_to_proper_sentence(parsed_sentence)
        self.metrics.features.successful_pronouns.inc()
        await interaction.response.send_message(complete_sentence)


class SuggestPronounsExamplesModal(CatherineModal, title="Suggest an example"):
    def __init__(self, interaction: discord.Interaction, bot: Catherine) -> None:
        super().__init__(
            interaction=interaction, custom_id="suggest_pronouns_example:modal"
        )
        self.sentence = discord.ui.TextInput(
            label="Sentence",
            placeholder="Enter your sentence",
            min_length=1,
            max_length=250,
            style=discord.TextStyle.long,
        )
        self.example_sentence = discord.ui.TextInput(
            label="Example Sentence",
            placeholder="Enter your example sentence with all of the correct pronouns here.",
            default=self.sentence.value,
            style=discord.TextStyle.long,
            min_length=1,
            max_length=250,
        )
        self.bot = bot
        self.cog: Pronouns = self.bot.get_cog("pronouns")  # type: ignore
        self.pool = self.bot.pool
        self.add_item(self.sentence)
        self.add_item(self.example_sentence)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.cog.validate(self.sentence.value) is False:
            msg = """
            It seems you tried to submit an invalid example. The example may be invalid for the following reasons:
            
            1. The example includes one or more variables that are invalid
            2. Your example contains no variables at all.
            
            Please fix your example based on these two reasons.
            """
            await interaction.response.send_message(msg, ephemeral=True)
            return

        query = """
        WITH pronouns_id AS (
            INSERT INTO pronouns_test_examples (owner_id, content)
            VALUES ($1, $2)
            RETURNING id
        )
        SELECT (id) FROM pronouns_id;
        """
        async with self.pool.acquire() as connection:
            example_id = 0
            tr = connection.transaction()
            await tr.start()

            try:
                example_id = await connection.fetchval(
                    query, interaction.user.id, self.sentence.value
                )
            except Exception as e:
                await tr.rollback()
                await interaction.response.send_message(
                    f"Suggestion entirely failed for unknown reason ({str(e)})",
                    ephemeral=True,
                )
            else:
                await tr.commit()
                channel = self.bot.get_channel(self.bot.approval_channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    view = ApprovePronounsExampleView(
                        self.bot,
                        self.sentence.value,
                        int(example_id),
                        interaction.user.id,
                    )
                    await channel.send(
                        content="<@here>",
                        embed=ApprovalEmbed(
                            sentence=self.sentence.value,
                            example=self.example_sentence.value,
                            user=interaction.user,
                        ),
                        view=view,
                    )
                    await interaction.response.send_message(
                        "Successfully suggested sentence", ephemeral=True
                    )


class ApprovePronounsExampleView(discord.ui.View):
    def __init__(self, bot: Catherine, sentence: str, example_id: int, owner_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.sentence = sentence
        self.example_id = example_id
        self.owner_id = owner_id

    @discord.ui.button(
        label="Approve",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
        custom_id="approve_pronouns_view:confirm",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        UPDATE pronouns_test_examples
        SET approved = $3
        WHERE id = $1 AND owner_id = $2;
        """
        await self.bot.pool.execute(query, self.example_id, self.owner_id, True)
        await interaction.response.edit_message(
            content=f"Successfully approved the sentence (From: {self.owner_id}, Example ID: {self.example_id})\n\nSentence: {self.sentence}",
            embed=None,
            view=None,
        )

    @discord.ui.button(
        label="Deny",
        style=discord.ButtonStyle.red,
        emoji="<:redTick:596576672149667840>",
        custom_id="approve_pronouns_view:deny",
    )
    async def deny(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        DELETE FROM pronouns_test_examples
        WHERE id = $1 AND owner_id = $2;
        """
        await self.bot.pool.execute(query, self.example_id, self.owner_id)
        await interaction.response.edit_message(
            content=f"Denied entry. (From: {self.owner_id}, ID: {self.example_id})\n\nSentence: {self.sentence}",
            embed=None,
            view=None,
        )


# We can't subclass CatherineView, and we essentially need to make our own ConfirmationView
# Thus, we need to subclass from discord.ui.View
class SuggestionView(discord.ui.View):
    def __init__(
        self,
        bot: Catherine,
        interaction: discord.Interaction,
        *,
        timeout: float = 180.0,
        delete_after: bool = True,
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.interaction = interaction
        self.delete_after = delete_after
        self.response: Optional[discord.InteractionMessage] = None

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if self.delete_after and self.response:
            await self.response.delete()
        elif self.response:
            await self.response.edit(view=None)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any],
        /,
    ) -> None:
        bot: Catherine = interaction.client  # type: ignore
        bot.logger.exception(
            "Ignoring view exception from %s: ", self.__class__.__name__, exc_info=error
        )
        await interaction.response.send_message(
            embed=FullErrorEmbed(error), ephemeral=True
        )
        self.stop()

    @discord.ui.button(
        label="Start",
        style=discord.ButtonStyle.green,
    )
    async def start(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        modal = SuggestPronounsExamplesModal(interaction, self.bot)
        await interaction.response.send_modal(modal)
        if self.delete_after:
            await interaction.delete_original_response()

        self.stop()


class ProfilePageSource(menus.PageSource):
    def __init__(self, locale: str):
        self.locale = locale

    def is_paginating(self) -> bool:
        return True

    def get_max_pages(self) -> Optional[int]:
        return 2

    async def get_page(self, page_number: int) -> Any:
        self.index = page_number
        return self

    ### Utilities

    def determine_bold(self, value: str, opinion: str) -> str:
        if "yes" in opinion:
            return f"**{value}**"
        return f"{value}"

    def determine_mutual(self, username: str, mutual: bool) -> str:
        if mutual:
            return f"**@{username}** (Mutual)"
        return f"**@{username}**"

    def parse_opinion(self, opinion: str) -> str:
        data = {
            "yes": "\U00002764",
            "jokingly": "\U0001f61b",
            "close": "\U0001f465",
            "meh": "\U0001f44c",
            "no": "\U0001f6ab",
        }
        try:
            return data[opinion]
        except KeyError:
            # Basically return a question mark
            # These are basically custom emojis that I can't predict
            return "\U00002753"

    def format_info(self, entry: ProfileInfo) -> PartialProfileInfo:
        return PartialProfileInfo(
            names="\n".join(
                f"{self.parse_opinion(sub_entry['opinion'])} {self.determine_bold(sub_entry['value'], sub_entry['opinion'])}"
                for sub_entry in entry.names
            ),
            pronouns="\n".join(
                f"{self.parse_opinion(sub_entry['opinion'])} {self.determine_bold(sub_entry['value'], sub_entry['opinion'])}"
                for sub_entry in entry.pronouns
            ),
            flags=", ".join(flag for flag in entry.flags),
            circle="\n".join(f"- {self.determine_mutual(entity['username'], entity['circleMutual'])}\n\t- Relationship: {entity['relationship']}" for entity in entry.meta.circle) if len(entry.meta.circle) != 0 else "None",  # type: ignore
        )

    async def format_page(self, menu: ProfilePages, page):
        menu.embed.clear_fields()

        entry = menu.entries[self.locale]
        menu.embed.title = f"@{entry.meta.username}"
        menu.embed.set_thumbnail(url=entry.meta.avatar)

        menu.embed.set_footer(
            text="\U00002764 = Yes | \U0001f61b = Jokingly | \U0001f465 = Only if we're close | \U0001f44c = Okay | \U0001f6ab = Nope"
        )
        if self.index == 0:
            menu.embed.description = entry.description
            profile_info = self.format_info(entry)
            menu.embed.add_field(name="Names", value=profile_info.names, inline=False)
            menu.embed.add_field(
                name="Pronouns", value=profile_info.pronouns, inline=False
            )
            menu.embed.add_field(name="Age", value=entry.meta.age, inline=False)
            menu.embed.add_field(name="Flags", value=profile_info.flags, inline=False)
            menu.embed.add_field(
                name="Timezone", value=entry.meta.tz or "Unknown", inline=False
            )
            menu.embed.add_field(
                name="Relationships", value=profile_info.circle, inline=False
            )
        elif self.index == 1:
            menu.embed.description = ""
            for entity in entry.words:
                fmt_words = "\n".join(
                    f"- {self.parse_opinion(entry['opinion'])} {entry['value']}"
                    for entry in entity["values"]
                )
                menu.embed.add_field(
                    name=entity["header"] or "Unknown", value=fmt_words, inline=False
                )
        return menu.embed


class ProfileLangMenu(discord.ui.Select["ProfilePages"]):
    def __init__(self, entries: dict[str, ProfileInfo]):
        super().__init__(placeholder="Select a language")
        self.entries = entries
        # The list of officially supported langs
        # https://gitlab.com/PronounsPage/PronounsPage/-/blob/main/locale/locales.js
        self.lang_codes = {
            "de": "Deutsch",
            "es": "Español",
            "eo": "Esperanto",
            "en": "English",
            "et": "Eesti keel",
            "fr": "Français",
            "gl": "Galego",
            "he": "עברית",
            "it": "Italiano",
            "lad": "Ladino (Djudezmo)",
            "nl": "Nederlands",
            "no": "Norsk (Bokmål)",
            "pl": "Polski",
            "pt": "Português",
            "ro": "Română",
            "sv": "Svenska",
            "tr": "Türkçe",
            "vi": "Tiếng Việt",
            "ar": "العربية",
            "ru": "Русский",
            "ua": "Українська",
            "ja": "日本語",
            "ko": "한국어",
            "yi": "ייִדיש",
            "zh": "中文",
            "tok": "toki pona",
        }
        self.__fill_options()

    def __fill_options(self):
        for entry in self.entries.keys():
            lang = self.lang_codes[entry]
            self.add_option(label=f"{lang}", value=entry)

    async def callback(self, interaction: discord.Interaction):
        if self.view is not None:
            value = self.values[0]
            if value == "en":
                await self.view.rebind(ProfilePageSource(locale="en"), interaction)
            else:
                await self.view.rebind(ProfilePageSource(locale=value), interaction)


class ProfilePages(CatherinePages):
    def __init__(
        self, entries: dict[str, ProfileInfo], *, interaction: discord.Interaction
    ):
        self.entries = entries
        super().__init__(
            ProfilePageSource(locale="en"),
            interaction=interaction,
            compact=True,
        )
        self.add_cats()

        self.embed = discord.Embed(colour=discord.Colour.from_rgb(255, 125, 212))

    def add_cats(self):
        self.clear_items()
        self.add_item(ProfileLangMenu(self.entries))
        self.fill_items()

    async def rebind(
        self, source: menus.PageSource, interaction: discord.Interaction
    ) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)


class Pronouns(commands.GroupCog, name="pronouns"):
    """Your to-go module for pronouns!"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.session = self.bot.session
        self.pool = self.bot.pool
        super().__init__()

    ### Pronouns tester utils

    # Thank you stack overflow
    # code comes from this: https://stackoverflow.com/a/15175239/16526522
    def parse_pronouns_sentence(
        self, replacements: dict[str, str], sentence: str
    ) -> str:
        regex = re.compile("(%s[s]?)" % "|".join(map(re.escape, replacements.keys())))
        return regex.sub(lambda mo: replacements[mo.group()], sentence)

    def convert_to_proper_sentence(self, sentence: str) -> str:
        regex = re.compile(r"((?<=[\.\?!]\s)(\w+)|(^\w+))")

        def cap(match: re.Match):
            return match.group().capitalize()

        return regex.sub(cap, sentence)

    def convert_to_proper_name(self, name: str) -> str:
        regex = re.compile("[^()0-9-]+")
        possible_match = regex.fullmatch(name)

        if possible_match is None:
            # If we didn't match any possible names, throw back the original name
            # Most of the times it will be improper, so we might as well just return the improper name so it does't just say None
            return name

        parsed_str = " ".join(
            word.title() if not word[0].isdigit() else word
            for word in possible_match.group().split()
        )
        return parsed_str

    def validate(self, sentence: str) -> bool:
        valid_variables = [
            "$subjective_pronoun",
            "$objective_pronoun",
            "$possessive_pronoun",
            "$possessive_determiner",
            "$reflective_pronoun",
            "$name",
        ]
        result = [item for item in sentence.split(" ") if item.startswith("$")]
        if len(result) == 0:
            return False

        is_valid = all(var in valid_variables for var in result)
        return is_valid

    ### Misc utils

    def parse_pronouns(self, entry: list[str]) -> str:
        pronouns = {
            "he": "he/him",
            "she": "she/her",
            "it": "it/its",
            "they": "they/them",
        }
        for idx, item in enumerate(entry):
            if item in pronouns:
                entry[idx] = pronouns[item]

        return ", ".join(entry)

    @app_commands.command(name="test")
    @app_commands.describe(
        name="The name to use in the sentence. This could be your own name or someone else's name"
    )
    async def test(self, interaction: discord.Interaction, name: str) -> None:
        """Basically a pronouns tester command"""
        # Based off of this query: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/tags.py#L182-L191
        query = """
        SELECT DISTINCT content
        FROM pronouns_test_examples
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
            PronounsTesterModal(self.bot, interaction, value, name)
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
        
        In order to provide an example, you will need to follow the template used. You essentially use these as variables so when others use your sentence, it will be formatted correctly. Here is the list:
        
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
        view = SuggestionView(self.bot, interaction)
        await interaction.response.send_message(embed=embed, view=view)
        view.response = await interaction.original_response()

    @app_commands.command(name="db")
    @app_commands.describe(member="The member to lookup")
    async def db(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        """Obtains the pronouns of a Discord user from PronounDB

        This is not directly from Discord but a third party extension
        """
        if member.bot:
            await interaction.response.send_message("My pronouns are she/her")
            return

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
                    f"{k}: {self.parse_pronouns(v)}"
                    for k, v in data[f"{member.id}"]["sets"].items()
                ]
            )
            await interaction.response.send_message(embed=embed)

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
                await interaction.followup.send("The profile was not found")
                return
            entries = {
                k: ProfileInfo(
                    names=v["names"],
                    description=v["description"],
                    pronouns=v["pronouns"],
                    flags=v["flags"],
                    meta=ProfileMeta(
                        username=data["username"],
                        locale=k,
                        avatar=data["avatarSource"],
                        tz=v["timezone"]["tz"] if v["timezone"] else None,
                        age=v["age"],
                        circle=v["circle"],
                    ),
                    words=v["words"],
                )
                for k, v in data["profiles"].items()
            }
            pages = ProfilePages(entries=entries, interaction=interaction)
            await pages.start()


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Pronouns(bot))
