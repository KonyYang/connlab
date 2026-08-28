"""Conservative filesystem operations for direct Test Record publication."""

from __future__ import annotations

from datetime import datetime
import hashlib
import os
from pathlib import Path
import shutil
from typing import Callable
from uuid import uuid4


class TestRecordPublicationTargetChangedError(RuntimeError):
    """Raised when the previewed target changes before publication."""


class TestRecordPublicationGateway:
    """Publish a staged project output without silently overwriting an operator file."""

    def __init__(
        self,
        recycle_file: Callable[[Path], None] | None = None,
        *,
        resource_label: str = "Test Record",
    ) -> None:
        self._recycle_file = recycle_file or _move_to_windows_recycle_bin
        self._resource_label = resource_label

    def fingerprint(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def publish(
        self,
        *,
        staged_path: Path,
        target_path: Path,
        conflict_action: str,
        history_dir: Path,
        expected_target_fingerprint: str | None,
    ) -> Path | None:
        staged = Path(staged_path)
        target = Path(target_path)
        if not staged.is_file():
            raise FileNotFoundError(f"Staged {self._resource_label} is missing: {staged}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if expected_target_fingerprint is None:
            if target.exists():
                raise TestRecordPublicationTargetChangedError(
                    f"{self._resource_label} target appeared after preview: {target}"
                )
            self._place_new_file(staged, target)
            return None
        if not target.is_file() or self.fingerprint(target) != expected_target_fingerprint:
            raise TestRecordPublicationTargetChangedError(
                f"{self._resource_label} target changed after preview: {target}"
            )
        if conflict_action == "archive":
            return self._archive_and_replace(staged, target, history_dir)
        if conflict_action == "recycle":
            self._recycle_and_replace(staged, target)
            return None
        raise ValueError(
            f"Unsupported {self._resource_label} conflict action: {conflict_action}"
        )

    def _archive_and_replace(
        self, staged: Path, target: Path, history_dir: Path
    ) -> Path:
        history_dir.mkdir(parents=True, exist_ok=True)
        archive = _unique_archive_path(
            target,
            history_dir,
            resource_label=self._resource_label,
        )
        os.replace(target, archive)
        try:
            self._place_new_file(staged, target)
        except Exception:
            if not target.exists() and archive.exists():
                os.replace(archive, target)
            raise
        return archive

    def _recycle_and_replace(self, staged: Path, target: Path) -> None:
        rollback = target.with_name(f".{target.name}.connlab-rollback-{uuid4().hex}.tmp")
        shutil.copy2(target, rollback)
        try:
            self._recycle_file(target)
            if target.exists():
                raise RuntimeError(f"Recycle Bin operation did not remove: {target}")
            self._place_new_file(staged, target)
        except Exception:
            if not target.exists() and rollback.exists():
                os.replace(rollback, target)
            raise
        finally:
            if rollback.exists():
                rollback.unlink()

    def _place_new_file(self, staged: Path, target: Path) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        descriptor = os.open(target, flags)
        try:
            with staged.open("rb") as source, os.fdopen(descriptor, "wb") as destination:
                shutil.copyfileobj(source, destination)
            shutil.copystat(staged, target)
        except Exception:
            if target.exists():
                target.unlink()
            raise
        finally:
            if staged.exists():
                staged.unlink()


def _unique_archive_path(
    target: Path,
    history_dir: Path,
    *,
    resource_label: str = "file",
) -> Path:
    stamp = datetime.fromtimestamp(target.stat().st_mtime).astimezone().strftime(
        "%Y%m%d-%H%M%S"
    )
    base = history_dir / f"{target.stem}_{stamp}{target.suffix}"
    if not base.exists():
        return base
    for index in range(2, 1000):
        candidate = history_dir / f"{target.stem}_{stamp} ({index}){target.suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot create a unique {resource_label} archive near: {base}")


def _move_to_windows_recycle_bin(path: Path) -> None:
    if os.name != "nt":
        raise RuntimeError("Recycle Bin publication is supported only on Windows.")
    from win32com.shell import shell, shellcon

    flags = (
        shellcon.FOF_ALLOWUNDO
        | shellcon.FOF_NOCONFIRMATION
        | shellcon.FOF_NOERRORUI
        | shellcon.FOF_SILENT
    )
    result = shell.SHFileOperation((0, shellcon.FO_DELETE, str(path), None, flags, None, None))
    code = result[0] if isinstance(result, tuple) else result
    aborted = bool(result[1]) if isinstance(result, tuple) and len(result) > 1 else False
    if code or aborted:
        raise OSError(int(code or 1), f"Unable to move file to Recycle Bin: {path}")
