"""Application settings for the ConnLab backend."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_LOG_LEVEL = "INFO"


@dataclass(frozen=True, slots=True)
class LtrWorkbookSettings:
    """Runtime settings for the optional external LTR workbook."""

    path: Path | None = None
    mode: str = "local_only"
    write_enabled: bool = False
    lock_dir: Path | None = None
    lock_timeout_seconds: int = 120
    backup_dir: Path | None = None
    modify_password: str | None = None
    require_operator_confirmation_for_year_sheet_bootstrap: bool = True
    allow_system_assisted_create_year_sheet: bool = False
    template_sheet_name: str | None = None
    sheet_bootstrap_clear_start_row: int = 2

    def safe_summary(self) -> dict[str, object]:
        """Return settings suitable for logs or diagnostics without secrets."""
        return {
            "path": str(self.path) if self.path else None,
            "mode": self.mode,
            "write_enabled": self.write_enabled,
            "lock_dir": str(self.lock_dir) if self.lock_dir else None,
            "lock_timeout_seconds": self.lock_timeout_seconds,
            "backup_dir": str(self.backup_dir) if self.backup_dir else None,
            "modify_password_configured": self.modify_password is not None,
            "require_operator_confirmation_for_year_sheet_bootstrap": (
                self.require_operator_confirmation_for_year_sheet_bootstrap
            ),
            "allow_system_assisted_create_year_sheet": (
                self.allow_system_assisted_create_year_sheet
            ),
            "template_sheet_name_configured": self.template_sheet_name is not None,
            "sheet_bootstrap_clear_start_row": self.sheet_bootstrap_clear_start_row,
        }


@dataclass(frozen=True, slots=True)
class TestRecordSettings:
    """Runtime settings for Test Record Word generation."""

    __test__ = False
    template_path: Path | None = None


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    data_dir: Path
    projects_dir: Path
    templates_dir: Path
    database_path: Path
    log_level: str = DEFAULT_LOG_LEVEL
    ltr_workbook: LtrWorkbookSettings = field(default_factory=LtrWorkbookSettings)
    test_record: TestRecordSettings = field(default_factory=TestRecordSettings)

    @classmethod
    def load(cls, base_dir: Path | None = None) -> "Settings":
        """Load settings from the environment and ensure required folders exist."""
        root_dir = base_dir or Path(__file__).resolve().parents[2]
        local_config = _load_local_config(root_dir)
        workbook_config = local_config.get("ltr_workbook", {})
        test_record_config = local_config.get("test_record", {})
        settings = cls(
            data_dir=_resolve_directory("CONNLAB_DATA_DIR", root_dir / "data", root_dir),
            projects_dir=_resolve_directory(
                "CONNLAB_PROJECTS_DIR",
                root_dir / "projects",
                root_dir,
            ),
            templates_dir=_resolve_directory(
                "CONNLAB_TEMPLATES_DIR",
                root_dir / "templates",
                root_dir,
            ),
            database_path=_resolve_file_path(
                "CONNLAB_DATABASE_PATH",
                root_dir / "data" / "connlab.sqlite3",
                root_dir,
            ),
            log_level=os.getenv("CONNLAB_LOG_LEVEL", DEFAULT_LOG_LEVEL).strip().upper()
            or DEFAULT_LOG_LEVEL,
            ltr_workbook=_load_ltr_workbook_settings(root_dir, workbook_config),
            test_record=_load_test_record_settings(root_dir, test_record_config),
        )
        settings.ensure_directories()
        return settings

    def ensure_directories(self) -> None:
        """Create configured directories when they do not exist yet."""
        for path in (self.data_dir, self.projects_dir, self.templates_dir):
            path.mkdir(parents=True, exist_ok=True)


def _resolve_directory(env_name: str, default: Path, base_dir: Path) -> Path:
    """Resolve a configured directory from the environment or a default path."""
    raw_value = os.getenv(env_name)
    if not raw_value:
        return default

    candidate = Path(raw_value).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve()


def _resolve_file_path(env_name: str, default: Path, base_dir: Path) -> Path:
    """Resolve a configured file path from the environment or a default path."""
    raw_value = os.getenv(env_name)
    if not raw_value:
        return default

    candidate = Path(raw_value).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve()


def _load_local_config(base_dir: Path) -> dict:
    """Load an optional operator-managed local TOML config."""
    raw_path = os.getenv("CONNLAB_LOCAL_CONFIG_PATH")
    path = Path(raw_path).expanduser() if raw_path else base_dir / "connlab.local.toml"
    if not path.is_absolute():
        path = base_dir / path
    if not path.is_file():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _load_ltr_workbook_settings(
    base_dir: Path,
    config: dict,
) -> LtrWorkbookSettings:
    """Load optional LTR workbook settings from local config and env overrides."""
    return LtrWorkbookSettings(
        path=_optional_path(
            os.getenv("CONNLAB_LTR_WORKBOOK_PATH", str(config.get("path", ""))),
            base_dir,
        ),
        mode=os.getenv("CONNLAB_LTR_WORKBOOK_MODE", str(config.get("mode", "local_only"))),
        write_enabled=_bool_setting(
            os.getenv("CONNLAB_LTR_WORKBOOK_WRITE_ENABLED"),
            bool(config.get("write_enabled", False)),
        ),
        lock_dir=_optional_path(
            os.getenv("CONNLAB_LTR_WORKBOOK_LOCK_DIR", str(config.get("lock_dir", ""))),
            base_dir,
        ),
        lock_timeout_seconds=_positive_int_setting(
            "lock_timeout_seconds",
            os.getenv(
                "CONNLAB_LTR_WORKBOOK_LOCK_TIMEOUT_SECONDS",
                str(config.get("lock_timeout_seconds", 120)),
            ),
        ),
        backup_dir=_optional_path(
            os.getenv("CONNLAB_LTR_WORKBOOK_BACKUP_DIR", str(config.get("backup_dir", ""))),
            base_dir,
        ),
        modify_password=_optional_secret(
            os.getenv(
                "CONNLAB_LTR_WORKBOOK_PASSWORD",
                str(config.get("modify_password", "")),
            )
        ),
        require_operator_confirmation_for_year_sheet_bootstrap=_bool_setting(
            os.getenv("CONNLAB_LTR_WORKBOOK_REQUIRE_BOOTSTRAP_CONFIRMATION"),
            bool(config.get("require_operator_confirmation_for_year_sheet_bootstrap", True)),
        ),
        allow_system_assisted_create_year_sheet=_bool_setting(
            os.getenv("CONNLAB_LTR_WORKBOOK_ALLOW_CREATE_YEAR_SHEET"),
            bool(config.get("allow_system_assisted_create_year_sheet", False)),
        ),
        template_sheet_name=_optional_secret(str(config.get("template_sheet_name", ""))),
        sheet_bootstrap_clear_start_row=_positive_int_setting(
            "sheet_bootstrap_clear_start_row",
            str(config.get("sheet_bootstrap_clear_start_row", 2)),
        ),
    )


def _load_test_record_settings(base_dir: Path, config: dict) -> TestRecordSettings:
    """Load optional Test Record generation settings."""
    raw_path = os.getenv(
        "CONNLAB_TEST_RECORD_TEMPLATE_PATH",
        str(config.get("template_path", "")),
    )
    return TestRecordSettings(
        template_path=_optional_path(raw_path, base_dir),
    )


def _optional_path(value: str, base_dir: Path) -> Path | None:
    """Resolve an optional path string."""
    if not value.strip():
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _optional_secret(value: str) -> str | None:
    """Return a non-empty secret-like string without logging it."""
    stripped = value.strip()
    return stripped or None


def _bool_setting(raw_value: str | None, default: bool) -> bool:
    """Parse a boolean config value."""
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _positive_int_setting(name: str, raw_value: str) -> int:
    """Parse a positive integer local setting."""
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer.") from exc
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return value
