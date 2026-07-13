"""Logging configuration.

``setup_logging`` is called exactly once, during application startup. Every
other module obtains its own logger via ``logging.getLogger(__name__)`` —
this keeps log output attributable to the subsystem that produced it,
per the coding standards ("Every subsystem owns its own logger").
"""

import logging
import sys

from app.core.config import Settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(settings: Settings) -> None:
    """Configure the root logger for the whole application.

    Args:
        settings: Application settings, used to determine log verbosity.
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Third-party libraries are noisy at INFO/DEBUG; keep them at WARNING
    # unless we are explicitly debugging the app itself.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
