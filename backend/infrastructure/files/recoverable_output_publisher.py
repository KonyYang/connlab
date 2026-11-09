"""Publish complete staged files with durable intent and proven file identity."""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import shutil
from uuid import uuid4

from backend.infrastructure.files.generation_journal import json_value
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway


def require_safe_output_path(path: Path) -> None:
    """Do not publish or recover through a replaced link/junction ancestor."""
    if OfficialWorkspaceManifestGateway.first_redirected_path(path, *path.parents) is not None:
        raise ValueError("Generation output path redirects through a link or junction; recovery stopped.")


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError("Generation target is not a regular file.")
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_identity(path: Path):
    stat = path.stat()
    if not stat.st_ino:
        raise ValueError("The filesystem cannot prove stable output identity. Manual review is required.")
    return [stat.st_dev, stat.st_ino]


class RecoverableOutputPublisher:
    def __init__(self, journal, state: dict, step: str, verify_context=None, publication_root=None):
        self.journal, self.state, self.step = journal, state, step
        self.verify_context = verify_context or (lambda: None)
        self.publication_root = publication_root

    @property
    def staging_directory(self):
        path = self.journal.project_path(self.state["project_id"]) / self.state["operation_id"] / "staging"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def publish_file(self, key, source: Path, target: Path, prior: str | None, record=None):
        self.verify_context()
        require_safe_output_path(target)
        effect_key = f"{self.step}:{key}"
        effect = self.state["effects"].get(effect_key)
        if effect is None:
            if file_hash(target) != prior:
                raise ValueError("Generation target changed before publication.")
            prior_identity = file_identity(target) if prior is not None else None
            target.parent.mkdir(parents=True, exist_ok=True)
            stage_root = self.publication_root or target.parent
            require_safe_output_path(stage_root)
            stage_root.mkdir(parents=True, exist_ok=True)
            staged = stage_root / f".connlab-{self.state['operation_id']}-{uuid4().hex}{target.suffix}"
            staged_identity = None
            try:
                with source.open("rb") as input_file, staged.open("xb") as output:
                    staged_identity = file_identity(staged)
                    shutil.copyfileobj(input_file, output)
                    output.flush()
                    os.fsync(output.fileno())
            except BaseException:
                if staged_identity is not None:
                    try:
                        require_safe_output_path(staged)
                        if file_identity(staged) != staged_identity:
                            raise ValueError("Staged output identity changed during source-copy failure.")
                        staged.unlink()
                    except (ValueError, OSError) as cleanup_error:
                        raise ValueError("Partial output staging could not be safely removed. Retain files and review recovery before syncing.") from cleanup_error
                raise
            effect = {"type": "file", "step": self.step, "target": str(target),
                      "stage": str(staged), "prior": prior, "sha": file_hash(staged),
                      "prior_identity": prior_identity,
                      "identity": file_identity(staged), "record": json_value(record)}
            self.state["effects"][effect_key] = effect
            self.journal.save(self.state)
        self._publish(effect)

    def _publish(self, effect):
        self.verify_context()
        target, staged = Path(effect["target"]), Path(effect["stage"])
        require_safe_output_path(target)
        require_safe_output_path(staged)
        current = file_hash(target)
        if current == effect["sha"] and file_identity(target) == effect["identity"]:
            self._remove_owned_stage(effect)
            return
        if current != effect["prior"] or (current is not None and file_identity(target) != effect["prior_identity"]):
            raise ValueError("Generation target changed; recovery will not overwrite it.")
        if not staged.is_file() or file_hash(staged) != effect["sha"] or file_identity(staged) != effect["identity"]:
            raise ValueError("Generation staged output is missing or changed; manual review is required.")
        if effect["prior"] is None:
            # Hard-link publication atomically fails if an unowned target appeared.
            os.link(staged, target)
        else:
            os.replace(staged, target)
        self._remove_owned_stage(effect)

    @staticmethod
    def _remove_owned_stage(effect):
        staged, target = Path(effect["stage"]), Path(effect["target"])
        if (staged != target and staged.is_file() and file_identity(staged) == effect["identity"]
                and file_hash(staged) == effect["sha"] and file_identity(target) == effect["identity"]):
            staged.unlink()

    def recover_files(self, register):
        for effect in self.state["effects"].values():
            if effect["type"] == "file" and effect["step"] == self.step:
                self._publish(effect)
                if effect["record"] is not None:
                    register(effect["record"])

    def verify_completed_files(self):
        latest = {}
        for effect in self.state["effects"].values():
            if effect["type"] == "file":
                latest[effect["target"]] = effect
        for effect in latest.values():
            if effect["step"] not in self.state["completed_steps"]:
                continue
            target = Path(effect["target"])
            require_safe_output_path(target)
            if file_hash(target) != effect["sha"] or file_identity(target) != effect["identity"]:
                raise ValueError("A completed generation target changed. Recovery stopped without overwriting it.")
