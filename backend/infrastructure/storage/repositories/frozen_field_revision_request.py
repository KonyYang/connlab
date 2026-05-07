"""Repository for frozen-field revision request records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import FrozenFieldRevisionRequest, FrozenFieldRevisionRequestStatus
from backend.infrastructure.storage.models import FrozenFieldRevisionRequestModel


class FrozenFieldRevisionRequestRepository:
    """Persist and load frozen-field revision request records."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, request: FrozenFieldRevisionRequest) -> FrozenFieldRevisionRequest:
        self._session.add(_to_model(request))
        self._session.flush()
        return request

    def get(self, request_id: str) -> FrozenFieldRevisionRequest | None:
        row = self._session.get(FrozenFieldRevisionRequestModel, request_id)
        return _to_domain(row) if row else None

    def list_by_case(self, case_id: str) -> list[FrozenFieldRevisionRequest]:
        rows = self._session.scalars(
            select(FrozenFieldRevisionRequestModel)
            .where(FrozenFieldRevisionRequestModel.intake_case_id == case_id)
            .order_by(FrozenFieldRevisionRequestModel.created_at.desc())
        ).all()
        return [_to_domain(row) for row in rows]

    def list_by_project(self, project_id: str) -> list[FrozenFieldRevisionRequest]:
        rows = self._session.scalars(
            select(FrozenFieldRevisionRequestModel)
            .where(FrozenFieldRevisionRequestModel.project_id == project_id)
            .order_by(FrozenFieldRevisionRequestModel.created_at.desc())
        ).all()
        return [_to_domain(row) for row in rows]


def _to_model(request: FrozenFieldRevisionRequest) -> FrozenFieldRevisionRequestModel:
    return FrozenFieldRevisionRequestModel(
        request_id=request.request_id,
        intake_case_id=request.intake_case_id,
        project_id=request.project_id,
        ltr_record_id=request.ltr_record_id,
        ltr_number=request.ltr_number,
        status=request.status.value,
        requested_by=request.requested_by,
        reason=request.reason,
        field_changes_json=request.field_changes_json,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )


def _to_domain(row: FrozenFieldRevisionRequestModel) -> FrozenFieldRevisionRequest:
    return FrozenFieldRevisionRequest(
        request_id=row.request_id,
        intake_case_id=row.intake_case_id,
        project_id=row.project_id,
        ltr_record_id=row.ltr_record_id,
        ltr_number=row.ltr_number,
        status=FrozenFieldRevisionRequestStatus(row.status),
        requested_by=row.requested_by,
        reason=row.reason,
        field_changes_json=row.field_changes_json,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
