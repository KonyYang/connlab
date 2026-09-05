"""Atomic local journal and OS-owned project lock for folder generation."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from hashlib import sha256
import json
import os
from pathlib import Path
from uuid import uuid4


def json_value(value):
    if is_dataclass(value):
        return json_value(asdict(value))
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_value(v) for v in value]
    if isinstance(value, (Path, Enum)):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def fingerprint(value) -> str:
    return sha256(json.dumps(json_value(value), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class GenerationJournal:
    """One durable operation per project; a lost process releases its lock."""

    def __init__(self, root: Path):
        self.root = root

    def project_path(self, project_id: str) -> Path:
        return self.root / sha256(project_id.encode()).hexdigest()

    @contextmanager
    def lock(self, project_id: str):
        directory = self.project_path(project_id)
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "lock").open("a+b") as handle:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise ValueError("Project folder generation is already running.") from exc
            else:
                import fcntl
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise ValueError("Project folder generation is already running.") from exc
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle, fcntl.LOCK_UN)

    def create(self, project_id: str, strategy: str | None, context: str) -> dict:
        previous = self.read(project_id)
        if previous is not None:
            self.archive(previous)
        state = {"version": 1, "project_id": project_id, "operation_id": uuid4().hex,
                 "strategy": strategy, "context": context, "status": "queued",
                 "step": 0, "completed_steps": [], "effects": {}, "message": None}
        self.save(state)
        return state

    def archive(self, state):
        self._write(state, self.project_path(state["project_id"]) / "history" / f"{state['operation_id']}.json")

    def read_archived(self, project_id, operation_id):
        if len(operation_id) != 32 or any(char not in "0123456789abcdef" for char in operation_id):
            raise ValueError("Invalid generation operation identity.")
        return self._read(project_id, self.project_path(project_id) / "history" / f"{operation_id}.json")

    def read(self, project_id: str) -> dict | None:
        path = self.project_path(project_id) / "operation.json"
        return self._read(project_id, path)

    def _read(self, project_id, path):
        if not path.exists():
            return None
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            state = envelope["state"]
            if (envelope["checksum"] != fingerprint(state) or state["version"] != 1
                    or state["project_id"] != project_id or not isinstance(state["effects"], dict)):
                raise ValueError("Invalid journal")
            return state
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValueError("Generation recovery journal is damaged; manual review is required.") from exc

    def save(self, state: dict):
        self._write(state, self.project_path(state["project_id"]) / "operation.json")

    def _write(self, state, path):
        directory = path.parent
        directory.mkdir(parents=True, exist_ok=True)
        temporary = directory / f"journal-{uuid4().hex}.tmp"
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump({"state": json_value(state), "checksum": fingerprint(state)}, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
