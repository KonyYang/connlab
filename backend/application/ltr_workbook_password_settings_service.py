"""Local settings update service for the LTR workbook password."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from backend.shared.config import Settings


class LtrWorkbookPasswordSettingsError(ValueError):
    """Raised when the LTR workbook password setting cannot be updated."""


@dataclass(frozen=True, slots=True)
class LtrWorkbookPasswordStatus:
    """Status and current value for the configured LTR workbook password."""

    configured: bool
    overridden_by_environment: bool = False
    password: str | None = None


class LtrWorkbookPasswordSettingsService:
    """Read and update the local LTR workbook password setting."""

    def __init__(self, *, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path(__file__).resolve().parents[2]

    def status(self) -> LtrWorkbookPasswordStatus:
        """Return the current effective password for the local Settings page editor."""
        settings = Settings.load(base_dir=self._base_dir)
        password = settings.ltr_workbook.modify_password or None
        return LtrWorkbookPasswordStatus(
            configured=bool(password),
            overridden_by_environment=_env_password_configured(),
            password=password,
        )

    def update_password(
        self,
        password: str,
        *,
        operator_confirmed: bool,
    ) -> LtrWorkbookPasswordStatus:
        """Update the local config password after explicit operator confirmation."""
        secret = password.strip()
        if not operator_confirmed:
            raise LtrWorkbookPasswordSettingsError("Confirm password update before saving.")
        if not secret:
            raise LtrWorkbookPasswordSettingsError("LTR workbook password cannot be blank.")
        path = _local_config_path(self._base_dir)
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            _upsert_ltr_workbook_secret(current, "modify_password", secret),
            encoding="utf-8",
        )
        return self.status()


def _local_config_path(base_dir: Path) -> Path:
    raw_path = os.getenv("CONNLAB_LOCAL_CONFIG_PATH")
    path = Path(raw_path).expanduser() if raw_path else base_dir / "connlab.local.toml"
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _env_password_configured() -> bool:
    return bool(os.getenv("CONNLAB_LTR_WORKBOOK_PASSWORD", "").strip())


def _upsert_ltr_workbook_secret(source: str, key: str, value: str) -> str:
    """Return TOML text with one [ltr_workbook] secret key updated."""
    lines = source.splitlines()
    secret_line = f'{key} = "{_toml_escape(value)}"'
    section_index = _find_section(lines, "ltr_workbook")
    if section_index is None:
        prefix = "\n" if lines and lines[-1].strip() else ""
        return f"{source.rstrip()}{prefix}[ltr_workbook]\n{secret_line}\n"

    next_section = _find_next_section(lines, section_index + 1)
    for index in range(section_index + 1, next_section):
        stripped = lines[index].strip()
        if stripped.startswith(f"{key} ") or stripped.startswith(f"{key}="):
            lines[index] = secret_line
            return "\n".join(lines).rstrip() + "\n"
    lines.insert(next_section, secret_line)
    return "\n".join(lines).rstrip() + "\n"


def _find_section(lines: list[str], section: str) -> int | None:
    target = f"[{section}]"
    for index, line in enumerate(lines):
        if line.strip() == target:
            return index
    return None


def _find_next_section(lines: list[str], start: int) -> int:
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            return index
    return len(lines)


def _toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
