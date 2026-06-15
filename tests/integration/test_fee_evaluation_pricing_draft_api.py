from __future__ import annotations

from fastapi.testclient import TestClient

from backend.api.dependencies import get_fee_evaluation_pricing_draft_service
from backend.api.main import app
from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    ConfirmedMatrixFeeTemplateBasicFillNotFoundError,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    DiscardFeeEvaluationPricingDraftCommand,
    FeeEvaluationPricingDraftConflictError,
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftDiscardResult,
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
    SaveFeeEvaluationPricingDraftCommand,
)


def test_pricing_draft_get_missing_returns_current_context() -> None:
    service = _Service(_missing_result())
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    try:
        response = TestClient(app).get(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "missing",
        "current_confirmed_matrix_id": "cmv-1",
        "current_confirmed_revision": 1,
        "current_fee_rule_version_id": "fee_rules_v2026_06_03",
        "saved_confirmed_matrix_id": None,
        "saved_confirmed_revision": None,
        "saved_fee_rule_version_id": None,
        "saved_draft_edit_id": None,
        "saved_updated_at": None,
        "payload": None,
    }


def test_pricing_draft_put_saves_payload_and_get_can_return_current_payload() -> None:
    service = _Service(_missing_result())
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    payload = _payload()
    try:
        save_response = TestClient(app).put(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json=payload,
        )
        get_response = TestClient(app).get(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
        )
    finally:
        app.dependency_overrides.clear()

    assert save_response.status_code == 200
    assert save_response.json()["status"] == "current"
    assert save_response.json()["saved_draft_edit_id"] == "fed-1"
    assert save_response.json()["payload"]["rows"][0]["notes"] == "operator note"
    assert save_response.json()["payload"]["manual_rows"][0] == {
        "row_kind": "sample_preparation",
        "confirmed_group_id": "cmg-1",
        "group_key": "g1",
        "group_label": "Group 1",
        "spend_time": "0.25",
        "unit_price": "15",
        "unit_type": "per sample",
        "units": "5",
        "base_fee": "2",
        "discount": "5%",
        "testing_fee": "73.25",
        "notes": "sample prep note",
    }
    assert service.commands[0].project_id == "P1"
    assert service.commands[0].edited_values.rows[0].unit_type == "per sample"
    assert service.commands[0].edited_values.manual_rows[0].row_kind == (
        "sample_preparation"
    )
    assert service.commands[0].edited_values.manual_rows[0].confirmed_group_id == "cmg-1"
    assert get_response.status_code == 200
    assert get_response.json()["saved_draft_edit_id"] == "fed-1"
    assert get_response.json()["payload"]["summary"]["external_cost_note"] == "tooling"


def test_pricing_draft_get_normalizes_historical_blank_unit_type() -> None:
    values = _edited_values()
    bad_values = FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id=values.rows[0].source_line_id,
                confirmed_group_id=values.rows[0].confirmed_group_id,
                confirmed_row_id=values.rows[0].confirmed_row_id,
                step_token=values.rows[0].step_token,
                step_index=values.rows[0].step_index,
                spend_time=values.rows[0].spend_time,
                unit_price=values.rows[0].unit_price,
                unit_type="",
                units=values.rows[0].units,
                base_fee=values.rows[0].base_fee,
                discount=values.rows[0].discount,
                testing_fee=values.rows[0].testing_fee,
                notes="historical note",
            ),
        ),
        summary=values.summary,
        manual_rows=values.manual_rows,
    )
    service = _Service(_current_result(bad_values))
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    try:
        response = TestClient(app).get(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    row = response.json()["payload"]["rows"][0]
    assert row["unit_type"] == "Pending"
    assert row["notes"] == "historical note"


def test_pricing_draft_get_normalizes_historical_pending_numeric_fields() -> None:
    values = _edited_values()
    bad_values = FeeEvaluationEditedExportValues(
        rows=(
            FeeEvaluationEditedExportRow(
                source_line_id=values.rows[0].source_line_id,
                confirmed_group_id=values.rows[0].confirmed_group_id,
                confirmed_row_id=values.rows[0].confirmed_row_id,
                step_token=values.rows[0].step_token,
                step_index=values.rows[0].step_index,
                spend_time="Pending",
                unit_price="Pending",
                unit_type=values.rows[0].unit_type,
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
    service = _Service(_current_result(bad_values))
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    try:
        response = TestClient(app).get(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()["payload"]
    assert payload["rows"][0] == {
        "source_line_id": "cmv-1:g1:cmr-visual:1:0",
        "confirmed_group_id": "cmg-1",
        "confirmed_row_id": "cmr-visual",
        "step_token": "1",
        "step_index": 0,
        "spend_time": "0",
        "unit_price": "0",
        "unit_type": "per sample",
        "units": "1",
        "base_fee": "0",
        "discount": "0%",
        "testing_fee": "0",
        "notes": "historical numeric note",
    }
    assert payload["summary"] == {
        "condition_confirmation_spend_time": "0",
        "external_cost": "0",
        "external_cost_note": "tooling",
        "lab_manpower_hourly_rate": "200",
    }


def test_pricing_draft_get_stale_does_not_return_payload() -> None:
    result = FeeEvaluationPricingDraftLoadResult(
        status="stale",
        current_context=_context(confirmed_revision=2),
        saved_snapshot=_snapshot(),
    )
    service = _Service(result)
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    try:
        response = TestClient(app).get(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "stale"
    assert body["current_confirmed_revision"] == 2
    assert body["saved_confirmed_revision"] == 1
    assert body["payload"] is None


def test_pricing_draft_delete_discards_current_payload() -> None:
    service = _Service(_current_result(_edited_values()))
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    try:
        response = TestClient(app).request(
            "DELETE",
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json={
                "expected_pricing_draft_edit_id": "fed-1",
                "expected_confirmed_matrix_id": "cmv-1",
                "expected_confirmed_revision": 1,
                "expected_fee_rule_version_id": "fee_rules_v2026_06_03",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "discarded": True,
        "current_confirmed_matrix_id": "cmv-1",
        "current_confirmed_revision": 1,
        "current_fee_rule_version_id": "fee_rules_v2026_06_03",
    }
    assert service.discard_commands == [
        DiscardFeeEvaluationPricingDraftCommand(
            project_id="P1",
            expected_pricing_draft_edit_id="fed-1",
            expected_confirmed_matrix_id="cmv-1",
            expected_confirmed_revision=1,
            expected_fee_rule_version_id="fee_rules_v2026_06_03",
        )
    ]


def test_pricing_draft_delete_maps_conflict_to_409() -> None:
    app.dependency_overrides[
        get_fee_evaluation_pricing_draft_service
    ] = lambda: _FailingService(
        FeeEvaluationPricingDraftConflictError("Pricing draft changed before discard.")
    )
    try:
        response = TestClient(app).request(
            "DELETE",
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json={"expected_pricing_draft_edit_id": "fed-other"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == {
        "code": "fee_pricing_draft_conflict",
        "message": "Pricing draft changed before discard.",
    }


def test_pricing_draft_put_rejects_duplicate_row_identity() -> None:
    service = _Service(_missing_result())
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    row = _payload()["rows"][0]
    try:
        response = TestClient(app).put(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json={**_payload(), "rows": [row, row]},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_pricing_draft_get_maps_missing_matrix_to_404() -> None:
    app.dependency_overrides[
        get_fee_evaluation_pricing_draft_service
    ] = lambda: _FailingService(
        ConfirmedMatrixFeeTemplateBasicFillNotFoundError("Active confirmed matrix not found.")
    )
    try:
        response = TestClient(app).get(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "confirmed matrix" in response.json()["detail"].lower()


def _payload() -> dict[str, object]:
    return {
        "rows": [
            {
                "source_line_id": "cmv-1:g1:cmr-visual:1:0",
                "confirmed_group_id": "cmg-1",
                "confirmed_row_id": "cmr-visual",
                "step_token": "1",
                "step_index": 0,
                "spend_time": "1.5",
                "unit_price": "20",
                "unit_type": "per sample",
                "units": "2",
                "base_fee": "5",
                "discount": "10%",
                "testing_fee": "41",
                "notes": "operator note",
            }
        ],
        "manual_rows": [
            {
                "row_kind": "sample_preparation",
                "confirmed_group_id": "cmg-1",
                "group_key": "g1",
                "group_label": "Group 1",
                "spend_time": "0.25",
                "unit_price": "15",
                "unit_type": "per sample",
                "units": "5",
                "base_fee": "2",
                "discount": "5%",
                "testing_fee": "73.25",
                "notes": "sample prep note",
            },
            {
                "row_kind": "report_preparation",
                "spend_time": "0.5",
                "unit_price": "100",
                "unit_type": "per report",
                "units": "1",
                "base_fee": "0",
                "discount": "0%",
                "testing_fee": "100",
                "notes": "",
            }
        ],
        "summary": {
            "condition_confirmation_spend_time": "0.25",
            "external_cost": "150",
            "external_cost_note": "tooling",
            "lab_manpower_hourly_rate": "200",
        },
    }


def _missing_result() -> FeeEvaluationPricingDraftLoadResult:
    return FeeEvaluationPricingDraftLoadResult(
        status="missing",
        current_context=_context(),
        saved_snapshot=None,
    )


def _current_result(values: FeeEvaluationEditedExportValues) -> FeeEvaluationPricingDraftLoadResult:
    return FeeEvaluationPricingDraftLoadResult(
        status="current",
        current_context=_context(),
        saved_snapshot=_snapshot(values=values),
    )


def _context(*, confirmed_revision: int = 1) -> FeeEvaluationPricingDraftContext:
    return FeeEvaluationPricingDraftContext(
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=confirmed_revision,
        fee_rule_version_id="fee_rules_v2026_06_03",
    )


def _snapshot(
    *,
    values: FeeEvaluationEditedExportValues | None = None,
) -> FeeEvaluationPricingDraftSnapshot:
    return FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="fed-1",
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        edited_values=values or _edited_values(),
        created_at="2026-06-09T09:00:00+00:00",
        updated_at="2026-06-09T09:10:00+00:00",
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
        self.commands: list[SaveFeeEvaluationPricingDraftCommand] = []
        self.discard_commands: list[DiscardFeeEvaluationPricingDraftCommand] = []

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        return self.result

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        self.commands.append(command)
        self.result = _current_result(command.edited_values)
        return self.result

    def discard(
        self, command: DiscardFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftDiscardResult:
        self.discard_commands.append(command)
        self.result = _missing_result()
        return FeeEvaluationPricingDraftDiscardResult(
            discarded=True,
            current_context=_context(),
        )


class _FailingService:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        raise self.exc

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        raise self.exc

    def discard(
        self, command: DiscardFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftDiscardResult:
        raise self.exc
