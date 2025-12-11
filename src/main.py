import os
import signal

import asyncpg
from aiohttp import ClientSession

from core import (
    Catherine,
    CatherineConfig,
    CatherineLogger,
    KeyboardInterruptHandler,
    find_config,
)

if os.name == "nt":
    from winloop import run
else:
    from uvloop import run

config = CatherineConfig.load_from_file(find_config())


async def main() -> None:
    async with (
        ClientSession() as session,
        asyncpg.create_pool(
            dsn=config.postgres_uri, min_size=20, max_size=20, command_timeout=60
        ) as pool,
        Catherine(config=config, session=session, pool=pool) as bot,
    ):
        bot.loop.add_signal_handler(signal.SIGTERM, KeyboardInterruptHandler(bot))
        bot.loop.add_signal_handler(signal.SIGINT, KeyboardInterruptHandler(bot))
        await bot.start(config.token)


def launch() -> None:
    with CatherineLogger():
        run(main())


if __name__ == "__main__":
    try:
        launch()
    except KeyboardInterrupt:
        pass
