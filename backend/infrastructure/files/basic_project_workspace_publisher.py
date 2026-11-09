"""Identity-bound, non-overwriting directory publication for basic workspaces."""

import json
import os
from pathlib import Path
from uuid import uuid4

from backend.infrastructure.files.generation_journal import GenerationJournal, json_value
from backend.infrastructure.files.recoverable_output_publisher import (
    RecoverableOutputPublisher, file_hash, file_identity, require_safe_output_path,
)
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway


class BasicProjectWorkspaceJournal(GenerationJournal):
    def save(self, state):
        try:
            super().save(state)
        except OSError as exc:
            raise ValueError("Basic folder recovery journal cannot be saved. Restore storage access before continuing.") from exc


class BasicMaterialPublisher(RecoverableOutputPublisher):
    def skip_failed_file(self, key):
        """Discard only an owned staged new copy after an ordinary file failure."""
        self.verify_context()
        effect_key = f"{self.step}:{key}"
        effect = self.state["effects"].get(effect_key)
        if effect is None:
            return
        if effect.get("prior") is not None:
            raise ValueError("Basic material archive cannot replace an existing file.")
        stage = Path(effect["stage"])
        require_safe_output_path(stage)
        if stage.exists():
            if file_identity(stage) != effect["identity"] or file_hash(stage) != effect["sha"]:
                raise ValueError("Owned material staging changed; retain files and review recovery.")
            stage.unlink()
        self.state["effects"].pop(effect_key)
        self.journal.save(self.state)


class BasicProjectWorkspacePublisher:
    def __init__(self, journal, state):
        self.journal, self.state = journal, state

    def directory(self, path: Path, *, accepted_identity):
        require_safe_output_path(path)
        key = "directory:" + str(path)
        effect = self.state["effects"].get(key)
        if effect:
            if not path.is_dir() or file_identity(path) != effect["identity"]:
                raise ValueError(f"Project directory changed during recovery: {path}")
            return
        if path.exists():
            if not path.is_dir() or accepted_identity is None or file_identity(path) != accepted_identity:
                raise ValueError(f"Reviewed project directory changed: {path}")
            identity = file_identity(path)
        else:
            # Stage identity is durable before publication. On Windows rename will not replace
            # another process's directory. POSIX uses the existing no-replace gateway primitive.
            from backend.infrastructure.files.public_folder_workflow_gateway import _rename_directory_no_replace
            stage = path.parent / f".connlab-basic-{self.state['operation_id']}-{uuid4().hex}"
            stage.mkdir()
            identity = file_identity(stage)
            self.state["effects"][key] = {"type": "basic_directory", "target": str(path), "stage": str(stage), "identity": identity}
            self.journal.save(self.state)
            _rename_directory_no_replace(stage, path)
        self.state["effects"][key] = {"type": "basic_directory", "target": str(path), "identity": identity}
        self.journal.save(self.state)

    def recover_directories(self):
        for effect in list(self.state["effects"].values()):
            if effect["type"] != "basic_directory":
                continue
            target = Path(effect["target"])
            require_safe_output_path(target)
            if target.exists():
                if not target.is_dir() or file_identity(target) != effect["identity"]:
                    raise ValueError("Project directory identity changed; recovery stopped.")
            elif effect.get("stage"):
                stage = Path(effect["stage"])
                require_safe_output_path(stage)
                if not stage.is_dir() or file_identity(stage) != effect["identity"]:
                    raise ValueError("Staged directory changed; retain files and review.")
                from backend.infrastructure.files.public_folder_workflow_gateway import _rename_directory_no_replace
                _rename_directory_no_replace(stage, target)
            else:
                raise ValueError("A completed project directory was removed; review before recovery.")

    def verify_directories(self):
        for effect in self.state["effects"].values():
            if effect["type"] != "basic_directory":
                continue
            path = Path(effect["target"])
            require_safe_output_path(path)
            if path.exists() and (not path.is_dir() or file_identity(path) != effect["identity"]):
                raise ValueError(f"Project directory identity changed: {path}")
            if not path.exists() and not effect.get("stage"):
                raise ValueError(f"Project directory was removed: {path}")

    def manifest(self, record):
        self.verify_directories()
        path = record.manifest_path
        require_safe_output_path(path)
        if path.exists():
            payload = OfficialWorkspaceManifestGateway().read(path)
            if payload.get("project_id") != record.project_id or payload.get("dl_number") != record.dl_number:
                raise ValueError("Existing workspace manifest belongs to another project.")
            if payload.get("schema_version") not in {1, 2}:
                raise ValueError("Workspace manifest version is unsupported.")
            if payload.get("official_project_folder_path") != str(record.official_folder_path):
                raise ValueError("Workspace manifest target differs; review the association.")
            registered = payload.get("official_folder_identity")
            if registered is not None and registered != file_identity(record.official_folder_path):
                raise ValueError("Workspace manifest directory identity changed.")
            return
        source = self.journal.project_path(record.project_id) / f"manifest-{self.state['operation_id']}.json"
        payload = {"schema_version": 2, **json_value(record),
                   "official_project_folder_path": str(record.official_folder_path),
                   "official_folder_identity": file_identity(record.official_folder_path)}
        with source.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        RecoverableOutputPublisher(self.journal, self.state, "directory").publish_file("manifest", source, path, None)
