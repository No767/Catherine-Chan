import sys
from pathlib import Path

path = Path(__file__).parents[1].joinpath("bot")
another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(path))
sys.path.append(str(another_path))

import discord.ext.test as dpytest
import pytest
from conftest import bot  # type: ignore
from libs.utils import ConfirmEmbed, Embed, ErrorEmbed, SuccessEmbed

new_bot = bot


@pytest.mark.asyncio
async def test_embed(bot):
    embed = Embed()
    await dpytest.message("!e")
    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
async def test_success_embed(bot):
    embed = SuccessEmbed()
    await dpytest.message("!se")
    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
async def test_error_embed(bot):
    embed = ErrorEmbed()
    await dpytest.message("!ee")
    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
async def test_confirm_embed(bot):
    embed = ConfirmEmbed()
    await dpytest.message("!ce")
    assert dpytest.verify().message().embed(embed)
