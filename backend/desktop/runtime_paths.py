"""Runtime path helpers for packaged ConnLab desktop releases."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "ConnLab"


@dataclass(frozen=True, slots=True)
class PackagedRuntimePaths:
    """Resolved immutable paths used by the portable desktop release."""

    app_root: Path
    frontend_dist: Path
    user_root: Path
    data_dir: Path
    projects_dir: Path
    templates_dir: Path
    logs_dir: Path
    config_dir: Path
    database_path: Path
    local_config_path: Path

    def ensure_user_directories(self) -> None:
        """Create mutable user-data directories without overwriting files."""
        for path in (
            self.user_root,
            self.data_dir,
            self.projects_dir,
            self.templates_dir,
            self.logs_dir,
            self.config_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
        if not self.local_config_path.exists():
            self.local_config_path.write_text(
                "# ConnLab local operator settings.\n"
                "# Keep external workbook, template, and public-drive paths empty "
                "until configured in ConnLab Settings.\n",
                encoding="utf-8",
            )


def is_packaged_runtime() -> bool:
    """Return whether ConnLab is running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def default_app_root() -> Path:
    """Resolve the application resource root for development or packaged mode."""
    if is_packaged_runtime():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)).resolve()
    return Path(__file__).resolve().parents[2]


def default_frontend_dist(app_root: Path | None = None) -> Path:
    """Resolve the built frontend directory bundled with the release."""
    root = app_root or default_app_root()
    packaged_candidate = root / "frontend_dist"
    if packaged_candidate.exists():
        return packaged_candidate.resolve()
    return (root / "frontend" / "dist").resolve()


def default_user_root(app_name: str = APP_NAME) -> Path:
    """Resolve ConnLab's per-user mutable data root."""
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return (Path(local_app_data) / app_name).resolve()
    return (Path.home() / "AppData" / "Local" / app_name).resolve()


def build_packaged_runtime_paths(
    *,
    app_root: Path | None = None,
    frontend_dist: Path | None = None,
    user_root: Path | None = None,
) -> PackagedRuntimePaths:
    """Build the packaged runtime path contract."""
    resolved_app_root = (app_root or default_app_root()).resolve()
    resolved_frontend = (frontend_dist or default_frontend_dist(resolved_app_root)).resolve()
    resolved_user_root = (user_root or default_user_root()).resolve()
    data_dir = resolved_user_root / "data"
    config_dir = resolved_user_root / "config"
    return PackagedRuntimePaths(
        app_root=resolved_app_root,
        frontend_dist=resolved_frontend,
        user_root=resolved_user_root,
        data_dir=data_dir,
        projects_dir=resolved_user_root / "projects",
        templates_dir=resolved_user_root / "templates",
        logs_dir=resolved_user_root / "logs",
        config_dir=config_dir,
        database_path=data_dir / "connlab.sqlite3",
        local_config_path=config_dir / "connlab.local.toml",
    )


def apply_packaged_environment_defaults(paths: PackagedRuntimePaths) -> None:
    """Apply packaged-mode environment defaults without overriding user choices."""
    program_data_root = Path(os.getenv("PROGRAMDATA", r"C:\ProgramData"))
    defaults = {
        "CONNLAB_DATA_DIR": paths.data_dir,
        "CONNLAB_PROJECTS_DIR": paths.projects_dir,
        "CONNLAB_TEMPLATES_DIR": paths.templates_dir,
        "CONNLAB_DATABASE_PATH": paths.database_path,
        "CONNLAB_LOCAL_CONFIG_PATH": paths.local_config_path,
        "CONNLAB_ADMIN_CONFIG_PATH": (
            program_data_root / APP_NAME / "config" / "connlab.admin.toml"
        ),
    }
    for name, value in defaults.items():
        os.environ.setdefault(name, str(value))


def prepare_packaged_runtime_environment(
    paths: PackagedRuntimePaths | None = None,
) -> PackagedRuntimePaths:
    """Create packaged user directories and apply safe environment defaults."""
    runtime_paths = paths or build_packaged_runtime_paths()
    runtime_paths.ensure_user_directories()
    apply_packaged_environment_defaults(runtime_paths)
    return runtime_paths
