"""Application settings for the ConnLab backend."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_LOG_LEVEL = "INFO"


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    data_dir: Path
    projects_dir: Path
    templates_dir: Path
    database_path: Path
    log_level: str = DEFAULT_LOG_LEVEL

    @classmethod
    def load(cls, base_dir: Path | None = None) -> "Settings":
        """Load settings from the environment and ensure required folders exist."""
        root_dir = base_dir or Path(__file__).resolve().parents[2]
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
