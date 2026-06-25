"""Write structured application data into the copied Project Folder Word form."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Protocol

from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_basic_information_output_identity import (
    application_form_identity,
)
from backend.application.project_application_form_target_selection import (
    ApplicationFormTargetSelectionError,
    RequestMaterialCollectionStore,
    target_application_form,
)
from backend.application.project_application_form_write_back_support import (
    ApplicationFormWriteBackTiming,
    NullReusableApplicationFormArtifactStore,
    ReusableApplicationFormArtifactStore,
    append_timing,
    is_current_target_reusable,
    office_timings,
    sha256_file,
    source_context_signature,
)
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_output_record_service import RegisterProjectOutputCommand
from backend.domain import (
    ApplicationForm,
    FileAsset,
    Project,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
)
from backend.infrastructure.office import OfficeFacade, WordSection2FieldChange
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable

_APPLICATION_FORM_WRITE_BACK_FIELDS = {
    "ltr_number",
    "lab",
    "project_leader",
    "received_date",
    "estimated_completion_date",
    "sample_condition",
}

_APPLICATION_FORM_REQUIRED_LABELS = {
    "ltr_number": "Lab Test Request Number",
    "lab": "Lab Performing the Tests",
    "project_leader": "Lab Personnel Assigned",
    "received_date": "Date Lab Received Samples",
    "estimated_completion_date": "Estimated Completion Date",
    "sample_condition": "Condition of Samples when Received",
}


class ProjectApplicationFormWriteBackError(ValueError):
    """Raised when Project Folder application write-back cannot proceed."""


class ProjectApplicationFormWriteBackNotFoundError(ProjectApplicationFormWriteBackError):
    """Raised when required project, workspace, form, or file data is missing."""


class ProjectStore(Protocol):
    """Project lookup port."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class WorkspaceStore(Protocol):
    """Official workspace lookup port."""

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the completed Official workspace for a project."""


class ApplicationFormStore(Protocol):
    """Application Form lookup port."""

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return Application Forms for a project."""


class FileAssetStore(Protocol):
    """Project file asset lookup port."""

    def list_by_project(self, project_id: str) -> list[FileAsset]:
        """Return FileAsset rows for a project."""


class ApplicationFormWordWriter(Protocol):
    """Office write boundary for Application Form fields."""

    def write_word_application_form_fields(
        self,
        source_path: Path,
        fields: dict[str, str],
    ) -> object:
        """Write known application fields into a Word document."""

    def write_word_application_form_fields_with_owned_session(
        self,
        source_path: Path,
        fields: dict[str, str],
    ) -> object:
        """Write known application fields inside an Office-owned Word session."""


class OutputRecordService(Protocol):
    """Project output registration dependency."""

    def get_status_summary(self, project_id: str) -> object:
        """Return current output status summary."""

    def register_output(self, command: RegisterProjectOutputCommand) -> object:
        """Register one generated/updated output record."""


@dataclass(frozen=True, slots=True)
class ProjectApplicationFormWriteBackResult:
    """Application Form write-back result."""

    project_id: str
    target_path: Path
    status: str
    changed_fields: tuple[WordSection2FieldChange, ...]
    unchanged_fields: tuple[WordSection2FieldChange, ...]
    warnings: tuple[str, ...]
    output_record_id: str | None
    timings: tuple[ApplicationFormWriteBackTiming, ...] = tuple()
    office_timings: tuple[ApplicationFormWriteBackTiming, ...] = tuple()


class ProjectApplicationFormWriteBackService:
    """Write application/project metadata into the copied request Word form."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        workspace_store: WorkspaceStore,
        application_form_store: ApplicationFormStore,
        file_asset_store: FileAssetStore,
        request_material_collection_store: RequestMaterialCollectionStore | None = None,
        basic_information_reader: ConfirmedBasicInformationReader,
        output_record_service: OutputRecordService,
        office: ApplicationFormWordWriter | None = None,
        reusable_artifact_store: ReusableApplicationFormArtifactStore | None = None,
    ) -> None:
        self._projects = project_store
        self._workspaces = workspace_store
        self._forms = application_form_store
        self._assets = file_asset_store
        self._request_material_collections = request_material_collection_store
        self._basic_information = basic_information_reader
        self._outputs = output_record_service
        self._office = office or OfficeFacade()
        self._reusable_artifacts = (
            reusable_artifact_store or NullReusableApplicationFormArtifactStore()
        )

    def write_back(self, project_id: str) -> ProjectApplicationFormWriteBackResult:
        """Write known project/application fields into the copied Word form."""
        total_start = perf_counter()
        timings: list[ApplicationFormWriteBackTiming] = []
        resolve_inputs_start = perf_counter()
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectApplicationFormWriteBackNotFoundError(
                f"Project not found: {project_id}"
            )
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None or not workspace.official_folder_path.is_dir():
            raise ProjectApplicationFormWriteBackNotFoundError(
                "Create the Official project folder before writing the Application Form."
            )
        form = _single_form(self._forms.list_by_project(project_id))
        append_timing(timings, "application_form.resolve_inputs", resolve_inputs_start)
        resolve_target_start = perf_counter()
        try:
            selected_target = target_application_form(
                workspace.official_folder_path / "Submitted Material",
                project_id,
                self._assets.list_by_project(project_id),
                self._request_material_collections,
            )
        except ApplicationFormTargetSelectionError as exc:
            raise ProjectApplicationFormWriteBackError(str(exc)) from exc
        target = selected_target.path
        append_timing(timings, "application_form.resolve_target", resolve_target_start)
        basic_start = perf_counter()
        basic_information = self._basic_information.get_latest_confirmed(project_id)
        if basic_information is None:
            raise ProjectApplicationFormWriteBackError(
                "Confirm Basic Information before writing the Application Form."
            )
        context_signature = source_context_signature(
            form,
            basic_information,
            source_sha256=selected_target.source_sha256,
        )
        fields = _fields(project, form, basic_information)
        append_timing(timings, "application_form.basic_information", basic_start)
        safety_start = perf_counter()
        summary = self._outputs.get_status_summary(project_id)
        _ensure_safe_managed_target(
            summary,
            target,
            source_sha256=selected_target.source_sha256,
        )
        current_item = _latest_section_write_back_item(summary, target)
        append_timing(timings, "application_form.safety_check", safety_start)
        reuse_start = perf_counter()
        if is_current_target_reusable(current_item, target, context_signature):
            append_timing(timings, "application_form.reuse_lookup", reuse_start)
            append_timing(timings, "application_form.total", total_start)
            return ProjectApplicationFormWriteBackResult(
                project_id=project_id,
                target_path=target,
                status="current",
                changed_fields=tuple(),
                unchanged_fields=tuple(),
                warnings=tuple(),
                output_record_id=None,
                timings=tuple(timings),
                office_timings=tuple(),
            )
        reusable = None
        if selected_target.source_sha256:
            reusable = self._reusable_artifacts.find_current_artifact(
                project_id=project_id,
                source_context_signature=context_signature,
                final_target_path=target,
            )
        append_timing(timings, "application_form.reuse_lookup", reuse_start)
        if reusable is not None:
            copy_start = perf_counter()
            shutil.copy2(reusable, target)
            append_timing(timings, "application_form.reuse_copy", copy_start)
            register_start = perf_counter()
            record = self._register_output(
                project_id=project_id,
                target=target,
                summary=summary,
                context_signature=context_signature,
            )
            append_timing(timings, "application_form.register_output", register_start)
            append_timing(timings, "application_form.total", total_start)
            return ProjectApplicationFormWriteBackResult(
                project_id=project_id,
                target_path=target,
                status="reused",
                changed_fields=tuple(),
                unchanged_fields=tuple(),
                warnings=tuple(),
                output_record_id=str(getattr(record, "output_record_id", "")) or None,
                timings=tuple(timings),
                office_timings=tuple(),
            )
        office_start = perf_counter()
        try:
            write_result = (
                self._office.write_word_application_form_fields_with_owned_session(
                    target,
                    fields,
                )
            )
        except OfficeAutomationUnavailable as exc:
            raise ProjectApplicationFormWriteBackError(str(exc)) from exc
        except ValueError as exc:
            raise ProjectApplicationFormWriteBackError(str(exc)) from exc
        append_timing(timings, "application_form.office_write", office_start)
        target_sha = sha256_file(target)
        try:
            self._reusable_artifacts.save_current_artifact(
                project_id=project_id,
                source_context_signature=context_signature,
                source_path=target,
                source_sha256=target_sha,
            )
        except OSError:
            pass
        register_start = perf_counter()
        record = self._register_output(
            project_id=project_id,
            target=target,
            summary=summary,
            context_signature=context_signature,
            target_sha256=target_sha,
        )
        append_timing(timings, "application_form.register_output", register_start)
        status = "updated" if write_result.changed_fields else "current"
        append_timing(timings, "application_form.total", total_start)
        return ProjectApplicationFormWriteBackResult(
            project_id=project_id,
            target_path=target,
            status=status,
            changed_fields=write_result.changed_fields,
            unchanged_fields=write_result.unchanged_fields,
            warnings=write_result.warnings,
            output_record_id=str(getattr(record, "output_record_id", "")) or None,
            timings=tuple(timings),
            office_timings=office_timings(write_result),
        )

    def _register_output(
        self,
        *,
        project_id: str,
        target: Path,
        summary: object,
        context_signature: str,
        target_sha256: str | None = None,
    ) -> object:
        active_draft_id = getattr(summary, "active_draft_id", None)
        sha = target_sha256 or sha256_file(target)
        return self._outputs.register_output(
            RegisterProjectOutputCommand(
                project_id=project_id,
                output_kind=ProjectOutputKind.SECTION2_WRITE_BACK,
                status=ProjectOutputStatus.CURRENT,
                source=ProjectOutputSource.SYSTEM_GENERATED,
                output_path=str(target),
                draft_id=active_draft_id,
                output_sha256=sha,
                output_size_bytes=target.stat().st_size,
                source_context_signature=context_signature,
            )
        )


def _single_form(forms: list[ApplicationForm]) -> ApplicationForm:
    if not forms:
        raise ProjectApplicationFormWriteBackNotFoundError(
            "Application Form is required before Word write-back."
        )
    if len(forms) > 1:
        raise ProjectApplicationFormWriteBackError(
            "Multiple Application Forms exist. Select the current Application Form before Word write-back."
        )
    return forms[0]


def _fields(
    project: Project,
    form: ApplicationForm,
    basic_information: ConfirmedBasicInformationSnapshot,
) -> dict[str, str]:
    values = application_form_identity(basic_information).fields
    if not str(values.get("project_leader", "") or "").strip():
        values["project_leader"] = form.assigned_personnel
    fields = {
        key: str(values.get(key, "") or "").strip()
        for key in _APPLICATION_FORM_WRITE_BACK_FIELDS
    }
    missing = [
        _APPLICATION_FORM_REQUIRED_LABELS[key]
        for key, value in fields.items()
        if not value
    ]
    if missing:
        raise ProjectApplicationFormWriteBackError(
            "Application Form write-back requires confirmed Basic Information: "
            + ", ".join(missing)
        )
    return fields


def _ensure_safe_managed_target(
    summary: object,
    target: Path,
    *,
    source_sha256: str | None = None,
) -> None:
    """Block write-back when a prior managed target was edited on disk."""
    item = _latest_section_write_back_item(summary, target)
    if item is None:
        return
    stored_sha = getattr(item, "output_sha256", None)
    if not stored_sha:
        raise ProjectApplicationFormWriteBackError(
            "Existing Application Form write-back record is missing a fingerprint."
        )
    current_sha = sha256_file(target)
    if current_sha != stored_sha and source_sha256 and current_sha == source_sha256:
        return
    if current_sha != stored_sha:
        raise ProjectApplicationFormWriteBackError(
            "Application Form target was changed outside ConnLab."
        )


def _latest_section_write_back_item(summary: object, target: Path) -> object | None:
    """Return the latest matching SECTION2 write-back status item."""
    items = getattr(summary, "items", tuple())
    for item in reversed(tuple(items)):
        if getattr(item, "output_kind", None) is not ProjectOutputKind.SECTION2_WRITE_BACK:
            continue
        if getattr(item, "output_path", None) == str(target):
            return item
    return None
