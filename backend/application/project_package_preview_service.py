"""Read-only project package readiness preview service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from backend.application.confirmed_fee_version_service import (
    ConfirmedFeeVersionReadResult,
)
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillError,
    ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
)
from backend.application.customer_feedback_template_discovery import (
    CustomerFeedbackTemplateDiscoveryError,
    discover_customer_feedback_template,
)
from backend.application.project_section2_sync_service import (
    ProjectSection2SyncCommand,
    ProjectSection2SyncError,
    ProjectSection2SyncResult,
)
from backend.domain import (
    ConfirmedMatrixSnapshot,
    ExternalResource,
    ExternalResourceType,
    Project,
    ProjectFolderRecord,
)


PackagePreviewStatus = Literal["ready", "blocked"]
PackagePreviewItemStatus = Literal["ready", "blocked", "warning", "deferred"]


class ProjectPackagePreviewProjectNotFoundError(LookupError):
    """Raised when the target project does not exist."""


class ProjectPackageProjectStore(Protocol):
    """Project lookup port."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class ProjectPackageFolderStore(Protocol):
    """Project folder read port."""

    def list_by_project(self, project_id: str) -> list[ProjectFolderRecord]:
        """Return folder records for a project."""


class ProjectPackageConfirmedMatrixStore(Protocol):
    """Confirmed Matrix authority read port."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return the active Confirmed Matrix authority snapshot."""


class ProjectPackageConfirmedFeeReader(Protocol):
    """Confirmed Fee status read port."""

    def get_latest(self, project_id: str) -> ConfirmedFeeVersionReadResult:
        """Return latest Confirmed Fee status."""


class ProjectPackageSection2Previewer(Protocol):
    """Application Form Section 2 sync preview port."""

    def preview(self, command: object) -> ProjectSection2SyncResult:
        """Preview Section 2 sync state."""


class ProjectPackageExternalResourceStore(Protocol):
    """External resource lookup port."""

    def get_by_type(self, resource_type: ExternalResourceType) -> ExternalResource | None:
        """Return an external resource by type."""


@dataclass(frozen=True, slots=True)
class ProjectPackageFolderPreview:
    """Package target project folder state."""

    status: PackagePreviewItemStatus
    path: str | None
    message: str


@dataclass(frozen=True, slots=True)
class ProjectPackageAuthorityContext:
    """Authority context used by the package preview."""

    confirmed_matrix_id: str | None
    confirmed_revision: int | None
    confirmed_fee_id: str | None
    confirmed_fee_revision: int | None
    confirmed_fee_status: str


@dataclass(frozen=True, slots=True)
class ProjectPackagePreviewItem:
    """One required or optional package preview item."""

    key: str
    label: str
    status: PackagePreviewItemStatus
    target_folder: str | None
    target_path: str | None
    message: str


@dataclass(frozen=True, slots=True)
class ProjectPackagePreview:
    """Read-only package readiness preview result."""

    project_id: str
    status: PackagePreviewStatus
    project_folder: ProjectPackageFolderPreview
    authority_context: ProjectPackageAuthorityContext
    required_items: tuple[ProjectPackagePreviewItem, ...]
    optional_items: tuple[ProjectPackagePreviewItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


class ProjectPackagePreviewService:
    """Build a read-only package preview from current project authority state."""

    def __init__(
        self,
        *,
        project_store: ProjectPackageProjectStore,
        folder_store: ProjectPackageFolderStore,
        confirmed_matrix_store: ProjectPackageConfirmedMatrixStore,
        confirmed_fee_reader: ProjectPackageConfirmedFeeReader,
        section2_previewer: ProjectPackageSection2Previewer,
        external_resource_store: ProjectPackageExternalResourceStore,
    ) -> None:
        """Create the preview service with explicit read-only dependencies."""
        self._project_store = project_store
        self._folder_store = folder_store
        self._confirmed_matrix_store = confirmed_matrix_store
        self._confirmed_fee_reader = confirmed_fee_reader
        self._section2_previewer = section2_previewer
        self._external_resource_store = external_resource_store

    def preview(self, project_id: str) -> ProjectPackagePreview:
        """Return project package readiness without mutating files or records."""
        project = self._project_store.get(project_id)
        if project is None:
            raise ProjectPackagePreviewProjectNotFoundError(
                f"Project not found: {project_id}"
            )

        blockers: list[str] = []
        warnings: list[str] = []
        folder_preview, target_folder = self._folder_preview(project_id, blockers)
        snapshot = self._confirmed_matrix_preview(project_id, blockers)
        confirmed_fee = self._confirmed_fee_preview(project_id, blockers)
        section2_item = self._section2_item(project_id, target_folder, blockers, warnings)
        customer_feedback_item = self._customer_feedback_item(target_folder, blockers)

        required_items = (
            self._test_record_item(target_folder, snapshot),
            self._fee_form_item(target_folder, confirmed_fee),
            section2_item,
            customer_feedback_item,
        )
        optional_items = (
            ProjectPackagePreviewItem(
                key="evidence_candidates",
                label="Evidence placement candidates",
                status="deferred",
                target_folder=str(target_folder) if target_folder else None,
                target_path=None,
                message="Evidence placement remains a later package execution concern.",
            ),
        )
        status: PackagePreviewStatus = "blocked" if blockers else "ready"
        latest_fee = (
            confirmed_fee.latest_confirmed_fee if confirmed_fee is not None else None
        )
        return ProjectPackagePreview(
            project_id=project.project_id,
            status=status,
            project_folder=folder_preview,
            authority_context=ProjectPackageAuthorityContext(
                confirmed_matrix_id=(
                    snapshot.version.confirmed_matrix_id if snapshot is not None else None
                ),
                confirmed_revision=(
                    snapshot.version.confirmed_revision if snapshot is not None else None
                ),
                confirmed_fee_id=latest_fee.confirmed_fee_id if latest_fee else None,
                confirmed_fee_revision=(
                    latest_fee.confirmed_fee_revision if latest_fee else None
                ),
                confirmed_fee_status=confirmed_fee.status if confirmed_fee else "blocked",
            ),
            required_items=required_items,
            optional_items=optional_items,
            blockers=tuple(blockers),
            warnings=tuple(warnings),
        )

    def _folder_preview(
        self,
        project_id: str,
        blockers: list[str],
    ) -> tuple[ProjectPackageFolderPreview, Path | None]:
        folders = self._folder_store.list_by_project(project_id)
        if not folders:
            message = "Create the project folder before previewing package targets."
            blockers.append(message)
            return ProjectPackageFolderPreview("blocked", None, message), None
        folder = max(folders, key=lambda item: (item.created_on is not None, item.created_on, item.folder_id))
        path = Path(folder.folder_path)
        if not path.is_dir():
            message = f"Latest project folder path is not available: {path}"
            blockers.append(message)
            return ProjectPackageFolderPreview("blocked", str(path), message), None
        return (
            ProjectPackageFolderPreview(
                "ready",
                str(path),
                "Latest project folder is available for package targets.",
            ),
            path,
        )

    def _confirmed_matrix_preview(
        self,
        project_id: str,
        blockers: list[str],
    ) -> ConfirmedMatrixSnapshot | None:
        snapshot = self._confirmed_matrix_store.get_active_by_project(project_id)
        if snapshot is None:
            blockers.append("Confirm Matrix before preparing the project package.")
        return snapshot

    def _confirmed_fee_preview(
        self,
        project_id: str,
        blockers: list[str],
    ) -> ConfirmedFeeVersionReadResult | None:
        try:
            result = self._confirmed_fee_reader.get_latest(project_id)
        except (
            ConfirmedMatrixFeeTemplateBasicFillError,
            ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
        ) as exc:
            blockers.append(f"Confirmed Fee readiness is blocked: {exc}")
            return None
        if result.status != "current":
            blockers.append("Confirm Fee before preparing the project package.")
        return result

    def _section2_item(
        self,
        project_id: str,
        target_folder: Path | None,
        blockers: list[str],
        warnings: list[str],
    ) -> ProjectPackagePreviewItem:
        try:
            result = self._section2_previewer.preview(
                ProjectSection2SyncCommand(project_id=project_id)
            )
        except ProjectSection2SyncError as exc:
            message = f"Section 2 date readiness is blocked: {exc}"
            blockers.append(message)
            return ProjectPackagePreviewItem(
                key="application_form_section2",
                label="Application Form Section 2",
                status="blocked",
                target_folder=str(target_folder) if target_folder else None,
                target_path=None,
                message=message,
            )
        if result.status == "ready":
            message = "Sync Section 2 dates before package execution."
            blockers.append(message)
            status: PackagePreviewItemStatus = "blocked"
        elif result.status == "blocked":
            message = "Section 2 dates are blocked."
            blockers.append(message)
            status = "blocked"
        elif result.status == "partial":
            message = "One Section 2 source date is missing; package preview can continue with a warning."
            warnings.append(message)
            status = "warning"
        else:
            message = "Section 2 dates are synchronized."
            status = "ready"
        return ProjectPackagePreviewItem(
            key="application_form_section2",
            label="Application Form Section 2",
            status=status,
            target_folder=str(target_folder) if target_folder else None,
            target_path=None,
            message=message,
        )

    def _customer_feedback_item(
        self,
        target_folder: Path | None,
        blockers: list[str],
    ) -> ProjectPackagePreviewItem:
        template_folder = self._external_resource_store.get_by_type(
            ExternalResourceType.PROJECT_FOLDER_TEMPLATE
        )
        if template_folder is None:
            message = "Template folder is not configured."
            blockers.append(message)
            return _blocked_item("customer_feedback_form", "Customer Feedback Form", target_folder, message)
        if not Path(template_folder.path).is_dir():
            message = f"Template folder does not exist or is not a folder: {template_folder.path}"
            blockers.append(message)
            return _blocked_item("customer_feedback_form", "Customer Feedback Form", target_folder, message)
        try:
            template_path = discover_customer_feedback_template(Path(template_folder.path))
        except CustomerFeedbackTemplateDiscoveryError as exc:
            message = str(exc)
            blockers.append(message)
            return _blocked_item("customer_feedback_form", "Customer Feedback Form", target_folder, message)
        return ProjectPackagePreviewItem(
            key="customer_feedback_form",
            label="Customer Feedback Form",
            status="ready",
            target_folder=str(target_folder) if target_folder else None,
            target_path=None,
            message=f"Template ready: {template_path.name}",
        )

    def _test_record_item(
        self,
        target_folder: Path | None,
        snapshot: ConfirmedMatrixSnapshot | None,
    ) -> ProjectPackagePreviewItem:
        if snapshot is None:
            return _blocked_item(
                "test_record",
                "Test Record",
                target_folder,
                "Confirm Matrix before Test Record generation.",
            )
        return ProjectPackagePreviewItem(
            key="test_record",
            label="Test Record",
            status="ready",
            target_folder=str(target_folder) if target_folder else None,
            target_path=None,
            message="Ready to generate from active Confirmed Matrix in TASK_313.",
        )

    def _fee_form_item(
        self,
        target_folder: Path | None,
        confirmed_fee: ConfirmedFeeVersionReadResult | None,
    ) -> ProjectPackagePreviewItem:
        if confirmed_fee is None or confirmed_fee.status != "current":
            return _blocked_item(
                "fee_form",
                "Fee Form",
                target_folder,
                "Confirm Fee before Fee Form package generation.",
            )
        return ProjectPackagePreviewItem(
            key="fee_form",
            label="Fee Form",
            status="ready",
            target_folder=str(target_folder) if target_folder else None,
            target_path=None,
            message="Ready to export from current Confirmed Fee in TASK_313.",
        )


def _blocked_item(
    key: str,
    label: str,
    target_folder: Path | None,
    message: str,
) -> ProjectPackagePreviewItem:
    return ProjectPackagePreviewItem(
        key=key,
        label=label,
        status="blocked",
        target_folder=str(target_folder) if target_folder else None,
        target_path=None,
        message=message,
    )
