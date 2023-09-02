import sys
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
path = Path(__file__).parents[1].joinpath("bot")
sys.path.append(str(another_path))
sys.path.append(str(path))

import discord.ext.test as dpytest
import pytest
from conftest import bot  # type: ignore
from libs.cog_utils.pronouns import (
    build_approve_embed,
    convert_to_proper_sentence,
    parse_pronouns,
    parse_pronouns_sentence,
)

new_bot = bot


@pytest.fixture()
def pronouns_entry():
    pronouns = ["he", "she", "it", "they"]
    return pronouns


def test_parse_pronouns(pronouns_entry):
    res = parse_pronouns(pronouns_entry)
    formatted_str = "he/him, she/her, it/its, they/them"
    assert res == formatted_str


@pytest.mark.asyncio
async def test_build_approve_embed(bot):
    res = build_approve_embed("Hey", "Hey", bot.users[0])
    await dpytest.message("!approve")
    assert dpytest.verify().message().embed(res)


def test_parse_pronouns_sentence():
    replacements = {
        "$subjective_pronoun": "she",
        "$objective_pronoun": "her",
        "$possessive_pronoun": "she",
        "$reflective_pronoun": "she",
        "$name": "Noelle",
    }
    sentence = "$subjective_pronoun is a very good person. nothing can stop $objective_pronoun. $name is a cutiepie."
    parsed_sentence = parse_pronouns_sentence(replacements, sentence)
    converted = convert_to_proper_sentence(parsed_sentence)
    assert (
        converted
        == "She is a very good person. Nothing can stop her. Noelle is a cutiepie."
    )


def test_convert_to_proper_sentence():
    sentence = "you are a good person. this is fun. yay."
    converted = convert_to_proper_sentence(sentence)
    assert converted == "You are a good person. This is fun. Yay."
