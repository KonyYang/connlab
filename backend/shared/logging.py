"""Logging setup helpers for the ConnLab backend."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_MANAGED_HANDLER_ATTRIBUTE = "_connlab_packaged_handler"


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


def configure_packaged_logging(
    *,
    log_path: Path,
    level: str = "INFO",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """Configure process-wide console and rotating-file logging for packaged runs."""
    root_logger = logging.getLogger()
    root_logger.setLevel(_resolve_level(level))

    for handler in list(root_logger.handlers):
        if getattr(handler, _MANAGED_HANDLER_ATTRIBUTE, False):
            root_logger.removeHandler(handler)
            handler.close()

    formatter = logging.Formatter(LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    setattr(console_handler, _MANAGED_HANDLER_ATTRIBUTE, True)
    root_logger.addHandler(console_handler)

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
    except OSError as exc:
        root_logger.warning("Persistent runtime logging is unavailable: %s", exc)
        return root_logger

    file_handler.setFormatter(formatter)
    setattr(file_handler, _MANAGED_HANDLER_ATTRIBUTE, True)
    root_logger.addHandler(file_handler)

    return root_logger


def _resolve_level(level: str) -> int:
    """Translate a string log level into the stdlib logging constant."""
    normalized_level = level.strip().upper()
    return getattr(logging, normalized_level, logging.INFO)
