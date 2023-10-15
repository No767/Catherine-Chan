from typing import List, Union

import asyncpg
from libs.cog_utils.commons import register_user

from .structs import (
    ExactAndSimilarTonetags,
    SimilarTonetags,
    StatsBareToneTag,
    TonetagInfo,
)
from .utils import parse_tonetag


async def get_exact_and_similar_tonetags(
    indicator: str, pool: asyncpg.Pool
) -> Union[List[ExactAndSimilarTonetags], None]:
    query = """
    SELECT indicator, definition
    FROM tonetags
    WHERE tonetags.indicator % $1
    ORDER BY similarity(indicator, $1) DESC
    LIMIT 100;
    """
    records = await pool.fetch(query, indicator)
    if len(records) == 0:
        return None
    return [ExactAndSimilarTonetags(record) for record in records]


async def get_tonetag_info(
    indicator: str, pool: asyncpg.Pool
) -> Union[TonetagInfo, None]:
    query = """
    SELECT tonetags_lookup.indicator, tonetags.definition, tonetags.created_at, tonetags.author_id, tonetags.uses, tonetags_lookup.tonetags_id
    FROM tonetags_lookup
    INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
    WHERE LOWER(tonetags_lookup.indicator) = $1;
    """
    parsed_tonetag = parse_tonetag(indicator)
    result = await pool.fetchrow(query, parsed_tonetag)
    if result is None:
        return None
    return TonetagInfo(result)


async def get_tonetag(
    indicator: str, pool: asyncpg.Pool
) -> Union[TonetagInfo, List[SimilarTonetags], None]:
    query = """
    SELECT tonetags_lookup.indicator, tonetags.definition, tonetags.created_at, tonetags.author_id, tonetags.uses, tonetags_lookup.tonetags_id
    FROM tonetags_lookup
    INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
    WHERE LOWER(tonetags_lookup.indicator) = $1;
    """
    update_query = """
    UPDATE tonetags
    SET uses = uses + 1
    WHERE id = $1;
    """
    parsed_tonetag = parse_tonetag(indicator)
    async with pool.acquire() as conn:
        first_result = await conn.fetchrow(query, parsed_tonetag)
        if first_result is None:
            search_query = """
            SELECT tonetags_lookup.indicator
            FROM tonetags_lookup
            WHERE tonetags_lookup.indicator % $1
            ORDER BY similarity(tonetags_lookup.indicator, $1) DESC
            LIMIT 5;
            """
            search_result = await conn.fetch(search_query, parsed_tonetag)
            if len(search_result) == 0:
                return None
            return [SimilarTonetags(row) for row in search_result]

        await conn.execute(update_query, first_result["tonetags_id"])
        return TonetagInfo(first_result)


async def get_top_tonetags(pool: asyncpg.Pool) -> List[StatsBareToneTag]:
    query = """
    SELECT tonetags_lookup.indicator, tonetags.uses, tonetags_lookup.tonetags_id
    FROM tonetags_lookup
    INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
    ORDER BY tonetags.uses DESC
    LIMIT 100;
    """
    records = await pool.fetch(query)
    return [StatsBareToneTag(row) for row in records]


async def edit_tonetag(
    indicator: str, definition: str, author_id: int, pool: asyncpg.Pool
) -> str:
    query = """
    UPDATE tonetags
    SET definition = $2
    WHERE indicator = $1 AND author_id = $3;
    """
    status = await pool.execute(query, indicator, definition, author_id)
    return status


async def create_tonetag(
    indicator: str, definition: str, author_id: int, pool: asyncpg.Pool
) -> str:
    query = """
    WITH tonetag_insert AS (
        INSERT INTO tonetags (indicator, definition, author_id)
        VALUES ($1, $2, $3)
        RETURNING id
    )
    INSERT INTO tonetags_lookup (indicator, author_id, tonetags_id)
    VALUES ($1, $3, (SELECT id FROM tonetag_insert));
    """
    async with pool.acquire() as conn:
        await register_user(author_id, conn)
        tr = conn.transaction()
        await tr.start()

        try:
            await conn.execute(
                query, parse_tonetag(indicator.lower()), definition.lower(), author_id
            )
        except asyncpg.UniqueViolationError:
            await tr.rollback()
            return f"The tonetag `{indicator}` already exists"
        else:
            await tr.commit()
            return f"Tonetag `{indicator}` successfully created"
