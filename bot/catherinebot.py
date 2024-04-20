import os
import signal
from pathlib import Path

import asyncpg
import discord
from aiohttp import ClientSession
from catherinecore import Catherine
from libs.utils.config import CatherineConfig
from libs.utils.handler import KeyboardInterruptHandler
from libs.utils.logger import CatherineLogger

if os.name == "nt":
    from winloop import run
else:
    from uvloop import run

config_path = Path(__file__).parent / "config.yml"
config = CatherineConfig(config_path)

TOKEN = config["bot"]["token"]
POSTGRES_URI = config["postgres"]["uri"]

intents = discord.Intents.default()
intents.members = True


async def main() -> None:
    async with ClientSession() as session, asyncpg.create_pool(
        dsn=POSTGRES_URI, min_size=25, max_size=25, command_timeout=60
    ) as pool:
        async with Catherine(
            config=config,
            intents=intents,
            session=session,
            pool=pool,
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
