"""Write structured application data into the copied Project Folder Word form."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Protocol

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_output_record_service import RegisterProjectOutputCommand
from backend.application.project_request_material_collection_helpers import (
    safe_material_filename,
)
from backend.domain import (
    ApplicationForm,
    FileAsset,
    FileAssetType,
    Project,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
)
from backend.infrastructure.office import OfficeFacade, WordSection2FieldChange


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


class ProjectApplicationFormWriteBackService:
    """Write application/project metadata into the copied request Word form."""

    def __init__(
        self,
        *,
        project_store: ProjectStore,
        workspace_store: WorkspaceStore,
        application_form_store: ApplicationFormStore,
        file_asset_store: FileAssetStore,
        output_record_service: OutputRecordService,
        office: ApplicationFormWordWriter | None = None,
    ) -> None:
        self._projects = project_store
        self._workspaces = workspace_store
        self._forms = application_form_store
        self._assets = file_asset_store
        self._outputs = output_record_service
        self._office = office or OfficeFacade()

    def write_back(self, project_id: str) -> ProjectApplicationFormWriteBackResult:
        """Write known project/application fields into the copied Word form."""
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
        target = _target_application_form(
            workspace.official_folder_path / "Submitted Material",
            self._assets.list_by_project(project_id),
        )
        fields = _fields(project, form)
        write_result = self._office.write_word_application_form_fields(target, fields)
        summary = self._outputs.get_status_summary(project_id)
        active_draft_id = getattr(summary, "active_draft_id", None)
        record = self._outputs.register_output(
            RegisterProjectOutputCommand(
                project_id=project_id,
                output_kind=ProjectOutputKind.SECTION2_WRITE_BACK,
                status=(
                    ProjectOutputStatus.CURRENT
                    if active_draft_id
                    else ProjectOutputStatus.MANUAL
                ),
                source=(
                    ProjectOutputSource.SYSTEM_GENERATED
                    if active_draft_id
                    else ProjectOutputSource.MANUAL
                ),
                output_path=str(target),
                draft_id=active_draft_id,
                output_sha256=_sha256(target),
                output_size_bytes=target.stat().st_size,
                source_context_signature=f"application-form:{form.form_id}",
            )
        )
        status = "updated" if write_result.changed_fields else "current"
        return ProjectApplicationFormWriteBackResult(
            project_id=project_id,
            target_path=target,
            status=status,
            changed_fields=write_result.changed_fields,
            unchanged_fields=write_result.unchanged_fields,
            warnings=write_result.warnings,
            output_record_id=str(getattr(record, "output_record_id", "")) or None,
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


def _target_application_form(submitted_material: Path, assets: list[FileAsset]) -> Path:
    selected = [
        asset
        for asset in assets
        if asset.asset_type is FileAssetType.APPLICATION_FORM
        or (asset.source_role or "").casefold() == "selected_application_form"
    ]
    if selected:
        name = safe_material_filename(
            selected[0].original_name or selected[0].path.name,
            selected[0].asset_id,
        )
        target = submitted_material / name
        if target.is_file():
            return target
    candidates = sorted(submitted_material.glob("*.docx"))
    candidates = [path for path in candidates if ".bak-" not in path.name]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ProjectApplicationFormWriteBackNotFoundError(
            f"No Application Form .docx found in Submitted Material: {submitted_material}"
        )
    raise ProjectApplicationFormWriteBackError(
        "Multiple .docx files exist in Submitted Material. Cannot choose the Application Form automatically."
    )


def _fields(project: Project, form: ApplicationForm) -> dict[str, str]:
    values = {
        "ltr_number": form.lab_test_request_number or project.project_no,
        "project_number": form.project_number or project.project_no,
        "product_description": project.product_name,
        "test_item": form.requested_testing,
        "requester": form.requester or project.requestor,
        "phone": form.phone,
        "email": form.email,
        "business_unit": form.business_unit or project.business_unit,
        "manufacturing_site": form.manufacturing_site,
        "requested_completion_date": form.requested_completion_date,
        "lab": form.lab,
        "assigned_personnel": form.assigned_personnel,
        "received_date": form.received_date,
        "estimated_completion_date": form.estimated_completion_date,
        "sample_condition": form.sample_condition,
    }
    return {key: value.strip() for key, value in values.items() if value and value.strip()}


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
