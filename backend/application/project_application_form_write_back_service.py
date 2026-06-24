"""Write structured application data into the copied Project Folder Word form."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Protocol

from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
    ConfirmedBasicInformationSnapshot,
)
from backend.application.project_basic_information_output_identity import (
    application_form_identity,
)
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


class RequestMaterialCollectionStore(Protocol):
    """Request-material collection lookup port."""

    def latest_by_project(self, project_id: str) -> object | None:
        """Return the latest request-material collection run."""

    def list_items(self, collection_id: str) -> tuple[object, ...]:
        """Return persisted request-material items for one collection run."""


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


@dataclass(frozen=True, slots=True)
class _SelectedApplicationFormTarget:
    """Selected copied Application Form target and source fingerprint."""

    path: Path
    source_sha256: str | None = None


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
    ) -> None:
        self._projects = project_store
        self._workspaces = workspace_store
        self._forms = application_form_store
        self._assets = file_asset_store
        self._request_material_collections = request_material_collection_store
        self._basic_information = basic_information_reader
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
        selected_target = _target_application_form(
            workspace.official_folder_path / "Submitted Material",
            project_id,
            self._assets.list_by_project(project_id),
            self._request_material_collections,
        )
        target = selected_target.path
        basic_information = self._basic_information.get_latest_confirmed(project_id)
        if basic_information is None:
            raise ProjectApplicationFormWriteBackError(
                "Confirm Basic Information before writing the Application Form."
            )
        summary = self._outputs.get_status_summary(project_id)
        _ensure_safe_managed_target(
            summary,
            target,
            source_sha256=selected_target.source_sha256,
        )
        fields = _fields(project, form, basic_information)
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
                source_context_signature=(
                    f"application-form:{form.form_id}|{basic_information.context_signature}"
                ),
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


def _target_application_form(
    submitted_material: Path,
    project_id: str,
    assets: list[FileAsset],
    collection_store: RequestMaterialCollectionStore | None,
) -> _SelectedApplicationFormTarget:
    from_collection = _target_from_latest_collection(
        submitted_material,
        project_id,
        collection_store,
    )
    if from_collection is not None:
        return from_collection
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
            return _SelectedApplicationFormTarget(
                path=target,
                source_sha256=_source_asset_sha256(selected[0], target),
            )
    candidates = sorted(submitted_material.glob("*.docx"))
    candidates = [path for path in candidates if ".bak-" not in path.name]
    if len(candidates) == 1:
        return _SelectedApplicationFormTarget(path=candidates[0])
    if not candidates:
        raise ProjectApplicationFormWriteBackNotFoundError(
            f"No Application Form .docx found in Submitted Material: {submitted_material}"
        )
    raise ProjectApplicationFormWriteBackError(
        "Multiple .docx files exist in Submitted Material. Cannot choose the Application Form automatically."
    )


def _target_from_latest_collection(
    submitted_material: Path,
    project_id: str,
    collection_store: RequestMaterialCollectionStore | None,
) -> _SelectedApplicationFormTarget | None:
    """Return the selected Application Form copied by Request Material collection."""
    if collection_store is None:
        return None
    collection = collection_store.latest_by_project(project_id)
    collection_id = getattr(collection, "collection_id", None)
    if not collection_id:
        return None
    for item in collection_store.list_items(collection_id):
        if getattr(item, "target_area", None) != "submitted_material":
            continue
        source_type = str(getattr(item, "source_asset_type", "") or "").casefold()
        source_role = str(getattr(item, "source_role", "") or "").casefold()
        if source_type != FileAssetType.APPLICATION_FORM.value and (
            source_role != "selected_application_form"
        ):
            continue
        target_path = Path(getattr(item, "target_path"))
        if not _is_direct_child(target_path, submitted_material) or not target_path.is_file():
            continue
        return _SelectedApplicationFormTarget(
            path=target_path,
            source_sha256=_collection_source_sha256(item, target_path),
        )
    return None


def _is_direct_child(path: Path, folder: Path) -> bool:
    try:
        return path.parent.resolve() == folder.resolve()
    except OSError:
        return path.parent == folder


def _collection_source_sha256(item: object, target: Path) -> str | None:
    sha = getattr(item, "sha256", None)
    if sha:
        return str(sha)
    source_path = Path(getattr(item, "source_path", ""))
    try:
        if source_path.resolve() == target.resolve():
            return None
    except OSError:
        if source_path == target:
            return None
    return _sha256(source_path) if source_path.is_file() else None


def _source_asset_sha256(asset: FileAsset, target: Path) -> str | None:
    if asset.sha256:
        return asset.sha256
    try:
        if asset.path.resolve() == target.resolve():
            return None
    except OSError:
        if asset.path == target:
            return None
    return _sha256(asset.path) if asset.path.is_file() else None


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
    current_sha = _sha256(target)
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


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
