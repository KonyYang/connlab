import logging

from backend.shared.logging import configure_logging


def test_configure_logging_is_idempotent() -> None:
    logger_name = "connlab.tests.logging"
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()

    configured_once = configure_logging(logger_name=logger_name, level="debug")
    configured_twice = configure_logging(logger_name=logger_name, level="debug")

    assert configured_once is configured_twice
    assert configured_once.level == logging.DEBUG
    assert len(configured_once.handlers) == 1

    logger.handlers.clear()
