"""Application service for Official project folder checks and folder repair."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_output_record_service import ProjectOutputStatusSummary
from backend.application.project_request_material_collection_types import RequestMaterialPreview
from backend.domain import Project, ProjectOutputKind, ProjectOutputStatus


REQUIRED_OFFICIAL_FOLDER_PATHS: tuple[tuple[str, str, Path], ...] = (
    ("official_root", "Official project folder", Path(".")),
    ("email", "E-mail", Path("E-mail")),
    ("submitted_material", "Submitted Material", Path("Submitted Material")),
    ("photos", "Photos", Path("Photos")),
    ("test_results", "Test results", Path("Test results")),
    ("final_examination", "Final Examination", Path("Test results") / "Final Examination"),
)


class OfficialProjectFolderCheckError(ValueError):
    """Base error for Official project folder check workflows."""


class OfficialProjectFolderCheckNotFoundError(LookupError):
    """Raised when the project cannot be found."""


class OfficialProjectFolderCheckConflictError(OfficialProjectFolderCheckError):
    """Raised when folder repair cannot continue because of conflicts."""


class OfficialFolderRepairFailureError(OfficialProjectFolderCheckError):
    """Raised by folder repair gateways after partial folder creation failure."""

    def __init__(
        self,
        message: str,
        *,
        created_paths: tuple[Path, ...] = tuple(),
        failed_path: Path | None = None,
    ) -> None:
        """Create a partial repair failure."""
        super().__init__(message)
        self.created_paths = created_paths
        self.failed_path = failed_path


class ProjectRepositoryPort(Protocol):
    """Project lookup operations required by this service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class OfficialWorkspaceRepositoryPort(Protocol):
    """Official workspace record lookup operations required by this service."""

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the completed local workspace record for a project."""


class OfficialFolderRepairGatewayPort(Protocol):
    """Missing-folder creation operations."""

    def create_missing_folders(self, paths: Sequence[Path]) -> tuple[Path, ...]:
        """Create the supplied missing folders and return created paths."""


class RequestMaterialPreviewerPort(Protocol):
    """Read-only request-material preview dependency."""

    def preview(self, project_id: str) -> RequestMaterialPreview:
        """Return request-material preview state for a project."""


class OutputStatusSummaryPort(Protocol):
    """Read-only project output status dependency."""

    def get_status_summary(self, project_id: str) -> ProjectOutputStatusSummary:
        """Return current project output status summary."""


@dataclass(frozen=True, slots=True)
class OfficialFolderCheckItem:
    """One Official project folder check item."""

    key: str
    label: str
    kind: str
    status: str
    path: Path | None
    message: str
    repairable: bool = False


@dataclass(frozen=True, slots=True)
class OfficialFolderCheckPreview:
    """Read-only preview of the Official project folder condition."""

    project_id: str
    status: str
    local_workspace_path: Path | None
    official_project_folder_path: Path | None
    required_folders: tuple[OfficialFolderCheckItem, ...]
    required_files: tuple[OfficialFolderCheckItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_action: str


@dataclass(frozen=True, slots=True)
class OfficialFolderRepairResult:
    """Result of a missing-folder-only repair operation."""

    project_id: str
    repair_status: str
    created_paths: tuple[Path, ...]
    unresolved_conflicts: tuple[Path, ...]
    errors: tuple[str, ...]
    preview: OfficialFolderCheckPreview


class OfficialProjectFolderCheckService:
    """Inspect and repair the local Official project folder structure."""

    def __init__(
        self,
        *,
        project_repository: ProjectRepositoryPort,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        repair_gateway: OfficialFolderRepairGatewayPort | None = None,
        request_material_service: RequestMaterialPreviewerPort | None = None,
        output_status_service: OutputStatusSummaryPort | None = None,
    ) -> None:
        """Create the check service."""
        self._projects = project_repository
        self._workspaces = workspace_repository
        self._repair_gateway = repair_gateway or _DefaultFolderRepairGateway()
        self._request_material_service = request_material_service
        self._output_status_service = output_status_service

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        """Return the current Official project folder check preview."""
        self._require_project(project_id)
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None or not workspace.official_folder_path.exists():
            return OfficialFolderCheckPreview(
                project_id=project_id,
                status="blocked",
                local_workspace_path=workspace.local_workspace_path if workspace else None,
                official_project_folder_path=(
                    workspace.official_folder_path if workspace else None
                ),
                required_folders=tuple(),
                required_files=self._required_files(project_id),
                blockers=("Create local project folder before checking the Project Folder.",),
                warnings=tuple(),
                next_action="none",
            )

        folder_items = self._required_folder_items(workspace.official_folder_path)
        file_items = self._required_files(project_id)
        blockers: list[str] = []
        warnings: list[str] = []
        if any(item.status == "conflict" for item in folder_items):
            status = "conflict"
            blockers.append("Required folder path conflict.")
            next_action = "none"
        elif any(item.status == "missing" for item in folder_items):
            status = "missing"
            next_action = "repair_folders"
        elif any(item.status == "conflict" for item in file_items):
            status = "conflict"
            blockers.append("Required file path conflict.")
            next_action = "none"
        elif any(item.status == "missing" for item in file_items):
            status = "missing"
            next_action = "none"
        elif any(item.status == "warning" for item in file_items):
            status = "warning"
            warnings.extend(item.message for item in file_items if item.status == "warning")
            next_action = "none"
        else:
            status = "ready"
            next_action = "none"
        return OfficialFolderCheckPreview(
            project_id=project_id,
            status=status,
            local_workspace_path=workspace.local_workspace_path,
            official_project_folder_path=workspace.official_folder_path,
            required_folders=folder_items,
            required_files=file_items,
            blockers=tuple(blockers),
            warnings=tuple(dict.fromkeys(warnings)),
            next_action=next_action,
        )

    def repair_folders(self, project_id: str) -> OfficialFolderRepairResult:
        """Create missing required folders only."""
        preview = self.preview(project_id)
        if preview.status == "blocked":
            detail = preview.blockers[0] if preview.blockers else "Project Folder check is blocked."
            raise OfficialProjectFolderCheckConflictError(detail)
        if preview.status == "conflict":
            detail = preview.blockers[0] if preview.blockers else "Project Folder has conflicts."
            raise OfficialProjectFolderCheckConflictError(detail)
        missing = tuple(
            item.path
            for item in preview.required_folders
            if item.status == "missing" and item.repairable and item.path is not None
        )
        if not missing:
            return OfficialFolderRepairResult(
                project_id=project_id,
                repair_status="completed",
                created_paths=tuple(),
                unresolved_conflicts=tuple(),
                errors=tuple(),
                preview=preview,
            )
        try:
            created = self._repair_gateway.create_missing_folders(missing)
        except OfficialFolderRepairFailureError as exc:
            after = self.preview(project_id)
            conflicts = tuple(
                item.path
                for item in after.required_folders
                if item.status == "conflict" and item.path is not None
            )
            return OfficialFolderRepairResult(
                project_id=project_id,
                repair_status="partial",
                created_paths=exc.created_paths,
                unresolved_conflicts=conflicts,
                errors=(str(exc),),
                preview=after,
            )
        except OSError as exc:
            after = self.preview(project_id)
            return OfficialFolderRepairResult(
                project_id=project_id,
                repair_status="partial",
                created_paths=tuple(
                    item.path
                    for item in preview.required_folders
                    if item.status == "missing"
                    and item.path is not None
                    and item.path.is_dir()
                ),
                unresolved_conflicts=tuple(),
                errors=(str(exc),),
                preview=after,
            )
        after = self.preview(project_id)
        return OfficialFolderRepairResult(
            project_id=project_id,
            repair_status="completed",
            created_paths=tuple(created),
            unresolved_conflicts=tuple(),
            errors=tuple(),
            preview=after,
        )

    def _require_project(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise OfficialProjectFolderCheckNotFoundError(f"Project not found: {project_id}")
        return project

    def _required_folder_items(
        self,
        official_folder_path: Path,
    ) -> tuple[OfficialFolderCheckItem, ...]:
        items: list[OfficialFolderCheckItem] = []
        for key, label, relative in REQUIRED_OFFICIAL_FOLDER_PATHS:
            path = official_folder_path if relative == Path(".") else official_folder_path / relative
            if path.is_dir():
                status = "ready"
                message = "Ready."
                repairable = False
            elif path.exists():
                status = "conflict"
                message = "Expected a folder, but a file exists at this path."
                repairable = False
            else:
                status = "missing"
                message = "Folder is missing."
                repairable = key != "official_root"
            items.append(
                OfficialFolderCheckItem(
                    key=key,
                    label=label,
                    kind="folder",
                    status=status,
                    path=path,
                    message=message,
                    repairable=repairable,
                )
            )
        return tuple(items)

    def _required_files(self, project_id: str) -> tuple[OfficialFolderCheckItem, ...]:
        items = [
            self._request_material_item(project_id),
            self._submitted_material_item(project_id),
            *self._output_items(project_id),
            OfficialFolderCheckItem(
                key="customer_feedback",
                label="Customer Feedback form",
                kind="file",
                status="deferred",
                path=None,
                message="Customer Feedback generation is handled by a later task.",
            ),
        ]
        return tuple(items)

    def _request_material_item(self, project_id: str) -> OfficialFolderCheckItem:
        preview = self._request_material_preview(project_id)
        if preview is None:
            return OfficialFolderCheckItem(
                key="request_material",
                label="Request material",
                kind="file",
                status="missing",
                path=None,
                message="Request material has not been collected.",
            )
        if preview.status == "collected":
            return OfficialFolderCheckItem(
                key="request_material",
                label="Request material",
                kind="file",
                status="ready",
                path=preview.official_project_folder_path,
                message="Collected.",
            )
        if preview.status == "review_required":
            return OfficialFolderCheckItem(
                key="request_material",
                label="Request material",
                kind="file",
                status="warning",
                path=preview.official_project_folder_path,
                message="Needs review before Submitted Material placement.",
            )
        if preview.status == "partial":
            return OfficialFolderCheckItem(
                key="request_material",
                label="Request material",
                kind="file",
                status="warning",
                path=preview.official_project_folder_path,
                message="Request material collection is partial.",
            )
        if preview.status in {"blocked", "conflict"}:
            return OfficialFolderCheckItem(
                key="request_material",
                label="Request material",
                kind="file",
                status="conflict",
                path=preview.official_project_folder_path,
                message=preview.blockers[0] if preview.blockers else "Request material is blocked.",
            )
        return OfficialFolderCheckItem(
            key="request_material",
            label="Request material",
            kind="file",
            status="missing",
            path=preview.official_project_folder_path,
            message="Request material is not collected.",
        )

    def _submitted_material_item(self, project_id: str) -> OfficialFolderCheckItem:
        preview = self._request_material_preview(project_id)
        if preview is None:
            return OfficialFolderCheckItem(
                key="submitted_material",
                label="Submitted Material",
                kind="file",
                status="deferred",
                path=None,
                message="Submitted Material readiness follows request material collection.",
            )
        confirmed_items = [
            item
            for item in preview.items
            if item.target_area == "submitted_material"
            and not item.review_required
            and item.status in {"already_present", "collected"}
        ]
        if confirmed_items:
            return OfficialFolderCheckItem(
                key="submitted_material",
                label="Submitted Material",
                kind="file",
                status="ready",
                path=confirmed_items[0].target_path,
                message="Confirmed collected files are present.",
            )
        if preview.status == "review_required":
            return OfficialFolderCheckItem(
                key="submitted_material",
                label="Submitted Material",
                kind="file",
                status="deferred",
                path=preview.official_project_folder_path,
                message="Only review-only candidates remain.",
            )
        if preview.status in {"blocked", "conflict"}:
            return OfficialFolderCheckItem(
                key="submitted_material",
                label="Submitted Material",
                kind="file",
                status="conflict",
                path=preview.official_project_folder_path,
                message="Submitted Material cannot be checked until request material is resolved.",
            )
        return OfficialFolderCheckItem(
            key="submitted_material",
            label="Submitted Material",
            kind="file",
            status="missing",
            path=preview.official_project_folder_path,
            message="Confirmed Submitted Material files are missing.",
        )

    def _output_items(self, project_id: str) -> tuple[OfficialFolderCheckItem, ...]:
        summary = (
            self._output_status_service.get_status_summary(project_id)
            if self._output_status_service
            else None
        )
        by_kind = {item.output_kind: item for item in summary.items} if summary else {}
        return (
            _output_item("test_record", "Test Record", by_kind.get(ProjectOutputKind.TEST_RECORD_FORM)),
            _output_item("fee_form", "Fee Form", by_kind.get(ProjectOutputKind.FEE_EVALUATION)),
            _output_item(
                "section2",
                "Application Form Section 2",
                by_kind.get(ProjectOutputKind.SECTION2_WRITE_BACK),
            ),
        )

    def _request_material_preview(self, project_id: str) -> RequestMaterialPreview | None:
        if self._request_material_service is None:
            return None
        return self._request_material_service.preview(project_id)


class _DefaultFolderRepairGateway:
    """Default missing-folder repair gateway used by tests and API wiring."""

    def create_missing_folders(self, paths: Sequence[Path]) -> tuple[Path, ...]:
        """Create each missing folder and return the paths created."""
        created: list[Path] = []
        for path in paths:
            if path.exists() and not path.is_dir():
                raise OfficialFolderRepairFailureError(
                    f"Expected a folder, but a file exists at this path: {path}",
                    created_paths=tuple(created),
                    failed_path=path,
                )
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)
        return tuple(created)


def _output_item(key: str, label: str, item: object | None) -> OfficialFolderCheckItem:
    """Map one ProjectOutputRecord status item into a folder check item."""
    if item is None:
        return OfficialFolderCheckItem(
            key=key,
            label=label,
            kind="file",
            status="deferred",
            path=None,
            message=f"{label} has not been generated in the current approved workflow.",
        )
    status = getattr(item, "status")
    output_path = getattr(item, "output_path")
    path = Path(output_path) if output_path else None
    if status in {ProjectOutputStatus.CURRENT, ProjectOutputStatus.MANUAL}:
        return OfficialFolderCheckItem(
            key=key,
            label=label,
            kind="file",
            status="ready",
            path=path,
            message=getattr(item, "reason", "Ready."),
        )
    if status is ProjectOutputStatus.STALE:
        return OfficialFolderCheckItem(
            key=key,
            label=label,
            kind="file",
            status="warning",
            path=path,
            message=getattr(item, "reason", "Output may be stale."),
        )
    if status is ProjectOutputStatus.FAILED:
        return OfficialFolderCheckItem(
            key=key,
            label=label,
            kind="file",
            status="warning",
            path=path,
            message=getattr(item, "reason", "Last output attempt failed."),
        )
    return OfficialFolderCheckItem(
        key=key,
        label=label,
        kind="file",
        status="deferred",
        path=path,
        message=f"{label} has not been generated in the current approved workflow.",
    )
