"""Read-only folder discovery, scoped to the two current Settings locations."""
from pathlib import Path

from .search import LibrarySearchService


class ConfiguredFolderCatalog:
    def __init__(self, store, roots):
        self.archive = store
        self.roots = roots

    def catalog(self):
        roots = {path: source for source, path, active in self.roots if active}
        entries = {}
        for row in self.archive.directory_rows():
            path = Path(row.folder_path)
            if not row.indexed_available or path.parent not in roots:
                continue
            entries[path] = dict(key="directory:" + row.folder_id, folder_path=str(path),
                                 number=row.number, title=row.title, source=roots[path.parent],
                                 test_item="", project_id=None, member_id=None, indexed_available=True)
        for op in self.archive.pending_directory_receipts():
            path = Path(op["target_path"])
            if roots.get(path.parent) != "materials":
                continue
            entries[path] = dict(key="archive:" + op["folder_id"], folder_path=str(path),
                                 number=op["number"], title=op["title"], source="materials", test_item="",
                                 project_id=None, member_id=None, operation_id=op["batch_id"],
                                 intake_status=op["status"], indexed_available=False,
                                 workspace_unavailable=True)
        return sorted(entries.values(), key=lambda row: (row["number"] or "", row["folder_path"].casefold()))

    def indexed_files(self, key):
        return self.archive.indexed_files(key)


class ConfiguredFolderLibrary(LibrarySearchService):
    def __init__(self, catalog, files, opener, scanner):
        super().__init__(catalog, files, opener)
        self.scanner = scanner

    def refresh(self):
        labels = {"materials": "Materials library folder", "projects": "Project default save location"}
        warnings, unavailable = [], []
        with self.scanner.lock():
            for source, root, active in self.store.roots:
                self.scanner.check_cancel()
                try:
                    if not active:
                        raise ValueError("Disabled location")
                    folders = self.scanner.children(root)
                except (OSError, ValueError):
                    self.store.archive.hide_absent_directories(root, set())
                    unavailable.append(str(root))
                    warnings.append(f"{labels[source]} is unavailable: {root}. Check the path in Settings and retry.")
                    continue
                self.store.archive.hide_absent_directories(root, set(folders))
                for path in folders:
                    self.scanner.check_cancel()
                    try:
                        number, title = self.scanner.directory_label(path)
                        items, notes = self.files.scan(path, check_cancel=self.scanner.check_cancel)
                        warnings.extend(f"{path}: {note}" for note in dict.fromkeys(notes))
                    except (OSError, ValueError):
                        self.scanner.check_cancel()
                        warnings.append(f"Could not fully index {path}. Check access and refresh.")
                        continue
                    self.store.archive.index_directory(path, number, title, items)
        return dict(available=not unavailable, warnings=warnings)
