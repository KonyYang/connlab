"""Application service for project use cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import uuid4

from backend.domain import Project, ProjectStatus, ProjectTemporaryContext


class ProjectRepositoryPort(Protocol):
    """Repository behavior required by the project service."""

    def create(self, project: Project) -> Project:
        """Persist a new project."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""

    def list(self) -> list[Project]:
        """Return all projects."""


class ProjectTemporaryContextStorePort(Protocol):
    """Persistence behavior for temporary planning context."""

    def create(self, context: ProjectTemporaryContext) -> ProjectTemporaryContext:
        """Persist temporary planning context."""


@dataclass(frozen=True, slots=True)
class CreateProjectCommand:
    """Input command for creating a project."""

    product_name: str
    requestor: str
    project_no: str | None = None
    business_unit: str | None = None


@dataclass(frozen=True, slots=True)
class CreateTemporaryProjectCommand:
    """Input command for an active temporary planning project."""

    request_summary: str | None = None
    sample_description: str | None = None
    test_item: str | None = None
    requestor: str | None = None
    source_asset_ids: tuple[str, ...] = ()
    notes: str | None = None


class ProjectNotFoundError(LookupError):
    """Raised when a requested project does not exist."""


class ProjectService:
    """Coordinate project use cases without depending on storage details."""

    def __init__(
        self,
        repository: ProjectRepositoryPort,
        temporary_context_store: ProjectTemporaryContextStorePort | None = None,
    ) -> None:
        """Create a project service with its repository port."""
        self._repository = repository
        self._temporary_context_store = temporary_context_store

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

    def create_temporary_project(self, command: CreateTemporaryProjectCommand) -> Project:
        """Create an active no-LTR project for early Matrix and Fee planning."""
        project = Project(
            project_id=uuid4().hex,
            project_no=None,
            product_name=_first_text(
                command.sample_description,
                command.request_summary,
                "Temporary planning project",
            ),
            requestor=_first_text(command.requestor, "Unknown requestor"),
            business_unit=None,
            # The current storage model has no separate temporary lifecycle enum.
            # A no-LTR draft remains active and is classified as Planning by the registry.
            status=ProjectStatus.DRAFT,
            created_on=date.today(),
        )
        created = self._repository.create(project)
        if self._temporary_context_store is not None:
            self._temporary_context_store.create(
                ProjectTemporaryContext(
                    context_id=uuid4().hex,
                    project_id=created.project_id,
                    request_summary=_optional_text(command.request_summary),
                    sample_description=_optional_text(command.sample_description),
                    test_item=_optional_text(command.test_item),
                    notes=_optional_text(command.notes),
                    source_asset_ids=tuple(
                        value
                        for value in (
                            _optional_text(item) for item in command.source_asset_ids
                        )
                        if value is not None
                    ),
                )
            )
        return created

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


def _first_text(*values: str | None) -> str:
    """Return the first non-empty text value."""
    for value in values:
        text = _optional_text(value)
        if text:
            return text
    return ""
