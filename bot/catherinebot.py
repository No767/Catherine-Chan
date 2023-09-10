import asyncio
import os
from pathlib import Path

import asyncpg
import discord
from aiohttp import ClientSession
from catherinecore import Catherine
from dotenv import load_dotenv
from libs.utils import CatherineLogger, read_env

# Only used for Windows development
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

load_dotenv()

ENV_PATH = Path(__file__).parent / ".env"

TOKEN = os.environ["TOKEN"]
DEV_MODE = os.getenv("DEV_MODE") in ("True", "TRUE")
IPC_SECRET_KEY = os.environ["IPC_SECRET_KEY"]
IPC_HOST = os.environ["IPC_HOST"]
POSTGRES_URI = os.environ["POSTGRES_URI"]


intents = discord.Intents.default()
if DEV_MODE is True:
    intents.message_content = True


async def main() -> None:
    async with ClientSession() as session, asyncpg.create_pool(
        dsn=POSTGRES_URI, min_size=25, max_size=25, command_timeout=60
    ) as pool:
        async with Catherine(
            config=read_env(ENV_PATH),
            ipc_secret_key=IPC_SECRET_KEY,
            ipc_host=IPC_HOST,
            intents=intents,
            session=session,
            pool=pool,
            dev_mode=DEV_MODE,
        ) as bot:
            await bot.start(TOKEN)


def launch() -> None:
    with CatherineLogger():
        asyncio.run(main())


if __name__ == "__main__":
    try:
        launch()
    except KeyboardInterrupt:
        pass
