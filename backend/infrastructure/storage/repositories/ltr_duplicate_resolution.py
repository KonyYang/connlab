"""Repositories for local LTR duplicate-resolution tokens and audit events."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain import LtrAssociationEvent, LtrDuplicateResolutionToken
from backend.infrastructure.storage.models import (
    LtrAssociationEventModel,
    LtrDuplicateResolutionTokenModel,
)


class LtrDuplicateResolutionTokenRepository:
    """Persist and load local LTR duplicate-resolution tokens."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, token: LtrDuplicateResolutionToken) -> LtrDuplicateResolutionToken:
        """Persist a duplicate-resolution token."""
        self._session.add(_token_to_model(token))
        self._session.flush()
        return token

    def get(self, token_id: str) -> LtrDuplicateResolutionToken | None:
        """Return one token by id."""
        row = self._session.get(LtrDuplicateResolutionTokenModel, token_id)
        return _token_to_domain(row) if row else None

    def update(self, token: LtrDuplicateResolutionToken) -> LtrDuplicateResolutionToken:
        """Update token state."""
        row = self._session.get(LtrDuplicateResolutionTokenModel, token.token_id)
        if row is None:
            raise ValueError(f"LTR duplicate resolution token not found: {token.token_id}")
        row.used_at = token.used_at
        row.metadata_json = token.metadata_json
        self._session.flush()
        return token


class LtrAssociationEventRepository:
    """Persist and load local LTR association audit events."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, event: LtrAssociationEvent) -> LtrAssociationEvent:
        """Persist an association event."""
        self._session.add(_event_to_model(event))
        self._session.flush()
        return event

    def list_by_ltr_number(self, ltr_number: str) -> list[LtrAssociationEvent]:
        """Return association events for one LTR number."""
        rows = self._session.scalars(
            select(LtrAssociationEventModel)
            .where(LtrAssociationEventModel.ltr_number == ltr_number)
            .order_by(LtrAssociationEventModel.created_at, LtrAssociationEventModel.event_id)
        ).all()
        return [_event_to_domain(row) for row in rows]


def _token_to_model(token: LtrDuplicateResolutionToken) -> LtrDuplicateResolutionTokenModel:
    return LtrDuplicateResolutionTokenModel(
        token_id=token.token_id,
        ltr_number=token.ltr_number,
        existing_ltr_id=token.existing_ltr_id,
        existing_project_id=token.existing_project_id,
        current_case_id=token.current_case_id,
        current_project_id=token.current_project_id,
        conflict_fingerprint=token.conflict_fingerprint,
        workbook_fingerprint=token.workbook_fingerprint,
        expires_at=token.expires_at,
        used_at=token.used_at,
        created_at=token.created_at,
        created_by=token.created_by,
        metadata_json=token.metadata_json,
    )

def _token_to_domain(row: LtrDuplicateResolutionTokenModel) -> LtrDuplicateResolutionToken:
    return LtrDuplicateResolutionToken(
        token_id=row.token_id,
        ltr_number=row.ltr_number,
        existing_ltr_id=row.existing_ltr_id,
        existing_project_id=row.existing_project_id,
        current_case_id=row.current_case_id,
        current_project_id=row.current_project_id,
        conflict_fingerprint=row.conflict_fingerprint,
        workbook_fingerprint=row.workbook_fingerprint,
        expires_at=row.expires_at,
        used_at=row.used_at,
        created_at=row.created_at,
        created_by=row.created_by,
        metadata_json=row.metadata_json,
    )


def _event_to_model(event: LtrAssociationEvent) -> LtrAssociationEventModel:
    return LtrAssociationEventModel(
        event_id=event.event_id,
        ltr_number=event.ltr_number,
        event_type=event.event_type,
        old_ltr_id=event.old_ltr_id,
        old_project_id=event.old_project_id,
        new_ltr_id=event.new_ltr_id,
        new_project_id=event.new_project_id,
        operator=event.operator,
        reason=event.reason,
        token_id=event.token_id,
        created_at=event.created_at,
        metadata_json=event.metadata_json,
    )


def _event_to_domain(row: LtrAssociationEventModel) -> LtrAssociationEvent:
    return LtrAssociationEvent(
        event_id=row.event_id,
        ltr_number=row.ltr_number,
        event_type=row.event_type,
        old_ltr_id=row.old_ltr_id,
        old_project_id=row.old_project_id,
        new_ltr_id=row.new_ltr_id,
        new_project_id=row.new_project_id,
        operator=row.operator,
        reason=row.reason,
        token_id=row.token_id,
        created_at=row.created_at,
        metadata_json=row.metadata_json,
    )
