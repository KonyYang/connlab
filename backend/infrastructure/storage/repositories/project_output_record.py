"""Repository for persisted project output lineage/status records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import (
    ProjectOutputKind,
    ProjectOutputRecord,
    ProjectOutputSource,
    ProjectOutputStatus,
)
from backend.infrastructure.storage.models import ProjectOutputRecordModel


class ProjectOutputRecordRepository:
    """Persist and read project output lineage/status records."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, record: ProjectOutputRecord) -> ProjectOutputRecord:
        self._session.add(_to_model(record))
        self._session.flush()
        return record

    def list_by_project(self, project_id: str) -> list[ProjectOutputRecord]:
        rows = self._session.scalars(
            select(ProjectOutputRecordModel)
            .where(ProjectOutputRecordModel.project_id == project_id)
            .order_by(ProjectOutputRecordModel.created_at, ProjectOutputRecordModel.output_record_id)
        ).all()
        return [_to_domain(row) for row in rows]


def _to_model(record: ProjectOutputRecord) -> ProjectOutputRecordModel:
    return ProjectOutputRecordModel(
        output_record_id=record.output_record_id,
        project_id=record.project_id,
        draft_id=record.draft_id,
        draft_version=record.draft_version,
        output_kind=record.output_kind.value,
        output_path=record.output_path,
        output_sha256=record.output_sha256,
        output_size_bytes=record.output_size_bytes,
        source_context_signature=record.source_context_signature,
        status=record.status.value,
        source=record.source.value,
        created_at=record.created_at,
        updated_at=record.updated_at,
        note=record.note,
    )


def _to_domain(row: ProjectOutputRecordModel) -> ProjectOutputRecord:
    return ProjectOutputRecord(
        output_record_id=row.output_record_id,
        project_id=row.project_id,
        draft_id=row.draft_id,
        draft_version=row.draft_version,
        output_kind=ProjectOutputKind(row.output_kind),
        output_path=row.output_path,
        output_sha256=row.output_sha256,
        output_size_bytes=row.output_size_bytes,
        source_context_signature=row.source_context_signature,
        status=ProjectOutputStatus(row.status),
        source=ProjectOutputSource(row.source),
        created_at=row.created_at,
        updated_at=row.updated_at,
        note=row.note,
    )
