"""Frozen-effect publisher with durable backups and exclusive target creation."""

import os
from pathlib import Path
from uuid import uuid4
from backend.application.project_file_generation_types import ProjectFileTargetLockedError

from backend.infrastructure.files.recoverable_output_publisher import (
    file_hash, file_identity, require_safe_output_path,
)
from backend.infrastructure.files.project_folder_required_forms_gateway import _move_without_replace
from backend.infrastructure.files.generation_journal import fingerprint


def sync_file(path):
    with Path(path).open("r+b") as handle:
        os.fsync(handle.fileno())


def sync_directory(path):
    if os.name != "nt":
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def target_action(action, *args):
    """Only classify filesystem calls, never journal or database permission errors."""
    try:
        return action(*args)
    except PermissionError as exc:
        raise ProjectFileTargetLockedError(str(exc)) from exc


class RecoverableProjectFilePublisher:
    def __init__(self, journal, state, verify_workspace=None):
        self.journal, self.state = journal, state
        self.verify_workspace = verify_workspace or (lambda: None)

    def prepare(self, stage, target, backup, *, expected_prior=None, expected_identity=None):
        stage, target = Path(stage), Path(target)
        for path in (stage, target):
            require_safe_output_path(path)
        prior = file_hash(target)
        if expected_prior is not None and prior != expected_prior:
            raise ValueError("Target changed during generation.")
        if expected_identity is not None and file_identity(target) != expected_identity:
            raise ValueError("Target identity changed during generation.")
        if prior is not None and backup is None:
            raise ValueError("Target reappeared; existing files require explicit backup replacement.")
        if backup is not None and prior is None:
            raise ValueError("Replacement target changed during generation.")
        sync_file(stage)
        effect = {"stage": str(stage), "target": str(target), "backup": str(backup) if backup else None,
                  "sha": file_hash(stage), "identity": file_identity(stage),
                  "prior": prior, "prior_identity": file_identity(target) if prior else None,
                  "phase": "ready", "stage_parent_identity": file_identity(stage.parent),
                  "target_parent_identity": file_identity(target.parent),
                  "backup_parent_identity": None}
        if backup:
            directories = []
            parent = Path(backup).parent
            while not parent.exists():
                directories.append({"path": str(parent), "identity": None})
                parent = parent.parent
            require_safe_output_path(parent)
            effect["history_anchor"] = {"path": str(parent), "identity": file_identity(parent)}
            effect["history_directories"] = list(reversed(directories))
        # Also prove hard-link support and volume compatibility before archiving.
        if stage.stat().st_dev != target.parent.stat().st_dev:
            raise ValueError("Staging and target must use the same filesystem volume.")
        probe = stage.parent / ("link-probe-" + uuid4().hex)
        os.link(stage, probe)
        probe.unlink()
        return effect

    def publish(self, effect):
        self.verify_workspace()
        stage, target = Path(effect["stage"]), Path(effect["target"])
        for path in (stage, target):
            require_safe_output_path(path)
        if (file_identity(stage.parent) != effect["stage_parent_identity"]
                or file_identity(target.parent) != effect["target_parent_identity"]):
            raise ValueError("Publication parent directory changed; retain files for review.")
        if file_hash(stage) != effect["sha"] or file_identity(stage) != effect["identity"]:
            raise ValueError("The owned staged file changed; retain it for recovery.")
        backup = Path(effect["backup"]) if effect["backup"] else None
        if backup is not None and effect["phase"] not in {"ready", "backup_intent"}:
            self._verify_backup(backup, effect)
        if target.exists() and target_action(file_hash, target) == effect["sha"] and file_identity(target) == effect["identity"]:
            effect["phase"] = "published"
            self.journal.save(self.state)
            return
        if effect["phase"] == "published":
            raise ValueError("Published target changed; recovery cannot overwrite manual changes.")
        if backup is not None:
            require_safe_output_path(backup)
            if backup.exists():
                self._verify_backup(backup, effect)
            else:
                if effect["phase"] not in {"ready", "backup_intent"}:
                    raise ValueError("Verified History backup disappeared; recovery stopped.")
                self._verify_prior(target, effect)
                effect["phase"] = "backup_intent"
                self.journal.save(self.state)
                self._prepare_history(effect)
                effect["backup_parent_identity"] = file_identity(backup.parent)
                self.journal.save(self.state)
                target_action(_move_without_replace, target, backup)
                # A manual replacement racing the move is retained in History;
                # it is never discarded or silently accepted as the old file.
                self._verify_backup(backup, effect)
                target_action(sync_file, backup)
                sync_directory(backup.parent)
                sync_directory(target.parent)
            if target.exists():
                raise ValueError("Target reappeared after backup; recovery stopped.")
            effect["phase"] = "removed"
            self.journal.save(self.state)
        elif target.exists():
            raise ValueError("Target reappeared; exclusive publication refused it.")
        effect["phase"] = "publication_intent"
        self.journal.save(self.state)
        self.verify_workspace()
        target_action(os.link, stage, target)
        target_action(sync_file, target)
        sync_directory(target.parent)
        if file_identity(target) != effect["identity"] or file_hash(target) != effect["sha"]:
            raise ValueError("Published target changed before receipt verification.")
        effect["phase"] = "published"
        self.journal.save(self.state)

    @staticmethod
    def _verify_prior(target, effect):
        if target_action(file_hash, target) != effect["prior"] or file_identity(target) != effect["prior_identity"]:
            raise ValueError("Replacement target changed; backup replacement stopped.")

    @staticmethod
    def _verify_backup(backup, effect):
        require_safe_output_path(backup)
        if (not backup.exists() or file_identity(backup.parent) != effect["backup_parent_identity"]
                or target_action(file_hash, backup) != effect["prior"] or file_identity(backup) != effect["prior_identity"]):
            raise ValueError("History backup changed; retain both files for review.")

    def _prepare_history(self, effect):
        anchor = effect["history_anchor"]
        path = Path(anchor["path"])
        require_safe_output_path(path)
        if file_identity(path) != anchor["identity"]:
            raise ValueError("History parent changed; retain files for review.")
        for directory in effect["history_directories"]:
            path = Path(directory["path"])
            require_safe_output_path(path)
            if directory["identity"] is not None:
                if not path.is_dir() or file_identity(path) != directory["identity"]:
                    raise ValueError("History directory changed during recovery.")
            else:
                if path.exists():
                    raise ValueError("History directory ownership is unknown; retain it for review.")
                self.journal.save(self.state)
                path.mkdir()
                directory["identity"] = file_identity(path)
                self.journal.save(self.state)


class ProjectFilePublicationGateway:
    """Filesystem seam for the application coordinator; retain every staged artifact."""

    hash = staticmethod(file_hash)
    identity = staticmethod(file_identity)
    require_safe = staticmethod(require_safe_output_path)
    fingerprint = staticmethod(fingerprint)
    is_dir = staticmethod(lambda path: Path(path).is_dir())
    is_file = staticmethod(lambda path: Path(path).is_file())
    is_empty = staticmethod(lambda path: not any(Path(path).iterdir()))
    size = staticmethod(lambda path: Path(path).stat().st_size)

    @staticmethod
    def facts(target):
        if target is None:
            return None
        target = Path(target)
        require_safe_output_path(target)
        return {"sha": file_hash(target), "identity": file_identity(target)} if target.exists() else None

    @staticmethod
    def prepare_stage(journal, state, item):
        stage = Path(state["workspace"]["stage_parent"]) / state["operation_id"] / item["key"]
        require_safe_output_path(stage)
        item.update(stage=str(stage), stage_identity=None, status="generating")
        journal.save(state)
        if stage.exists():
            raise ValueError("Unowned staging location is occupied; retain it for review.")
        stage.mkdir(parents=True)
        item["stage_identity"] = file_identity(stage)
        journal.save(state)
        return stage

    @staticmethod
    def verify_generated(item, generated):
        stage, generated = Path(item["stage"]), Path(generated)
        require_safe_output_path(generated)
        if generated.parent != stage or file_identity(stage) != item["stage_identity"]:
            raise ValueError("Generator returned a file outside its owned staging directory.")

    @staticmethod
    def verify_stage(item):
        stage = Path(item["stage"])
        require_safe_output_path(stage)
        if stage.exists() and (not item.get("stage_identity") or file_identity(stage) != item["stage_identity"]):
            raise ValueError("Incomplete staging ownership is unknown. Retain files for manual review.")

    @staticmethod
    def verify_incomplete_stage(item):
        ProjectFilePublicationGateway.verify_stage(item)
        stage = Path(item["stage"])
        if stage.exists() and any(stage.iterdir()):
            raise ValueError("Unjournaled staged bytes need manual review. Retain this operation and all staged files.")

    @staticmethod
    def prepare(journal, state, item, generated):
        target = Path(item["target"])
        if ProjectFilePublicationGateway.facts(target) != item["prior"]:
            raise ValueError("Target changed during generation; generated staging was retained.")
        backup = (Path(state["workspace"]["local"]) / "History" / "Files" / state["operation_id"] / target.name
                  if item["action"] == "replace_with_backup" else None)
        return RecoverableProjectFilePublisher(journal, state).prepare(generated, target, backup,
            expected_prior=item["prior"]["sha"] if item["prior"] else None,
            expected_identity=item["prior"]["identity"] if item["prior"] else None)

    @staticmethod
    def publish(journal, state, effect, verify_workspace):
        RecoverableProjectFilePublisher(journal, state, verify_workspace).publish(effect)
