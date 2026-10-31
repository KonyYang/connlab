"""Describe a copied project's standard envelope without rewriting its materials."""
from pathlib import Path


def reception_layout(source):
    number = source.get("ltr_number")
    if source["kind"] != "project" or not number or source.get("has_portable"):
        return None
    path = Path(source["source_path"])
    children = [Path(child) for child in source["child_folders"]]
    business = [child for child in children if child.name.upper().startswith(number.upper() + " ")]
    if path.name.upper() == number.upper() and len(business) == 1:
        if (path / "Source Book").exists() and not (path / "Source Book").is_dir():
            return None
        return {"root_name": number, "prefix": ""}
    if path.name.upper().startswith(number.upper() + " ") and not (path / "Source Book").exists():
        return {"root_name": number, "prefix": path.name}
    return None


def material_entries(entries):
    """Identity and portable transport metadata do not establish material equality."""
    ignored = {".connlab", ".connlab/library.json", ".connlab/manifest.json", ".connlab/portable"}
    return [row for row in entries if row["relative_path"] not in ignored
            and not row["relative_path"].startswith(".connlab/portable/")]


def received_material(source):
    entries = material_entries(source["entries"])
    layout = source.get("reception_layout")
    if not layout:
        return entries
    prefix = layout["prefix"]
    if prefix:
        entries = [{**row, "relative_path": prefix + "/" + row["relative_path"]} for row in entries]
        entries.append({"relative_path": prefix, "directory": True, "size": 0, "sha256": None})
    if not any(row["relative_path"].casefold() == "source book" for row in entries):
        entries.append({"relative_path": "Source Book", "directory": True, "size": 0, "sha256": None})
    return entries
