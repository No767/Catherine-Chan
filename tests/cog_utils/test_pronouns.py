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
    parse_pronouns,
    parse_tester_sentence,
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


def test_parse_tester_sentence():
    sentence = "$subject_pronouns is doing a nice thing."
    parsed_sen = "she is doing a nice thing."
    res = parse_tester_sentence(
        sentence,
        subjective_pronouns="she",
        objective_pronoun="her",
        possessive_pronoun="she",
        reflective_pronoun="she",
    )
    assert res == parsed_sen
