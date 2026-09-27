"""Filesystem gateway for Project Folder Required forms placement."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
from uuid import uuid4

from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity
from backend.infrastructure.files.generation_journal import json_value

from backend.application.project_folder_required_forms_service import (
    RequiredFormsTargetChangedError,
    compute_sha256,
)


class ProjectFolderRequiredFormsFileGateway:
    """Safely place generated Required forms into the Official project folder."""

    def create_new(self, source: Path, target: Path, *, key: str) -> None:
        """Copy a new file to target and fail if the target already exists."""
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            with source.open("rb") as input_file:
                shutil.copyfileobj(input_file, output)

    def update_managed(
        self,
        source: Path,
        target: Path,
        *,
        key: str,
        expected_existing_sha256: str,
    ) -> None:
        """Replace a ConnLab-managed target only if it is still unchanged."""
        if compute_sha256(target) != expected_existing_sha256:
            raise RequiredFormsTargetChangedError(str(target))
        temporary = target.with_name(f".{target.name}.connlab-tmp")
        try:
            shutil.copyfile(source, temporary)
            if compute_sha256(target) != expected_existing_sha256:
                raise RequiredFormsTargetChangedError(str(target))
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)


class RecoverableContactRecordPublisher:
    """Archive an existing measured form before no-clobber publication of a new blank form.

    The generation journal owns every transition. A retry accepts only the exact
    original inode or the exact archive/new inode recorded before the first move.
    """

    _STEP = "llcr_cr_records"

    def __init__(self, journal, state: dict, workspace: Path, verify_context):
        self.journal, self.state = journal, state
        self.workspace = Path(workspace)
        self.verify_context = verify_context

    def publish(self, record_type: str, source: Path, target: Path, expected_old: dict | None, record=None) -> None:
        if record_type not in {"llcr", "cr"}:
            raise ValueError("Only LLCR and CR forms are supported.")
        key = f"{self._STEP}:{record_type}"
        effect = self.state["effects"].get(key)
        if effect is None:
            target = Path(target)
            self._check_target_path(target)
            current = self._facts(target)
            if current != expected_old:
                raise ValueError("Contact record target changed after preview; no file was moved.")
            source = Path(source)
            if self._facts(source) is None:
                raise ValueError("The staged contact record is missing.")
            stage_dir = self.workspace / ".connlab" / "generation" / self.state["operation_id"]
            self._ensure_directory(stage_dir)
            staged = stage_dir / f"{record_type}-{uuid4().hex}.xlsx"
            with source.open("rb") as input_file, staged.open("xb") as output:
                shutil.copyfileobj(input_file, output)
                output.flush()
                os.fsync(output.fileno())
            history = self.workspace / "History" / "Test results"
            archive = history / f"{target.stem} {self.state['operation_id']}{target.suffix}"
            effect = {
                "type": "contact_record", "step": self._STEP, "record_type": record_type,
                "target": str(target), "archive": str(archive), "stage": str(staged),
                "prior": current, "new": self._facts(staged), "record": json_value(record),
                "workspace_identity": file_identity(self.workspace),
                "target_parent_identity": file_identity(target.parent),
                "stage_parent_identity": file_identity(staged.parent),
            }
            self.state["effects"][key] = effect
            self.journal.save(self.state)
        self._recover_one(effect)

    def recover(self, register=None) -> None:
        for effect in self.state["effects"].values():
            if effect.get("type") == "contact_record" and effect.get("step") == self._STEP:
                self._recover_one(effect)
                if register is not None and effect.get("record") is not None:
                    register(effect["record"])

    def verify_completed(self) -> None:
        if self._STEP not in self.state["completed_steps"]:
            return
        for effect in self.state["effects"].values():
            if effect.get("type") != "contact_record" or effect.get("step") != self._STEP:
                continue
            target, archive = Path(effect["target"]), Path(effect["archive"])
            self._check_target_path(target)
            if (file_identity(self.workspace) != effect["workspace_identity"]
                    or file_identity(target.parent) != effect["target_parent_identity"]):
                raise ValueError("Completed contact record directory changed; recovery stopped.")
            if effect.get("archive_parent_identity") is not None and (
                not archive.parent.is_dir()
                or _is_redirected(archive.parent)
                or file_identity(archive.parent) != effect["archive_parent_identity"]
            ):
                raise ValueError("Completed contact record History directory changed; recovery stopped.")
            if self._facts(target) != effect["new"]:
                raise ValueError("A completed contact record changed; recovery stopped.")
            if effect["prior"] is not None and self._facts(archive) != effect["prior"]:
                raise ValueError("An archived contact record changed; recovery stopped.")

    def _recover_one(self, effect: dict) -> None:
        self.verify_context()
        target, archive, staged = (Path(effect[key]) for key in ("target", "archive", "stage"))
        self._check_target_path(target)
        self._ensure_directory(staged.parent)
        if (file_identity(self.workspace) != effect["workspace_identity"]
                or file_identity(target.parent) != effect["target_parent_identity"]
                or file_identity(staged.parent) != effect["stage_parent_identity"]):
            raise ValueError("Contact record directories changed; recovery stopped.")
        prior, new = effect["prior"], effect["new"]
        if os.path.lexists(archive.parent):
            self._ensure_directory(archive.parent)
        if effect.get("archive_parent_identity") is not None:
            if not archive.parent.is_dir() or file_identity(archive.parent) != effect["archive_parent_identity"]:
                raise ValueError("Contact record History directory changed; recovery stopped.")
        existing, archived = self._facts(target), self._facts(archive)
        if existing == new:
            if prior is not None and archived != prior:
                raise ValueError("Archived contact record changed; recovery stopped.")
            self._remove_owned_stage(staged, target, new)
            return
        if prior is None:
            if existing is not None or archived is not None:
                raise ValueError("Contact record target appeared; recovery will not overwrite it.")
        else:
            if archived is None:
                if existing != prior:
                    raise ValueError("Measured contact record changed before archive; recovery stopped.")
                self._ensure_directory(archive.parent)
                effect["archive_parent_identity"] = file_identity(archive.parent)
                self.journal.save(self.state)
                self.verify_context()
                if (self._facts(target) != prior
                        or file_identity(archive.parent) != effect["archive_parent_identity"]):
                    raise ValueError("Measured contact record changed before archive; recovery stopped.")
                _move_without_replace(target, archive)
                archived = self._facts(archive)
                if file_identity(archive.parent) != effect["archive_parent_identity"]:
                    raise ValueError("Contact record History directory changed during archive.")
            if archived != prior:
                raise ValueError("Archived contact record changed; recovery stopped.")
            if self._facts(target) is not None:
                raise ValueError("Contact record target changed during archive; recovery stopped.")
        if self._facts(staged) != new:
            raise ValueError("Staged contact record changed; recovery stopped.")
        self.verify_context()
        if self._facts(target) is not None:
            raise ValueError("Contact record target appeared; recovery will not overwrite it.")
        os.link(staged, target)
        if self._facts(target) != new:
            raise ValueError("Published contact record identity changed; recovery stopped.")
        self._remove_owned_stage(staged, target, new)

    def _remove_owned_stage(self, staged: Path, target: Path, expected: dict) -> None:
        if os.path.lexists(staged):
            if (self._facts(staged) != expected or self._facts(target) != expected
                    or file_identity(staged) != file_identity(target)):
                raise ValueError("Contact record stage changed; it was not removed.")
            staged.unlink()

    def _check_target_path(self, target: Path) -> None:
        if not target.is_relative_to(self.workspace) or target == self.workspace:
            raise ValueError("Contact record target is outside the project workspace.")
        self._ensure_directory(target.parent)

    def _ensure_directory(self, directory: Path) -> None:
        if not directory.is_relative_to(self.workspace):
            raise ValueError("Contact record path is outside the project workspace.")
        current = self.workspace
        if _is_redirected(current) or not current.is_dir():
            raise ValueError("Contact record workspace is missing or redirected.")
        for part in directory.relative_to(self.workspace).parts:
            current = current / part
            self._require_safe_directory(current)

    @staticmethod
    def _require_safe_directory(current: Path) -> None:
        if _is_redirected(current):
            raise ValueError("Contact record directory is redirected.")
        if current.exists() and not current.is_dir():
            raise ValueError("Contact record directory is not a directory.")
        if not current.exists():
            current.mkdir()

    @staticmethod
    def _facts(path: Path) -> dict | None:
        if os.path.lexists(path) and (_is_redirected(path) or not path.is_file()):
            raise ValueError("Contact record path is not a regular file.")
        sha = file_hash(path)
        return {"sha": sha, "identity": file_identity(path)} if sha is not None else None


def _is_redirected(path: Path) -> bool:
    if not os.path.lexists(path):
        return False
    info = path.lstat()
    return path.is_symlink() or bool(
        getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _move_without_replace(source: Path, destination: Path) -> None:
    """Move atomically, never replacing an operator-owned History entry."""
    if os.name == "nt":
        # os.rename uses MoveFileExW without REPLACE_EXISTING on Windows.
        source.rename(destination)
        return
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    move = getattr(libc, "renameat2", None)
    if move is None:
        raise ValueError("No atomic no-replace archive move is available on this filesystem.")
    move.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    move.restype = ctypes.c_int
    if move(-100, os.fsencode(source), -100, os.fsencode(destination), 1) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(source))
