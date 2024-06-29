import sys
from pathlib import Path

path = Path(__file__).parents[1].joinpath("bot")
another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(path))
sys.path.append(str(another_path))

import discord.ext.test as dpytest
import pytest
from conftest import bot  # type: ignore
from libs.cog_utils.hrt.embeds import (
    EstrogenEmbed,
    ProgEmbed,
    ProlactinEmbed,
    TestosteroneEmbed,
)
from libs.utils import (
    ConfirmEmbed,
    Embed,
    ErrorEmbed,
    SuccessEmbed,
    TimeoutEmbed,
)

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


@pytest.mark.asyncio
async def test_estrogen_embed(bot):
    embed = EstrogenEmbed()
    await dpytest.message("!estrogenembed")
    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
async def test_progestrone_embed(bot):
    embed = ProgEmbed()
    await dpytest.message("!progestroneembed")
    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
async def test_testosterone_embed(bot):
    embed = TestosteroneEmbed()
    await dpytest.message("!testosteroneembed")
    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
async def test_prolactin_embed(bot):
    embed = ProlactinEmbed()
    await dpytest.message("!prolactinembed")
    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
async def test_timeout_embed(bot):
    embed = TimeoutEmbed()
    await dpytest.message("!timeoutembed")
    assert dpytest.verify().message().embed(embed)
