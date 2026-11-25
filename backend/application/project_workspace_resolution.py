"""Explicit, recoverable resolution of one registered project's missing workspace."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from backend.application.basic_project_workspace_service import registered_directory_missing
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.infrastructure.files.basic_project_workspace_publisher import BasicProjectWorkspacePublisher
from backend.infrastructure.files.generation_journal import GenerationJournal, fingerprint, json_value
from backend.infrastructure.files.recoverable_output_publisher import (
    RecoverableOutputPublisher, file_hash, file_identity, require_safe_output_path,
)
from backend.infrastructure.official_workspace_manifest import workspace_locations_overlap


def _record(values):
    paths = ("local_workspace_path", "source_book_path", "official_folder_path", "manifest_path", "template_source_path")
    return OfficialWorkspaceRecord(**{**values, **{key: Path(values[key]) if values[key] else None for key in paths}})


def _directory(value):
    if not value:
        raise ValueError("Choose an existing folder.")
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("Choose an absolute folder path.")
    require_safe_output_path(path)
    if not path.is_dir():
        raise ValueError(f"Folder is unavailable: {path}. Choose an accessible folder.")
    return path


class ProjectWorkspaceResolutionService:
    def __init__(self, basic, workspaces, default_root):
        self.basic = basic
        self.workspaces = workspaces
        self.default_root = default_root
        self.journal = basic.journal
        self.relocations = GenerationJournal(self.journal.root.parent / "official_folder_relocation")

    def _authority(self, project_id):
        _, _, number = self.basic.registered_identity(project_id)
        self.basic.check_other_writes(project_id)
        for journal in (self.basic.shared, self.relocations):
            operation = journal.read(project_id)
            if operation and operation["status"] != "completed":
                raise ValueError("Resume the unfinished project folder operation before changing its location.")
        record = self.workspaces.get_by_project(project_id)
        if record is None or record.project_id != project_id or record.dl_number != number:
            raise ValueError("The workspace must be registered to this project and its current LTR.")
        return record

    def _plan(self, project_id, strategy, path):
        old = self._authority(project_id)
        pending = self.journal.read(project_id)
        if pending and pending["status"] != "completed":
            raise ValueError("Resume the unfinished folder operation before selecting another location.")
        if not registered_directory_missing(old):
            raise ValueError("The registered location is present. Recheck the existing folder before continuing.")
        manifest_info = None
        if strategy == "recreate":
            parent = _directory(path or self.default_root())
            workspace = parent / old.dl_number
            require_safe_output_path(workspace)
            if workspace.exists():
                raise ValueError(f"The destination already exists: {workspace}. Choose another parent folder.")
        elif strategy == "relink":
            selected = _directory(path)
            workspace = selected.parent if selected.name == old.official_folder_path.name else selected
            parent = workspace.parent
            manifest_info = self._candidate(old, workspace)
        else:
            raise ValueError("Choose whether to link an existing folder or create a new workspace.")

        if workspace_locations_overlap(workspace, old.local_workspace_path):
            raise ValueError("Choose a workspace separate from the old registered location.")
        self.workspaces.require_workspace_unclaimed(project_id, workspace)
        record = replace(old, local_workspace_path=workspace, source_book_path=workspace / "Source Book",
                         official_folder_path=workspace / old.official_folder_path.name,
                         manifest_path=workspace / ".connlab" / "manifest.json")
        if strategy == "recreate":
            record = replace(record, creation_kind="basic", template_source_path=None)
        facts = {"previous_record": json_value(old), "record": json_value(record), "strategy": strategy,
                 "parent_identity": file_identity(parent), "candidate": manifest_info}
        return facts

    def _candidate(self, old, workspace):
        target = _directory(workspace / old.official_folder_path.name)
        source_book = _directory(workspace / "Source Book")
        manifest = workspace / ".connlab" / "manifest.json"
        require_safe_output_path(manifest)
        if not manifest.is_file():
            raise ValueError("Select the existing LTR workspace or its project folder with its .connlab identity manifest.")
        raw = manifest.read_bytes()
        try:
            payload = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("The selected project's identity manifest cannot be read.") from exc
        if (not isinstance(payload, dict) or payload.get("schema_version") not in (1, 2)
                or payload.get("project_id") != old.project_id or payload.get("dl_number") != old.dl_number
                or payload.get("workspace_id", old.workspace_id) != old.workspace_id):
            raise ValueError("This manifest does not match this project, its registered LTR and its previous workspace.")
        recorded_root = Path(str(payload.get("local_workspace_path")))
        digest = hashlib.sha256(raw).hexdigest()
        identity = file_identity(manifest)
        prior_location = recorded_root == old.local_workspace_path
        if recorded_root == workspace:
            prior_location = (payload.get("official_folder_identity") == file_identity(target)
                              and self._published_before_abandon(old, manifest, digest, identity))
        if (not prior_location
                or Path(str(payload.get("official_project_folder_path"))) != recorded_root / target.name
                or Path(str(payload.get("source_book_path"))) != recorded_root / source_book.name):
            raise ValueError("The project identity manifest does not match the registered folder layout.")
        return {"workspace_identity": file_identity(workspace), "folder_identity": file_identity(target),
                "source_book_identity": file_identity(source_book), "manifest_identity": identity,
                "manifest_sha": digest, "manifest": payload}

    def _published_before_abandon(self, old, manifest, digest, identity):
        # A retained candidate can have the new absolute paths even though registration
        # never committed. Accept only the exact identity file that this instance wrote.
        for receipt in self.journal.resolution_receipts(old.project_id):
            if receipt.get("resolution_outcome") != "abandoned" or receipt["previous_record"] != json_value(old):
                continue
            step = "resolution" if receipt["strategy"] == "relink" else "directory"
            effect = receipt["effects"].get(f"{step}:manifest")
            if (effect and Path(effect["target"]) == manifest and effect["sha"] == digest
                    and effect["identity"] == identity):
                return True
        return False

    def preview(self, project_id, strategy, path=None):
        facts = self._plan(project_id, strategy, path)
        return {"project_id": project_id, "strategy": strategy, "expected_context": fingerprint(facts),
                "old_path": facts["previous_record"]["official_folder_path"],
                "target_path": facts["record"]["official_folder_path"]}

    def apply(self, project_id, strategy, path, expected_context, request_id):
        if not request_id:
            raise ValueError("A request identity is required to resolve a folder.")
        with self.basic.shared.lock(project_id):
            state = self.journal.read(project_id)
            for prior in self.journal.resolution_receipts(project_id):
                if prior["request_id"] != request_id:
                    continue
                if (prior["strategy"], prior["path"], prior["context"]) != (strategy, str(path or ""), expected_context):
                    raise ValueError("This request already belongs to a different folder resolution.")
                return self._run(prior)
            facts = self._plan(project_id, strategy, path)
            if fingerprint(facts) != expected_context:
                raise ValueError("The project folder or destination changed. Review the location again.")
            if state:
                self.journal.archive(state)
            state = {**facts, "version": 1, "kind": "resolution", "project_id": project_id,
                     "request_id": request_id, "operation_id": uuid4().hex, "context": expected_context,
                     "path": str(path or ""), "status": "queued", "completed_steps": [], "effects": {}, "message": None}
            self.journal.save(state)
            return self._run(state)

    def resume(self, project_id, operation_id):
        with self.basic.shared.lock(project_id):
            state = self.journal.read(project_id)
            if not state or state.get("kind") != "resolution" or state["operation_id"] != operation_id:
                raise ValueError("Folder resolution has changed. Recheck the project folder.")
            return self._run(state)

    def abandon(self, project_id, operation_id):
        with self.basic.shared.lock(project_id):
            self.basic.registered_identity(project_id)
            state = self.journal.read(project_id)
            if not state or state.get("kind") != "resolution" or state["operation_id"] != operation_id:
                raise ValueError("Folder resolution has changed. Recheck the project folder.")
            old = _record(state["previous_record"])
            if (self.workspaces.get_by_project(project_id) != old
                    or state["status"] == "completed" and state.get("resolution_outcome") != "abandoned"):
                raise ValueError("The registered location has already changed. Review the active project folder.")
            if state.get("resolution_outcome") != "abandoned":
                state.update(status="completed", resolution_outcome="abandoned")
                self.journal.save(state)
            try:
                self.basic._verify_record(old)
                available = True
            except (OSError, ValueError):
                available = False
            return {"operation_id": operation_id, "status": "abandoned", "directory_available": available,
                    "official_project_folder_path": str(old.official_folder_path), "issues": [], "message": None}

    def _run(self, state):
        if state.get("resolution_outcome") == "abandoned":
            raise ValueError("This folder resolution was ended. Review the folder before starting a new attempt.")
        record = _record(state["record"])
        old = _record(state["previous_record"])

        def verify_context():
            indexed = self._authority(record.project_id)
            if indexed not in (old, record):
                raise ValueError("The active project folder changed. Review the registered location.")
            if indexed == old and not registered_directory_missing(old):
                raise ValueError("The previous workspace is accessible again. Recheck its location before continuing.")
            parent = _directory(record.local_workspace_path.parent)
            if file_identity(parent) != state["parent_identity"]:
                raise ValueError("The selected destination parent was replaced.")
            if workspace_locations_overlap(record.local_workspace_path, old.local_workspace_path):
                raise ValueError("The destination now overlaps the previous workspace.")
            self.workspaces.require_workspace_unclaimed(record.project_id, record.local_workspace_path)

        if state["status"] != "completed":
            try:
                verify_context()
                if state["strategy"] == "recreate":
                    publisher = BasicProjectWorkspacePublisher(self.journal, state)
                    publisher.recover_directories()
                    for path in self.basic._directories(record):
                        verify_context()
                        publisher.verify_directories()
                        publisher.directory(path, accepted_identity=None)
                    verify_context()
                    publisher.manifest(record)
                    publisher.verify_directories()
                else:
                    self._relink_manifest(record, state, verify_context)
                verify_context()
                self.basic._verify_record(record)
                manifest_step = "directory" if state["strategy"] == "recreate" else "resolution"
                effect = state["effects"].get(f"{manifest_step}:manifest")
                if (not effect or file_hash(record.manifest_path) != effect["sha"]
                        or file_identity(record.manifest_path) != effect["identity"]):
                    raise ValueError("The reviewed project identity manifest changed. Retain it and review the folder.")
                self.workspaces.save(record)
                self.basic.commit()
                state.update(status="completed", message=None)
                self.journal.save(state)
            except (ValueError, OSError, RuntimeError) as error:
                state.update(status="blocked", message=str(error))
                self.journal.save(state)
                raise
        available = self.workspaces.get_by_project(record.project_id) == record
        if available:
            self.basic._verify_record(record)
        return {"operation_id": state["operation_id"], "status": state["status"], "directory_available": available,
                "official_project_folder_path": str(record.official_folder_path), "issues": [], "message": None}

    def _relink_manifest(self, record, state, verify_context):
        candidate = state["candidate"]

        def verify_candidate():
            verify_context()
            for path, key in ((record.local_workspace_path, "workspace_identity"),
                              (record.official_folder_path, "folder_identity"), (record.source_book_path, "source_book_identity")):
                if file_identity(_directory(path)) != candidate[key]:
                    raise ValueError("The selected project directory changed after review.")
            require_safe_output_path(record.manifest_path)
            if "resolution:manifest" not in state["effects"] and file_identity(record.manifest_path) != candidate["manifest_identity"]:
                raise ValueError("The reviewed identity manifest was replaced.")

        verify_candidate()
        payload = {**candidate["manifest"], "workspace_id": record.workspace_id, "local_workspace_path": str(record.local_workspace_path),
                   "official_project_folder_path": str(record.official_folder_path), "source_book_path": str(record.source_book_path),
                   "official_folder_identity": candidate["folder_identity"]}
        for key in ("official_folder_path", "manifest_path"):
            if key in payload:
                payload[key] = str(getattr(record, key))
        source = self.journal.project_path(record.project_id) / f"resolution-{state['operation_id']}.json"
        source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        publisher = RecoverableOutputPublisher(self.journal, state, "resolution", verify_context=verify_candidate)
        publisher.publish_file("manifest", source, record.manifest_path, candidate["manifest_sha"])
        verify_candidate()
