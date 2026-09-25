"""Recover only an operation-owned workspace, including manifest/index gaps."""

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import stat
from backend.shared.operation_diagnostics import stage
from uuid import uuid4

from backend.application.official_project_workspace_service import (
    _unique_backup_path,
    _require_archive_path_capacity,
    merge_missing_workspace_tree,
    OfficialWorkspaceRecord,
    OfficialWorkspaceCreateResult,
)
from backend.application.project_folder_generation_service import (
    ProjectFolderInUseError,
)
from backend.infrastructure.files.generation_journal import fingerprint, json_value
from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity, RecoverableOutputPublisher
from backend.infrastructure.official_workspace_manifest import (
    OfficialWorkspaceManifestGateway, stable_folder_identity,
)


def _is_redirected(path: Path):
    # lstat also identifies Windows junctions on supported Python 3.11 runtimes.
    return path.is_symlink() or bool(
        getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def tree_hash(path: Path):
    if not path.exists():
        return None
    if _is_redirected(path) or not path.is_dir():
        raise ValueError("Workspace target is not a regular directory.")
    entries = []
    for item in sorted(path.rglob("*")):
        if _is_redirected(item):
            raise ValueError("Workspace contains a symbolic link; manual review is required.")
        entries.append((str(item.relative_to(path)), file_hash(item) if item.is_file() else "directory"))
    return fingerprint(entries)


def _require_manifest_source_identity(manifest_path, source, actual_folder, project_id, dl_number):
    """Honor a retained inode proof without rejecting legacy manifests that lack one."""
    if not manifest_path.is_file():
        raise ValueError("Workspace manifest identity needs review before archive.")
    try:
        manifest = OfficialWorkspaceManifestGateway().read(manifest_path)
    except (OSError, ValueError) as exc:
        raise ValueError("Workspace manifest identity needs review before archive.") from exc
    if (not isinstance(manifest, dict)
            or manifest.get("project_id") != project_id
            or manifest.get("dl_number") not in (None, "", dl_number)
            or manifest.get("official_project_folder_path") != str(source)):
        raise ValueError("Workspace manifest identity needs review before archive.")
    retained = manifest.get("official_folder_identity")
    if retained is not None and retained != stable_folder_identity(actual_folder):
        raise ValueError("Official folder identity differs from the workspace manifest.")


class RecoverableWorkspacePublisher:
    def __init__(self, journal, state, verify_context=None, verify_initial_preview=None):
        self.journal, self.state = journal, state
        self.verify_context = verify_context or (lambda: None)
        self.verify_initial_preview = verify_initial_preview or (lambda: None)

    def remember_existing(self, record):
        """Bind an unchanged, already indexed workspace before later steps use it."""
        if self.state.get("strategy") == "update_in_place":
            payload = OfficialWorkspaceManifestGateway().read(record.manifest_path)
            if (
                not isinstance(payload, dict)
                or payload.get("project_id") != record.project_id
                or payload.get("dl_number") != record.dl_number
                or payload.get("official_project_folder_path") != str(record.official_folder_path)
                or (payload.get("official_folder_identity") is not None
                    and payload["official_folder_identity"] != stable_folder_identity(record.official_folder_path))
                or OfficialWorkspaceManifestGateway.first_redirected_path(
                    record.local_workspace_path.parent, record.local_workspace_path,
                    record.source_book_path, record.official_folder_path,
                    record.manifest_path.parent, record.manifest_path,
                ) is not None
            ):
                raise ValueError(
                    "Existing official folder identity is unproven; review the folder before updating in place."
                )
        if "workspace_directories" in self.state:
            self.verify_directories(record)
            return
        self.state["workspace_directories"] = {
            key: {"path": str(getattr(record, key)), "identity": file_identity(getattr(record, key))}
            for key in ("local_workspace_path", "official_folder_path", "source_book_path")
        }
        self.journal.save(self.state)

    def finalize(self):
        """Discard the confirmed overwrite copy only after the caller completes its chain.

        Persist a bounded deletion inventory before removing anything. A power loss
        can leave an unchanged subset, but must never authorize deleting new content.
        History mode intentionally retains its old directory.
        """
        effect = self.state["effects"].get("workspace")
        if (not effect or effect.get("strategy") != "overwrite_rebuild"
                or not effect.get("overwrite_cleanup") or effect["prior"] is None):
            return
        backup = Path(effect["backup"])
        workspace = Path(effect["record"]["local_workspace_path"])
        operation_root = workspace.parent / ".connlab" / "generation" / self.state["operation_id"]
        if backup != operation_root / "overwrite-old":
            raise ValueError("Overwrite recovery directory is outside its approved location.")
        if any(_is_redirected(path) for path in backup.parents if path.exists()):
            raise ValueError("Overwrite recovery directory parent is redirected.")
        inventory = effect.get("overwrite_delete_inventory")
        if not os.path.lexists(backup):
            if inventory is None:
                raise ValueError("Overwrite recovery copy disappeared before finalization.")
            effect["overwrite_deleted"] = True
            self.journal.save(self.state)
            return
        identity = effect.get("backup_identity") or effect.get(
            "existing_workspace_identity" if effect["whole"] else "existing_target_identity"
        )
        if identity is None or _is_redirected(backup) or file_identity(backup) != identity:
            raise ValueError("Overwrite recovery directory identity changed; deletion stopped.")
        self.verify_context()
        current = {}
        for item in backup.rglob("*"):
            if _is_redirected(item):
                raise ValueError("Overwrite recovery copy contains redirected content.")
            current[str(item.relative_to(backup))] = {
                "identity": file_identity(item),
                "sha": None if item.is_dir() else file_hash(item),
                "directory": item.is_dir(),
            }
        if inventory is None:
            if tree_hash(backup) != effect["prior"]:
                raise ValueError("Overwrite recovery copy changed; deletion stopped.")
            inventory = effect["overwrite_delete_inventory"] = current
            self.journal.save(self.state)
        elif any(inventory.get(key) != value for key, value in current.items()):
            raise ValueError("Overwrite recovery copy changed during deletion; review required.")
        for relative in sorted(current, key=lambda key: len(Path(key).parts), reverse=True):
            item = backup / relative
            self._remove_overwrite_entry(item, backup, identity, current[relative])
        self._remove_overwrite_entry(
            backup, backup, identity, {"identity": identity, "directory": True}
        )
        effect["overwrite_deleted"] = True
        self.journal.save(self.state)

    def _remove_overwrite_entry(self, item, backup, identity, expected):
        def verify_entry():
            if (any(_is_redirected(path) for path in (item, *item.parents))
                    or file_identity(backup) != identity
                    or file_identity(item) != expected["identity"]
                    or item.is_dir() != expected["directory"]
                    or (not expected["directory"] and file_hash(item) != expected["sha"])):
                raise ValueError("Overwrite recovery entry changed before deletion.")

        def verify_retry():
            verify_entry()
            self.verify_context()
            inventory = self.state["effects"]["workspace"]["overwrite_delete_inventory"]
            for remaining in backup.rglob("*"):
                if _is_redirected(remaining):
                    raise ValueError("Overwrite recovery copy contains redirected content.")
                actual = {"identity": file_identity(remaining),
                          "sha": None if remaining.is_dir() else file_hash(remaining),
                          "directory": remaining.is_dir()}
                if inventory.get(str(remaining.relative_to(backup))) != actual:
                    raise ValueError("Overwrite recovery copy changed during deletion; review required.")
            if expected["directory"] and any(item.iterdir()):
                raise ValueError("Overwrite recovery directory is no longer empty; deletion stopped.")
            verify_entry()

        remove = item.rmdir if expected["directory"] else item.unlink
        verify_entry()
        try:
            remove()
        except PermissionError:
            if os.name != "nt":
                raise
            verify_retry()
            info = item.lstat()
            if not info.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY:
                raise
            if not expected["directory"] and info.st_nlink != 1:
                raise ValueError(
                    "Overwrite recovery file may have another hard link; "
                    "review before changing readonly attributes."
                )
            # Windows chmod changes only READONLY, never ACLs or other attributes.
            # File attributes are shared by hard links, including outside this copy.
            item.chmod(stat.S_IWRITE)
            verify_retry()
            remove()

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
            conflict = preview.conflict_paths[0] if len(preview.conflict_paths) == 1 else target
            identity_only_archive = (strategy == "backup_and_recreate" and conflict != workspace
                                     and self.state.get("archive_source_identity_only") is True)
            if identity_only_archive and target.parent != workspace:
                raise ValueError("New official folder must remain inside the indexed LTR workspace.")
            # Continuing an existing folder never reads, moves, or replaces its
            # current files. Directory identity is sufficient; hashing the whole
            # tree would make an open Office/PDF file an unnecessary blocker.
            try:
                with stage("inspect_existing_folder", target=conflict):
                    prior = (None if strategy == "continue_existing" else
                             "directory_identity" if identity_only_archive else tree_hash(conflict))
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
            if identity_only_archive:
                _require_manifest_source_identity(
                    preview.manifest_path, conflict, conflict, preview.project_id, preview.dl_number,
                )
                if (not conflict.is_dir() or _is_redirected(conflict)
                        or conflict.parent != workspace
                        or not conflict.name.startswith(f"{preview.dl_number} ")
                        or (target != conflict and os.path.lexists(target))):
                    raise ValueError("Reviewed active project folder changed before archive.")
                active = [child for child in workspace.iterdir()
                          if child.name.startswith(f"{preview.dl_number} ")]
                if active != [conflict]:
                    raise ValueError("Exactly one active LTR folder is required before archive.")
            backup = conflict.with_name(f"{conflict.name}.connlab-backup-{self.state['operation_id']}")
            if prior is not None:
                backup = (_unique_backup_path(
                    conflict, shallow=identity_only_archive,
                    dl_number=preview.dl_number if identity_only_archive else None,
                ) if strategy == "backup_and_recreate"
                          else stage_root / "overwrite-old")
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
                "archive_source_identity_only": identity_only_archive,
                "archive_parent_identity": file_identity(workspace) if identity_only_archive else None,
                "backup": str(backup),
                "backup_identity": file_identity(conflict) if prior is not None else None,
                "overwrite_cleanup": strategy == "overwrite_rebuild",
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
        if effect.get("archive_source_identity_only") and target.parent != record.local_workspace_path:
            raise ValueError("New official folder must remain inside the indexed LTR workspace.")
        if effect.get("strategy") == "continue_existing":
            self._continue_existing(effect, record, staged)
            return self._publish_manifest_and_record(effect, record, repository)
        publish_target = Path(effect["publish_target"])
        owned = publish_target.is_dir() and file_identity(publish_target) == effect["publish_identity"]
        if owned and effect.get("archive_source_identity_only"):
            active = [child for child in record.local_workspace_path.iterdir()
                      if child.name.startswith(f"{record.dl_number} ")]
            if (file_identity(record.local_workspace_path) != effect.get("archive_parent_identity")
                    or active != [target]):
                raise ValueError("An unexpected active LTR folder appeared after publication; review before recovery.")
        if not owned:
            self.verify_context()
            conflict, backup = Path(effect["conflict"]), Path(effect["backup"])
            if effect["prior"] is not None:
                if effect.get("strategy") == "backup_and_recreate":
                    self._prepare_archive_destination(effect, record, conflict, backup)
                if os.path.lexists(backup):
                    if effect.get("archive_source_identity_only"):
                        _require_manifest_source_identity(
                            record.manifest_path, conflict, backup, record.project_id, record.dl_number,
                        )
                        if (file_identity(record.local_workspace_path) != effect.get("archive_parent_identity")
                                or file_hash(record.manifest_path) != effect.get("manifest_prior")):
                            raise ValueError("Reviewed LTR workspace or manifest changed during archive recovery.")
                        active = [child for child in record.local_workspace_path.iterdir()
                                  if child.name.startswith(f"{record.dl_number} ")]
                        if active:
                            raise ValueError("An unexpected active LTR folder appeared after archive; review before recovery.")
                    if ((not effect.get("archive_source_identity_only")
                         and tree_hash(backup) != effect["prior"]) or conflict.exists()
                            or _is_redirected(backup)
                            or (effect.get("backup_identity") is not None
                                and file_identity(backup) != effect["backup_identity"])):
                        raise ValueError("Workspace conflict target changed during recovery.")
                else:
                    if effect.get("archive_source_identity_only"):
                        _require_manifest_source_identity(
                            record.manifest_path, conflict, conflict, record.project_id, record.dl_number,
                        )
                        if (not conflict.is_dir() or _is_redirected(conflict)
                                or conflict.parent != record.local_workspace_path
                                or file_identity(conflict) != effect.get("backup_identity")
                                or file_identity(record.local_workspace_path) != effect.get("archive_parent_identity")
                                or file_hash(record.manifest_path) != effect.get("manifest_prior")
                                or (record.official_folder_path != conflict and os.path.lexists(record.official_folder_path))):
                            raise ValueError("Reviewed active project folder changed before archive.")
                        active = [child for child in record.local_workspace_path.iterdir()
                                  if child.name.startswith(f"{record.dl_number} ")]
                        if active != [conflict]:
                            raise ValueError("Exactly one active LTR folder is required before archive.")
                    elif tree_hash(conflict) != effect["prior"]:
                        if self._discard_unpublished_stage(effect, record, staged):
                            raise ValueError(
                                "The existing project folder changed before rebuilding. "
                                "Your files were preserved. Review a fresh preview and "
                                "start a new generation; choose Continue existing folder "
                                "to keep its current contents."
                            )
                        raise ValueError("Workspace conflict target changed before rebuild.")
                    if (effect.get("backup_identity") is not None
                            and file_identity(conflict) != effect["backup_identity"]):
                        raise ValueError("Workspace directory identity changed before rebuild.")
                    try:
                        with stage("move_existing_folder_to_backup", target=conflict, backup=backup):
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

    def _prepare_archive_destination(self, effect, record, conflict, backup):
        """Journal and recheck History/Folders ownership before moving a business child."""
        history = record.local_workspace_path / "History"
        folders = history / "Folders"
        if backup.parent != folders:
            # Interrupted operations from older releases retain their original
            # reviewed destination; no new operation chooses that layout.
            if effect.get("history_directories") is not None:
                raise ValueError("History archive destination changed during recovery.")
            return
        if (effect["whole"] or conflict.parent != record.local_workspace_path
                or not conflict.name.startswith(f"{record.dl_number} ")):
            raise ValueError("Only the reviewed active LTR folder can be archived.")
        _require_archive_path_capacity(
            conflict, backup, shallow=effect.get("archive_source_identity_only", False),
        )
        saved = effect.get("history_directories")
        if saved is None:
            for directory in (history, folders):
                if os.path.lexists(directory):
                    if _is_redirected(directory) or not directory.is_dir():
                        raise ValueError("History archive path is redirected or not a directory.")
                else:
                    directory.mkdir()
            saved = {str(path): file_identity(path) for path in (history, folders)}
            effect["history_directories"] = saved
            self.journal.save(self.state)
        for path in (history, folders):
            if (not path.is_dir() or _is_redirected(path)
                    or file_identity(path) != saved.get(str(path))):
                raise ValueError("History archive directory changed during recovery.")

    def _discard_unpublished_stage(self, effect, record, staged):
        """Release a pre-move checkpoint without touching the operator's folder."""
        if "workspace" in self.state["completed_steps"] or set(self.state["effects"]) != {"workspace"}:
            return False
        conflict, backup = Path(effect["conflict"]), Path(effect["backup"])
        expected_conflict = record.local_workspace_path if effect["whole"] else Path(effect["conflict"])
        expected_identity = effect.get(
            "existing_workspace_identity" if effect["whole"] else
            "backup_identity" if effect.get("archive_source_identity_only") else
            "existing_target_identity"
        )
        root = record.local_workspace_path.parent / ".connlab" / "generation" / self.state["operation_id"]
        try:
            # A backup (including a dangling link), changed directory identity, or
            # a foreign stage means publication cannot be proven not to have run.
            if (os.path.lexists(backup) or conflict != expected_conflict
                    or (not effect.get("archive_source_identity_only")
                        and Path(effect["publish_target"]) != expected_conflict)
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
                    "official_folder_identity": stable_folder_identity(record.official_folder_path),
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
