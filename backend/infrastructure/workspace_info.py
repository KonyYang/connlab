"""Read-only, allowlisted runtime details from the active SQLAlchemy connection."""
from importlib.metadata import version, PackageNotFoundError
import json
import os
from pathlib import Path
import sys


class WorkspaceInfoReader:
    def __init__(self, session, settings):
        self.session, self.settings = session, settings

    def read(self):
        bind = self.session.get_bind()
        database = bind.url.database
        sqlite = bind.dialect.name == "sqlite"
        user_version = self.session.connection().exec_driver_sql("PRAGMA user_version").scalar() if sqlite else None
        if sqlite:
            # PRAGMA is authoritative even if the engine URL is relative or URI-based.
            rows = self.session.connection().exec_driver_sql("PRAGMA database_list").all()
            database = next((row[2] or ":memory:" for row in rows if row[1] == "main"), database)
        packaged = bool(getattr(sys, "frozen", False))
        root = Path(__file__).resolve().parents[2]
        expected = root / "data" / "connlab.sqlite3"
        mode = "packaged" if packaged else "development"
        if not packaged and database not in {None, ":memory:"} and Path(database).resolve() != expected:
            mode = "custom"
        try:
            application_version = version("connlab")
        except PackageNotFoundError:
            application_version = "unavailable"
        release, release_status = {}, "not_available"
        manifest_path = os.getenv("CONNLAB_RELEASE_MANIFEST_PATH")
        if manifest_path:
            try:
                with Path(manifest_path).open("rb") as handle:
                    raw = handle.read(65537)
                if len(raw) > 65536:
                    raise ValueError("Release metadata too large")
                value = json.loads(raw.decode("utf-8-sig"))
                release = {key: value[key] for key in ("version", "built_at_utc", "git_commit", "release_name", "build_id")
                           if isinstance(value, dict) and isinstance(value.get(key), str) and len(value[key]) <= 255}
                release_status = "available"
            except (ValueError, OSError, UnicodeError):
                release_status = "unavailable"
        config = os.getenv("CONNLAB_LOCAL_CONFIG_PATH") or str(root / "connlab.local.toml")
        config_path = Path(config).expanduser()
        if not config_path.is_absolute():
            config_path = root / config_path
        return {"runtime_mode": mode, "database_path": database, "data_directory": str(self.settings.data_dir),
                "config_path": str(config_path.resolve()), "application_version": application_version,
                "release": release, "release_status": release_status, "sqlite_user_version": user_version,
                "schema_status": "unversioned" if user_version == 0 else "reported_only",
                "notice": "SQLite user_version is not a compatibility guarantee. Keep development/test copies separate; do not share a writable formal database between different program versions. No merge or database switch is performed here."}
