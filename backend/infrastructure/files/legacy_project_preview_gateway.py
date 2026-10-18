"""Bounded filesystem reads only; no database, Office automation or source writes."""
import json
import os
from pathlib import Path
import stat

from backend.application.legacy_project_preview_service import LegacyFolder


class LegacyProjectPreviewGateway:
    MAX_ENTRIES = 2000
    MAX_METADATA_BYTES = 65536
    SKIP = {".git", ".connlab", "history", "node_modules", "__pycache__", ".venv", "$recycle.bin"}

    def reset_identity_cache(self):
        self._identity_cache = {}

    @staticmethod
    def normalized_path(path: str) -> str:
        return str(path).replace("\\", "/").rstrip("/").casefold()

    def overlaps(self, left: str, right: str) -> bool:
        a, b = self.normalized_path(left), self.normalized_path(right)
        if a == b or a.startswith(b + "/") or b.startswith(a + "/"):
            return True
        # A bounded plan compares hundreds of pairs. Read each current identity
        # once for that plan, never persist inode values as durable ownership.
        if not hasattr(self, "_identity_cache"):
            self.reset_identity_cache()
        def identity(path):
            if path not in self._identity_cache:
                try:
                    info = os.stat(path)
                    self._identity_cache[path] = (info.st_dev, info.st_ino)
                except OSError:
                    self._identity_cache[path] = None
            return self._identity_cache[path]
        first, second = identity(left), identity(right)
        return first is not None and first == second

    def _path(self, raw):
        path = Path(raw).expanduser()
        if not path.is_absolute():
            raise ValueError("Select an absolute directory.")
        for part in [*reversed(path.parents), path]:
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("Redirected paths are not inspected.")
        return path.resolve()

    def folder(self, raw: str) -> LegacyFolder:
        path = self._path(raw)
        if not path.is_dir():
            raise ValueError("Select a directory.")
        info = path.stat()
        files, children, notes = [], [], []
        truncated = False
        with os.scandir(path) as entries:
            for index, entry in enumerate(entries):
                if index >= self.MAX_ENTRIES:
                    truncated = True
                    notes.append("This folder contains too many entries; only partial results are shown.")
                    break
                if entry.name.casefold() in self.SKIP or entry.name.startswith(("~$", "~WRL")) or ".connlab-backup-" in entry.name:
                    continue
                try:
                    data = entry.stat(follow_symlinks=False)
                    if entry.is_symlink() or getattr(data, "st_file_attributes", 0) & 0x400:
                        notes.append(f"Redirected entry skipped: {entry.name}")
                    elif entry.is_dir(follow_symlinks=False):
                        children.append(entry.name)
                    elif entry.is_file(follow_symlinks=False):
                        files.append(entry.name)
                except OSError:
                    notes.append(f"Cannot read entry: {entry.name}")
        manifest = self._metadata(path / ".connlab" / "manifest.json", notes)
        application = self._metadata(path / "application_data.json", notes)
        return LegacyFolder(str(path), (info.st_dev, info.st_ino), tuple(sorted(files)),
                            tuple(sorted(children)), manifest, application, tuple(notes), truncated)

    def _metadata(self, path, notes):
        if not path.exists() and not path.is_symlink():
            return {}
        try:
            checked = self._path(path)
            if not stat.S_ISREG(checked.stat().st_mode):
                raise ValueError("Metadata is not a regular file.")
            with checked.open("rb") as handle:
                info = os.fstat(handle.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size > self.MAX_METADATA_BYTES:
                    raise ValueError("Metadata is too large or not a regular file.")
                raw = handle.read(self.MAX_METADATA_BYTES + 1)
            if len(raw) > self.MAX_METADATA_BYTES:
                raise ValueError("Metadata is too large.")
            data = json.loads(raw.decode("utf-8-sig"))
            if not isinstance(data, dict):
                raise ValueError("Metadata must be an object.")
            # Only identity hints leave the filesystem boundary; never expose contacts or report data.
            return {key: value for key, value in data.items()
                    if key in {"DL", "dl_number", "project_id", "local_workspace_path"}
                    and isinstance(value, str) and len(value) <= 4096}
        except (OSError, ValueError, UnicodeError, RecursionError):
            notes.append(f"Cannot use legacy metadata {path.name}; folder-based preview is still available.")
            return {}
