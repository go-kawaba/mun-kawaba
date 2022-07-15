import logging
from logging.handlers import RotatingFileHandler

from config import LOG_LEVEL

log = logging.getLogger("hun_kawaba")


def setup_logging():
    logging.getLogger("discord").setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    file_handler = RotatingFileHandler(
        filename="bot.log",
        encoding="utf-8",
        mode="w",
        maxBytes=32 * 1024 * 1024,
        backupCount=5,
    )
    datefmt = "%Y-%m-%d %H:%M:%S"
    fmt = logging.Formatter(
        "[{asctime}] [{levelname}] {name}: {message}", datefmt, style="{"
    )

    file_handler.setFormatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
