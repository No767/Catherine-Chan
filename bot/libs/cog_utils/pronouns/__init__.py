from typing import List, Union

import discord
from discord.utils import utcnow
from libs.utils import Embed


def parse_pronouns(entry: List[str]) -> str:
    """A helper func in order to parse out pronouns

    Args:
        entry (List[str]): List of pronouns

    Returns:
        str: Formatted string of pronouns
    """
    pronouns = {
        "he": "he/him",
        "she": "she/her",
        "it": "it/its",
        "they": "they/them",
    }
    for idx, item in enumerate(entry):
        if item in pronouns:
            entry[idx] = pronouns[item]

    return ", ".join(entry).rstrip(",")


def build_approve_embed(
    sentence: str, example_sentence: str, user: Union[discord.User, discord.Member]
) -> Embed:
    embed = Embed(color=discord.Colour.from_rgb(255, 61, 255))
    embed.title = "New Pronouns Example Suggestion"
    embed.description = (
        f"**Sentence**: \n{sentence}\n\n**Example Sentence**: \n{example_sentence}"
    )
    embed.add_field(name="Suggested By", value=user.mention)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="Created at")
    embed.timestamp = utcnow()
    return embed


def parse_tester_sentence(
    sentence: str,
    subjective_pronouns: str,
    objective_pronoun: str,
    possessive_pronoun: str,
    reflective_pronoun: str,
):
    # I can't think of any other way to do this. But my idea is using Regex for this.
    return (
        sentence.replace("$subject_pronouns", subjective_pronouns)
        .replace("$objective_pronouns", objective_pronoun)
        .replace("$possessive_pronouns", possessive_pronoun)
        .replace("$reflective_pronouns", reflective_pronoun)
    )
