from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.api.dependencies import get_confirmed_matrix_fee_draft_service
from backend.api.main import app
from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
)
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from tests.unit.test_confirmed_matrix_fee_cr_specified_current_authority import (
    _Adapter,
    _Store,
    _two_group_plan,
    _two_group_snapshot,
)


def test_fee_draft_api_uses_exact_cr_targets_for_each_group() -> None:
    _override(_service(_two_group_snapshot(), _two_group_plan()))
    try:
        response = TestClient(app).get("/api/projects/p1/confirmed-matrix/fee-draft")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    groups = response.json()["groups"]
    assert [(groups[0]["line_items"][0]["units"], groups[0]["line_items"][0]["unit_price"]),
            (groups[1]["line_items"][0]["units"], groups[1]["line_items"][0]["unit_price"])] == [
                ("40", "10"), ("36", "5")
            ]


def test_fee_draft_api_blocks_invalid_owning_quantity_without_units_or_fee() -> None:
    snapshot = _two_group_snapshot()
    invalid_group = replace(snapshot.groups[0], sample_quantity_expression="0.5")
    snapshot = replace(snapshot, groups=(invalid_group, snapshot.groups[1]))
    _override(_service(snapshot, _two_group_plan()))
    try:
        response = TestClient(app).get("/api/projects/p1/confirmed-matrix/fee-draft")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    line = response.json()["groups"][0]["line_items"][0]
    assert line["review_required"] is True
    assert line["units"] is None
    assert line["testing_fee"] is None


def test_fee_draft_api_blocks_missing_target_without_legacy_fallback() -> None:
    plan = replace(_two_group_plan(), targets=())
    _override(_service(_two_group_snapshot(), plan))
    try:
        response = TestClient(app).get("/api/projects/p1/confirmed-matrix/fee-draft")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    line = response.json()["groups"][0]["line_items"][0]
    assert line["review_required"] is True
    assert line["units"] is None
    assert line["testing_fee"] is None


def _service(snapshot, plan) -> ConfirmedMatrixFeeDraftService:
    return ConfirmedMatrixFeeDraftService(
        confirmed_store=_Store(snapshot),
        contact_measurement_adapter=_Adapter(plan),
    )


def _override(service: ConfirmedMatrixFeeDraftService) -> None:
    app.dependency_overrides[get_confirmed_matrix_fee_draft_service] = lambda: service
