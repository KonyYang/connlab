"""Dedicated, checksummed file-generation receipts; never parsed as legacy v1."""

import json
from uuid import uuid4

from backend.infrastructure.files.generation_journal import GenerationJournal, fingerprint


class ProjectFileGenerationJournal(GenerationJournal):
    KIND = "project_file_generation"

    def create(self, project_id, request_id, signature, workspace_token, items, *, workspace=None, owner=None):
        previous = self.read(project_id)
        if previous:
            if previous["status"] != "completed":
                raise ValueError("An unfinished file operation must be resumed first.")
            self.archive(previous)
        state = {"version": 1, "kind": self.KIND, "project_id": project_id,
                 "operation_id": uuid4().hex, "request_id": request_id,
                 "request_signature": signature, "workspace_token": workspace_token,
                 "status": "queued", "outcome": None, "items": items,
                 "workspace": workspace or {}, "owner": owner,
                 "effects": {}, "message": None, "warnings": []}
        self.save(state)
        return state

    def _read(self, project_id, path):
        if not path.exists():
            return None
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            state = envelope["state"]
            if (envelope["checksum"] != fingerprint(state) or state["version"] != 1
                    or state["kind"] != self.KIND or state["project_id"] != project_id
                    or not isinstance(state["effects"], dict) or not isinstance(state["items"], list)
                    or not isinstance(state["workspace"], dict)
                    or not isinstance(state["request_id"], str) or not state["request_id"]
                    or not isinstance(state["request_signature"], str)
                    or not isinstance(state["workspace_token"], str)
                    or not isinstance(state["operation_id"], str) or len(state["operation_id"]) != 32
                    or any(char not in "0123456789abcdef" for char in state["operation_id"])
                    or state["status"] not in {"queued", "running", "interrupted", "completed"}):
                raise ValueError("Invalid file journal")
            keys = [item["key"] for item in state["items"]]
            if len(set(keys)) != len(keys) or not all(isinstance(item, dict) for item in state["effects"].values()):
                raise ValueError("Invalid per-file receipts")
            return state
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValueError("File generation recovery journal is damaged; retain files for review.") from exc

    def find_request(self, project_id, request_id):
        current = self.read(project_id)
        matches = [current] if current and current["request_id"] == request_id else []
        history = self.project_path(project_id) / "history"
        if history.exists():
            for path in history.glob("*.json"):
                state = self._read(project_id, path)
                if state["request_id"] == request_id:
                    matches.append(state)
        if len({state["request_signature"] for state in matches}) > 1:
            raise ValueError("File request identity has conflicting recovery receipts.")
        return matches[0] if matches else None
