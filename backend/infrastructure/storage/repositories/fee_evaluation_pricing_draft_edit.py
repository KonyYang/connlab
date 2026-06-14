"""Repository for saved Fee Evaluation pricing draft edits."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
    edited_values_from_json,
    edited_values_to_json,
)
from backend.infrastructure.storage.models import FeeEvaluationPricingDraftEditModel


class FeeEvaluationPricingDraftEditRepository:
    """Persist saved Fee Evaluation pricing draft edit payloads."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_current(
        self, snapshot: FeeEvaluationPricingDraftSnapshot
    ) -> FeeEvaluationPricingDraftSnapshot:
        """Create or replace the draft for one project/Matrix/rule context."""
        existing = self._session.scalar(
            select(FeeEvaluationPricingDraftEditModel).where(
                FeeEvaluationPricingDraftEditModel.project_id == snapshot.project_id,
                FeeEvaluationPricingDraftEditModel.confirmed_matrix_id
                == snapshot.confirmed_matrix_id,
                FeeEvaluationPricingDraftEditModel.confirmed_revision
                == snapshot.confirmed_revision,
                FeeEvaluationPricingDraftEditModel.fee_rule_version_id
                == snapshot.fee_rule_version_id,
            )
        )
        payload_json = edited_values_to_json(snapshot.edited_values)
        if existing is None:
            self._session.add(
                FeeEvaluationPricingDraftEditModel(
                    draft_edit_id=snapshot.draft_edit_id,
                    project_id=snapshot.project_id,
                    confirmed_matrix_id=snapshot.confirmed_matrix_id,
                    confirmed_revision=snapshot.confirmed_revision,
                    fee_rule_version_id=snapshot.fee_rule_version_id,
                    payload_json=payload_json,
                    created_at=snapshot.created_at,
                    updated_at=snapshot.updated_at,
                )
            )
            self._session.flush()
            return snapshot
        existing.payload_json = payload_json
        existing.updated_at = snapshot.updated_at
        self._session.flush()
        return _to_snapshot(existing)

    def get_latest_by_project(
        self, project_id: str
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return the latest saved pricing draft for one project."""
        row = self._session.scalar(
            select(FeeEvaluationPricingDraftEditModel)
            .where(FeeEvaluationPricingDraftEditModel.project_id == project_id)
            .order_by(
                FeeEvaluationPricingDraftEditModel.updated_at.desc(),
                FeeEvaluationPricingDraftEditModel.draft_edit_id.desc(),
            )
        )
        return _to_snapshot(row) if row is not None else None

    def get_by_context(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Return the saved pricing draft for one exact project/Matrix/rule context."""
        row = self._session.scalar(
            select(FeeEvaluationPricingDraftEditModel).where(
                FeeEvaluationPricingDraftEditModel.project_id == project_id,
                FeeEvaluationPricingDraftEditModel.confirmed_matrix_id
                == confirmed_matrix_id,
                FeeEvaluationPricingDraftEditModel.confirmed_revision
                == confirmed_revision,
                FeeEvaluationPricingDraftEditModel.fee_rule_version_id
                == fee_rule_version_id,
            )
        )
        return _to_snapshot(row) if row is not None else None

    def delete_current(
        self,
        *,
        project_id: str,
        confirmed_matrix_id: str,
        confirmed_revision: int,
        fee_rule_version_id: str,
    ) -> bool:
        """Delete the saved pricing draft for one exact project/Matrix/rule context."""
        row = self._session.scalar(
            select(FeeEvaluationPricingDraftEditModel).where(
                FeeEvaluationPricingDraftEditModel.project_id == project_id,
                FeeEvaluationPricingDraftEditModel.confirmed_matrix_id
                == confirmed_matrix_id,
                FeeEvaluationPricingDraftEditModel.confirmed_revision
                == confirmed_revision,
                FeeEvaluationPricingDraftEditModel.fee_rule_version_id
                == fee_rule_version_id,
            )
        )
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True


def _to_snapshot(
    row: FeeEvaluationPricingDraftEditModel,
) -> FeeEvaluationPricingDraftSnapshot:
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id=row.draft_edit_id,
        project_id=row.project_id,
        confirmed_matrix_id=row.confirmed_matrix_id,
        confirmed_revision=row.confirmed_revision,
        fee_rule_version_id=row.fee_rule_version_id,
        edited_values=edited_values_from_json(row.payload_json),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
