"""Describe a copied project's standard envelope without rewriting its materials."""
from pathlib import Path


def reception_layout(source):
    number = source.get("ltr_number")
    if source["kind"] != "project" or not number or source.get("has_portable"):
        return None
    path = Path(source["source_path"])
    children = [Path(child) for child in source["child_folders"]]
    business = [child for child in children if child.name.upper().startswith(number.upper() + " ")]
    if len(business) == 1 and (path.name.upper() == number.upper() or (path / "Source Book").is_dir()):
        if (path / "Source Book").exists() and not (path / "Source Book").is_dir():
            return None
        return {"root_name": number, "prefix": ""}
    if path.name.upper() == number.upper() and not business:
        return {"root_name": number, "prefix": number + " Imported files"}
    if path.name.upper().startswith(number.upper() + " "):
        return {"root_name": number, "prefix": path.name}
    return None


def boundary_problem(source):
    if source["kind"] != "project" or source.get("has_portable"):
        return None
    path = Path(source["source_path"])
    if not source.get("ltr_number") and not source.get("project_id") and path.name.casefold() in {
        "photos", "source book", "test results", "submitted material", "e-mail", "final examination"
    }:
        return "This appears to be part of a project. Select the complete project folder, or assign these materials to an existing project."
    number = source.get("ltr_number")
    if number and path.name.upper() == number.upper():
        if (path / "Source Book").exists() and not (path / "Source Book").is_dir():
            return "Source Book is a file where the project expects a directory. Review the project structure before importing."
        business = [Path(child) for child in source["child_folders"] if Path(child).name.upper().startswith(number.upper() + " ")]
        if len(business) > 1:
            return "This project root contains several same-LTR folders. Select the intended business folder before importing; no version will be chosen automatically."
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
