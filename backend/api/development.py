"""Uvicorn development factory; configure logging in each reload worker."""
import os
from pathlib import Path

from backend.shared.logging import configure_packaged_logging


def apply_development_environment_defaults(root: Path) -> None:
    from backend.shared.runtime_environment import apply_entry_defaults, prepare_entry_config, configured_library_root
    base = {"CONNLAB_LOCAL_CONFIG_PATH": root / "connlab.local.toml", "CONNLAB_ADMIN_CONFIG_PATH": root / "connlab.admin.toml"}
    configured = prepare_entry_config("development", base)
    library = configured_library_root(configured)
    defaults = {**base, "CONNLAB_DATA_DIR": library / "Data" if library else root / "data",
                "CONNLAB_DATABASE_PATH": library / "Data/connlab.sqlite3" if library else root / "data/connlab.sqlite3",
                "CONNLAB_LOGS_DIR": library / "Logs" if library else root / "logs"}
    if library:
        defaults["CONNLAB_LIBRARY_ROOT"] = library
    apply_entry_defaults("development", defaults)


def create_app():
    root = Path(__file__).resolve().parents[2]
    apply_development_environment_defaults(root)
    default_logs = root / "logs"
    logs_dir = Path(os.environ.get("CONNLAB_LOGS_DIR") or default_logs).resolve()
    # The export endpoint must read the very directory the file handler writes.
    os.environ["CONNLAB_LOGS_DIR"] = str(logs_dir)
    logger = configure_packaged_logging(
        log_path=logs_dir / "connlab.log",
        level=os.environ.get("CONNLAB_LOG_LEVEL") or "INFO",
    )
    logger.info("Development runtime logging initialized.")
    from backend.shared.config import Settings
    from backend.shared.runtime_environment import configure_process_temporary_storage
    configure_process_temporary_storage(Settings.load(base_dir=root))
    from backend.api.main import app
    from backend.api.runtime_binding import initialize_runtime_binding
    initialize_runtime_binding(app)

    return app
