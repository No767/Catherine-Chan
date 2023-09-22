from typing import Any, Dict, List, Union

import asyncpg
from libs.cog_utils.commons import register_user

from .utils import format_options, parse_tonetag


async def get_tonetags(
    indicator: str, pool: asyncpg.Pool
) -> Union[str, List[Dict[str, Any]], None]:
    query = """
    SELECT tonetags_lookup.indicator, tonetags.definition, tonetags.created_at, tonetags.author_id, tonetags_lookup.tonetags_id
    FROM tonetags_lookup
    INNER JOIN tonetags ON tonetags.id = tonetags_lookup.tonetags_id
    WHERE LOWER(tonetags_lookup.indicator) = $1
    LIMIT 100;
    """
    parsed_tonetag = parse_tonetag(indicator)
    async with pool.acquire() as conn:
        res = await conn.fetch(query, parsed_tonetag)
        if len(res) == 0:
            query = """
            SELECT tonetags_lookup.indicator
            FROM tonetags_lookup
            WHERE tonetags_lookup.indicator % $1
            ORDER BY similarity(tonetags_lookup.indicator, $1) DESC
            LIMIT 5;
            """
            new_res = await conn.fetch(query, parsed_tonetag)
            if len(new_res) == 0:
                return None

            return format_options([dict(row) for row in new_res])
        return [dict(row) for row in res]


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
