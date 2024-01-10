import os
import signal
from pathlib import Path

import asyncpg
import discord
from aiohttp import ClientSession
from catherinecore import Catherine
from dotenv import load_dotenv
from libs.utils import CatherineLogger, KeyboardInterruptHandler, read_env

if os.name == "nt":
    from winloop import run
else:
    from uvloop import run

load_dotenv()

ENV_PATH = Path(__file__).parent / ".env"

TOKEN = os.environ["TOKEN"]
DEV_MODE = os.getenv("DEV_MODE") in ("True", "TRUE")
IPC_SECRET_KEY = os.environ["IPC_SECRET_KEY"]
IPC_HOST = os.environ["IPC_HOST"]
POSTGRES_URI = os.environ["POSTGRES_URI"]

intents = discord.Intents.default()
intents.members = True


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
            bot.loop.add_signal_handler(signal.SIGTERM, KeyboardInterruptHandler(bot))
            bot.loop.add_signal_handler(signal.SIGINT, KeyboardInterruptHandler(bot))
            await bot.start(TOKEN)


def launch() -> None:
    with CatherineLogger():
        run(main())


if __name__ == "__main__":
    try:
        launch()
    except KeyboardInterrupt:
        pass
