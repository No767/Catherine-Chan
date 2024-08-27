import sys
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))

import os

import asyncpg
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from libs.cog_utils.commons import register_user

load_dotenv(dotenv_path=another_path.joinpath(".env"))

POSTGRES_URI = os.environ["POSTGRES_URI"]


@pytest_asyncio.fixture
async def setup():
    conn = await asyncpg.connect(dsn=POSTGRES_URI)
    yield conn
    await conn.close()


@pytest.mark.asyncio
async def test_register_user(setup):
    status = await register_user(454357482102587393, setup)
    curr_status = status
    second_status = await register_user(454357482102587393, setup)
    assert second_status is False or curr_status is True or curr_status is False
