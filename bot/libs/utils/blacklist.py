from typing import Dict, Optional

import asyncpg


async def load_blacklist(pool: asyncpg.Pool) -> Dict[int, bool]:
    """Loads the global blacklist into cache from the database

    Args:
        pool (asyncpg.Pool): A global connection pool

    Returns:
        Dict[int, str]: The cached mapping. Will be a 1:1 mapping of the data from the database.
    """
    query = """
    SELECT id, blacklist_status
    FROM blacklist;
    """
    records = await pool.fetch(query)
    return {record["id"]: record["blacklist_status"] for record in records}


# Circular import so bot is untyped
async def get_or_fetch_blacklist(bot, id: int, pool: asyncpg.Pool) -> bool:
    """Gets or fetches a user's blacklist status

    Args:
        bot (Catherine): The bot instance
        id (int): The user's ID
        pool (asyncpg.Pool): A global connection pool

    Returns:
        bool: The user's blacklist status
    """
    if id in bot.blacklist_cache:
        return bot.blacklist_cache[id]

    query = """
    SELECT blacklist_status
    FROM blacklist
    WHERE id = $1;
    """
    record = await pool.fetchrow(query, id)
    if record is None:
        return False
    bot.blacklist_cache[id] = record["blacklist_status"]
    return record["blacklist_status"]


async def get_or_fetch_full_blacklist(
    bot, pool: asyncpg.Pool
) -> Optional[Dict[int, bool]]:
    cache = bot.blacklist_cache

    # We can guarantee these to be 1:1 mappings
    if len(cache) != 0:
        return cache

    query = """
    SELECT id, blacklist_status
    FROM blacklist;
    """
    records = await pool.fetch(query)
    if len(records) == 0:
        return None

    converted_records = {record["id"]: record["blacklist_status"] for record in records}
    bot.replace_blacklist_cache(converted_records)
    return converted_records
