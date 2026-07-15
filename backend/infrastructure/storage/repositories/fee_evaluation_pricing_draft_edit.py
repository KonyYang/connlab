"""Repository for saved Fee Evaluation pricing draft edits."""

from __future__ import annotations

import json

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftCasExpectation,
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_from_json,
    edited_values_to_json,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftEnvelopeError,
    decode_pricing_draft_payload,
    validation_token_for,
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
        payload_json = snapshot.payload_json or edited_values_to_json(snapshot.edited_values)
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

    def compare_and_swap(
        self,
        snapshot: FeeEvaluationPricingDraftSnapshot,
        expectation: FeeEvaluationPricingDraftCasExpectation | None,
    ) -> FeeEvaluationPricingDraftSnapshot | None:
        """Persist a V2 snapshot only when its predecessor is still current."""
        payload_json = snapshot.payload_json or edited_values_to_json(snapshot.edited_values)
        if expectation is None:
            if self.get_by_context(
                project_id=snapshot.project_id,
                confirmed_matrix_id=snapshot.confirmed_matrix_id,
                confirmed_revision=snapshot.confirmed_revision,
                fee_rule_version_id=snapshot.fee_rule_version_id,
            ) is not None:
                return None
            self._session.add(_model_from_snapshot(snapshot, payload_json))
            try:
                self._session.flush()
            except IntegrityError:
                self._session.rollback()
                return None
            row = self._session.get(FeeEvaluationPricingDraftEditModel, snapshot.draft_edit_id)
            return _to_snapshot(row) if row is not None else None

        statement = (
            update(FeeEvaluationPricingDraftEditModel)
            .where(
                FeeEvaluationPricingDraftEditModel.draft_edit_id
                == expectation.draft_edit_id,
                FeeEvaluationPricingDraftEditModel.updated_at == expectation.updated_at,
            )
            .values(payload_json=payload_json, updated_at=snapshot.updated_at)
        )
        if expectation.payload_json is not None:
            statement = statement.where(
                FeeEvaluationPricingDraftEditModel.payload_json
                == expectation.payload_json
            )
        result = self._session.execute(statement)
        if result.rowcount != 1:
            return None
        self._session.flush()
        row = self._session.get(FeeEvaluationPricingDraftEditModel, expectation.draft_edit_id)
        return _to_snapshot(row) if row is not None else None

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
    decoded = _decode_payload(row.payload_json)
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id=row.draft_edit_id,
        project_id=row.project_id,
        confirmed_matrix_id=row.confirmed_matrix_id,
        confirmed_revision=row.confirmed_revision,
        fee_rule_version_id=row.fee_rule_version_id,
        edited_values=edited_values_from_json(
            json.dumps(decoded.edited_values_payload, ensure_ascii=False)
        ),
        created_at=row.created_at,
        updated_at=row.updated_at,
        generation=decoded.generation,
        payload_json=row.payload_json,
        payload_fingerprint=decoded.payload_fingerprint,
        source_context_fingerprint=decoded.source_context_fingerprint,
        validation_token=(
            validation_token_for(
                draft_edit_id=row.draft_edit_id,
                generation=decoded.generation,
                source_context_fingerprint=decoded.source_context_fingerprint or "",
                payload_fingerprint=decoded.payload_fingerprint or "",
            )
            if decoded.kind == "v2" and decoded.generation is not None
            else None
        ),
        source_context=decoded.source_context,
    )


def _model_from_snapshot(
    snapshot: FeeEvaluationPricingDraftSnapshot,
    payload_json: str,
) -> FeeEvaluationPricingDraftEditModel:
    return FeeEvaluationPricingDraftEditModel(
        draft_edit_id=snapshot.draft_edit_id,
        project_id=snapshot.project_id,
        confirmed_matrix_id=snapshot.confirmed_matrix_id,
        confirmed_revision=snapshot.confirmed_revision,
        fee_rule_version_id=snapshot.fee_rule_version_id,
        payload_json=payload_json,
        created_at=snapshot.created_at,
        updated_at=snapshot.updated_at,
    )


def _decode_payload(payload_json: str):
    try:
        return decode_pricing_draft_payload(payload_json)
    except FeePricingDraftEnvelopeError:
        payload = json.loads(payload_json)
        if not isinstance(payload, dict):
            raise
        return type(
            "LegacyPricingDraftPayload",
            (),
            {
                "kind": "legacy",
                "generation": None,
                "payload_fingerprint": None,
                "source_context_fingerprint": None,
                "source_context": None,
                "edited_values_payload": payload,
            },
        )()
