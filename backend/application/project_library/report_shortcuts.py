"""Explicit ordinary report links; no report authority or file version tracking."""
from backend.application.project_library.catalog_entry import catalog_entry
from backend.domain.project_library import ProjectLibraryConflict


class ReportShortcutService:
    def __init__(self, store, files, catalog):
        self.store, self.files, self.catalog = store, files, catalog

    def list(self, key):
        entry = catalog_entry(self.catalog, key)
        if entry.get("workspace_unavailable") or not entry["folder_path"]:
            return {"key": entry["key"], "items": []}
        items = [{**pointer, **self.files.report_pointer(entry["folder_path"], pointer["relative_path"])}
                 for pointer in self.store.list(entry["key"])]
        return {"key": entry["key"], "items": items}

    def _current(self, key, role, expected):
        if role not in {"internal", "customer"}:
            raise ValueError("Choose Internal report or Customer report.")
        current = next((row["relative_path"] for row in self.store.list(key) if row["role"] == role), None)
        if current != expected:
            raise ProjectLibraryConflict("The report shortcut changed. Refresh before changing it.")
        return current

    def set(self, key, role, relative_path, expected_path, replacement_confirmed=False):
        with self.files.lock():
            entry = catalog_entry(self.catalog, key)
            current = self._current(entry["key"], role, expected_path)
            if entry.get("workspace_unavailable") or not entry["folder_path"]:
                raise ValueError("The materials folder is unavailable.")
            path = self.files.report_pointer(entry["folder_path"], relative_path, require_file=True)["relative_path"]
            if current and current != path and not replacement_confirmed:
                raise ProjectLibraryConflict("Confirm replacement after reviewing the current and selected report.")
            self.store.write(entry["key"], role, path)
        return self.list(entry["key"])

    def clear(self, key, role, expected_path):
        with self.files.lock():
            entry = catalog_entry(self.catalog, key)
            self._current(entry["key"], role, expected_path)
            self.store.write(entry["key"], role, None)
        return self.list(entry["key"])
