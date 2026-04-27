"""Controlled file storage for Phase 6 intake packages."""

from __future__ import annotations

import hashlib
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StoredIntakeFile:
    """Metadata for a file copied into controlled intake storage."""

    original_name: str
    stored_path: Path
    size_bytes: int
    sha256: str


class IntakeStorage:
    """Resolve and write files under `data/intake/{package_id}`."""

    def __init__(self, intake_root: Path) -> None:
        """Create storage rooted at an explicit intake directory."""
        self._intake_root = Path(intake_root)

    def sanitize_filename(self, original_name: str) -> str:
        """Return a Windows-safe file name without path separators."""
        cleaned = Path(original_name).name.replace("/", "_").replace("\\", "_")
        cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "_", cleaned).strip(" .")
        return cleaned or "file"

    def package_root(self, package_id: str) -> Path:
        """Return the root directory for one intake package."""
        safe_package_id = self._safe_package_id(package_id)
        return self._intake_root / safe_package_id

    def source_dir(self, package_id: str) -> Path:
        """Return the source directory for one intake package."""
        return self.package_root(package_id) / "source"

    def attachments_dir(self, package_id: str) -> Path:
        """Return the attachments directory for one intake package."""
        return self.package_root(package_id) / "attachments"

    def snapshots_dir(self, package_id: str) -> Path:
        """Return the snapshots directory for one intake package."""
        return self.package_root(package_id) / "snapshots"

    def copy_source_file(
        self,
        package_id: str,
        source_path: Path,
        *,
        original_name: str | None = None,
    ) -> StoredIntakeFile:
        """Copy an imported source file into `source/` without overwriting."""
        return self._copy_file(
            source_path=source_path,
            target_dir=self.source_dir(package_id),
            original_name=original_name or Path(source_path).name,
        )

    def copy_attachment(
        self,
        package_id: str,
        asset_id: str,
        source_path: Path,
        *,
        original_name: str | None = None,
    ) -> StoredIntakeFile:
        """Copy an attachment into `attachments/` with asset id prefix."""
        safe_asset_id = self._safe_package_id(asset_id)
        safe_original = self.sanitize_filename(original_name or Path(source_path).name)
        return self._copy_file(
            source_path=source_path,
            target_dir=self.attachments_dir(package_id),
            original_name=f"{safe_asset_id}__{safe_original}",
        )

    def snapshot_path(self, package_id: str, snapshot_name: str) -> Path:
        """Return a non-overwriting path under `snapshots/`."""
        directory = self.snapshots_dir(package_id)
        directory.mkdir(parents=True, exist_ok=True)
        return self._unique_destination(directory, self.sanitize_filename(snapshot_name))

    def sha256(self, path: Path) -> str:
        """Return the SHA-256 digest for a file."""
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _copy_file(
        self,
        *,
        source_path: Path,
        target_dir: Path,
        original_name: str,
    ) -> StoredIntakeFile:
        """Copy a file into a target directory and return metadata."""
        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(f"Intake source file does not exist: {source}")
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = self._unique_destination(
            target_dir,
            self.sanitize_filename(original_name),
        )
        shutil.copy2(source, destination)
        return StoredIntakeFile(
            original_name=Path(original_name).name,
            stored_path=destination,
            size_bytes=destination.stat().st_size,
            sha256=self.sha256(destination),
        )

    def _unique_destination(self, directory: Path, filename: str) -> Path:
        """Return a non-overwriting destination in a directory."""
        candidate = directory / filename
        if not candidate.exists():
            return candidate
        stem = candidate.stem
        suffix = candidate.suffix
        index = 2
        while True:
            next_candidate = directory / f"{stem}_{index}{suffix}"
            if not next_candidate.exists():
                return next_candidate
            index += 1

    def _safe_package_id(self, value: str) -> str:
        """Return a safe directory segment for IDs."""
        cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._- ")
        if not cleaned:
            raise ValueError("Intake storage id cannot be empty.")
        return cleaned
