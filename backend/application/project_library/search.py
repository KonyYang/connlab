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
        for entry in self.store.catalog():
            if project and entry["key"] != project or source != "all" and entry["source"] != source:
                continue
            entry = {**entry, "available": self.files.available(entry["folder_path"])}
            metadata = " ".join(str(entry.get(k) or "") for k in ("number", "title", "test_item", "description")).casefold()
            if all(token in metadata for token in tokens):
                projects.append(entry)
            if not entry["available"]:
                warnings.append(f"{entry['number'] or entry['title']}: material location unavailable. Locate the folder before opening files.")
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
                    matches.append({**row, "key": entry["key"], "title": entry["title"],
                                    "number": entry["number"], "kind": category,
                                    "directory": str(PurePosixPath(row["relative_path"]).parent)})
        matches.sort(key=lambda row: (row["name"].casefold() != query.casefold(), row["number"] or "", row["relative_path"]))
        return {"projects": projects, "files": matches[offset:offset + limit], "total": len(matches),
                "warnings": list(dict.fromkeys(warnings))}

    def open(self, key, relative="", containing=False):
        entry = next((entry for entry in self.store.catalog() if entry["key"] == key), None)
        if entry is None:
            raise LookupError("Project library entry not found.")
        path = self.files.resolve(entry["folder_path"], relative)
        if containing and relative:
            path = path.parent
        if not path.is_dir() and path.suffix.casefold() not in {
            ".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".pdf", ".txt", ".csv",
            ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".ppt", ".pptx"}:
            raise ValueError("Open this file from its folder using a suitable application.")
        self.opener(path)
        return {"status": "opened", "message": "Folder opened." if path.is_dir() else "File opened."}
