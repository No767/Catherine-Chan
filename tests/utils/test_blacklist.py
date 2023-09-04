import sys
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))
import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from libs.utils import load_blacklist

load_dotenv(dotenv_path=another_path.joinpath(".env"))

POSTGRES_URI = os.environ["POSTGRES_URI"]

import asyncpg


@pytest_asyncio.fixture
async def setup():
    async with asyncpg.create_pool(dsn=POSTGRES_URI) as pool:
        yield pool


@pytest.mark.asyncio
async def test_load_blacklist(setup):
    res = await load_blacklist(setup)
    assert isinstance(res, dict) and len(res) >= 0
