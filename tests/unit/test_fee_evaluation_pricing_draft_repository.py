from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftSnapshot,
)
from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.models import FeeEvaluationPricingDraftEditModel
from backend.infrastructure.storage.repositories.fee_evaluation_pricing_draft_edit import (
    FeeEvaluationPricingDraftEditRepository,
)


def test_fee_evaluation_pricing_draft_repository_upserts_current_tuple() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        repo = FeeEvaluationPricingDraftEditRepository(session)

        first = repo.upsert_current(_snapshot("draft-1", unit_price="10"))
        second = repo.upsert_current(_snapshot("draft-2", unit_price="25"))
        latest = repo.get_latest_by_project("P1")
        row_count = len(
            session.scalars(select(FeeEvaluationPricingDraftEditModel)).all()
        )

    assert row_count == 1
    assert first.draft_edit_id == "draft-1"
    assert second.draft_edit_id == "draft-1"
    assert latest is not None
    assert latest.edited_values.rows[0].unit_price == "25"


def _snapshot(draft_edit_id: str, *, unit_price: str) -> FeeEvaluationPricingDraftSnapshot:
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id=draft_edit_id,
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        edited_values=FeeEvaluationEditedExportValues(
            rows=(
                FeeEvaluationEditedExportRow(
                    source_line_id="line-1",
                    confirmed_group_id="group-1",
                    confirmed_row_id="row-1",
                    step_token="1",
                    step_index=0,
                    spend_time="1",
                    unit_price=unit_price,
                    unit_type="per sample",
                    units="1",
                    base_fee="0",
                    discount="0%",
                    testing_fee=unit_price,
                    notes="",
                ),
            ),
            summary=FeeEvaluationEditedExportSummary(
                condition_confirmation_spend_time="0",
                external_cost="0",
                external_cost_note="",
                lab_manpower_hourly_rate="200",
            ),
        ),
        created_at="2026-06-09T09:00:00+00:00",
        updated_at="2026-06-09T09:10:00+00:00",
    )
