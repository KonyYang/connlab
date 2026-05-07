"""Lifecycle actions for pre-project creation drafts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

from backend.domain import IntakeCase, IntakeCaseStatus, IntakePackage, IntakePackageStatus
from backend.infrastructure.files import IntakeStorage


class ProjectCreationDraftLifecycleError(ValueError):
    """Raised when a creation draft lifecycle action is not allowed."""


class ProjectCreationDraftLifecycleNotFoundError(LookupError):
    """Raised when the requested creation package cannot be found."""


class IntakePackageStore(Protocol):
    """Persistence port for intake packages."""

    def get(self, package_id: str) -> IntakePackage | None: ...

    def update(self, package: IntakePackage) -> IntakePackage: ...

    def delete(self, package_id: str) -> bool: ...


class IntakeCaseStore(Protocol):
    """Persistence port for intake cases."""

    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...

    def delete_by_package(self, package_id: str) -> int: ...


class IntakeAssetStore(Protocol):
    """Persistence port for intake assets."""

    def delete_by_package(self, package_id: str) -> int: ...


class IntakeDraftStore(Protocol):
    """Persistence port for intake drafts."""

    def delete_by_package(self, package_id: str) -> int: ...


@dataclass(frozen=True)
class ProjectCreationDraftLifecycleResult:
    """Result returned after saving or discarding one creation draft package."""

    package_id: str
    action: str
    package_status: str | None
    deleted_package: bool = False
    deleted_assets: int = 0
    deleted_cases: int = 0
    deleted_drafts: int = 0
    deleted_files: bool = False


class ProjectCreationDraftLifecycleService:
    """Coordinates save and discard actions for New Project creation drafts."""

    _protected_package_statuses = {
        IntakePackageStatus.DRAFT_SAVED,
        IntakePackageStatus.PARTIALLY_CONFIRMED,
        IntakePackageStatus.CONFIRMED,
    }

    def __init__(
        self,
        storage: IntakeStorage,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
    ) -> None:
        """Create the service with explicit storage and persistence ports."""
        self._storage = storage
        self._package_store = package_store
        self._asset_store = asset_store
        self._case_store = case_store
        self._draft_store = draft_store

    def save_draft(self, package_id: str) -> ProjectCreationDraftLifecycleResult:
        """Mark one unconfirmed creation package as intentionally saved."""
        package = self._get_package(package_id)
        self._ensure_unconfirmed(package.package_id)
        saved = self._package_store.update(
            replace(package, status=IntakePackageStatus.DRAFT_SAVED)
        )
        return ProjectCreationDraftLifecycleResult(
            package_id=saved.package_id,
            action="save_draft",
            package_status=saved.status.value,
        )

    def discard_unsaved(self, package_id: str) -> ProjectCreationDraftLifecycleResult:
        """Delete one unsaved creation package and its ConnLab-owned stored files."""
        package = self._get_package(package_id)
        self._ensure_discard_allowed(package)
        return self._delete_package_graph(package, "discard_unsaved")

    def discard_saved_draft(self, package_id: str) -> ProjectCreationDraftLifecycleResult:
        """Delete one explicitly saved draft from Drafts / In Progress."""
        package = self._get_package(package_id)
        self._ensure_unconfirmed(package.package_id)
        if package.status is not IntakePackageStatus.DRAFT_SAVED:
            raise ProjectCreationDraftLifecycleError(
                "Only saved creation drafts can be discarded from Drafts / In Progress."
            )
        return self._delete_package_graph(package, "discard_saved_draft")

    def _delete_package_graph(
        self,
        package: IntakePackage,
        action: str,
    ) -> ProjectCreationDraftLifecycleResult:
        """Delete one package graph and its ConnLab-owned storage directory."""
        deleted_drafts = self._draft_store.delete_by_package(package.package_id)
        deleted_cases = self._case_store.delete_by_package(package.package_id)
        deleted_assets = self._asset_store.delete_by_package(package.package_id)
        deleted_package = self._package_store.delete(package.package_id)
        deleted_files = self._storage.delete_package(package.package_id)
        return ProjectCreationDraftLifecycleResult(
            package_id=package.package_id,
            action=action,
            package_status=None,
            deleted_package=deleted_package,
            deleted_assets=deleted_assets,
            deleted_cases=deleted_cases,
            deleted_drafts=deleted_drafts,
            deleted_files=deleted_files,
        )

    def _get_package(self, package_id: str) -> IntakePackage:
        """Return an intake package or raise a lifecycle not-found error."""
        package = self._package_store.get(package_id)
        if package is None:
            raise ProjectCreationDraftLifecycleNotFoundError(
                f"Creation draft package not found: {package_id}"
            )
        return package

    def _ensure_discard_allowed(self, package: IntakePackage) -> None:
        """Reject discard when package state indicates an intentional save."""
        self._ensure_unconfirmed(package.package_id)
        if package.status in self._protected_package_statuses:
            raise ProjectCreationDraftLifecycleError(
                "This creation draft was saved or confirmed. Use Discard draft from Drafts / In Progress."
            )

    def _ensure_unconfirmed(self, package_id: str) -> None:
        """Reject lifecycle actions for packages that already created a project."""
        if any(
            case.status is IntakeCaseStatus.CONFIRMED or case.confirmed_project_id
            for case in self._case_store.list_by_package(package_id)
        ):
            raise ProjectCreationDraftLifecycleError(
                "This intake package already created a project and cannot be discarded here."
            )
