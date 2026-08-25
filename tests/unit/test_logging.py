import logging
from pathlib import Path

import pytest

from backend.shared import logging as logging_helpers
from backend.shared.logging import configure_logging, configure_packaged_logging


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


def test_configure_packaged_logging_persists_and_rotates_runtime_logs(
    tmp_path: Path,
) -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    root.handlers.clear()
    try:
        log_path = tmp_path / "logs" / "connlab.log"
        configured_once = configure_packaged_logging(
            log_path=log_path,
            level="info",
            max_bytes=160,
            backup_count=2,
        )
        configured_twice = configure_packaged_logging(
            log_path=log_path,
            level="info",
            max_bytes=160,
            backup_count=2,
        )

        configured_twice.info("runtime diagnostic message %s", "A" * 120)
        configured_twice.info("runtime diagnostic message %s", "B" * 120)
        for handler in configured_twice.handlers:
            handler.flush()

        assert configured_once is configured_twice
        assert log_path.is_file()
        assert (tmp_path / "logs" / "connlab.log.1").is_file()
        assert len(configured_twice.handlers) == 2
    finally:
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()
        root.handlers.extend(original_handlers)
        root.setLevel(original_level)


def test_configure_packaged_logging_falls_back_to_console_when_file_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    root.handlers.clear()

    def fail_file_handler(*args, **kwargs):
        raise PermissionError("log file unavailable")

    monkeypatch.setattr(logging_helpers, "RotatingFileHandler", fail_file_handler)
    try:
        configured = configure_packaged_logging(log_path=tmp_path / "connlab.log")
        assert len(configured.handlers) == 1
        assert isinstance(configured.handlers[0], logging.StreamHandler)
    finally:
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()
        root.handlers.extend(original_handlers)
        root.setLevel(original_level)
