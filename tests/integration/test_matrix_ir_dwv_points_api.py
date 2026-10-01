from dataclasses import asdict, replace
from decimal import Decimal
from pathlib import Path

import pytest

from backend.api.main import app
from backend.api.dependencies import get_session, get_settings, get_confirmed_matrix_fee_draft_service
from backend.application.confirmed_matrix_fee_draft_models import BuildConfirmedMatrixFeeDraftCommand
from backend.application.fee_evaluation_pricing_draft_serialization import edited_values_to_payload, edited_values_from_payload
from backend.application.matrix_fee_rebase_promotion_values import edited_values_from_fee_draft, summary_from_edited_values
from backend.application.matrix_test_points_authority import effective_matrix_point_profile
from backend.domain.matrix_contact_measurement_models import MatrixPointCategory, MatrixPointProfile
from tests.unit.test_confirmed_matrix_llcr_cr_record_projection import _snapshot
from tests.integration.test_matrix_editor_session_api import (
    _client, _seed_project, _seed_source_import, _valid_matrix_dates,
)


def _payload(seed, *, ir="1", dwv="2"):
    draft = seed["editor_draft"]
    group = {**draft["groups"][0], "sample_quantity_expression": "5+5(d)"}
    row = {**draft["rows"][0], "test_item": "Insulation Resistance", "condition": "500VDC, 2 minutes"}
    dwv_row = {**row, "draft_row_id": draft["rows"][1]["draft_row_id"] if len(draft["rows"]) > 1 else "dwv-row",
               "source_row_snapshot_id": draft["rows"][1]["source_row_snapshot_id"] if len(draft["rows"]) > 1 else None,
               "row_order": row["row_order"] + 1, "test_item": "Dielectric Withstanding Voltage",
               "condition": "1500VDC, 60 seconds"}
    return {**draft, **_valid_matrix_dates(), "groups": [group], "rows": [row, dwv_row],
            "cells": [{"draft_group_id": group["draft_group_id"], "draft_row_id": item["draft_row_id"],
                       "cell_value": str(step)} for item, step in [(row, 4), (dwv_row, 5)]],
            "source_import_id": seed["editor_source_import_id"],
            "source_snapshot_id": seed["editor_source_snapshot_id"],
            "expected_active_confirmed_matrix_id": seed["active_confirmed_matrix_id"],
            "expected_active_confirmed_revision": seed["active_confirmed_revision"],
            "point_profile": {"categories": [], "delta_r_enabled": True,
                              "ir_points_per_sample": ir, "dwv_points_per_sample": dwv,
                              "electrical_point_pairs": None}}


def test_ir_dwv_draft_points_publish_only_on_confirm_and_refresh_fee(tmp_path: Path):
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        imported = _seed_source_import("P1", tmp_path)
        assert client.post("/api/projects/P1/matrix-drafts", json={
            "source_import_id": imported, "selected_group_keys": ["g1"]}).status_code == 201
        seed = client.get("/api/projects/P1/matrix-editor/session").json()
        payload = _payload(seed)
        saved = client.put("/api/projects/P1/matrix-editor/session/draft", json=payload)
        assert saved.status_code == 200, saved.text
        reopened = client.get("/api/projects/P1/matrix-editor/session").json()
        assert reopened["editor_draft"]["point_profile"] == payload["point_profile"]
        assert reopened["active_confirmed_matrix_id"] is None
        confirmed = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
            **payload, "confirmed_by": "operator"})
        assert confirmed.status_code in (200, 201), confirmed.text
        fee = client.get("/api/projects/P1/confirmed-matrix/fee-draft")
        assert fee.status_code == 200, fee.text
        lines = fee.json()["groups"][0]["line_items"]
        assert [line["units"] for line in lines] == ["5", "10"], [line["review_reason"] for line in lines]
        seed = client.get("/api/projects/P1/matrix-editor/session").json()
        updated = _payload(seed, ir="3", dwv="1")
        updated["groups"][0]["sample_quantity_expression"] = "7"
        saved = client.put("/api/projects/P1/matrix-editor/session/draft", json=updated)
        assert saved.status_code == 200, saved.text
        assert [line["units"] for line in client.get(
            "/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]] == ["5", "10"]
        confirmed = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
            **updated, "confirmed_by": "operator",
            "expected_editor_draft_id": saved.json()["editor_draft_id"],
            "expected_saved_payload_signature": saved.json()["saved_payload_signature"]})
        assert confirmed.status_code in (200, 201), confirmed.text
        assert [line["units"] for line in client.get(
            "/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]] == ["21", "7"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture
def imported_session(tmp_path):
    client, engine, _ = _client(tmp_path)
    _seed_project("P1", tmp_path)
    imported = _seed_source_import("P1", tmp_path)
    assert client.post("/api/projects/P1/matrix-drafts", json={
        "source_import_id": imported, "selected_group_keys": ["g1"]}).status_code == 201
    try:
        yield client, client.get("/api/projects/P1/matrix-editor/session").json()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.mark.parametrize("invalid", ["0", "-1", "1.5", "unknown", "8193"])
def test_invalid_ir_point_count_is_rejected_without_publishing(imported_session, invalid):
    client, seed = imported_session
    result = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **_payload(seed, ir=invalid), "confirmed_by": "operator"})
    assert result.status_code == 422
    assert "IR test points per sample" in result.text
    assert client.get("/api/projects/P1/matrix-editor/session").json()["active_confirmed_matrix_id"] is None


def test_shared_points_generate_the_same_units_for_ir_and_dwv(imported_session):
    client, seed = imported_session
    result = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **_payload(seed, ir="2", dwv="2"), "confirmed_by": "operator"})
    assert result.status_code in (200, 201), result.text
    lines = client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]
    assert [line["units"] for line in lines] == ["10", "10"]


def test_shared_pair_text_is_retained_and_prices_only_after_matrix_confirmation(imported_session):
    client, seed = imported_session
    expression = "Odd&Even，P1&P2, P1 and S2； PE-HOUSING"
    payload = _payload(seed, ir=None, dwv=None)
    payload["point_profile"]["electrical_point_pairs"] = expression
    saved = client.put("/api/projects/P1/matrix-editor/session/draft", json=payload)
    assert saved.status_code == 200, saved.text
    reopened = client.get("/api/projects/P1/matrix-editor/session").json()
    assert reopened["editor_draft"]["point_profile"]["electrical_point_pairs"] == expression
    assert reopened["active_confirmed_matrix_id"] is None
    confirmed = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **payload, "confirmed_by": "operator",
        "expected_editor_draft_id": saved.json()["editor_draft_id"],
        "expected_saved_payload_signature": saved.json()["saved_payload_signature"]})
    assert confirmed.status_code in (200, 201), confirmed.text
    lines = client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]
    assert [line["units"] for line in lines] == ["20", "20"]
    assert client.get("/api/projects/P1/matrix-editor/session").json()["editor_draft"]["point_profile"]["electrical_point_pairs"] == expression
    seed = client.get("/api/projects/P1/matrix-editor/session").json()
    updated = _payload(seed, ir=None, dwv=None)
    updated["point_profile"]["electrical_point_pairs"] = "P1&P2、P1 and S2；PE-HOUSING"
    updated["groups"][0]["sample_quantity_expression"] = "7+7"
    saved = client.put("/api/projects/P1/matrix-editor/session/draft", json=updated)
    assert saved.status_code == 200, saved.text
    assert [line["units"] for line in client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]] == ["20", "20"]
    confirmed = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **updated, "confirmed_by": "operator",
        "expected_editor_draft_id": saved.json()["editor_draft_id"],
        "expected_saved_payload_signature": saved.json()["saved_payload_signature"]})
    assert confirmed.status_code in (200, 201), confirmed.text
    assert [line["units"] for line in client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]] == ["21", "21"]
    seed = client.get("/api/projects/P1/matrix-editor/session").json()
    cleared = _payload(seed, ir="9", dwv="9")
    cleared["point_profile"]["electrical_point_pairs"] = ""
    saved = client.put("/api/projects/P1/matrix-editor/session/draft", json=cleared)
    assert saved.status_code == 200, saved.text
    confirmed = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **cleared, "confirmed_by": "operator",
        "expected_editor_draft_id": saved.json()["editor_draft_id"],
        "expected_saved_payload_signature": saved.json()["saved_payload_signature"]})
    assert confirmed.status_code in (200, 201), confirmed.text
    lines = client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]
    assert all(line["units"] is None and line["review_required"] for line in lines)


@pytest.mark.parametrize("pairs,units", [
    ("Odd&Even，P1&P2, P1 and S2；PE-HOUSING、P3&P4;P5&P6", "30"),
    (" , P1&P2；；P1 and S2、 ", "10"),
    ("PE-HOUSING", "5"),
    ("Odd&Even\nPE-HOUSING", "10"),
])
def test_pair_separators_do_not_split_the_endpoints(imported_session, pairs, units):
    client, seed = imported_session
    payload = _payload(seed, ir=None, dwv=None)
    payload["point_profile"]["electrical_point_pairs"] = pairs
    confirmed = client.post("/api/projects/P1/matrix-editor/session/confirm", json={**payload, "confirmed_by": "operator"})
    assert confirmed.status_code in (200, 201), confirmed.text
    lines = client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]
    assert [line["units"] for line in lines] == [units, units]


@pytest.mark.parametrize("pairs", ["， , ;；、", "P1&P2," * 8193, "A" * 65537],
                         ids=["separators-only", "too-many-pairs", "too-long"])
def test_invalid_pair_list_is_rejected_before_publishing(imported_session, pairs):
    client, seed = imported_session
    payload = _payload(seed, ir=None, dwv=None)
    payload["point_profile"]["electrical_point_pairs"] = pairs
    result = client.post("/api/projects/P1/matrix-editor/session/confirm", json={**payload, "confirmed_by": "operator"})
    assert result.status_code == 422
    assert "measurement pairs" in result.text
    assert client.get("/api/projects/P1/matrix-editor/session").json()["active_confirmed_matrix_id"] is None


def test_added_steps_inherit_points_and_clearing_cannot_reuse_old_counts(imported_session):
    client, seed = imported_session
    initial = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **_payload(seed), "confirmed_by": "operator"})
    assert initial.status_code in (200, 201), initial.text
    seed = client.get("/api/projects/P1/matrix-editor/session").json()
    updated = _payload(seed, ir="", dwv="3")
    updated["cells"][1]["cell_value"] = "5,12"  # New DWV step inherits 3 points.
    saved = client.put("/api/projects/P1/matrix-editor/session/draft", json=updated)
    assert saved.status_code == 200, saved.text
    result = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **updated, "confirmed_by": "operator",
        "expected_editor_draft_id": saved.json()["editor_draft_id"],
        "expected_saved_payload_signature": saved.json()["saved_payload_signature"]})
    assert result.status_code in (200, 201), result.text
    snapshot = client.get("/api/projects/P1/confirmed-matrix/active-snapshot").json()
    assert sorted(cell["cell_value"] for cell in snapshot["cells"]) == ["4", "5,12"]
    lines = client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"]
    assert lines[0]["units"] is None
    assert lines[0]["review_required"]
    assert lines[1]["units"] == "15"


@pytest.mark.parametrize("condition", ["500VDC", "500VDC, 30 seconds"])
def test_known_ir_points_populate_units_even_when_duration_price_needs_review(imported_session, condition):
    client, seed = imported_session
    payload = _payload(seed)
    payload["rows"][0]["condition"] = condition
    result = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **payload, "confirmed_by": "operator"})
    assert result.status_code in (200, 201), result.text
    line = client.get("/api/projects/P1/confirmed-matrix/fee-draft").json()["groups"][0]["line_items"][0]
    assert line["units"] == "5"
    assert line["unit_price"] is None
    assert line["review_required"]


def test_electrical_settings_leave_llcr_cr_projection_and_fingerprint_unchanged():
    snapshot = _snapshot()
    profile = MatrixPointProfile((MatrixPointCategory("HP", "1-4", True),))
    original = effective_matrix_point_profile(replace(snapshot, version=replace(snapshot.version, point_profile=profile)))
    updated = effective_matrix_point_profile(replace(snapshot, version=replace(
        snapshot.version, point_profile=replace(profile, ir_points_per_sample="1", dwv_points_per_sample="2"))))
    assert original == updated
    pair_profile = replace(profile, electrical_point_pairs="Odd&Even，PE-HOUSING")
    assert original == effective_matrix_point_profile(replace(snapshot, version=replace(snapshot.version, point_profile=pair_profile)))


def test_confirmed_electrical_points_rebase_fee_editor_units_without_losing_prices(imported_session):
    client, seed = imported_session
    result = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **_payload(seed), "confirmed_by": "operator"})
    assert result.status_code in (200, 201), result.text
    session_generator = app.dependency_overrides[get_session]()
    session = next(session_generator)
    try:
        settings = app.dependency_overrides[get_settings]()
        draft = get_confirmed_matrix_fee_draft_service(session, settings).build_draft(
            BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))
        values = edited_values_from_fee_draft(draft)
    finally:
        session_generator.close()
    values = replace(values, summary=replace(values.summary,
        condition_confirmation_spend_time="0", external_cost="0", lab_manpower_hourly_rate="200"), rows=tuple(replace(
        row, unit_price="99", testing_fee=str(Decimal("99") * Decimal(row.units)),
        notes="Agreed price") for row in values.rows))
    current_fee = client.get("/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft").json()
    saved = client.put("/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft", json={
        **edited_values_to_payload(values),
        "expected_pricing_draft_edit_id": current_fee["saved_draft_edit_id"],
        "expected_generation": current_fee["saved_generation"],
        "expected_payload_fingerprint": current_fee["saved_payload_fingerprint"],
        "expected_updated_at": current_fee["saved_updated_at"],
    })
    assert saved.status_code == 200, saved.text
    saved_fee = saved.json()
    confirmation = client.post("/api/projects/P1/confirmed-fee/versions", json={
        "confirmed_by": "operator", "expected_pricing_draft_edit_id": saved_fee["saved_draft_edit_id"],
        "expected_generation": saved_fee["saved_generation"],
        "expected_payload_fingerprint": saved_fee["saved_payload_fingerprint"],
        "expected_validation_token": saved_fee["saved_validation_token"],
        "summary": asdict(summary_from_edited_values(edited_values_from_payload(saved_fee["payload"]))),
    })
    assert confirmation.status_code == 200, confirmation.text
    seed = client.get("/api/projects/P1/matrix-editor/session").json()
    updated = _payload(seed, ir="3", dwv="1")
    updated["groups"][0]["sample_quantity_expression"] = "7"
    saved_matrix = client.put("/api/projects/P1/matrix-editor/session/draft", json=updated)
    assert saved_matrix.status_code == 200, saved_matrix.text
    result = client.post("/api/projects/P1/matrix-editor/session/confirm", json={
        **updated, "confirmed_by": "operator",
        "expected_editor_draft_id": saved_matrix.json()["editor_draft_id"],
        "expected_saved_payload_signature": saved_matrix.json()["saved_payload_signature"]})
    assert result.status_code in (200, 201), result.text
    fee_editor = client.get("/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft")
    assert fee_editor.status_code == 200, fee_editor.text
    assert fee_editor.json()["payload"] is not None, fee_editor.text
    rows = fee_editor.json()["payload"]["rows"]
    assert {row["step_token"]: row["units"] for row in rows} == {"4": "21", "5": "7"}
    assert all(row["unit_price"] == "99" and row["notes"] == "Agreed price" for row in rows), fee_editor.text
