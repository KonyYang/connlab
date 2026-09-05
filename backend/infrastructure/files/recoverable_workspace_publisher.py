"""Recover only an operation-owned workspace, including manifest/index gaps."""

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
from uuid import uuid4

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord, OfficialWorkspaceCreateResult
from backend.infrastructure.files.generation_journal import fingerprint, json_value
from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity, RecoverableOutputPublisher


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
            prior = tree_hash(conflict)
            if prior is not None and strategy not in {"backup_and_recreate", "overwrite_rebuild"}:
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
            if not whole and not preview.source_book_path.exists():
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
                "source_book_identity": file_identity(staged / "Source Book" if whole else source_book_stage or preview.source_book_path),
                "source_book_stage": str(source_book_stage) if source_book_stage is not None else None,
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
                        raise ValueError("Workspace conflict target changed before rebuild.")
                    conflict.rename(backup)
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
        manifest = {"schema_version": 1, "project_id": record.project_id, "dl_number": record.dl_number,
                    "local_workspace_path": str(record.local_workspace_path), "source_book_path": str(record.source_book_path),
                    "official_project_folder_path": str(target), "template_source_path": str(record.template_source_path),
                    "created_at": record.created_at}
        manifest_source = self.journal.project_path(record.project_id) / f"{self.state['operation_id']}-manifest-{uuid4().hex}.json"
        with manifest_source.open("x", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        publisher = RecoverableOutputPublisher(self.journal, self.state, "workspace")
        publisher.publish_file("manifest", manifest_source, record.manifest_path, effect["manifest_prior"])
        return repository.save(record)
