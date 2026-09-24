"""Repository for persisted project output lineage/status records."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import (
    ProjectOutputKind,
    ProjectOutputRecord,
    ProjectOutputSource,
    ProjectOutputStatus,
)
from backend.infrastructure.storage.models import ProjectOutputRecordModel
from backend.infrastructure.files.recoverable_output_publisher import file_hash
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway


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

    def append_verified_relocations(
        self, project_id: str, *, source: Path, target: Path, operation_id: str
    ) -> None:
        """Append new live paths; retain the old immutable output history."""
        rows = self._session.scalars(
            select(ProjectOutputRecordModel)
            .where(ProjectOutputRecordModel.project_id == project_id)
            .order_by(ProjectOutputRecordModel.created_at, ProjectOutputRecordModel.output_record_id)
        ).all()
        latest = {row.output_kind: row for row in rows}
        now = datetime.now(UTC).isoformat()
        for row in latest.values():
            if not row.output_path:
                continue
            old = Path(row.output_path)
            if not old.is_relative_to(source):
                continue
            new = target / old.relative_to(source)
            if OfficialWorkspaceManifestGateway.first_redirected_path(
                *[path for path in (new, *new.parents) if path == target or path.is_relative_to(target)]
            ) is not None:
                raise ValueError("A relocated output path redirects through a link or junction.")
            actual_hash = file_hash(new)
            size = new.stat().st_size if actual_hash is not None else None
            verified = (
                actual_hash is not None
                and row.output_sha256 is not None
                and actual_hash == row.output_sha256
                and (row.output_size_bytes is None or size == row.output_size_bytes)
            )
            note = f"Official folder relocation {operation_id}; source output {row.output_record_id}."
            if not verified:
                note += " Target file is missing or differs from its registered fingerprint; regenerate or review."
            self._session.add(ProjectOutputRecordModel(
                output_record_id=f"por-{uuid4().hex}", project_id=project_id,
                draft_id=row.draft_id, draft_version=row.draft_version,
                output_kind=row.output_kind, output_path=str(new),
                output_sha256=actual_hash if verified else None,
                output_size_bytes=size if verified else None,
                source_context_signature=row.source_context_signature,
                status=row.status if verified else ProjectOutputStatus.FAILED.value,
                source=row.source, created_at=now, updated_at=now, note=note,
            ))
        self._session.flush()


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
