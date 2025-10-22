from sys import stderr

from loguru import logger


def logger_settings(level: str = "WARNING"):
    logger.remove()
    logger.add(
        stderr,
        level=level,
        backtrace=level in ("TRACE", "DEBUG"),
        diagnose=False,
    )
