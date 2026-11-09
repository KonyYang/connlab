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
        if effect is not None and effect.get("preparing"):
            self._discard_preparing(effect_key, effect)
            effect = None
        if effect is None:
            if file_hash(target) != prior:
                raise ValueError("Generation target changed before publication.")
            prior_identity = file_identity(target) if prior is not None else None
            target.parent.mkdir(parents=True, exist_ok=True)
            stage_root = self.publication_root or target.parent
            require_safe_output_path(stage_root)
            stage_root.mkdir(parents=True, exist_ok=True)
            staged = stage_root / f".connlab-{self.state['operation_id']}-{uuid4().hex}{target.suffix}"
            # Save the pathname before creating a file: even failure to read the
            # opened handle's identity must leave recovery provenance, not an orphan.
            effect = {"type": "file", "step": self.step, "target": str(target),
                      "stage": str(staged), "prior": prior, "sha": None,
                      "prior_identity": prior_identity, "identity": None,
                      "record": json_value(record), "preparing": True}
            self.state["effects"][effect_key] = effect
            self.journal.save(self.state)
            try:
                with source.open("rb") as input_file, staged.open("xb") as output:
                    opened = os.fstat(output.fileno())
                    if not opened.st_ino:
                        raise ValueError("The filesystem cannot prove staged output ownership.")
                    effect["identity"] = [opened.st_dev, opened.st_ino]
                    self.journal.save(self.state)
                    try:
                        if file_identity(staged) != effect["identity"]:
                            raise ValueError("Staged output was replaced before source copy.")
                    except OSError as exc:
                        raise ValueError("Staged output identity cannot be verified before source copy.") from exc
                    shutil.copyfileobj(input_file, output)
                    output.flush()
                    os.fsync(output.fileno())
                try:
                    digest = file_hash(staged)
                    if file_identity(staged) != effect["identity"]:
                        raise ValueError("Staged output was replaced during source copy.")
                except OSError as exc:
                    raise ValueError("Staged output metadata cannot be verified after source copy.") from exc
                effect.update(sha=digest, preparing=False)
                self.journal.save(self.state)
            except BaseException:
                self._discard_preparing(effect_key, effect)
                raise
        self._publish(effect)

    def _discard_preparing(self, effect_key, effect):
        self.verify_context()
        staged = Path(effect["stage"])
        try:
            require_safe_output_path(staged)
            if staged.exists():
                if effect.get("identity") is None or file_identity(staged) != effect["identity"]:
                    raise ValueError("Incomplete staged output ownership cannot be proved.")
                staged.unlink()
        except (ValueError, OSError) as exc:
            raise ValueError(f"Incomplete staging needs manual recovery: {staged}. Reason: {exc}. Retain this file; the operation cannot complete or sync.") from exc
        self.state["effects"].pop(effect_key)
        self.journal.save(self.state)

    def _publish(self, effect):
        if effect.get("preparing"):
            raise ValueError("Incomplete output staging must be recovered before publication.")
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
        for effect_key, effect in list(self.state["effects"].items()):
            if effect["type"] == "file" and effect["step"] == self.step:
                if effect.get("preparing"):
                    self._discard_preparing(effect_key, effect)
                    continue
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
