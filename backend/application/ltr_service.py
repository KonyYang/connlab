"""Application service for LTR registration and lookup."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import uuid4

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


@dataclass(frozen=True, slots=True)
class RegisterLtrCommand:
    """Input command for registering an LTR."""

    ltr_number: str
    requested_by: str | None = None
    requested_date: date | None = None
    notes: str | None = None


class LtrService:
    """Coordinate LTR registration and lookup use cases."""

    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        ltr_repository: LtrRepositoryPort,
    ) -> None:
        """Create an LTR service with repository ports."""
        self._projects = project_repository
        self._ltrs = ltr_repository

    def register_ltr(self, project_id: str, command: RegisterLtrCommand) -> LtrRecord:
        """Register one active LTR for a project."""
        if not command.ltr_number.strip():
            raise LtrError("LTR number is required.")
        project = self._get_project(project_id)
        existing = self._ltrs.list_by_project(project_id)
        if any(ltr.status is LtrStatus.REGISTERED for ltr in existing):
            raise DuplicateActiveLtrError(
                f"Project already has an active registered LTR: {project_id}"
            )
        ltr = LtrRecord(
            ltr_id=uuid4().hex,
            project_id=project.project_id,
            ltr_number=command.ltr_number.strip(),
            status=LtrStatus.REGISTERED,
            registered_on=date.today(),
            requested_by=command.requested_by,
            requested_date=command.requested_date,
            notes=command.notes,
        )
        created = self._ltrs.create(ltr)
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
