"""Repository for local official project workspace records."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.infrastructure.storage.models import ProjectOfficialWorkspaceRecordModel


class ProjectOfficialWorkspaceRepository:
    """Persist and load local official project workspace records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        """Return the workspace record for a project when one exists."""
        row = self._session.scalar(
            select(ProjectOfficialWorkspaceRecordModel).where(
                ProjectOfficialWorkspaceRecordModel.project_id == project_id
            )
        )
        return _to_domain(row) if row else None

    def save(self, record: OfficialWorkspaceRecord) -> OfficialWorkspaceRecord:
        """Create or update the workspace record for a project."""
        row = self._session.scalar(
            select(ProjectOfficialWorkspaceRecordModel).where(
                ProjectOfficialWorkspaceRecordModel.project_id == record.project_id
            )
        )
        if row is None:
            self._session.add(_to_model(record))
        else:
            row.workspace_id = record.workspace_id
            row.dl_number = record.dl_number
            row.local_workspace_path = str(record.local_workspace_path)
            row.source_book_path = str(record.source_book_path)
            row.official_folder_path = str(record.official_folder_path)
            row.manifest_path = str(record.manifest_path)
            row.template_source_path = str(record.template_source_path)
            row.created_at = record.created_at
        self._session.flush()
        return record


def _to_model(record: OfficialWorkspaceRecord) -> ProjectOfficialWorkspaceRecordModel:
    """Convert a domain-like record to an ORM row."""
    return ProjectOfficialWorkspaceRecordModel(
        workspace_id=record.workspace_id,
        project_id=record.project_id,
        dl_number=record.dl_number,
        local_workspace_path=str(record.local_workspace_path),
        source_book_path=str(record.source_book_path),
        official_folder_path=str(record.official_folder_path),
        manifest_path=str(record.manifest_path),
        template_source_path=str(record.template_source_path),
        created_at=record.created_at,
    )


def _to_domain(row: ProjectOfficialWorkspaceRecordModel) -> OfficialWorkspaceRecord:
    """Convert an ORM row to a domain-like record."""
    return OfficialWorkspaceRecord(
        workspace_id=row.workspace_id,
        project_id=row.project_id,
        dl_number=row.dl_number,
        local_workspace_path=Path(row.local_workspace_path),
        source_book_path=Path(row.source_book_path),
        official_folder_path=Path(row.official_folder_path),
        manifest_path=Path(row.manifest_path),
        template_source_path=Path(row.template_source_path),
        created_at=row.created_at,
    )
