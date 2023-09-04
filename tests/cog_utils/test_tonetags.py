import sys
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))
import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from libs.cog_utils.tonetags import (
    create_tonetag,
    edit_tonetag,
    format_options,
    get_tonetags,
    parse_tonetag,
)

load_dotenv(dotenv_path=another_path.joinpath(".env"))

POSTGRES_URI = os.environ["POSTGRES_URI"]

import asyncpg


@pytest_asyncio.fixture
async def setup():
    async with asyncpg.create_pool(dsn=POSTGRES_URI) as pool:
        yield pool


def test_parse_tonetag():
    tag = "/j"
    parsed_tonetag = parse_tonetag(tag)
    assert parsed_tonetag == "j"


def test_format_options():
    rows = [{"indicator": "j"}, {"indicator": "k"}]
    assert (
        format_options(None) == "No tonetags found"
        and format_options([]) == "No tonetags found"
    )
    names = "\n".join([row["indicator"] for row in rows])
    final_str = f"Tonetag not found. Did you mean:\n{names}"
    assert format_options(rows) == final_str


@pytest.mark.asyncio
async def test_create_tonetag(setup):
    defs = {"indicator": "j", "definition": "joking", "author_id": 454357482102587393}
    status = await create_tonetag(
        defs["indicator"], defs["definition"], defs["author_id"], setup
    )
    status_again = await create_tonetag(
        defs["indicator"], defs["definition"], defs["author_id"], setup
    )
    assert (status == "Tonetag `j` successfully created") or (
        status_again == "The tonetag `j` already exists"
    )


@pytest.mark.asyncio
async def test_edit_tonetag(setup):
    query = """
    SELECT definition
    FROM tonetags
    WHERE indicator = $1 AND author_id = $2;
    """
    exists_query = (
        "SELECT EXISTS(SELECT 1 FROM tonetags WHERE indicator = $1 AND author_id = $2);"
    )
    defs = {
        "indicator": "j",
        "definition": "joking again",
        "author_id": 454357482102587393,
    }

    does_exists = await setup.fetchval(
        exists_query, defs["indicator"], defs["author_id"]
    )
    if does_exists is False:
        await create_tonetag(defs["indicator"], "joking", defs["author_id"], setup)
    old_def = await setup.fetchval(query, defs["indicator"], defs["author_id"])
    status = await edit_tonetag(
        defs["indicator"], defs["definition"], defs["author_id"], setup
    )
    assert (status[-1] != "0") or (old_def != defs["definition"])


@pytest.mark.asyncio
async def test_get_tonetags(setup):
    new_def = {
        "indicator": "jkk",
        "definition": "joking and kidding",
        "author_id": 454357482102587393,
    }
    await create_tonetag(
        new_def["indicator"], new_def["definition"], new_def["author_id"], setup
    )

    res = await get_tonetags("j", setup)
    assert len(res) != 0 and res[0]["indicator"] == "j"

    new_res = await get_tonetags("kop", setup)
    assert new_res is None

    res_again = await get_tonetags("jkkkkklmao", setup)

    assert "Tonetag not found. Did you mean:" in res_again
