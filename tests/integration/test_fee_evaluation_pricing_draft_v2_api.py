"""TASK_361L V2 pricing-draft API contract regressions."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.api.dependencies import get_fee_evaluation_pricing_draft_service
from backend.api.main import app
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportRow,
    FeeEvaluationEditedExportSummary,
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftConflictError,
    FeeEvaluationPricingDraftContext,
    FeeEvaluationPricingDraftLoadResult,
    FeeEvaluationPricingDraftSnapshot,
    SaveFeeEvaluationPricingDraftCommand,
)
from backend.application.project_lifecycle_write_guard import ProjectLifecycleReadonlyError
from backend.domain import ProjectLifecycleState


def test_pricing_draft_get_returns_v2_and_review_payloads() -> None:
    values = _edited_values()
    snapshot = FeeEvaluationPricingDraftSnapshot(
        draft_edit_id="fed-v2",
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        edited_values=values,
        created_at="2026-07-15T00:00:00+00:00",
        updated_at="2026-07-15T00:00:01+00:00",
        generation=2,
        payload_fingerprint="payload-fingerprint",
        source_context_fingerprint="source-fingerprint",
        validation_token="validation-token",
    )
    for status in ("current_v2", "rebase_required"):
        app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = (
            lambda: _Service(FeeEvaluationPricingDraftLoadResult(status, _context(), snapshot))
        )
        try:
            response = TestClient(app).get(
                "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json()["status"] == status
        assert (
            response.json()["payload"]["rows"][0]["source_line_id"]
            == values.rows[0].source_line_id
        )


def test_pricing_draft_put_forwards_expected_context_tokens() -> None:
    service = _Service(_missing_result())
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    payload = {
        **_payload(),
        "expected_confirmed_matrix_id": "cmv-1",
        "expected_confirmed_revision": 1,
        "expected_fee_rule_version_id": "fee_rules_v2026_06_03",
    }
    try:
        response = TestClient(app).put(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json=payload,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.commands[0].expected_confirmed_matrix_id == "cmv-1"
    assert service.commands[0].expected_confirmed_revision == 1
    assert service.commands[0].expected_fee_rule_version_id == "fee_rules_v2026_06_03"


def test_pricing_draft_put_maps_conflict_to_409() -> None:
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: _FailingService(
        FeeEvaluationPricingDraftConflictError(
            "Pricing draft Matrix context changed before save."
        )
    )
    try:
        response = TestClient(app).put(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json={**_payload(), "expected_confirmed_matrix_id": "cmv-old"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == {
        "code": "fee_pricing_draft_conflict",
        "message": "Pricing draft Matrix context changed before save.",
    }


def test_pricing_draft_put_stopped_returns_structured_409_without_mutation() -> None:
    service = _ReadonlyService()
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    try:
        response = TestClient(app, raise_server_exceptions=False).put(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json=_payload(),
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["project_id"] == "P1"
    assert detail["lifecycle_state"] == "stopped"
    assert detail["closure_type"] is None
    assert detail["close_reason_category"] is None
    assert detail["close_reason_label"] is None
    assert detail["message"] == "This project is stopped. Activate it before making changes."
    assert detail["allowed_actions"] == ["activate"]
    assert service.save_commands == []


def _payload() -> dict[str, object]:
    return {
        "rows": [],
        "manual_rows": [],
        "summary": {
            "condition_confirmation_spend_time": "0",
            "external_cost": "0",
            "external_cost_note": "",
            "lab_manpower_hourly_rate": "200",
        },
    }


def _missing_result() -> FeeEvaluationPricingDraftLoadResult:
    return FeeEvaluationPricingDraftLoadResult(
        status="missing",
        current_context=_context(),
        saved_snapshot=None,
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
            condition_confirmation_spend_time="0",
            external_cost="0",
            external_cost_note="",
            lab_manpower_hourly_rate="200",
        ),
    )


class _Service:
    def __init__(self, result: FeeEvaluationPricingDraftLoadResult) -> None:
        self.result = result
        self.commands: list[SaveFeeEvaluationPricingDraftCommand] = []

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        return self.result

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        self.commands.append(command)
        return self.result


class _FailingService:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
        raise self.exc

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        raise self.exc


class _ReadonlyService:
    def __init__(self) -> None:
        self.save_commands: list[SaveFeeEvaluationPricingDraftCommand] = []

    def save(
        self, command: SaveFeeEvaluationPricingDraftCommand
    ) -> FeeEvaluationPricingDraftLoadResult:
        raise ProjectLifecycleReadonlyError(
            project_id=command.project_id,
            lifecycle_state=ProjectLifecycleState.STOPPED,
            closure_type=None,
            message="This project is stopped. Activate it before making changes.",
            allowed_actions=("activate",),
        )
