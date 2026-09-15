"""Concrete short-session execution for the dedicated Project Folder operation."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

from backend.api import dependencies as deps
from backend.api.project_folder_preflight import package_preflight
from backend.application.project_folder_generation_service import (
    ProjectFolderGenerationService,
    basic_information_generation_blocker,
)
from backend.application.project_folder_required_forms_service import GenerateRequiredFormsCommand, RequiredFormsGenerateTarget
from backend.application.project_output_record_service import RegisterProjectOutputCommand
from backend.application.project_lifecycle_write_guard import LifecycleWriteOperation
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
from backend.infrastructure.files.generation_journal import GenerationJournal, fingerprint
from backend.infrastructure.files.recoverable_output_publisher import RecoverableOutputPublisher, file_hash
from backend.infrastructure.files.recoverable_workspace_publisher import RecoverableWorkspacePublisher, tree_hash


PROJECT_SCHEDULE_GENERATION_BLOCKER = (
    "Project Schedule is not confirmed. Open Matrix Editor, complete Project "
    "Schedule, and click Confirm schedule before generating Project Folder outputs. "
    "This date authority is required for Customer Feedback, Application Form, and "
    "Test Report."
)


class ProjectFolderGenerationRunner:
    def __init__(self, sessions, settings):
        self.sessions, self.settings = sessions, settings
        self.journal = GenerationJournal(settings.data_dir / "project_folder_generation")
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="project-folder")

    def service(self):
        return ProjectFolderGenerationService(self.journal, self.context, self.run_step, self.pool.submit, self.preview_context, self.preview, self.finalize)

    def finalize(self, state):
        if self.context(state["project_id"]) != state["context"]:
            raise ValueError("Generation inputs changed before final cleanup.")
        RecoverableWorkspacePublisher(self.journal, state).finalize()

    def context(self, project_id):
        with self.sessions() as session:
            deps.get_project_lifecycle_write_guard(session).require_write_allowed(project_id, LifecycleWriteOperation.REQUIRED_FORMS_GENERATE)
            assets = deps.FileAssetRepository(session).list_by_project(project_id)
            resources = deps.ExternalResourceRepository(session).list_all()
            try:
                fee_template = deps.resolve_fee_evaluation_template_path(deps.ExternalResourceRepository(session))
            except ValueError:
                # Missing/ambiguous templates remain a Required Forms business blocker, not a folder-creation blocker.
                fee_template = None
            matrix = deps.ConfirmedMatrixAuthorityRepository(session).get_active_by_project(project_id)
            schedule = deps.get_project_schedule_output_reader(session).get_latest_confirmed(project_id)
            template_files = []
            relevant_resources = []
            for resource in resources:
                kind = str(resource.resource_type)
                if not any(word in kind for word in ("template", "project_output_root", "public_drive_root")):
                    continue
                relevant_resources.append(resource)
                if resource.active and "template" in kind:
                    path = Path(resource.path)
                    template_files.append((str(path), self._template_context(path, fee_template)))
            return fingerprint({
                "project": deps.ProjectRepository(session).get(project_id),
                "assets": assets,
                "source_files": [(str(asset.path), file_hash(Path(asset.path))) for asset in assets],
                "forms": deps.ApplicationFormRepository(session).list_by_project(project_id),
                "ltrs": deps.LtrRecordRepository(session).list_by_project(project_id),
                "matrix": matrix,
                "schedule": schedule,
                "basic": deps.ProjectBasicInformationSnapshotReader(deps.ProjectBasicInformationRepository(session)).get_latest_confirmed(project_id),
                "fee": (deps.get_confirmed_fee_version_service(session).get_latest(project_id)
                        if matrix is not None else deps.ConfirmedFeeAuthorityRepository(session).get_latest_by_project(project_id)),
                "resources": relevant_resources, "templates": template_files,
                "test_record_template": (str(self.settings.test_record.template_path),
                    file_hash(self.settings.test_record.template_path) if self.settings.test_record.template_path else None),
            })

    @staticmethod
    def _template_context(path, fee_template):
        if not path.is_dir():
            return file_hash(path)
        values = []
        for item in sorted(path.rglob("*")):
            if item.is_symlink():
                raise ValueError("Template contains a symbolic link; review it before generation.")
            if item == fee_template and item.suffix.lower() == ".xls":
                # Preserve the existing controlled-form revision/path/size policy for Excel OLE metadata churn.
                value = deps._fee_form_template_context(item)
            else:
                value = file_hash(item) if item.is_file() else "directory"
            values.append((str(item.relative_to(path)), value))
        return fingerprint(values)

    def preview_context(self, project_id):
        return self.preview(project_id)["expected_context"]

    def preview(self, project_id):
        from backend.api.routes_official_project_workspace import _preview_response
        with self.sessions() as session:
            preview = deps.get_official_project_workspace_service(session).preview(project_id)
            basic_information = deps.get_project_basic_information_service(session).get(project_id)
            basic_information_blocker = basic_information_generation_blocker(
                status=basic_information.status,
                missing_required_labels=basic_information.missing_required_labels,
            )
            confirmed_matrix = deps.ConfirmedMatrixAuthorityRepository(session).get_active_by_project(project_id)
            schedule_blocker = None
            if basic_information_blocker is None and confirmed_matrix is not None:
                confirmed_schedule = deps.get_project_schedule_output_reader(session).get_latest_confirmed(project_id)
                if confirmed_schedule is None:
                    schedule_blocker = PROJECT_SCHEDULE_GENERATION_BLOCKER
            start_blockers = list(
                dict.fromkeys(
                    [
                        *(
                            preview.blockers
                            if preview.status == "blocked"
                            else tuple()
                        ),
                        *(
                            blocker
                            for blocker in (
                                basic_information_blocker,
                                schedule_blocker,
                            )
                            if blocker is not None
                        ),
                    ]
                )
            )
            paths = preview.conflict_paths or ((preview.official_folder_path,) if preview.official_folder_path else ())
            current_context = self.context(project_id)
            saved_operation = self.journal.read(project_id)
            recovery = None
            if saved_operation and saved_operation["status"] != "completed":
                recovery = {
                    "operation_id": saved_operation["operation_id"],
                    "inputs_match": saved_operation["context"] == current_context,
                    "rebuild_pending": saved_operation.get("strategy") in {"backup_and_recreate", "overwrite_rebuild"}
                        and "workspace" not in saved_operation["completed_steps"],
                }
            try:
                target_facts = [(str(path), tree_hash(path)) for path in paths]
            except OSError:
                # Keep file readiness visible, but never authorize a write with
                # an incomplete target fingerprint. Start rechecks this blocker.
                target_facts = None
                start_blockers.append("Cannot verify all existing folder files. Check file access or locks before generation.")
            token = fingerprint({"context": current_context, "preview": preview,
                                "targets": target_facts,
                                "manifest": file_hash(preview.manifest_path) if preview.manifest_path else None})
            workspace_preview = _preview_response(preview).model_dump()
            file_preflight = package_preflight(project_id, preview, session, self.settings, rebuilding=True)
            file_conflicts = [
                f"{item['label']}: {item['message']}"
                for item in file_preflight["items"] if item["status"] in {"conflict", "blocked"}
            ]
            if file_conflicts and not start_blockers:
                start_blockers.append("; ".join(file_conflicts))
            if start_blockers:
                workspace_preview["status"] = "blocked"
                workspace_preview["blockers"] = list(
                    dict.fromkeys(
                        [*workspace_preview["blockers"], *start_blockers]
                    )
                )
            return {
                "expected_context": token,
                "recovery": recovery,
                "start_blockers": start_blockers,
                "workspace_preview": {
                    **workspace_preview,
                    "generation_context": token,
                    "file_preflight": file_preflight,
                },
            }

    def run_step(self, state, name):
        project_id = state["project_id"]
        with self.sessions() as session:
            try:
                deps.get_project_lifecycle_write_guard(session).require_write_allowed(project_id, LifecycleWriteOperation.REQUIRED_FORMS_GENERATE)
                def verify_context():
                    if self.context(project_id) != state["context"]:
                        raise ValueError("Generation inputs changed before publication. No further target was written.")
                    if name != "workspace":
                        RecoverableWorkspacePublisher(self.journal, state).verify_directories(workspace_record)
                workspace_record = deps.ProjectOfficialWorkspaceRepository(session).get_by_project(project_id)
                if name != "workspace":
                    RecoverableWorkspacePublisher(self.journal, state).verify_directories(workspace_record)
                publication_root = (workspace_record.local_workspace_path / ".connlab" / "generation" / state["operation_id"]
                                    if workspace_record is not None and name != "workspace" else None)
                publisher = RecoverableOutputPublisher(self.journal, state, name, verify_context, publication_root)
                publisher.verify_completed_files()
                outputs = deps.get_project_output_record_service(session)
                publisher.recover_files(lambda payload: self._register_once(outputs, payload))
                if name == "workspace":
                    def verify_initial_preview():
                        if self.preview_context(project_id) != state["preview_context"]:
                            raise ValueError("Workspace preview or target changed. Refresh and review before generating.")
                    workspace = RecoverableWorkspacePublisher(self.journal, state, verify_context, verify_initial_preview)
                    if "workspace" in state["effects"]:
                        workspace.recover(deps.ProjectOfficialWorkspaceRepository(session))
                    else:
                        verify_initial_preview()
                        deps.get_official_project_workspace_service(session).create(project_id, state["strategy"], recovery=workspace)
                elif name == "materials":
                    latest = deps.ProjectRequestMaterialCollectionRepository(session).latest_by_project(project_id)
                    if latest is None or latest.collection_id != state["operation_id"]:
                        result = deps.get_project_request_material_collection_service(session).collect(
                            project_id, recovery=publisher, collection_id=state["operation_id"])
                        # A missing optional request email is a retained warning, not a failed copy.
                        # Check concrete placement outcomes rather than the warning-bearing "partial" label.
                        if (result.blockers or result.missing_source_paths or result.conflict_paths or result.skipped_paths
                                or any(item.action != "already_present" for item in result.items)):
                            raise ValueError(result.blockers[0] if result.blockers else
                                             "Request material collection has missing, conflicting, or unresolved source files. Review them before continuing.")
                elif name == "check":
                    result = deps.get_official_project_folder_check_service(session).preview(project_id)
                    # Required-form files are expected to be absent at this stage; its own preview owns readiness.
                elif name == "application_form":
                    deps.get_project_application_form_write_back_service(session, self.settings).write_back(project_id, recovery=publisher)
                else:
                    # Generated Office inputs are reproducible; they do not need the
                    # durable journal's deep project-hash path. Keep operation isolation
                    # while preserving all existing journal/recovery locations.
                    operation_settings = replace(
                        self.settings,
                        data_dir=self.settings.data_dir / "stage" / state["operation_id"],
                    )
                    service = deps.get_project_folder_required_forms_service(session, operation_settings)
                    preview = service.preview(project_id)
                    self._require_result(preview)
                    selected = next((item for item in preview.items if item.key == name), None)
                    if selected is None or selected.action == "conflict":
                        raise ValueError("Required form target needs review before generation.")
                    if selected.action != "skip":
                        command = GenerateRequiredFormsCommand(
                            project_id=project_id,
                            expected_official_project_folder_path=preview.official_project_folder_path,
                            expected_confirmed_matrix_id=preview.confirmed_matrix_id,
                            expected_confirmed_revision=preview.confirmed_revision,
                            expected_confirmed_fee_id=preview.confirmed_fee_id,
                            expected_confirmed_fee_revision=preview.confirmed_fee_revision,
                            expected_confirmed_fee_pricing_draft_edit_id=preview.confirmed_fee_pricing_draft_edit_id,
                            expected_confirmed_basic_information_version=preview.confirmed_basic_information_version,
                            expected_confirmed_basic_information_source_signature_hash=preview.confirmed_basic_information_source_signature_hash,
                            expected_customer_feedback_template_path=preview.customer_feedback_template_path,
                            expected_targets=(RequiredFormsGenerateTarget(name, selected.target_path),),
                        )
                        self._require_result(service.generate(command, recovery=publisher))
                # Any publication/registration gap is reconciled before committing this step.
                publisher.recover_files(lambda payload: self._register_once(outputs, payload))
                session.commit()
            except BaseException:
                session.rollback()
                raise

    @staticmethod
    def _register_once(outputs, payload):
        data = dict(payload)
        data["output_kind"] = ProjectOutputKind(data["output_kind"])
        data["source"] = ProjectOutputSource(data["source"])
        data["status"] = ProjectOutputStatus(data["status"])
        command = RegisterProjectOutputCommand(**data)
        for record in outputs.list_records(command.project_id):
            if all(getattr(record, key) == getattr(command, key) for key in (
                "output_kind", "output_path", "source", "status", "draft_id", "output_sha256", "output_size_bytes", "source_context_signature")):
                return record
        return outputs.register_output(command)

    @staticmethod
    def _require_result(result):
        if result.status in {"blocked", "conflict", "partial"}:
            blockers = getattr(result, "blockers", ())
            raise ValueError("; ".join(blockers) if blockers else "Project folder generation needs review before continuing.")
