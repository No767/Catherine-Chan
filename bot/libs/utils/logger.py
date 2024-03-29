import logging
from logging.handlers import RotatingFileHandler
from types import TracebackType
from typing import Optional, Type, TypeVar

import discord

BE = TypeVar("BE", bound=BaseException)


class CatherineLogger:
    def __init__(self) -> None:
        self.self = self
        self.log = logging.getLogger("catherine")

    def __enter__(self) -> None:
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        self.log.setLevel(logging.INFO)
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        handler = RotatingFileHandler(
            filename="catherine.log",
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=5,
        )
        fmt = logging.Formatter(
            fmt="%(asctime)s %(levelname)s    %(message)s",
            datefmt="[%Y-%m-%d %H:%M:%S]",
        )
        handler.setFormatter(fmt)
        self.log.addHandler(handler)
        discord.utils.setup_logging(formatter=fmt)

    def __exit__(
        self,
        exc_type: Optional[Type[BE]],
        exc: Optional[BE],
        traceback: Optional[TracebackType],
    ) -> None:
        self.log.info("Shutting down Catherine...")
        handlers = self.log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            self.log.removeHandler(hdlr)
