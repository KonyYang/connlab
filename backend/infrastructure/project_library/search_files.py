"""Bounded metadata-only traversal and workstation file access."""
from datetime import datetime, timezone
import os
from pathlib import Path
from .material_paths import checked_material_path, display_path, material_io_path, shell_path


def internal_material_path(relative):
    path=Path(relative)
    name=path.name.casefold()
    return any(part.casefold()=='.connlab' for part in path.parts) or name.endswith(('.db','.sqlite','.sqlite3','.db-wal','.db-shm','.sqlite-wal','.sqlite-shm','.sqlite3-wal','.sqlite3-shm','.db-journal','.sqlite-journal','.sqlite3-journal'))

class SearchFiles:
    def __init__(self, *, exclude_internal=False):
        self.exclude_internal = exclude_internal

    def available(self, root):
        try:
            return checked_material_path(root).is_dir()
        except (OSError, ValueError):
            return False

    def scan(self, root, limit=20000, check_cancel=None):
        root = checked_material_path(root)
        files, warnings = [], []
        pending = [(root, 0)]
        visited = 0
        while pending:
            folder, depth = pending.pop()
            try:
                with os.scandir(folder) as entries:
                    for entry in entries:
                        if check_cancel:
                            check_cancel()
                        if internal_material_path(str(Path(entry.path).relative_to(root))): continue
                        visited += 1
                        if visited > limit:
                            return files, [*warnings, "Search is incomplete: folder scan limit reached."]
                        try:
                            path = checked_material_path(entry.path)
                            if not path.is_relative_to(root):
                                raise ValueError("Outside project folder")
                            if path.is_dir():
                                if depth < 40:
                                    pending.append((path, depth + 1))
                                else:
                                    warnings.append("Search is incomplete: directory depth limit reached.")
                            elif path.is_file():
                                files.append({"name": path.name, "relative_path": path.relative_to(root).as_posix()})
                        except (OSError, ValueError):
                            warnings.append(f"Search is incomplete: {entry.name} is unavailable or redirected.")
            except OSError:
                warnings.append("Search is incomplete: a directory cannot be read.")
        return files, warnings

    def browse(self, root, relative, limit=20000):
        base = checked_material_path(root)
        folder = self._resolve(base, relative)
        if not folder.is_dir():
            raise ValueError("Choose a directory inside the material folder.")
        rows, warnings = [], []
        with os.scandir(folder) as entries:
            for index, entry in enumerate(entries):
                if index >= limit:
                    warnings.append("Directory listing is incomplete: entry limit reached.")
                    break
                try:
                    if internal_material_path(str(Path(entry.path).relative_to(base))): continue
                    path = checked_material_path(entry.path)
                    if not path.is_relative_to(base):
                        raise ValueError("Outside material folder")
                    directory = path.is_dir()
                    if not directory and not path.is_file():
                        raise ValueError("Unsupported material entry")
                    rows.append({"name": path.name, "relative_path": path.relative_to(base).as_posix(),
                        "is_directory": directory, "extension": "" if directory else path.suffix.casefold(),
                        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()})
                except (OSError, ValueError):
                    warnings.append(f"{entry.name} is unavailable or redirected.")
        rows.sort(key=lambda row: (not row["is_directory"], row["name"].casefold()))
        return "" if folder == base else folder.relative_to(base).as_posix(), rows, warnings

    def resolve(self, root, relative, *, containing=False):
        path = self._resolve(checked_material_path(root), relative)
        return display_path(path.parent if containing and relative else path)

    def _resolve(self, base, relative):
        # Reject Windows drive, ADS, UNC and traversal syntax on every platform.
        parts = relative.replace("\\", "/").split("/")
        if self.exclude_internal and internal_material_path("/".join(parts)):
            raise ValueError("Internal project files are excluded from materials browsing.")
        if relative and (":" in relative or relative.startswith(("/", "\\")) or ".." in parts):
            raise ValueError("Choose a file inside the project folder.")
        path = checked_material_path(base.joinpath(*parts))
        if not path.is_relative_to(base):
            raise ValueError("Choose a file inside the project folder.")
        return path

    def is_directory(self, path):
        return material_io_path(path).is_dir()


def open_document(path):
    launcher = getattr(os, "startfile", None)
    if launcher is None:
        raise ValueError("Opening files requires the local Windows workstation.")
    try:
        launcher(shell_path(path))
    except OSError as error:
        if getattr(error, "winerror", None) == 206:
            raise ValueError("Windows could not open this long path. Open its containing folder or copy the file to a shorter location.") from error
        raise
