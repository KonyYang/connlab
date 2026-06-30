"""Filesystem gateway for TASK_346C public folder workflow operations."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from uuid import uuid4


class PublicFolderWorkflowTargetChangedError(RuntimeError):
    """Raised when a previewed filesystem target changes before execute."""


class PublicFolderWorkflowGateway:
    """Conservative file operations for Sync, Submit, and Pull."""

    def fingerprint(self, path: Path) -> str:
        """Return a SHA-256 fingerprint for a file."""
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def list_files(self, root: Path) -> tuple[Path, ...]:
        """Return files under a root in deterministic order."""
        return tuple(sorted((path for path in root.rglob("*") if path.is_file()), key=str))

    def list_directories(self, root: Path) -> tuple[Path, ...]:
        """Return directories under a root in deterministic order."""
        return tuple(sorted((path for path in root.rglob("*") if path.is_dir()), key=str))

    def create_directory(self, target: Path) -> None:
        """Create a preview-listed directory."""
        target.mkdir(parents=True, exist_ok=True)

    def copy_new_file(self, source: Path, target: Path) -> None:
        """Copy a file only when the target is still missing."""
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise PublicFolderWorkflowTargetChangedError(
                f"Public folder target appeared before copy: {target}"
            )
        temporary = self._copy_to_temporary(source, target)
        try:
            self._place_new_file_without_overwrite(temporary, target)
        finally:
            if temporary.exists():
                temporary.unlink()

    def replace_managed_file(
        self,
        source: Path,
        target: Path,
        *,
        expected_public_fingerprint: str | None,
    ) -> None:
        """Replace a managed public file after verifying the expected fingerprint."""
        if expected_public_fingerprint is None:
            raise PublicFolderWorkflowTargetChangedError(
                "Missing previous workflow file record for managed update."
            )
        if not target.is_file():
            raise PublicFolderWorkflowTargetChangedError(
                f"Public folder target is no longer a file: {target}"
            )
        if self.fingerprint(target) != expected_public_fingerprint:
            raise PublicFolderWorkflowTargetChangedError(
                f"Public folder file changed before update: {target}"
            )
        temporary = self._copy_to_temporary(source, target)
        try:
            os.replace(temporary, target)
        finally:
            if temporary.exists():
                temporary.unlink()

    def move_directory_no_overwrite(self, source: Path, target: Path) -> None:
        """Move one directory only when the target does not already exist."""
        if not source.is_dir():
            raise PublicFolderWorkflowTargetChangedError(
                f"Public Open working copy is missing: {source}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise PublicFolderWorkflowTargetChangedError(
                f"Public Closed target already exists: {target}"
            )
        shutil.move(str(source), str(target))

    def copy_tree_no_overwrite(self, source: Path, target: Path) -> None:
        """Copy a directory tree only when the target does not already exist."""
        if not source.is_dir():
            raise PublicFolderWorkflowTargetChangedError(
                f"Public Closed source is missing: {source}"
            )
        if target.exists():
            raise PublicFolderWorkflowTargetChangedError(
                f"Local pull target already exists: {target}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)

    def unique_history_target(self, current_local_folder: Path, timestamp: str) -> Path:
        """Return a unique local history target next to the current local folder."""
        safe_stamp = (
            timestamp.replace(":", "")
            .replace("+", "")
            .replace(".", "")
            .replace("-", "")
        )
        base = current_local_folder.with_name(f"{current_local_folder.name} - Pull {safe_stamp}")
        candidate = base
        index = 2
        while candidate.exists():
            candidate = base.with_name(f"{base.name} ({index})")
            index += 1
        return candidate

    def _copy_to_temporary(self, source: Path, target: Path) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.connlab-{uuid4().hex}.tmp")
        try:
            shutil.copy2(source, temporary)
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise
        return temporary

    def _place_new_file_without_overwrite(self, temporary: Path, target: Path) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        try:
            descriptor = os.open(target, flags)
        except FileExistsError as exc:
            raise PublicFolderWorkflowTargetChangedError(
                f"Public folder target appeared before copy: {target}"
            ) from exc
        try:
            with temporary.open("rb") as source_handle, os.fdopen(descriptor, "wb") as target_handle:
                shutil.copyfileobj(source_handle, target_handle)
            shutil.copystat(temporary, target)
        except Exception:
            if target.exists():
                target.unlink()
            raise
