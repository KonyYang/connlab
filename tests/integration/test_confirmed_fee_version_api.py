from __future__ import annotations

from fastapi.testclient import TestClient

from backend.api.dependencies import get_confirmed_fee_version_service
from backend.api.main import app
from backend.application.confirmed_fee_version_service import (
    ConfirmFeeVersionCommand,
    ConfirmedFeePricingDraftChangedError,
    ConfirmedFeePricingDraftMissingError,
    ConfirmedFeeVersionConflictError,
    ConfirmedFeeVersionReadResult,
)
from backend.application.fee_evaluation_pricing_draft_persistence_service import (
    FeeEvaluationPricingDraftContext,
)
from backend.domain.confirmed_fee import ConfirmedFeeSummary, ConfirmedFeeVersion


def test_confirmed_fee_get_missing_returns_current_context() -> None:
    service = _Service(_missing_result())
    app.dependency_overrides[get_confirmed_fee_version_service] = lambda: service
    try:
        response = TestClient(app).get("/api/projects/P1/confirmed-fee/latest")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "missing",
        "current_confirmed_matrix_id": "cmv-1",
        "current_confirmed_revision": 1,
        "current_fee_rule_version_id": "fee_rules_v2026_06_03",
        "fee_review_required_count": 0,
        "confirmed_fee": None,
    }


def test_confirmed_fee_post_creates_version_without_client_confirmed_at() -> None:
    service = _Service(_missing_result())
    app.dependency_overrides[get_confirmed_fee_version_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-fee/versions",
            json={
                "confirmed_by": "Lab User",
                "expected_pricing_draft_edit_id": "fed-1",
                "summary": _summary_payload(testing_fee_total="41"),
                "confirmation_note": "ready",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "current"
    assert body["confirmed_fee"]["confirmed_fee_revision"] == 1
    assert body["confirmed_fee"]["pricing_draft_edit_id"] == "fed-1"
    assert body["confirmed_fee"]["summary"]["testing_fee_total"] == "41"
    assert body["confirmed_fee"]["confirmed_at"] == "2026-06-10T09:00:00+00:00"
    assert service.commands[0].expected_pricing_draft_edit_id == "fed-1"


def test_confirmed_fee_post_rejects_expected_draft_id_mismatch() -> None:
    app.dependency_overrides[get_confirmed_fee_version_service] = lambda: _FailingService(
        ConfirmedFeePricingDraftChangedError("Fee Evaluation draft changed.")
    )
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-fee/versions",
            json={
                "confirmed_by": "Lab User",
                "expected_pricing_draft_edit_id": "old-fed",
                "summary": _summary_payload(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "changed" in response.json()["detail"].lower()


def test_confirmed_fee_post_maps_concurrent_lineage_conflict_to_typed_409() -> None:
    app.dependency_overrides[get_confirmed_fee_version_service] = lambda: _FailingService(
        ConfirmedFeeVersionConflictError(
            "Fee Evaluation confirmation changed concurrently. Reload and confirm again."
        )
    )
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-fee/versions",
            json={
                "confirmed_by": "Lab User",
                "expected_pricing_draft_edit_id": "fed-1",
                "summary": _summary_payload(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "concurrently" in response.json()["detail"].lower()


def test_confirmed_fee_post_rejects_missing_saved_pricing_draft() -> None:
    app.dependency_overrides[get_confirmed_fee_version_service] = lambda: _FailingService(
        ConfirmedFeePricingDraftMissingError("Save Fee Evaluation pricing before confirming.")
    )
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-fee/versions",
            json={
                "confirmed_by": "Lab User",
                "expected_pricing_draft_edit_id": "fed-1",
                "summary": _summary_payload(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "save fee evaluation" in response.json()["detail"].lower()


def test_confirmed_fee_post_rejects_blank_confirmed_by() -> None:
    service = _Service(_missing_result())
    app.dependency_overrides[get_confirmed_fee_version_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-fee/versions",
            json={
                "confirmed_by": "   ",
                "expected_pricing_draft_edit_id": "fed-1",
                "summary": _summary_payload(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "confirmed_by" in response.json()["detail"]


def _summary_payload(*, testing_fee_total: str = "41") -> dict[str, str]:
    return {
        "testing_fee_total": testing_fee_total,
        "working_hours": "1.5",
        "lab_manpower_cost": "300",
        "external_cost": "150",
        "grand_cost": "191",
    }


def _missing_result() -> ConfirmedFeeVersionReadResult:
    return ConfirmedFeeVersionReadResult(
        status="missing",
        current_context=_context(),
        latest_confirmed_fee=None,
    )


def _current_result(version: ConfirmedFeeVersion) -> ConfirmedFeeVersionReadResult:
    return ConfirmedFeeVersionReadResult(
        status="current",
        current_context=_context(),
        latest_confirmed_fee=version,
    )


def _context() -> FeeEvaluationPricingDraftContext:
    return FeeEvaluationPricingDraftContext(
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
    )


def _version() -> ConfirmedFeeVersion:
    return ConfirmedFeeVersion(
        confirmed_fee_id="cfv-1",
        project_id="P1",
        confirmed_fee_revision=1,
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        pricing_draft_edit_id="fed-1",
        pricing_effective_from=None,
        summary=ConfirmedFeeSummary(**_summary_payload()),
        pricing_snapshot_json='{"rows":[]}',
        confirmed_by="Lab User",
        confirmed_at="2026-06-10T09:00:00+00:00",
        confirmation_note="ready",
    )


class _Service:
    def __init__(self, result: ConfirmedFeeVersionReadResult) -> None:
        self.result = result
        self.commands: list[ConfirmFeeVersionCommand] = []

    def get_latest(self, project_id: str) -> ConfirmedFeeVersionReadResult:
        return self.result

    def confirm(self, command: ConfirmFeeVersionCommand) -> ConfirmedFeeVersion:
        self.commands.append(command)
        version = _version()
        self.result = _current_result(version)
        return version


class _FailingService:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def get_latest(self, project_id: str) -> ConfirmedFeeVersionReadResult:
        raise self.exc

    def confirm(self, command: ConfirmFeeVersionCommand) -> ConfirmedFeeVersion:
        raise self.exc
