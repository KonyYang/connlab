from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftCasExpectation,
    FeeEvaluationPricingDraftSnapshot,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
    encode_pricing_draft_v2,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.repositories.fee_evaluation_pricing_draft_edit import (
    FeeEvaluationPricingDraftEditRepository,
)


def test_compare_and_swap_rejects_a_stale_snapshot_without_overwrite() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        repository = FeeEvaluationPricingDraftEditRepository(session)
        initial = _snapshot(generation=1, updated_at="2026-07-15T09:00:00+00:00")
        repository.upsert_current(initial)
        current = repository.get_by_context(
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            fee_rule_version_id="fee-rules",
        )
        assert current is not None
        winner = _snapshot(generation=2, updated_at="2026-07-15T09:01:00+00:00")
        saved = repository.compare_and_swap(
            winner,
            FeeEvaluationPricingDraftCasExpectation.from_snapshot(current),
        )
        stale = _snapshot(generation=2, updated_at="2026-07-15T09:02:00+00:00")
        rejected = repository.compare_and_swap(
            stale,
            FeeEvaluationPricingDraftCasExpectation.from_snapshot(current),
        )

        reloaded = repository.get_by_context(
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            fee_rule_version_id="fee-rules",
        )

    assert saved is not None
    assert rejected is None
    assert reloaded is not None
    assert reloaded.generation == 2
    assert reloaded.updated_at == "2026-07-15T09:01:00+00:00"


def _snapshot(*, generation: int, updated_at: str) -> FeeEvaluationPricingDraftSnapshot:
    values = FeeEvaluationEditedExportValues(
        rows=(),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0",
            external_cost="0",
            external_cost_note="",
            lab_manpower_hourly_rate="200",
        ),
    )
    source_context = FeePricingDraftSourceContext(
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee-rules",
        point_profile_status="not_started",
        point_profile_revision_id=None,
        point_profile_revision_sequence=None,
        point_profile_fingerprint=None,
        automatic_defaults_fingerprint=f"defaults-{generation}",
    )
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="draft-1",
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee-rules",
        edited_values=values,
        created_at="2026-07-15T09:00:00+00:00",
        updated_at=updated_at,
        generation=generation,
        payload_json=encode_pricing_draft_v2(
            generation=generation,
            source_context=source_context,
            edited_values_payload={
                "rows": [],
                "summary": {
                    "condition_confirmation_spend_time": "0",
                    "external_cost": "0",
                    "external_cost_note": "",
                    "lab_manpower_hourly_rate": "200",
                },
                "manual_rows": [],
                "inactive_rows": [],
            },
            row_provenance={},
            summary_provenance=(),
        ),
    )
