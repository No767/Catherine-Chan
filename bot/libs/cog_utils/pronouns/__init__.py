import re
from typing import Dict, List, Union

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


# Thank you stack overflow
# code comes from this: https://stackoverflow.com/a/15175239/16526522
def parse_pronouns_sentence(replacements: Dict[str, str], sentence: str) -> str:
    regex = re.compile("(%s[s]?)" % "|".join(map(re.escape, replacements.keys())))
    return regex.sub(lambda mo: replacements[mo.group()], sentence)


def convert_to_proper_sentence(sentence: str) -> str:
    regex = re.compile(r"((?<=[\.\?!]\s)(\w+)|(^\w+))")

    def cap(match: re.Match):
        return match.group().capitalize()

    return regex.sub(cap, sentence)


def convert_to_proper_name(name: str) -> str:
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


def validate_for_templating(sentence: str) -> bool:
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
