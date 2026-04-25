"""Logging setup helpers for the ConnLab backend."""

from __future__ import annotations

import logging


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(
    logger_name: str = "connlab",
    level: str = "INFO",
) -> logging.Logger:
    """Create or update a named logger without duplicating handlers."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(_resolve_level(level))
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    return logger


def _resolve_level(level: str) -> int:
    """Translate a string log level into the stdlib logging constant."""
    normalized_level = level.strip().upper()
    return getattr(logging, normalized_level, logging.INFO)
