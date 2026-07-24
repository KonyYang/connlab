"""Historical pricing-draft payload compatibility API regressions."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.api.dependencies import get_fee_evaluation_pricing_draft_service
from backend.api.main import app
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedManualRow,
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
)


def test_pricing_draft_get_normalizes_historical_blank_unit_type() -> None:
    values = _edited_values()
    bad_values = FeeEvaluationEditedExportValues(
        rows=(_row(values, unit_type="", notes="historical note"),),
        summary=values.summary,
        manual_rows=values.manual_rows,
    )
    response = _get_payload(bad_values)

    assert response.status_code == 200
    row = response.json()["payload"]["rows"][0]
    assert row["unit_type"] == "Pending"
    assert row["notes"] == "historical note"


def test_pricing_draft_get_preserves_pending_dependent_pricing_fields() -> None:
    values = _edited_values()
    bad_values = FeeEvaluationEditedExportValues(
        rows=(
            _row(
                values,
                spend_time="Pending",
                unit_price="Pending",
                units="Pending",
                base_fee="Pending",
                discount="Pending",
                testing_fee="Pending",
                notes="historical numeric note",
            ),
        ),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="Pending",
            external_cost="Pending",
            external_cost_note="tooling",
            lab_manpower_hourly_rate="Pending",
        ),
        manual_rows=values.manual_rows,
    )
    response = _get_payload(bad_values)

    assert response.status_code == 200
    assert response.json()["payload"]["rows"][0] == {
        "source_line_id": "cmv-1:g1:cmr-visual:1:0",
        "confirmed_group_id": "cmg-1",
        "confirmed_row_id": "cmr-visual",
        "step_token": "1",
        "step_index": 0,
        "spend_time": "0",
        "unit_price": "",
        "unit_type": "per sample",
        "units": "",
        "base_fee": "0",
        "discount": "0%",
        "testing_fee": "",
        "notes": "historical numeric note",
    }
    assert response.json()["payload"]["summary"] == {
        "condition_confirmation_spend_time": "0",
        "external_cost": "0",
        "external_cost_note": "tooling",
        "lab_manpower_hourly_rate": "200",
    }


def test_pricing_draft_get_keeps_manual_pending_distinct_from_explicit_zero() -> None:
    values = _edited_values()
    pending_manual_row = FeeEvaluationEditedManualRow(
        row_kind="report_preparation",
        spend_time="0",
        unit_price="Pending",
        unit_type="Pending",
        units="",
        base_fee="0",
        discount="0%",
        testing_fee="Pending",
        notes="",
    )
    response = _get_payload(
        FeeEvaluationEditedExportValues(
            rows=(_row(values, unit_price="0", units="0", testing_fee="0"),),
            summary=values.summary,
            manual_rows=(pending_manual_row,),
        )
    )

    payload = response.json()["payload"]
    assert payload["rows"][0]["unit_price"] == "0"
    assert payload["rows"][0]["units"] == "0"
    assert payload["rows"][0]["testing_fee"] == "0"
    assert payload["manual_rows"][0]["unit_price"] == ""
    assert payload["manual_rows"][0]["unit_type"] == "Pending"
    assert payload["manual_rows"][0]["units"] == ""
    assert payload["manual_rows"][0]["base_fee"] == "0"
    assert payload["manual_rows"][0]["testing_fee"] == ""


def _get_payload(values: FeeEvaluationEditedExportValues):
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: _Service(
        _current_result(values)
    )
    try:
        return TestClient(app).get(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
        )
    finally:
        app.dependency_overrides.clear()


def _row(values: FeeEvaluationEditedExportValues, **overrides: str):
    source = values.rows[0]
    return FeeEvaluationEditedExportRow(
        source_line_id=source.source_line_id,
        confirmed_group_id=source.confirmed_group_id,
        confirmed_row_id=source.confirmed_row_id,
        step_token=source.step_token,
        step_index=source.step_index,
        spend_time=overrides.get("spend_time", source.spend_time),
        unit_price=overrides.get("unit_price", source.unit_price),
        unit_type=overrides.get("unit_type", source.unit_type),
        units=overrides.get("units", source.units),
        base_fee=overrides.get("base_fee", source.base_fee),
        discount=overrides.get("discount", source.discount),
        testing_fee=overrides.get("testing_fee", source.testing_fee),
        notes=overrides.get("notes", source.notes),
    )


def _current_result(values: FeeEvaluationEditedExportValues):
    return FeeEvaluationPricingDraftLoadResult(
        status="current",
        current_context=_context(),
        saved_snapshot=FeeEvaluationPricingDraftSnapshot(
            draft_edit_id="fed-1",
            project_id="P1",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            fee_rule_version_id="fee_rules_v2026_06_03",
            edited_values=values,
            created_at="2026-06-09T09:00:00+00:00",
            updated_at="2026-06-09T09:10:00+00:00",
        ),
    )


def _context() -> FeeEvaluationPricingDraftContext:
    return FeeEvaluationPricingDraftContext(
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
    )


def _edited_values() -> FeeEvaluationEditedExportValues:
    return FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id="cmv-1:g1:cmr-visual:1:0",
                confirmed_group_id="cmg-1",
                confirmed_row_id="cmr-visual",
                step_token="1",
                step_index=0,
                spend_time="1.5",
                unit_price="20",
                unit_type="per sample",
                units="2",
                base_fee="5",
                discount="10%",
                testing_fee="41",
                notes="operator note",
            ),
        ),
        manual_rows=(),
        summary=FeeEvaluationEditedExportSummary(
            condition_confirmation_spend_time="0.25",
            external_cost="150",
            external_cost_note="tooling",
            lab_manpower_hourly_rate="200",
        ),
    )


class _Service:
    def __init__(self, result: FeeEvaluationPricingDraftLoadResult) -> None:
        self.result = result

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        return self.result
