"""Preview legacy folder boundaries and identity evidence without persistence."""
from dataclasses import dataclass
from collections import Counter, defaultdict
from itertools import chain
from pathlib import Path
import re
from typing import Protocol


NUMBER = re.compile(r"\bDL-\d{4}-\d{2}-\d{3}(?:[A-Z][A-Z0-9]*)?\b", re.I)
DOCUMENTS = {".doc", ".docx", ".docm", ".xls", ".xlsx", ".xlsm", ".pdf", ".msg", ".csv"}
MATERIAL_FOLDERS = {"source book", "submitted material", "photos", "test results", "e-mail"}


@dataclass(frozen=True)
class LegacyFolder:
    path: str
    identity: tuple[int, int]
    files: tuple[str, ...]
    children: tuple[str, ...]
    manifest: dict
    application: dict
    notes: tuple[str, ...] = ()
    truncated: bool = False


class LegacyPreviewGateway(Protocol):
    def folder(self, path: str) -> LegacyFolder: ...


class LegacyProjectPreviewService:
    """One bounded batch, independent of Project/LTR/Matrix stores."""

    MAX_FOLDERS = 10000
    MAX_DEPTH = 6

    def __init__(self, gateway: LegacyPreviewGateway):
        self.gateway = gateway

    def inspect_project(self, path: str) -> dict:
        """Re-read one candidate for registration; identity hints remain untrusted."""
        folder = self.gateway.folder(path)
        if not self._is_project(folder):
            raise ValueError("No project files found in this folder. Start Preview again.")
        result = self._project(folder)
        result["identity"] = folder.identity
        return result

    def preview(self, roots: list[str]) -> dict:
        selected, diagnostics, duplicate_roots = self._roots(roots)
        projects, seen = [], set()
        pending = [(folder.path, 0, folder) for folder in reversed(selected)]
        scanned, truncated = 0, False
        while pending and scanned < self.MAX_FOLDERS:
            path, depth, folder = pending.pop()
            scanned += 1
            try:
                folder = folder or self.gateway.folder(path)
            except (OSError, ValueError):
                diagnostics.append(f"Cannot read folder or redirected folder skipped: {path}")
                continue
            if folder.identity in seen:
                continue
            seen.add(folder.identity)
            truncated |= folder.truncated
            if self._is_project(folder):
                projects.append(self._project(folder))
                continue
            diagnostics.extend(folder.notes)
            if depth >= self.MAX_DEPTH:
                if folder.children:
                    truncated = True
                continue
            for child in reversed(folder.children):
                pending.append((str(Path(folder.path) / child), depth + 1, None))
        truncated |= bool(pending)
        self._mark_duplicates(projects)
        return {"read_only": True, "projects": projects, "scanned_folders": scanned,
                "duplicate_roots": duplicate_roots, "diagnostics": diagnostics,
                "truncated": truncated}

    def _roots(self, roots):
        folders, diagnostics = [], []
        for path in roots:
            try:
                folders.append(self.gateway.folder(path))
            except (OSError, ValueError):
                diagnostics.append(f"Folder unavailable or redirected: {path}")
        selected = []
        for folder in sorted(folders, key=lambda item: (len(Path(item.path).parts), item.path.casefold())):
            if any(folder.identity == other.identity or Path(folder.path).is_relative_to(Path(other.path))
                   for other in selected):
                continue
            selected.append(folder)
        return selected, diagnostics, len(folders) - len(selected)

    def _is_project(self, folder):
        if NUMBER.search(Path(folder.path).name) or folder.manifest or folder.application:
            return True
        if any(name.casefold() == "source book" for name in folder.children):
            return True
        if any(NUMBER.search(name) for name in folder.children):
            return False
        return (any(Path(name).suffix.lower() in DOCUMENTS for name in folder.files)
                or any(name.casefold() in MATERIAL_FOLDERS for name in folder.children))

    def _project(self, folder):
        name = Path(folder.path).name
        match = NUMBER.search(name)
        folder_number = match.group(0).upper() if match else None
        evidence = set()
        for value in (folder.manifest.get("dl_number"), folder.application.get("DL"),
                      folder.application.get("dl_number")):
            if isinstance(value, str) and (found := NUMBER.fullmatch(value.strip())):
                evidence.add(found.group(0).upper())
        for filename in (*folder.files, *folder.children):
            if found := NUMBER.search(filename):
                evidence.add(found.group(0).upper())
        if folder_number:
            evidence.add(folder_number)
        number = folder_number or (next(iter(evidence)) if len(evidence) == 1 else None)
        notes = list(folder.notes)
        if len(evidence) > 1:
            notes.append("Conflicting numbers in the folder or legacy files: " + ", ".join(sorted(evidence)))
        old_path = folder.manifest.get("local_workspace_path")
        if isinstance(old_path, str) and old_path.replace("\\", "/").casefold() != folder.path.replace("\\", "/").casefold():
            notes.append("Legacy metadata refers to a previous location; this preview uses the selected folder.")
        title = NUMBER.sub("", name, count=1).strip(" _-") if folder_number else name
        if not title and number:
            title = next((NUMBER.sub("", child, count=1).strip(" _-") for child in folder.children
                          if (found := NUMBER.search(child)) and found.group(0).upper() == number), "")
        if re.fullmatch(r"[a-f0-9]{32}", title, re.I):
            title = "Name needed"
        source_id = folder.manifest.get("project_id")
        return {"folder": folder.path, "number": number, "name": title or name,
                "number_evidence": sorted(evidence),
                "status": "review" if len(evidence) > 1 else "ready", "notes": notes,
                "source_id": source_id if isinstance(source_id, str) else None,
                "duplicate_folders": []}

    def _mark_duplicates(self, projects):
        by_number, by_source, pairs = defaultdict(list), defaultdict(list), Counter()
        for project in projects:
            if project["number"]:
                by_number[project["number"]].append(project)
            if project["source_id"]:
                by_source[project["source_id"]].append(project)
            if project["number"] and project["source_id"]:
                pairs[project["number"], project["source_id"]] += 1
        for project in projects:
            numbered = by_number.get(project["number"], [])
            identified = by_source.get(project["source_id"], [])
            total = len(numbered) + len(identified) - pairs[project["number"], project["source_id"]]
            project["duplicate_count"] = max(0, total - 1)
            if project["duplicate_count"]:
                project["status"] = "review"
                project["notes"].append("Other selected folders share this number or legacy identifier. Review them; no automatic merge will occur.")
                # A batch may contain hundreds of copies. Keep explanations bounded too.
                for other in chain(numbered, identified):
                    if other is not project and other["folder"] not in project["duplicate_folders"]:
                        project["duplicate_folders"].append(other["folder"])
                    if len(project["duplicate_folders"]) == 5:
                        break
        for project in projects:
            project.pop("source_id")
