"""Synchronize LTR workbook Settings paths into local runtime config."""

from __future__ import annotations

import os
from pathlib import Path


class LtrWorkbookLocalConfigSyncError(ValueError):
    """Raised when ConnLab cannot update local LTR workbook config."""


class LtrWorkbookLocalConfigService:
    """Maintain non-secret LTR workbook config required by write workflows."""

    def __init__(self, *, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path(__file__).resolve().parents[2]

    def sync_workbook_path(self, workbook_path: Path) -> None:
        """Persist the selected LTR workbook path without overwriting user secrets."""
        target = workbook_path.expanduser()
        if not target.is_absolute():
            target = (self._base_dir / target).resolve()

        config_path = _local_config_path(self._base_dir)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        defaults_root = _default_runtime_root(config_path, self._base_dir)
        lock_dir = defaults_root / "locks"
        backup_dir = defaults_root / "backups"
        lock_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.mkdir(parents=True, exist_ok=True)

        source = config_path.read_text(encoding="utf-8") if config_path.is_file() else ""
        updated = _upsert_ltr_workbook_keys(
            source,
            replace={
                "path": _quoted_path(target),
            },
            insert_if_missing={
                "mode": '"excel_com"',
                "write_enabled": "true",
                "lock_dir": _quoted_path(lock_dir),
                "backup_dir": _quoted_path(backup_dir),
            },
        )
        config_path.write_text(updated, encoding="utf-8")


def _local_config_path(base_dir: Path) -> Path:
    raw_path = os.getenv("CONNLAB_LOCAL_CONFIG_PATH")
    path = Path(raw_path).expanduser() if raw_path else base_dir / "connlab.local.toml"
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _default_runtime_root(config_path: Path, base_dir: Path) -> Path:
    if config_path.parent.name.lower() == "config":
        return config_path.parent.parent
    return base_dir


def _upsert_ltr_workbook_keys(
    source: str,
    *,
    replace: dict[str, str],
    insert_if_missing: dict[str, str],
) -> str:
    lines = source.splitlines()
    section_index = _find_section(lines, "ltr_workbook")
    if section_index is None:
        prefix = "\n" if lines and lines[-1].strip() else ""
        body = [
            "[ltr_workbook]",
            *[f"{key} = {value}" for key, value in replace.items()],
            *[f"{key} = {value}" for key, value in insert_if_missing.items()],
        ]
        return f"{source.rstrip()}{prefix}" + "\n".join(body) + "\n"

    next_section = _find_next_section(lines, section_index + 1)
    existing = {
        _setting_key(lines[index]): index
        for index in range(section_index + 1, next_section)
        if _setting_key(lines[index]) is not None
    }
    for key, value in replace.items():
        line = f"{key} = {value}"
        if key in existing:
            lines[existing[key]] = line
        else:
            lines.insert(next_section, line)
            next_section += 1
    for key, value in insert_if_missing.items():
        if key not in existing:
            lines.insert(next_section, f"{key} = {value}")
            next_section += 1
    return "\n".join(lines).rstrip() + "\n"


def _setting_key(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    return stripped.split("=", 1)[0].strip()


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


def _quoted_path(path: Path) -> str:
    return f'"{path.as_posix().replace(chr(34), chr(92) + chr(34))}"'
