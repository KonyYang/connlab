"""Read-only search and explicit access; independent of intake and recovery."""
from pathlib import PurePosixPath


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
            associated = bool(entry["folder_path"].strip())
            available = associated and self.files.available(entry["folder_path"])
            location_state = "unassociated" if not associated else "available" if available else "unavailable"
            entry = {**entry, "available": available, "location_state": location_state}
            if location_state == "unassociated" and entry.get("project_id") and not tokens and not project:
                continue
            metadata = " ".join(str(entry.get(k) or "") for k in ("number", "title", "test_item", "description")).casefold()
            if all(token in metadata for token in tokens):
                projects.append(entry)
            if location_state == "unassociated":
                continue
            if not entry["available"]:
                continue
            if not tokens and not project and kind == "all":
                continue
            rows, notes = self.files.scan(entry["folder_path"])
            warnings.extend(f"{entry['title']}: {note}" for note in notes)
            for row in rows:
                category = material_kind(row["name"])
                if kind != "all" and kind != category:
                    continue
                if all(token in metadata + " " + row["name"].casefold() for token in tokens):
                    if not any(project_row["key"] == entry["key"] for project_row in projects):
                        projects.append(entry)
                    matches.append({**row, "key": entry["key"], "title": entry["title"],
                                    "number": entry["number"], "kind": category,
                                    "directory": str(PurePosixPath(row["relative_path"]).parent)})
        matches.sort(key=lambda row: (row["name"].casefold() != query.casefold(), row["number"] or "", row["relative_path"]))
        return {"projects": projects, "files": matches[offset:offset + limit], "total": len(matches),
                "warnings": list(dict.fromkeys(warnings))}

    def browse(self, key, relative_directory=""):
        catalog = self.store.catalog()
        entry = next((row for row in catalog if row["key"] == key), None)
        if entry is None and key.startswith("member:"):
            entry = next((row for row in catalog if row.get("member_id") == key.removeprefix("member:")), None)
        if entry is None:
            raise LookupError("Project library entry not found.")
        root = entry["folder_path"]
        state = "unassociated" if not root.strip() else "available" if self.files.available(root) else "unavailable"
        directory, rows, warnings = "", [], []
        if state == "available":
            directory, rows, warnings = self.files.browse(root, relative_directory)
        elif state == "unavailable":
            warnings.append("The material folder is unavailable. Refresh the library.")
        return {"key": entry["key"], "root": root, "current_directory": directory,
                "location_state": state, "items": rows, "warnings": warnings}

    def open(self, key, relative="", containing=False):
        entry = next((entry for entry in self.store.catalog() if entry["key"] == key), None)
        if entry is None:
            raise LookupError("Project library entry not found.")
        if not entry["folder_path"].strip():
            raise ValueError("A material folder is not linked to this project yet. Use its workspace to associate one.")
        path = self.files.resolve(entry["folder_path"], relative)
        if containing and relative:
            path = path.parent
        if not path.is_dir() and path.suffix.casefold() not in {
            ".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".pdf", ".txt", ".csv",
            ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".ppt", ".pptx"}:
            raise ValueError("Open this file from its folder using a suitable application.")
        self.opener(path)
        return {"status": "opened", "message": "Folder opened." if path.is_dir() else "File opened."}
