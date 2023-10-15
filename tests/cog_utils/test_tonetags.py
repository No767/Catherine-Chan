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
    format_similar_tonetags,
    get_exact_and_similar_tonetags,
    get_tonetag,
    get_tonetag_info,
    get_top_tonetags,
    parse_tonetag,
    validate_tonetag,
)

load_dotenv(dotenv_path=another_path.joinpath(".env"))

POSTGRES_URI = os.environ["POSTGRES_URI"]

import asyncpg


@pytest_asyncio.fixture
async def setup():
    async with asyncpg.create_pool(dsn=POSTGRES_URI) as pool:
        yield pool


def test_validate_tonetag():
    tag = "/j"
    parsed_tonetag = parse_tonetag(tag)
    assert validate_tonetag(parsed_tonetag) is True

    second_tag = parse_tonetag("/srs")
    assert validate_tonetag(second_tag) is True

    another_tag = "fsdoubfosydfbsiydfsf"
    parsed_another_tag = parse_tonetag(another_tag)
    assert validate_tonetag(parsed_another_tag) is False

    third_tag = "jf3"
    assert validate_tonetag(parse_tonetag(third_tag)) is False

    fourth_tag = "j3."
    assert validate_tonetag(parse_tonetag(fourth_tag)) is False

    sus_word_tag = "sex"
    assert validate_tonetag(parse_tonetag(sus_word_tag)) is False


def test_parse_tonetag():
    tag = "/j"
    parsed_tonetag = parse_tonetag(tag)
    assert parsed_tonetag == "j"


def test_format_similar_tonetags():
    rows = [{"indicator": "j"}, {"indicator": "k"}]
    assert (
        format_similar_tonetags(None) == "No tonetags found"
        and format_similar_tonetags([]) == "No tonetags found"
    )
    names = "\n".join([row["indicator"] for row in rows])
    final_str = f"Tonetag not found. Did you mean:\n{names}"
    assert format_similar_tonetags(rows) == final_str


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
async def test_get_tonetag(setup):
    exists_query = (
        "SELECT EXISTS(SELECT 1 FROM tonetags WHERE indicator = $1 AND author_id = $2);"
    )

    defs = {
        "indicator": "pkpk",
        "definition": "pokpok",
        "author_id": 454357482102587393,
    }
    new_def = {
        "indicator": "pkpkf",
        "definition": "something",
        "author_id": 454357482102587393,
    }
    does_exists = await setup.fetchval(
        exists_query, defs["indicator"], defs["author_id"]
    )

    if does_exists is False:
        await create_tonetag(
            defs["indicator"], defs["definition"], defs["author_id"], setup
        )

    new_def_res = await create_tonetag(
        new_def["indicator"], new_def["definition"], new_def["author_id"], setup
    )

    assert (
        new_def_res == "Tonetag `pkpkf` successfully created"
        or new_def_res == "The tonetag `pkpkf` already exists"
    )

    res = await get_tonetag("pkpk", setup)
    assert (
        isinstance(res, dict)
        and res["indicator"] == "pkpk"
        and res["author_id"] == 454357482102587393
    )

    second_res = await get_tonetag("pkpkd", setup)

    assert second_res[1]["indicator"] == new_def["indicator"]

    third_res = await get_tonetag("pfffsdfnsod", setup)
    assert third_res is None


@pytest.mark.asyncio
async def test_get_tonetag_info(setup):
    indicator = "pkpk"
    author_id = 454357482102587393
    definition = "pokpok"

    tt_info = await get_tonetag_info(indicator, setup)

    assert (
        tt_info["indicator"] == indicator
        and tt_info["author_id"] == author_id
        and tt_info["definition"] == definition
    )

    tt_info_none = await get_tonetag_info("sfdosihfbsodubsoufdosudbfsoudfbsoub", setup)
    assert tt_info_none is None


@pytest.mark.asyncio
async def test_get_exact_and_similar_tonetags(setup):
    author_id = 454357482102587393
    exact_result = {
        "indicator": "pkpk",
        "definition": "pokpok",
    }
    similar_result = {
        "indicator": "pkpkf",
        "definition": "something",
    }

    exists_query = (
        "SELECT EXISTS(SELECT 1 FROM tonetags WHERE indicator = $1 AND author_id = $2);"
    )

    async with setup.acquire() as conn:
        exact_does_exists = await conn.fetchval(
            exists_query, exact_result["indicator"], author_id
        )
        similar_does_exists = await conn.fetchval(
            exists_query, similar_result["indicator"], author_id
        )

        if exact_does_exists is False or similar_does_exists is False:
            await create_tonetag(
                exact_result["indicator"], exact_result["definition"], author_id, setup
            )
            await create_tonetag(
                similar_result["indicator"],
                similar_result["definition"],
                author_id,
                setup,
            )

        exact_res = await get_exact_and_similar_tonetags(
            exact_result["indicator"], setup
        )
        assert exact_res[0] == exact_result and exact_res[1] == similar_result

        no_res = await get_exact_and_similar_tonetags("fspudfpsubufyeeeSOF", setup)
        assert no_res is None


@pytest.mark.asyncio
async def test_get_top_tonetags(setup):
    init_res = await get_top_tonetags(setup)
    assert isinstance(init_res, list)
