"""Repository for Project Basic Information authority records."""

from __future__ import annotations

import json

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.application.project_basic_information_service import (
    ProjectBasicInformationRecord,
    ProjectBasicInformationVersionConflictError,
)
from backend.infrastructure.storage.models import ProjectBasicInformationRecordModel


class ProjectBasicInformationRepository:
    """Persist and load Project Basic Information records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def get_latest_draft(self, project_id: str) -> ProjectBasicInformationRecord | None:
        """Return the latest draft for one project."""
        row = self._session.scalar(
            select(ProjectBasicInformationRecordModel)
            .where(
                ProjectBasicInformationRecordModel.project_id == project_id,
                ProjectBasicInformationRecordModel.status == "draft",
            )
            .order_by(ProjectBasicInformationRecordModel.updated_at.desc())
        )
        return _to_domain(row) if row is not None else None

    def get_latest_confirmed(
        self, project_id: str
    ) -> ProjectBasicInformationRecord | None:
        """Return the latest confirmed record for one project."""
        row = self._session.scalar(
            select(ProjectBasicInformationRecordModel)
            .where(
                ProjectBasicInformationRecordModel.project_id == project_id,
                ProjectBasicInformationRecordModel.status == "confirmed",
            )
            .order_by(ProjectBasicInformationRecordModel.version.desc())
        )
        return _to_domain(row) if row is not None else None

    def list_confirmed_by_project(
        self, project_id: str
    ) -> list[ProjectBasicInformationRecord]:
        """Return confirmed records ordered by version."""
        rows = self._session.scalars(
            select(ProjectBasicInformationRecordModel)
            .where(
                ProjectBasicInformationRecordModel.project_id == project_id,
                ProjectBasicInformationRecordModel.status == "confirmed",
            )
            .order_by(ProjectBasicInformationRecordModel.version)
        ).all()
        return [_to_domain(row) for row in rows]

    def save_draft(
        self, record: ProjectBasicInformationRecord
    ) -> ProjectBasicInformationRecord:
        """Create or update the single current draft for a project."""
        existing = self._session.scalar(
            select(ProjectBasicInformationRecordModel).where(
                ProjectBasicInformationRecordModel.project_id == record.project_id,
                ProjectBasicInformationRecordModel.status == "draft",
            )
        )
        if existing is None:
            self._session.add(_to_model(record))
        else:
            existing.values_json = _values_to_json(record.values)
            existing.source_signature_json = record.source_signature
            existing.updated_at = record.updated_at
        self._session.flush()
        return record

    def create_confirmed(
        self, record: ProjectBasicInformationRecord
    ) -> ProjectBasicInformationRecord:
        """Persist a new confirmed Basic Information version."""
        self._session.add(_to_model(record))
        try:
            self._session.flush()
        except IntegrityError as exc:
            raise ProjectBasicInformationVersionConflictError(
                "Basic Information confirmed version already exists. Please retry."
            ) from exc
        return record

    def next_confirmed_version(self, project_id: str) -> int:
        """Return the next confirmed version number for one project."""
        latest_version = self._session.scalar(
            select(func.max(ProjectBasicInformationRecordModel.version)).where(
                ProjectBasicInformationRecordModel.project_id == project_id,
                ProjectBasicInformationRecordModel.status == "confirmed",
            )
        )
        return int(latest_version or 0) + 1


def _to_model(record: ProjectBasicInformationRecord) -> ProjectBasicInformationRecordModel:
    """Convert domain record to ORM row."""
    return ProjectBasicInformationRecordModel(
        record_id=record.record_id,
        project_id=record.project_id,
        status=record.status,
        version=record.version,
        values_json=_values_to_json(record.values),
        source_signature_json=record.source_signature,
        created_at=record.created_at,
        updated_at=record.updated_at,
        confirmed_at=record.confirmed_at,
        confirmed_by=record.confirmed_by,
    )


def _to_domain(row: ProjectBasicInformationRecordModel) -> ProjectBasicInformationRecord:
    """Convert ORM row to domain record."""
    return ProjectBasicInformationRecord(
        record_id=row.record_id,
        project_id=row.project_id,
        status=row.status,
        version=row.version,
        values=_values_from_json(row.values_json),
        source_signature=row.source_signature_json,
        created_at=row.created_at,
        updated_at=row.updated_at,
        confirmed_at=row.confirmed_at,
        confirmed_by=row.confirmed_by,
    )


def _values_to_json(values: dict[str, str]) -> str:
    """Serialize Basic Information values."""
    return json.dumps(values, ensure_ascii=False, sort_keys=True)


def _values_from_json(payload: str) -> dict[str, str]:
    """Deserialize Basic Information values."""
    loaded = json.loads(payload)
    if not isinstance(loaded, dict):
        return {}
    return {str(key): str(value) for key, value in loaded.items()}
