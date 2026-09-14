"""Uvicorn development factory; configure logging in each reload worker."""
import os
from pathlib import Path

from backend.shared.logging import configure_packaged_logging


def create_app():
    default_logs = Path(__file__).resolve().parents[2] / "logs"
    logs_dir = Path(os.environ.get("CONNLAB_LOGS_DIR") or default_logs).resolve()
    # The export endpoint must read the very directory the file handler writes.
    os.environ["CONNLAB_LOGS_DIR"] = str(logs_dir)
    logger = configure_packaged_logging(
        log_path=logs_dir / "connlab.log",
        level=os.environ.get("CONNLAB_LOG_LEVEL") or "INFO",
    )
    logger.info("Development runtime logging initialized.")
    from backend.api.main import app

    return app
