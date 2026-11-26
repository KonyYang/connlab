"""Read-only search and explicit access; independent of intake and recovery."""
from pathlib import PurePosixPath, PureWindowsPath
from .catalog_entry import catalog_entry, checked_material_entry


def material_kind(name):
    text = name.casefold()
    if PurePosixPath(text).suffix in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}:
        return "photo"
    for kind, terms in (("report", ("report", "报告")), ("record", ("record", "记录")),
                        ("plan", ("plan", "计划")), ("application", ("application", "申请"))):
        if any(term in text for term in terms):
            return kind
    return "other"


class LibrarySearchService:
    def __init__(self, store, files, opener):
        self.store, self.files, self.opener = store, files, opener

    def search(self, query="", source="all", kind="all", project="", offset=0, limit=100):
        tokens = query.casefold().split()
        projects, matches, warnings = [], [], []
        catalog = self.store.catalog()
        selected_key = project
        if project.startswith("member:") and not any(entry["key"] == project for entry in catalog):
            selected_key = next((entry["key"] for entry in catalog
                                 if entry.get("member_id") == project.removeprefix("member:")), project)
        for entry in catalog:
            if selected_key and entry["key"] != selected_key or source != "all" and entry["source"] != source:
                continue
            if selected_key:
                entry = checked_material_entry(self.store, entry)
            associated = bool(entry["folder_path"].strip())
            available = entry.get("indexed_available")
            if available is None:
                available = associated and not entry.get("workspace_unavailable", False) and (self.store.indexed_available(entry["folder_path"]) if hasattr(self.store,"indexed_files") else self.files.available(entry["folder_path"]))
            location_state = "unassociated" if not associated else "available" if available else "unavailable"
            entry = {**entry, "available": available, "location_state": location_state}
            if location_state == "unassociated" and entry.get("project_id") and not tokens and not project:
                continue
            metadata = (" ".join(str(entry.get(k) or "") for k in ("number", "title", "test_item", "description")) + " " + PureWindowsPath(entry["folder_path"]).name).casefold()
            listed = kind == "all" and all(token in metadata for token in tokens)
            if listed:
                projects.append(entry)
            if location_state == "unassociated":
                continue
            if not entry["available"]:
                continue
            if not tokens and not project and kind == "all":
                continue
            rows, notes = (self.store.indexed_files(entry["key"]), []) if hasattr(self.store,"indexed_files") else self.files.scan(entry["folder_path"])
            warnings.extend(f"{entry['title']}: {note}" for note in notes)
            for row in rows:
                category = material_kind(row["name"])
                if kind != "all" and kind != category:
                    continue
                if all(token in metadata + " " + row["name"].casefold() for token in tokens):
                    if not listed:
                        projects.append(entry)
                        listed = True
                    matches.append({**row, "key": entry["key"], "title": entry["title"],
                                    "number": entry["number"], "kind": category,
                                    "directory": str(PurePosixPath(row["relative_path"]).parent)})
        if getattr(self.store,'archive_index_error',False):
            warnings.append('Materials index is unavailable. Refresh the library to retry; project work is unaffected.')
        matches.sort(key=lambda row: (row["name"].casefold() != query.casefold(), row["number"] or "", row["relative_path"]))
        return {"projects": projects, "files": matches[offset:offset + limit], "total": len(matches),
                "warnings": list(dict.fromkeys(warnings))}

    def browse(self, key, relative_directory=""):
        entry = catalog_entry(self.store, key)
        root = entry["folder_path"]
        state = "unassociated" if not root.strip() else "available" if not entry.get("workspace_unavailable") and self.files.available(root) else "unavailable"
        directory, rows, warnings = "", [], []
        if state == "available":
            directory, rows, warnings = self.files.browse(root, relative_directory)
        elif state == "unavailable":
            warnings.append("The material folder is unavailable. Refresh the library.")
        return {"key": entry["key"], "root": root, "current_directory": directory,
                "location_state": state, "items": rows, "warnings": warnings}

    def open(self, key, relative="", containing=False):
        entry = catalog_entry(self.store, key)
        if not entry["folder_path"].strip():
            raise ValueError("A material folder is not linked to this project yet. Use its workspace to associate one.")
        if entry.get("workspace_unavailable"):
            raise ValueError("The registered project folder is unavailable. Review its location in the Workbench.")
        path = self.files.resolve(entry["folder_path"], relative, containing=containing)
        directory = self.files.is_directory(path)
        if not directory and path.suffix.casefold() not in {
            ".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".pdf", ".txt", ".csv",
            ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".ppt", ".pptx"}:
            raise ValueError("Open this file from its folder using a suitable application.")
        self.opener(path)
        return {"status": "opened", "message": "Folder opened." if directory else "File opened."}

    def refresh(self):
        """Explicit cache refresh for existing catalog sources; queries never perform this walk."""
        for entry in self.store.catalog():
            entry = checked_material_entry(self.store, entry)
            if entry.get('workspace_unavailable') or not entry.get('folder_path') or not hasattr(self.store,'cache_index'):continue
            if not self.files.available(entry['folder_path']):continue
            rows,warnings=self.files.scan(entry['folder_path'])
            if not warnings:self.store.cache_index(entry,rows)
