"""Register historical folders without creating business lifecycle authority."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.legacy_project_preview_service import LegacyProjectPreviewService


class RegistrationRepository(Protocol):
    def write(self): ...
    def references(self) -> list[dict]: ...
    def records(self) -> list[dict]: ...
    def get(self, record_id: str) -> dict | None: ...
    def add(self, record: dict) -> dict: ...
    def relocate(self, record_id: str, path: str, normalized: str, now: str) -> dict: ...


class RegistrationFolders(Protocol):
    def folder(self, path: str): ...
    def normalized_path(self, path: str) -> str: ...
    def overlaps(self, left: str, right: str) -> bool: ...
    def reset_identity_cache(self): ...


class LegacyProjectRegistrationService:
    def __init__(self, repository: RegistrationRepository, folders: RegistrationFolders, opener=None):
        self.repository, self.folders, self.opener = repository, folders, opener
        self.preview = LegacyProjectPreviewService(folders)

    def plan(self, paths: list[str]) -> dict:
        self.folders.reset_identity_cache()
        refs = self.repository.references()
        candidates = []
        for path in dict.fromkeys(paths):
            try:
                candidates.append(self.preview.inspect_project(path))
            except (OSError, ValueError) as exc:
                candidates.append({"folder": path, "name": Path(path).name, "number": None,
                                   "status": "failed", "notes": [str(exc)], "fingerprint": ""})
        return {"projects": [self._planned(item, refs, candidates) for item in candidates]}

    def _planned(self, item, refs, batch):
        if item["status"] == "failed":
            return item
        row = dict(item)
        row["notes"] = list(item["notes"])
        conflicts, already = [], []
        for ref in refs:
            if any(self.folders.overlaps(item["folder"], path) for path in ref["paths"]):
                already.append(ref)
            elif (set(item["number_evidence"]) & set(ref["numbers"]) or
                  item["source_id"] and item["source_id"] == ref["source_id"]):
                conflicts.append(ref)
        related = sorted(other["folder"] for other in batch if other is not item and
                         other["status"] != "failed" and
                         (set(item["number_evidence"]) & set(other["number_evidence"]) or
                          item["source_id"] and item["source_id"] == other["source_id"]))
        overlap = sorted(other["folder"] for other in batch if other is not item and
                         other["status"] != "failed" and self.folders.overlaps(item["folder"], other["folder"]))
        row["status"] = "already_added" if already else "review" if conflicts or related or overlap or item["status"] == "review" else "ready"
        if already:
            row["notes"].append("This folder is already added or overlaps a registered project location.")
        if conflicts:
            row["notes"].append("An existing project shares a number or legacy identifier. Keep Separate creates an independent historical record.")
        if related:
            row["notes"].append("Other selected folders share a number or legacy identifier. No automatic merge will occur.")
        if overlap:
            row["notes"].append("Selected project boundaries overlap. Choose a single project boundary and preview again.")
        row["can_keep_separate"] = not overlap and row["status"] == "review"
        evidence = {"folder": item, "existing": sorted(already + conflicts, key=lambda ref: (ref["kind"], ref["id"])),
                    "related": related, "overlap": overlap}
        row["fingerprint"] = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
        return row

    def register(self, paths: list[str], selected: list[dict]) -> dict:
        outcomes = []
        with self.repository.write():
            # Capture the complete plan before adding any rows, so a deliberately
            # separate pair does not stale its own second item during the batch.
            planned = {row["folder"]: row for row in self.plan(paths)["projects"]}
            occupied_paths = [row["folder_path"] for row in self.repository.records()]
            seen = set()
            for choice in selected:
                path = choice["folder"]
                if path in seen:
                    continue
                seen.add(path)
                row = planned.get(path)
                status, message, record_id = "review", "Refresh the registration check before importing.", None
                if row and row["status"] in {"failed", "already_added"}:
                    status, message = row["status"], " ".join(row["notes"])
                elif row and row["fingerprint"] == choice["fingerprint"]:
                    if row["status"] == "ready" or choice.get("keep_separate") and row["can_keep_separate"]:
                        # Deduplicate physical/case aliases selected in one batch.
                        occupied = any(self.folders.overlaps(row["folder"], existing) for existing in occupied_paths)
                        if occupied:
                            status, message = "already_added", "Folder already added."
                        else:
                            now = datetime.now(timezone.utc).isoformat()
                            record_id = str(uuid4())
                            self.repository.add({"record_id": record_id, "name": Path(row["folder"]).name,
                                "number": row["number"], "number_evidence": row["number_evidence"],
                                "source_id": row["source_id"], "folder_path": row["folder"],
                                "normalized_path": self.folders.normalized_path(row["folder"]),
                                "notes": row["notes"], "imported_at": now, "updated_at": now})
                            occupied_paths.append(row["folder"])
                            status, message = "added", "Historical project added. Original files remain unchanged."
                    else:
                        message = "Review conflicts and explicitly choose Keep Separate."
                outcomes.append({"folder": path, "status": status, "message": message, "record_id": record_id})
        return {"items": outcomes, "counts": {key: sum(row["status"] == key for row in outcomes)
                for key in ("added", "already_added", "review", "failed")}}

    def search(self, query: str = "") -> list[dict]:
        query = query.strip().casefold()
        return [self._public(row) for row in sorted(self.repository.records(), key=lambda row: (row["imported_at"], row["record_id"]), reverse=True)
                if not query or query in " ".join([row["name"], row["folder_path"], *row["number_evidence"]]).casefold()]

    def get(self, record_id):
        row = self.repository.get(record_id)
        if row is None:
            raise LookupError("Legacy project not found.")
        return self._public(row)

    @staticmethod
    def _public(row):
        return {key: value for key, value in row.items() if key not in {"source_id", "normalized_path"}}

    def open_folder(self, record_id):
        row = self.get(record_id)
        try:
            folder = self.folders.folder(row["folder_path"])
        except (OSError, ValueError):
            return {"status": "blocked", "message": "Folder is unavailable. Use Change Location to reconnect it."}
        result = self.opener.open_directory(Path(folder.path))
        return {"status": result.status, "message": result.message}

    def change_location(self, record_id, path, expected_revision):
        self.folders.reset_identity_cache()
        with self.repository.write():
            row = self.get(record_id)
            folder = self.folders.folder(path)
            if row["revision"] != expected_revision:
                raise ValueError("This record changed. Reload it before changing its location.")
            for ref in self.repository.references():
                if ref["kind"] == "legacy" and ref["id"] == record_id:
                    continue
                if any(self.folders.overlaps(folder.path, existing) for existing in ref["paths"]):
                    raise ValueError("This location belongs to another registered project.")
            return self._public(self.repository.relocate(record_id, folder.path,
                self.folders.normalized_path(folder.path), datetime.now(timezone.utc).isoformat()))
