"""Project repository implementation."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import Project, ProjectStatus
from backend.infrastructure.storage.models import ProjectModel


class ProjectRepository:
    """Persist and load project domain records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, project: Project) -> Project:
        """Persist a new project and return the domain record."""
        self._session.add(_to_model(project))
        self._session.flush()
        return project

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID, or None when it does not exist."""
        row = self._session.get(ProjectModel, project_id)
        return _to_domain(row) if row else None

    def list(self) -> list[Project]:
        """Return all projects ordered by optional project number and product."""
        rows = self._session.scalars(
            select(ProjectModel).order_by(ProjectModel.project_no, ProjectModel.product_name)
        ).all()
        return [_to_domain(row) for row in rows]

    def update(self, project: Project) -> Project:
        """Update an existing project from a domain record."""
        row = self._session.get(ProjectModel, project.project_id)
        if row is None:
            raise ValueError(f"Project not found: {project.project_id}")
        row.project_no = project.project_no
        row.product_name = project.product_name
        row.requestor = project.requestor
        row.status = project.status.value
        row.business_unit = project.business_unit
        row.created_on = project.created_on
        self._session.flush()
        return project


def _to_model(project: Project) -> ProjectModel:
    """Convert a project domain record to an ORM row."""
    return ProjectModel(
        project_id=project.project_id,
        project_no=project.project_no,
        product_name=project.product_name,
        requestor=project.requestor,
        status=project.status.value,
        business_unit=project.business_unit,
        created_on=project.created_on,
    )


def _to_domain(row: ProjectModel) -> Project:
    """Convert a project ORM row to a domain record."""
    return Project(
        project_id=row.project_id,
        project_no=row.project_no,
        product_name=row.product_name,
        requestor=row.requestor,
        status=ProjectStatus(row.status),
        business_unit=row.business_unit,
        created_on=row.created_on,
    )
