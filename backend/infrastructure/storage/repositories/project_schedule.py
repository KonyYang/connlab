"""SQLite adapter for Project Schedule authority."""

from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.domain.project_schedule_models import ProjectScheduleRevision
from backend.infrastructure.storage.models_project_schedule import ProjectScheduleRevisionModel


class ProjectScheduleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def active_revision(self, project_id: str) -> ProjectScheduleRevision | None:
        row = self._session.query(ProjectScheduleRevisionModel).filter_by(
            project_id=project_id, state="confirmed"
        ).one_or_none()
        return _to_domain(row) if row is not None else None

    def highest_revision_sequence(self, project_id: str) -> int:
        return int(
            self._session.query(func.max(ProjectScheduleRevisionModel.revision_sequence))
            .filter_by(project_id=project_id)
            .scalar()
            or 0
        )

    def add(self, revision: ProjectScheduleRevision) -> None:
        self._session.add(_to_model(revision))

    def supersede_active(self, project_id: str, *, at: str) -> None:
        row = self._session.scalar(
            select(ProjectScheduleRevisionModel).where(
                ProjectScheduleRevisionModel.project_id == project_id,
                ProjectScheduleRevisionModel.state == "confirmed",
            )
        )
        if row is None:
            return
        row.state = "superseded"
        row.superseded_at = at
        row.superseded_reason = "Superseded by confirmed Project Schedule revision."

    def flush(self) -> None:
        self._session.flush()

    @contextmanager
    def transaction(self):
        with self._session.begin_nested():
            yield


def _to_domain(row: ProjectScheduleRevisionModel) -> ProjectScheduleRevision:
    return ProjectScheduleRevision(
        revision_id=row.revision_id,
        project_id=row.project_id,
        revision_sequence=row.revision_sequence,
        state=row.state,
        fingerprint=row.fingerprint,
        matrix_input_fingerprint=row.matrix_input_fingerprint,
        based_on_confirmed_matrix_id=row.based_on_confirmed_matrix_id,
        based_on_confirmed_matrix_revision=row.based_on_confirmed_matrix_revision,
        based_on_basic_information_version=row.based_on_basic_information_version,
        sample_received_date=row.sample_received_date,
        post_test_buffer_days=row.post_test_buffer_days,
        test_start_date=row.test_start_date,
        test_complete_date=row.test_complete_date,
        estimated_completion_date=row.estimated_completion_date,
        confirmed_by=row.confirmed_by,
        confirmed_at=row.confirmed_at,
        superseded_at=row.superseded_at,
        superseded_reason=row.superseded_reason,
    )


def _to_model(value: ProjectScheduleRevision) -> ProjectScheduleRevisionModel:
    return ProjectScheduleRevisionModel(**{
        field: getattr(value, field)
        for field in (
            "revision_id", "project_id", "revision_sequence", "state", "fingerprint",
            "matrix_input_fingerprint", "based_on_confirmed_matrix_id",
            "based_on_confirmed_matrix_revision", "based_on_basic_information_version",
            "sample_received_date", "post_test_buffer_days", "test_start_date",
            "test_complete_date", "estimated_completion_date", "confirmed_by",
            "confirmed_at", "superseded_at", "superseded_reason",
        )
    })
