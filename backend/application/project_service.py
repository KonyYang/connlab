"""Application service for project use cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import uuid4

from backend.domain import Project, ProjectStatus


class ProjectRepositoryPort(Protocol):
    """Repository behavior required by the project service."""

    def create(self, project: Project) -> Project:
        """Persist a new project."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""

    def list(self) -> list[Project]:
        """Return all projects."""


@dataclass(frozen=True, slots=True)
class CreateProjectCommand:
    """Input command for creating a project."""

    product_name: str
    requestor: str
    project_no: str | None = None
    business_unit: str | None = None


class ProjectNotFoundError(LookupError):
    """Raised when a requested project does not exist."""


class ProjectService:
    """Coordinate project use cases without depending on storage details."""

    def __init__(self, repository: ProjectRepositoryPort) -> None:
        """Create a project service with its repository port."""
        self._repository = repository

    def create_project(self, command: CreateProjectCommand) -> Project:
        """Create a project with the default draft status."""
        project = Project(
            project_id=uuid4().hex,
            project_no=_optional_text(command.project_no),
            product_name=command.product_name,
            requestor=command.requestor,
            business_unit=command.business_unit,
            status=ProjectStatus.DRAFT,
            created_on=date.today(),
        )
        return self._repository.create(project)

    def list_projects(self) -> list[Project]:
        """Return all projects."""
        return self._repository.list()

    def get_project(self, project_id: str) -> Project:
        """Return one project or raise when it cannot be found."""
        project = self._repository.get(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project not found: {project_id}")
        return project


def _optional_text(value: str | None) -> str | None:
    """Normalize optional project metadata text."""
    if value is None:
        return None
    text = value.strip()
    return text or None
