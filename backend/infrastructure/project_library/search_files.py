"""Bounded metadata-only traversal and workstation file access."""
from datetime import datetime, timezone
import os
from pathlib import Path
from backend.infrastructure.project_library.files import checked_path


def internal_material_path(relative):
    path=Path(relative)
    name=path.name.casefold()
    return any(part.casefold()=='.connlab' for part in path.parts) or name.endswith(('.db','.sqlite','.sqlite3','.db-wal','.db-shm','.sqlite-wal','.sqlite-shm','.sqlite3-wal','.sqlite3-shm','.db-journal','.sqlite-journal','.sqlite3-journal'))

class SearchFiles:
    def available(self, root):
        try:
            return checked_path(root).is_dir()
        except (OSError, ValueError):
            return False

    def scan(self, root, limit=20000):
        root = checked_path(root)
        files, warnings = [], []
        pending = [(root, 0)]
        visited = 0
        while pending:
            folder, depth = pending.pop()
            try:
                with os.scandir(folder) as entries:
                    for entry in entries:
                        if internal_material_path(str(Path(entry.path).relative_to(root))): continue
                        visited += 1
                        if visited > limit:
                            return files, [*warnings, "Search is incomplete: folder scan limit reached."]
                        try:
                            path = checked_path(entry.path)
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
        folder = self.resolve(root, relative)
        base = checked_path(root)
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
                    path = checked_path(entry.path)
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

    def resolve(self, root, relative):
        # Reject Windows drive, ADS, UNC and traversal syntax on every platform.
        parts = relative.replace("\\", "/").split("/")
        if relative and (":" in relative or relative.startswith(("/", "\\")) or ".." in parts):
            raise ValueError("Choose a file inside the project folder.")
        base = checked_path(root)
        path = checked_path(base.joinpath(*parts))
        if not path.is_relative_to(base):
            raise ValueError("Choose a file inside the project folder.")
        return path


def open_document(path):
    launcher = getattr(os, "startfile", None)
    if launcher is None:
        raise ValueError("Opening files requires the local Windows workstation.")
    launcher(str(path))
