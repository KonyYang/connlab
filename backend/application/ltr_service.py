"""Application service for LTR registration and lookup."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import uuid4

from backend.application.ltr_duplicate_resolution_service import (
    DuplicateResolutionCommand,
    LocalLtrDuplicateResolutionService,
)
from backend.application.project_lifecycle_service import LifecycleOperation
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus


class LtrError(ValueError):
    """Base error for LTR service failures."""


class LtrNotFoundError(LookupError):
    """Raised when an LTR resource cannot be found."""


class DuplicateActiveLtrError(LtrError):
    """Raised when a project already has an active registered LTR."""


class ProjectRepositoryPort(Protocol):
    """Project repository behavior required by LTR service."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""

    def update(self, project: Project) -> Project:
        """Update a project."""


class LtrRepositoryPort(Protocol):
    """LTR repository behavior required by LTR service."""

    def create(self, ltr: LtrRecord) -> LtrRecord:
        """Persist an LTR record."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""

    def search(self, query: str) -> list[LtrRecord]:
        """Search LTR records."""

    def find_current_by_ltr_number(self, ltr_number: str) -> LtrRecord | None:
        """Return current registered owner for one LTR number."""


class ProjectLifecycleGuardPort(Protocol):
    """Lifecycle guard behavior required by LTR registration."""

    def require_allowed(
        self,
        project_id: str,
        operation: LifecycleOperation,
    ) -> None:
        """Raise when an operation is not allowed."""


@dataclass(frozen=True, slots=True)
class RegisterLtrCommand:
    """Input command for registering an LTR."""

    ltr_number: str
    requested_by: str | None = None
    requested_date: date | None = None
    notes: str | None = None
    current_case_id: str | None = None
    duplicate_resolution: DuplicateResolutionCommand | None = None


class LtrService:
    """Coordinate LTR registration and lookup use cases."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        ltr_repository: LtrRepositoryPort,
        lifecycle_guard: ProjectLifecycleGuardPort | None = None,
        duplicate_resolution_service: LocalLtrDuplicateResolutionService | None = None,
    ) -> None:
        """Create an LTR service with repository ports."""
        self._projects = project_repository
        self._ltrs = ltr_repository
        self._lifecycle = lifecycle_guard
        self._duplicates = duplicate_resolution_service

    def register_ltr(self, project_id: str, command: RegisterLtrCommand) -> LtrRecord:
        """Register one active LTR for a project."""
        if not command.ltr_number.strip():
            raise LtrError("LTR number is required.")
        if self._lifecycle is not None:
            self._lifecycle.require_allowed(project_id, LifecycleOperation.LTR_COMMIT)
        project = self._get_project(project_id)
        existing = self._ltrs.list_by_project(project_id)
        if any(ltr.status is LtrStatus.REGISTERED for ltr in existing):
            raise DuplicateActiveLtrError(
                f"Project already has an active registered LTR: {project_id}"
            )
        old_owner = None
        if self._duplicates is not None:
            old_owner = self._duplicates.ensure_no_conflict_or_valid_confirmation(
                ltr_number=command.ltr_number.strip(),
                current_project=project,
                current_case_id=command.current_case_id or project_id,
                resolution=command.duplicate_resolution,
            )
        ltr_id = uuid4().hex
        if self._duplicates is not None:
            self._duplicates.retire_old_owner_before_replacement(
                old_owner=old_owner,
                new_ltr_id=ltr_id,
                resolution=command.duplicate_resolution,
            )
        ltr = LtrRecord(
            ltr_id=ltr_id,
            project_id=project.project_id,
            ltr_number=command.ltr_number.strip(),
            status=LtrStatus.REGISTERED,
            registered_on=date.today(),
            requested_by=command.requested_by,
            requested_date=command.requested_date,
            notes=command.notes,
            is_current_owner=True,
        )
        created = self._ltrs.create(ltr)
        if self._duplicates is not None:
            self._duplicates.apply_confirmed_replacement(
                old_owner=old_owner,
                new_owner=created,
                resolution=command.duplicate_resolution,
                operator=command.requested_by,
            )
        self._projects.update(project.with_status(ProjectStatus.LTR_REGISTERED))
        return created

    def list_project_ltrs(self, project_id: str) -> list[LtrRecord]:
        """Return LTR records for a project."""
        self._get_project(project_id)
        return self._ltrs.list_by_project(project_id)

    def search_ltrs(self, query: str) -> list[LtrRecord]:
        """Search LTR records by query string."""
        return self._ltrs.search(query.strip()) if query.strip() else []

    def _get_project(self, project_id: str) -> Project:
        """Load a project or raise not found."""
        project = self._projects.get(project_id)
        if project is None:
            raise LtrNotFoundError(f"Project not found: {project_id}")
        return project
