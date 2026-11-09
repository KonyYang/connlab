"""Create and reuse a trusted project directory independently of derived files."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from backend.application.official_project_workspace_naming import build_official_project_folder_name
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord, REQUIRED_TEMPLATE_PATHS
from backend.application.project_identity import resolve_project_identity
from backend.application.project_lifecycle_write_guard import ProjectLifecycleWriteGuard, LifecycleWriteOperation
from backend.infrastructure.files.basic_project_workspace_publisher import BasicProjectWorkspacePublisher, BasicProjectWorkspaceJournal
from backend.infrastructure.files.generation_journal import GenerationJournal, fingerprint, json_value
from backend.infrastructure.files.recoverable_output_publisher import file_identity, require_safe_output_path
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway
from backend.modules.ltr import parse_ltr_number
from backend.domain import LtrStatus


class BasicProjectWorkspaceService:
    def __init__(self, *, projects, workspaces, ltrs, settings, data_dir, collect_materials=None, commit=None, check_other_writes=None):
        self.projects, self.workspaces, self.ltrs = projects, workspaces, ltrs
        self.settings, self.data_dir = settings, data_dir
        self.journal = BasicProjectWorkspaceJournal(data_dir / "basic_project_workspace")
        self.shared = GenerationJournal(data_dir / "project_folder_generation")
        self.collect_materials = collect_materials
        self.commit = commit or (lambda: None)
        self.check_other_writes = check_other_writes or (lambda _: None)

    def _identity(self, project_id):
        project = self.projects.get(project_id)
        if project is None:
            raise LookupError("Project not found.")
        ProjectLifecycleWriteGuard(self.projects).require_write_allowed(project_id, LifecycleWriteOperation.REQUIRED_FORMS_GENERATE)
        registered = [record for record in self.ltrs.list_by_project(project_id) if record.status is LtrStatus.REGISTERED]
        identity = resolve_project_identity(project, registered)
        if not identity.has_registered_ltr:
            raise ValueError("A registered LTR number is required before creating the project folder.")
        number = parse_ltr_number(identity.ltr_number).normalized
        root = self.settings.local_workspace_root
        if root is None or not root.is_dir():
            raise ValueError(f"Project default save location must be an existing folder: {root}")
        require_safe_output_path(root)
        return project, identity, number, root

    def _record(self, project_id):
        project, identity, number, root = self._identity(project_id)
        record = self.workspaces.get_by_project(project_id)
        if record:
            if record.project_id != project_id or record.dl_number != number:
                raise ValueError("The linked folder identity does not match this project.")
            if (record.local_workspace_path == root or not record.local_workspace_path.is_relative_to(root)
                    or record.official_folder_path.parent != record.local_workspace_path
                    or record.source_book_path != record.local_workspace_path / "Source Book"
                    or record.manifest_path != record.local_workspace_path / ".connlab" / "manifest.json"):
                raise ValueError("The linked project folder is outside its registered workspace.")
            self._verify_record(record)
            return record
        workspace = root / number
        folder = workspace / build_official_project_folder_name(dl_number=number, product_description=identity.sample_description, test_description=identity.test_item)
        return OfficialWorkspaceRecord(uuid4().hex, project_id, number, workspace, workspace / "Source Book", folder,
            workspace / ".connlab" / "manifest.json", None, datetime.now(UTC).isoformat(), "basic")

    @staticmethod
    def _verify_record(record):
        for path in (record.local_workspace_path, record.official_folder_path, record.manifest_path):
            require_safe_output_path(path)
        if not record.official_folder_path.is_dir() or not record.manifest_path.is_file():
            raise ValueError("The linked project folder or identity manifest is missing. Review its association; no replacement folder was created.")
        data = OfficialWorkspaceManifestGateway().read(record.manifest_path)
        if (data.get("schema_version") not in {1, 2} or data.get("project_id") != record.project_id
                or data.get("dl_number") not in {None, "", record.dl_number}
                or data.get("official_project_folder_path") != str(record.official_folder_path)):
            raise ValueError("Project folder manifest identity needs review.")
        if data.get("official_folder_identity") is not None and data["official_folder_identity"] != file_identity(record.official_folder_path):
            raise ValueError("The linked project directory was replaced; review before writing.")

    def preview(self, project_id):
        blockers, record, target_identity, directories = [], None, None, {}
        try:
            record = self._record(project_id)
            require_safe_output_path(record.official_folder_path)
            linked = self.workspaces.get_by_project(project_id) is not None
            existing = record.official_folder_path.exists()
            if record.local_workspace_path.exists() and not record.local_workspace_path.is_dir():
                raise ValueError("The LTR workspace path is not a directory.")
            if existing and not record.official_folder_path.is_dir():
                raise ValueError("The project folder target is not a directory.")
            # An unregistered manifest must be reviewed, but another project's identity is never claimable.
            if record.manifest_path.exists() and not linked:
                self._verify_record(record)
            if record.local_workspace_path.is_dir() and not linked:
                candidates = [item for item in record.local_workspace_path.iterdir()
                              if item.is_dir() and item.name.startswith(record.dl_number + " ")]
                if any(item != record.official_folder_path for item in candidates):
                    raise ValueError("Another same-LTR folder exists. Review its association instead of creating another.")
            target_identity = file_identity(record.official_folder_path) if existing else None
            for path in self._directories(record):
                require_safe_output_path(path)
                if path.exists() and not path.is_dir():
                    raise ValueError(f"A required directory path is a file: {path}")
                directories[str(path)] = file_identity(path) if path.exists() else None
            status = "available" if linked else "review_required" if existing else "ready"
        except (ValueError, OSError) as exc:
            status = "blocked"
            blockers.append(str(exc))
        operation = self.journal.read(project_id)
        legacy = self.shared.read(project_id)
        if legacy and legacy["status"] != "completed":
            blockers.append("Project folder generation is unfinished. Resume the existing operation first.")
        if operation and operation["status"] != "completed":
            blockers.append("A basic project folder operation needs recovery.")
            status = "recovery_required"
        elif blockers:
            status = "blocked"
        available = False
        if self.workspaces.get_by_project(project_id):
            try:
                self._verify_record(self.workspaces.get_by_project(project_id))
                available = True
            except (ValueError, OSError):
                pass
        facts = {"project_id": project_id, "status": status, "directory_available": available,
                 "official_project_folder_path": str(record.official_folder_path) if record else None,
                 "target_identity": target_identity, "blockers": blockers,
                 "directories": directories,
                 "operation_id": operation["operation_id"] if operation and operation["status"] != "completed" else None}
        return {**facts, "expected_context": fingerprint(facts)}

    def create(self, project_id, expected_context, request_id, *, confirm_existing=False):
        with self.shared.lock(project_id):
            self._require_other_writes_clear(project_id)
            pending = self.journal.read(project_id)
            if pending and pending.get("request_id") == request_id:
                return self._run(pending) if pending["status"] != "completed" else self._result(pending)
            if pending and pending["status"] != "completed":
                raise ValueError("Resume the unfinished basic project folder operation before starting another.")
            preview = self.preview(project_id)
            if preview["expected_context"] != expected_context:
                raise ValueError("Project folder preview changed. Review it again before creating.")
            if preview["status"] not in {"ready", "available", "review_required"}:
                raise ValueError(preview["blockers"][0] if preview["blockers"] else "Project folder needs review.")
            if preview["status"] == "review_required" and not confirm_existing:
                raise ValueError("Confirm that the existing folder belongs to this project before linking it.")
            record = self._record(project_id)
            if pending:
                self.journal.archive(pending)
            state = {"version": 1, "project_id": project_id, "operation_id": uuid4().hex,
                     "strategy": None, "context": expected_context, "status": "queued", "step": 0,
                     "effects": {}, "message": None, "kind": "basic", "request_id": request_id,
                     "record": json_value(record), "directories": preview["directories"], "issues": [], "completed_steps": []}
            state["configured_root"] = str(self._identity(project_id)[3])
            self.journal.save(state)
            return self._run(state)

    def resume(self, project_id, operation_id):
        with self.shared.lock(project_id):
            self._require_other_writes_clear(project_id)
            state = self.journal.read(project_id)
            if not state or state["operation_id"] != operation_id or state.get("kind") != "basic":
                raise ValueError("The basic project folder operation changed; refresh and review.")
            return self._result(state) if state["status"] == "completed" else self._run(state)

    def _require_other_writes_clear(self, project_id):
        self._identity(project_id)
        legacy = self.shared.read(project_id)
        if legacy and legacy["status"] != "completed":
            raise ValueError("Project folder generation is unfinished. Resume the existing operation first.")
        self.check_other_writes(project_id)

    def _run(self, state):
        data = state["record"]
        record = OfficialWorkspaceRecord(**{**data, **{key: Path(data[key]) for key in
            ("local_workspace_path", "source_book_path", "official_folder_path", "manifest_path")},
            "template_source_path": Path(data["template_source_path"]) if data.get("template_source_path") else None})
        publisher = BasicProjectWorkspacePublisher(self.journal, state)
        def validate_inputs():
            _, _, number, root = self._identity(record.project_id)
            if number != record.dl_number or str(root) != state["configured_root"]:
                raise ValueError("Registered LTR or project save location changed. Review the interrupted folder operation before continuing.")
            publisher.verify_directories()
        try:
            validate_inputs()
            publisher.recover_directories()
            state["status"] = "running"
            self.journal.save(state)
            for path in self._directories(record):
                validate_inputs()
                publisher.directory(path, accepted_identity=state["directories"][str(path)])
            validate_inputs()
            publisher.manifest(record)
            validate_inputs()
            self.workspaces.save(record)
            self.commit()
            if "directory" not in state["completed_steps"]:
                state["completed_steps"].append("directory")
                self.journal.save(state)
            if self.collect_materials:
                validate_inputs()
                state["issues"] = self.collect_materials(record.project_id, self.journal, state, validate_inputs) or []
                self.commit()
            state.update(status="completed", message=None)
            self.journal.save(state)
        except Exception as exc:
            state.update(status="blocked", message=str(exc))
            self.journal.save(state)
            raise
        return self._result(state)

    @staticmethod
    def _directories(record):
        return (record.local_workspace_path, record.source_book_path, record.local_workspace_path / ".connlab",
                record.official_folder_path, *(record.official_folder_path / part for part in REQUIRED_TEMPLATE_PATHS))

    def _result(self, state):
        record = self.workspaces.get_by_project(state["project_id"])
        available = False
        if record:
            try:
                self._verify_record(record)
                available = True
            except (ValueError, OSError):
                pass
        return {"operation_id": state["operation_id"], "status": state["status"], "directory_available": available,
                "official_project_folder_path": str(record.official_folder_path) if record else None,
                "issues": state.get("issues", []), "message": state.get("message")}
