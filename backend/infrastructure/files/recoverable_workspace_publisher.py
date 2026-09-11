"""Recover only an operation-owned workspace, including manifest/index gaps."""

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import stat
from uuid import uuid4

from backend.application.official_project_workspace_service import (
    merge_missing_workspace_tree,
    OfficialWorkspaceRecord,
    OfficialWorkspaceCreateResult,
)
from backend.application.project_folder_generation_service import (
    ProjectFolderInUseError,
)
from backend.infrastructure.files.generation_journal import fingerprint, json_value
from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity, RecoverableOutputPublisher


def _is_redirected(path: Path):
    # lstat also identifies Windows junctions on supported Python 3.11 runtimes.
    return path.is_symlink() or bool(
        getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def tree_hash(path: Path):
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_dir():
        raise ValueError("Workspace target is not a regular directory.")
    entries = []
    for item in sorted(path.rglob("*")):
        if item.is_symlink():
            raise ValueError("Workspace contains a symbolic link; manual review is required.")
        entries.append((str(item.relative_to(path)), file_hash(item) if item.is_file() else "directory"))
    return fingerprint(entries)


class RecoverableWorkspacePublisher:
    def __init__(self, journal, state, verify_context=None, verify_initial_preview=None):
        self.journal, self.state = journal, state
        self.verify_context = verify_context or (lambda: None)
        self.verify_initial_preview = verify_initial_preview or (lambda: None)

    def remember_existing(self, record):
        """Bind an unchanged, already indexed workspace before later steps use it."""
        if "workspace_directories" in self.state:
            self.verify_directories(record)
            return
        self.state["workspace_directories"] = {
            key: {"path": str(getattr(record, key)), "identity": file_identity(getattr(record, key))}
            for key in ("local_workspace_path", "official_folder_path", "source_book_path")
        }
        self.journal.save(self.state)

    def verify_directories(self, record):
        """Check directory ownership, not the changing contents generated inside it."""
        effect = self.state["effects"].get("workspace")
        directories = self.state.get("workspace_directories")
        if effect is not None:
            directories = {key: {"path": effect["record"][key], "identity": effect[identity]}
                           for key, identity in (("local_workspace_path", "workspace_identity"),
                                                 ("official_folder_path", "identity"),
                                                 ("source_book_path", "source_book_identity"))}
        if directories is None:
            if "workspace" in self.state["completed_steps"]:
                raise ValueError("Generation workspace directory ownership is unproven; review before continuing.")
            return
        for key, saved in directories.items():
            path = Path(saved["path"])
            if (record is None or getattr(record, key) != path or path.is_symlink() or not path.is_dir()
                    or file_identity(path) != saved["identity"]):
                raise ValueError("Generation workspace directory changed; recovery stopped before writing files.")

    def create(self, preview, strategy, repository):
        if "workspace" not in self.state["effects"]:
            target = preview.official_folder_path
            workspace = preview.local_workspace_path
            conflict = workspace if preview.conflict_paths == (workspace,) else target
            # Continuing an existing folder never reads, moves, or replaces its
            # current files. Directory identity is sufficient; hashing the whole
            # tree would make an open Office/PDF file an unnecessary blocker.
            try:
                prior = None if strategy == "continue_existing" else tree_hash(conflict)
            except PermissionError as exc:
                raise ProjectFolderInUseError(str(conflict)) from exc
            if prior is not None and strategy not in {
                "continue_existing",
                "backup_and_recreate",
                "overwrite_rebuild",
            }:
                raise ValueError("Review the existing workspace conflict before rebuilding.")
            stage_root = workspace.parent / ".connlab" / "generation" / self.state["operation_id"]
            stage_root.mkdir(parents=True, exist_ok=True)
            staged = stage_root / f"{uuid4().hex}-workspace"
            whole = not workspace.exists() or conflict == workspace
            staged_official = staged / target.name if whole else staged
            shutil.copytree(preview.template_path, staged_official)
            if whole:
                (staged / "Source Book").mkdir()
            source_book_stage = None
            if strategy == "continue_existing":
                if (
                    preview.source_book_path.exists()
                    and not preview.source_book_path.is_dir()
                ):
                    raise ValueError(
                        "Existing Source Book is not a directory. Review the "
                        "workspace before generating."
                    )
            elif not whole and not preview.source_book_path.exists():
                source_book_stage = stage_root / f"{uuid4().hex}-source-book"
                source_book_stage.mkdir()
            elif not whole and not preview.source_book_path.is_dir():
                raise ValueError("Existing Source Book is not a directory. Review the workspace before generating.")
            record = OfficialWorkspaceRecord(
                workspace_id=uuid4().hex, project_id=preview.project_id, dl_number=preview.dl_number,
                local_workspace_path=workspace, source_book_path=preview.source_book_path,
                official_folder_path=target, manifest_path=preview.manifest_path,
                template_source_path=preview.template_path, created_at=datetime.now(UTC).isoformat(),
            )
            self.verify_initial_preview()
            self.state["effects"]["workspace"] = {
                "type": "workspace", "step": "workspace", "record": json_value(record),
                "stage": str(staged), "sha": tree_hash(staged_official), "identity": file_identity(staged_official),
                "publish_target": str(workspace if whole else target), "publish_identity": file_identity(staged),
                "whole": whole, "workspace_identity": file_identity(staged if whole else workspace),
                "source_book_identity": (
                    None
                    if strategy == "continue_existing"
                    else file_identity(
                        staged / "Source Book"
                        if whole
                        else source_book_stage or preview.source_book_path
                    )
                ),
                "source_book_stage": str(source_book_stage) if source_book_stage is not None else None,
                "strategy": strategy,
                "existing_workspace_identity": (
                    file_identity(workspace) if workspace.is_dir() else None
                ),
                "existing_target_identity": (
                    file_identity(target) if target.is_dir() else None
                ),
                "existing_source_book_identity": (
                    file_identity(preview.source_book_path)
                    if preview.source_book_path.is_dir()
                    else None
                ),
                "manifest_prior": None if whole else file_hash(preview.manifest_path),
                "conflict": str(conflict), "prior": prior,
                "backup": str(conflict.with_name(f"{conflict.name}.connlab-backup-{self.state['operation_id']}")),
            }
            self.journal.save(self.state)
        saved = self.recover(repository)
        return OfficialWorkspaceCreateResult(record=saved, created_paths=(saved.official_folder_path,), warnings=preview.warnings)

    def recover(self, repository):
        effect = self.state["effects"].get("workspace")
        if effect is None:
            return None
        payload = dict(effect["record"])
        for key in ("local_workspace_path", "source_book_path", "official_folder_path", "manifest_path", "template_source_path"):
            payload[key] = Path(payload[key])
        record = OfficialWorkspaceRecord(**payload)
        target, staged = record.official_folder_path, Path(effect["stage"])
        if effect.get("strategy") == "continue_existing":
            self._continue_existing(effect, record, staged)
            return self._publish_manifest_and_record(effect, record, repository)
        publish_target = Path(effect["publish_target"])
        owned = publish_target.is_dir() and file_identity(publish_target) == effect["publish_identity"]
        if not owned:
            self.verify_context()
            conflict, backup = Path(effect["conflict"]), Path(effect["backup"])
            if effect["prior"] is not None:
                if backup.exists():
                    if tree_hash(backup) != effect["prior"] or conflict.exists():
                        raise ValueError("Workspace conflict target changed during recovery.")
                else:
                    if tree_hash(conflict) != effect["prior"]:
                        if self._discard_unpublished_stage(effect, record, staged):
                            raise ValueError(
                                "The existing project folder changed before rebuilding. "
                                "Your files were preserved. Review a fresh preview and "
                                "start a new generation; choose Continue existing folder "
                                "to keep its current contents."
                            )
                        raise ValueError("Workspace conflict target changed before rebuild.")
                    try:
                        conflict.rename(backup)
                    except PermissionError as exc:
                        # Nothing outside the operation-owned stage changed when
                        # Windows refused the first publication move. Discard the
                        # effect so the caller may explicitly choose a different
                        # conflict strategy instead of being trapped in a
                        # non-replaceable checkpoint.
                        self._discard_unpublished_stage(effect, record, staged)
                        raise ProjectFolderInUseError(str(conflict)) from exc
            if publish_target.exists():
                raise ValueError("Workspace target has unknown provenance; recovery stopped.")
            staged_official = staged / target.name if effect["whole"] else staged
            if tree_hash(staged_official) != effect["sha"] or file_identity(staged) != effect["publish_identity"]:
                raise ValueError("Workspace stage changed; recovery stopped.")
            # Windows rename fails if destination appeared. Staging shares this volume.
            if os.name != "nt" and publish_target.exists():
                raise ValueError("Workspace target appeared before publication.")
            staged.rename(publish_target)
        if not record.source_book_path.exists() and effect.get("source_book_stage"):
            source_book_stage = Path(effect["source_book_stage"])
            if not source_book_stage.is_dir() or file_identity(source_book_stage) != effect["source_book_identity"]:
                raise ValueError("Source Book stage changed before publication.")
            source_book_stage.rename(record.source_book_path)
        if (tree_hash(target) != effect["sha"] or file_identity(target) != effect["identity"]
                or file_identity(record.local_workspace_path) != effect["workspace_identity"]
                or file_identity(record.source_book_path) != effect["source_book_identity"]):
            raise ValueError("Published workspace changed before recovery completed.")
        return self._publish_manifest_and_record(effect, record, repository)

    def _discard_unpublished_stage(self, effect, record, staged):
        """Release a pre-move checkpoint without touching the operator's folder."""
        if "workspace" in self.state["completed_steps"] or set(self.state["effects"]) != {"workspace"}:
            return False
        conflict, backup = Path(effect["conflict"]), Path(effect["backup"])
        expected_conflict = record.local_workspace_path if effect["whole"] else record.official_folder_path
        expected_identity = effect.get("existing_workspace_identity" if effect["whole"] else "existing_target_identity")
        root = record.local_workspace_path.parent / ".connlab" / "generation" / self.state["operation_id"]
        try:
            # A backup (including a dangling link), changed directory identity, or
            # a foreign stage means publication cannot be proven not to have run.
            if (os.path.lexists(backup) or conflict != expected_conflict
                    or Path(effect["publish_target"]) != expected_conflict
                    or expected_identity is None or _is_redirected(conflict) or not conflict.is_dir()
                    or file_identity(conflict) != expected_identity
                    or file_identity(conflict) == effect["publish_identity"]):
                return False
            if any(_is_redirected(path) for path in (root, *root.parents)):
                return False
            owned_paths = [(staged, effect["publish_identity"])]
            if effect.get("source_book_stage"):
                owned_paths.append((Path(effect["source_book_stage"]), effect["source_book_identity"]))
            for path, identity in owned_paths:
                if (_is_redirected(path) or not path.is_dir()
                        or path.resolve().parent != root.resolve()
                        or file_identity(path) != identity):
                    return False
            staged_official = staged / record.official_folder_path.name if effect["whole"] else staged
            if (any(_is_redirected(path) for path in staged.rglob("*"))
                    or tree_hash(staged_official) != effect["sha"]):
                return False
            source_stage = staged / "Source Book" if effect["whole"] else (
                Path(effect["source_book_stage"]) if effect.get("source_book_stage") else None
            )
            if source_stage is not None and (
                _is_redirected(source_stage) or not source_stage.is_dir()
                or file_identity(source_stage) != effect["source_book_identity"]
                or any(source_stage.iterdir())
            ):
                return False
            if effect["whole"] and set(staged.iterdir()) != {staged_official, source_stage}:
                return False
            self.verify_context()
            # Only the absolute, identity-checked operation stages above are removed.
            # Fail closed if cleanup cannot finish; never abandon unknown state.
            for path, _identity in owned_paths:
                shutil.rmtree(path.resolve())
        except (OSError, ValueError):
            return False
        self.state["effects"].pop("workspace")
        self.journal.save(self.state)
        return True

    def _continue_existing(self, effect, record, staged):
        """Adopt a reviewed folder and add only missing template entries."""
        workspace = record.local_workspace_path
        target = record.official_folder_path
        source_book = record.source_book_path
        if effect.get("adopted"):
            if (
                not workspace.is_dir()
                or file_identity(workspace) != effect["workspace_identity"]
                or not target.is_dir()
                or file_identity(target) != effect["identity"]
                or not source_book.is_dir()
                or file_identity(source_book) != effect["source_book_identity"]
            ):
                raise ValueError("Continued project workspace directories changed during recovery.")
            return
        self.verify_context()
        expected_workspace_identity = effect.get("existing_workspace_identity")
        if (
            expected_workspace_identity is None
            or not workspace.is_dir()
            or workspace.is_symlink()
            or file_identity(workspace) != expected_workspace_identity
        ):
            raise ValueError("Existing project workspace changed before it could be continued.")
        expected_target_identity = effect.get("existing_target_identity")
        if expected_target_identity is not None and (
            not target.is_dir()
            or target.is_symlink()
            or file_identity(target) != expected_target_identity
        ):
            raise ValueError("Existing official project folder changed before it could be continued.")
        expected_source_book_identity = effect.get("existing_source_book_identity")
        if expected_source_book_identity is not None and (
            not source_book.is_dir()
            or source_book.is_symlink()
            or file_identity(source_book) != expected_source_book_identity
        ):
            raise ValueError("Existing Source Book folder changed before it could be continued.")
        staged_official = staged / target.name if effect["whole"] else staged
        if tree_hash(staged_official) != effect["sha"]:
            raise ValueError("Workspace stage changed before existing content was continued.")
        source_book.mkdir(parents=True, exist_ok=True)
        merge_missing_workspace_tree(staged_official, target)
        effect.update(
            adopted=True,
            identity=file_identity(target),
            workspace_identity=file_identity(workspace),
            source_book_identity=file_identity(source_book),
        )
        self.journal.save(self.state)
        try:
            if (
                staged.is_dir()
                and not staged.is_symlink()
                and file_identity(staged) == effect["publish_identity"]
            ):
                shutil.rmtree(staged)
        except OSError:
            # The continued workspace is already journaled. A locked operation-
            # owned stage is harmless and may be cleaned on a later maintenance pass.
            pass

    def _publish_manifest_and_record(self, effect, record, repository):
        manifest = {"schema_version": 1, "project_id": record.project_id, "dl_number": record.dl_number,
                    "local_workspace_path": str(record.local_workspace_path), "source_book_path": str(record.source_book_path),
                    "official_project_folder_path": str(record.official_folder_path),
                    "template_source_path": str(record.template_source_path),
                    "created_at": record.created_at}
        manifest_source = self.journal.project_path(record.project_id) / f"{self.state['operation_id']}-manifest-{uuid4().hex}.json"
        with manifest_source.open("x", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        publisher = RecoverableOutputPublisher(self.journal, self.state, "workspace")
        publisher.publish_file("manifest", manifest_source, record.manifest_path, effect["manifest_prior"])
        return repository.save(record)
