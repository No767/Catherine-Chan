import asyncpg


async def register_user(user_id: int, conn: asyncpg.connection.Connection) -> bool:
    query = """
    INSERT INTO catherine_users (id)
    VALUES ($1)
    ON CONFLICT (id) DO NOTHING;
    """
    status = await conn.execute(query, user_id)
    if status[-1] != "0":
        return True
    return False
