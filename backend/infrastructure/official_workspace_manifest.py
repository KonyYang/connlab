"""Portable manifest gateway for local official project workspaces."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path, PureWindowsPath


@dataclass(frozen=True, slots=True)
class OfficialWorkspaceManifest:
    """Portable local workspace manifest payload."""

    schema_version: int
    project_id: str
    dl_number: str
    local_workspace_path: str
    source_book_path: str
    official_project_folder_path: str
    template_source_path: str
    created_at: str


class OfficialWorkspaceManifestGateway:
    """Read and write official workspace manifest JSON files."""

    def read(self, path: Path) -> dict[str, object]:
        """Read a manifest JSON file as a dictionary."""
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, path: Path, manifest: OfficialWorkspaceManifest) -> None:
        """Write a manifest JSON file in UTF-8."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(manifest), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def write_adoption(self, path: Path, manifest: OfficialWorkspaceManifest) -> None:
        """Create or rebind same-project identity without replacing a racing claimant."""
        path.parent.mkdir(parents=True, exist_ok=True)
        _reject_redirected_manifest(path)
        serialized = json.dumps(
            asdict(manifest), ensure_ascii=False, indent=2, sort_keys=True
        )
        if not path.exists():
            try:
                with path.open("x", encoding="utf-8") as handle:
                    handle.write(serialized)
                    handle.flush()
                    os.fsync(handle.fileno())
                return
            except FileExistsError:
                # Another process created the identity file. Validate that exact
                # claimant below; adoption must never replace it blindly.
                pass

        # This first adapter read preserves the normal read seam. The identity is
        # validated again from the locked handle before any byte is changed, which
        # closes the check/replace race that existed in the old temp-file path.
        self._validate_adoption_identity(self.read(path), manifest)
        _reject_redirected_manifest(path)
        try:
            with path.open("r+", encoding="utf-8") as handle:
                self._lock_manifest(handle)
                try:
                    opened = os.fstat(handle.fileno())
                    current = os.stat(path, follow_symlinks=False)
                    if not _same_file_identity(opened, current):
                        raise ValueError("Workspace manifest changed while it was being linked.")
                    handle.seek(0)
                    self._validate_adoption_identity(json.load(handle), manifest)
                    handle.seek(0)
                    handle.write(serialized)
                    handle.truncate()
                    handle.flush()
                    os.fsync(handle.fileno())
                    current = os.stat(path, follow_symlinks=False)
                    if not _same_file_identity(opened, current):
                        raise ValueError("Workspace manifest changed while it was being linked.")
                finally:
                    self._unlock_manifest(handle)
        except FileNotFoundError as exc:
            raise ValueError(
                "Workspace manifest changed while it was being linked."
            ) from exc

    @staticmethod
    def first_redirected_path(*paths: Path) -> Path | None:
        """Return the first identity path that redirects through a link/reparse point."""
        for path in paths:
            if not path.exists() and not path.is_symlink():
                continue
            try:
                stat_result = os.lstat(path)
            except OSError:
                return path
            attributes = getattr(stat_result, "st_file_attributes", 0)
            if path.is_symlink() or attributes & 0x400:
                return path
        return None

    @staticmethod
    def _validate_adoption_identity(
        payload: dict[str, object], manifest: OfficialWorkspaceManifest
    ) -> None:
        if not isinstance(payload, dict):
            raise ValueError("Workspace manifest cannot be read as an identity record.")
        if payload.get("project_id") != manifest.project_id:
            raise ValueError("Workspace manifest belongs to another ConnLab project.")
        manifest_dl = payload.get("dl_number")
        if manifest_dl not in {None, "", manifest.dl_number}:
            raise ValueError("Workspace manifest does not match the registered DL number.")
        reviewed_folder = _portable_leaf(payload.get("official_project_folder_path"))
        requested_folder = _portable_leaf(manifest.official_project_folder_path)
        if reviewed_folder is None or reviewed_folder != requested_folder:
            raise ValueError(
                "Workspace manifest does not match the reviewed official project folder."
            )

    @staticmethod
    def _lock_manifest(handle) -> None:
        """Take a non-blocking process lock while validating and rebinding identity."""
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError("Workspace manifest is busy; try linking again.") from exc
            return
        import fcntl

        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError("Workspace manifest is busy; try linking again.") from exc

    @staticmethod
    def _unlock_manifest(handle) -> None:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            return
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _same_file_identity(left: os.stat_result, right: os.stat_result) -> bool:
    """Return whether two stats describe the same manifest file object."""
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def _reject_redirected_manifest(path: Path) -> None:
    """Fail closed when the identity file itself redirects outside the workspace."""
    if OfficialWorkspaceManifestGateway.first_redirected_path(path) is not None:
        raise ValueError("Workspace manifest cannot be a symbolic link or junction.")


def _portable_leaf(value: object) -> str | None:
    """Return one portable folder identity component from stored path metadata."""
    if not isinstance(value, str) or not value.strip():
        return None
    leaf = PureWindowsPath(value.replace("/", "\\")).name
    return leaf if leaf not in {"", ".", ".."} else None
