"""Repository for controlled project cleanup audit records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application.no_ltr_project_cleanup_service import (
    ProjectCleanupAuditRecord,
)
from backend.infrastructure.storage.models import ProjectCleanupAuditRecordModel


class ProjectCleanupAuditRecordRepository:
    """Persist and load project cleanup audit records."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        record: ProjectCleanupAuditRecord,
    ) -> ProjectCleanupAuditRecord:
        """Persist a new cleanup audit record."""
        self._session.add(_to_model(record))
        self._session.flush()
        return record

    def list(self) -> list[ProjectCleanupAuditRecord]:
        """Return all cleanup audit records ordered by creation time."""
        rows = self._session.scalars(
            select(ProjectCleanupAuditRecordModel).order_by(
                ProjectCleanupAuditRecordModel.created_at,
                ProjectCleanupAuditRecordModel.cleanup_id,
            )
        ).all()
        return [_to_domain(row) for row in rows]


def _to_model(record: ProjectCleanupAuditRecord) -> ProjectCleanupAuditRecordModel:
    return ProjectCleanupAuditRecordModel(
        cleanup_id=record.cleanup_id,
        project_id=record.project_id,
        cleanup_type=record.cleanup_type,
        previous_status=record.previous_status,
        new_status=record.new_status,
        reason=record.reason,
        operator=record.operator,
        created_at=record.created_at,
        details_json=record.details_json,
    )


def _to_domain(row: ProjectCleanupAuditRecordModel) -> ProjectCleanupAuditRecord:
    return ProjectCleanupAuditRecord(
        cleanup_id=row.cleanup_id,
        project_id=row.project_id,
        cleanup_type=row.cleanup_type,
        previous_status=row.previous_status,
        new_status=row.new_status,
        reason=row.reason,
        operator=row.operator,
        created_at=row.created_at,
        details_json=row.details_json,
    )
