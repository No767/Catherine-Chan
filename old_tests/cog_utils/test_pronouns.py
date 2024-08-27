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
    convert_to_proper_name,
    convert_to_proper_sentence,
    parse_pronouns,
    parse_pronouns_sentence,
    validate_for_templating,
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


def test_convert_to_proper_name():
    # Ofc i'm using my own name
    name = "noelle wang"
    proper_name = "Noelle Wang"
    improper_name = "69 what is up my dude"

    converted_name = convert_to_proper_name(name)
    assert converted_name == proper_name

    attempted_converted_name = convert_to_proper_name(improper_name)
    assert attempted_converted_name == improper_name


def test_validate_template():
    template = "$subjective_pronoun is cute!"
    template_with_name = "$subjective_pronoun is hanging out with $name today."
    invalid_template = "$sfsdf is cute"
    valid_with_invalid_template = (
        "$name is cute and $subjfct_pronoun is hanging out with $name"
    )
    no_spaces = "$sfsfiscute"
    no_variables = "sfdsfsdf"

    first_template = validate_for_templating(template)
    assert first_template is True

    second_template = validate_for_templating(template_with_name)
    assert second_template is True

    third_template = validate_for_templating(invalid_template)
    assert third_template is False

    fourth_template = validate_for_templating(no_spaces)
    assert fourth_template is False

    mix_template = validate_for_templating(valid_with_invalid_template)
    assert mix_template is False

    no_variables_template = validate_for_templating(no_variables)
    assert no_variables_template is False
