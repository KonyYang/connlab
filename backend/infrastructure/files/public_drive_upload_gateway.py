"""Filesystem gateway for safe public-drive Project Folder upload."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from uuid import uuid4

from backend.application.public_drive_upload_service import (
    PublicDriveUploadTargetChangedError,
)


class PublicDriveUploadGateway:
    """Provide conservative file operations for public-drive upload."""

    def fingerprint(self, path: Path) -> str:
        """Return a SHA-256 fingerprint for a file."""
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def list_files(self, root: Path) -> tuple[Path, ...]:
        """Return all files under the supplied root."""
        return tuple(path for path in root.rglob("*") if path.is_file())

    def list_directories(self, root: Path) -> tuple[Path, ...]:
        """Return all directories under the supplied root, excluding the root itself."""
        return tuple(path for path in root.rglob("*") if path.is_dir())

    def create_directory(self, target: Path) -> None:
        """Create a target public-drive directory."""
        target.mkdir(parents=True, exist_ok=True)

    def copy_new_file(self, source: Path, target: Path) -> None:
        """Copy a new public-drive file only when the target is still missing."""
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise PublicDriveUploadTargetChangedError(
                f"Public-drive target appeared before copy: {target}"
            )
        temporary = self._copy_to_temporary(source, target)
        try:
            self._before_new_file_final_create(target)
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
        """Replace a managed file after verifying it was not changed externally."""
        if expected_public_fingerprint is None:
            raise PublicDriveUploadTargetChangedError(
                "Missing previous upload record for managed update."
            )
        if not target.is_file():
            raise PublicDriveUploadTargetChangedError(
                f"Public-drive target is no longer a file: {target}"
            )
        current = self.fingerprint(target)
        if current != expected_public_fingerprint:
            raise PublicDriveUploadTargetChangedError(
                f"Public-drive file changed before update: {target}"
            )
        self._atomic_copy(source, target)

    def _atomic_copy(self, source: Path, target: Path) -> None:
        """Copy through a same-directory temporary file, then replace atomically."""
        temporary = self._copy_to_temporary(source, target)
        try:
            os.replace(temporary, target)
        finally:
            if temporary.exists():
                temporary.unlink()

    def _copy_to_temporary(self, source: Path, target: Path) -> Path:
        """Copy source to a same-directory temporary file."""
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
        """Create the final file with exclusive semantics so unmanaged files survive races."""
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        try:
            descriptor = os.open(target, flags)
        except FileExistsError as exc:
            raise PublicDriveUploadTargetChangedError(
                f"Public-drive target appeared before copy: {target}"
            ) from exc
        try:
            with temporary.open("rb") as source_handle, os.fdopen(descriptor, "wb") as target_handle:
                shutil.copyfileobj(source_handle, target_handle)
            shutil.copystat(temporary, target)
        except Exception:
            if target.exists():
                target.unlink()
            raise

    def _before_new_file_final_create(self, target: Path) -> None:
        """Extension point before exclusive final placement."""
        return None
