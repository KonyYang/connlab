from __future__ import annotations

from pathlib import Path

from backend.application.project_basic_information_service import (
    ProjectBasicInformationRecord,
)
from backend.infrastructure.storage.repositories import ProjectBasicInformationRepository
from tests.integration.test_confirmed_matrix_authority_api import (
    _client,
    _seed_project,
    _seed_source_import,
)


def test_matrix_step_quantity_api_imports_defaults_and_saves_override(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        with session_factory() as session:
            ProjectBasicInformationRepository(session).create_confirmed(
                ProjectBasicInformationRecord(
                    record_id="bi-qty",
                    project_id="P1",
                    status="confirmed",
                    version=1,
                    values={
                        "test_points_per_sample": "3",
                        "readings_per_point": "2",
                        "contact_points_per_sample": "4",
                    },
                    source_signature="{}",
                    created_at="2026-07-08T08:00:00+00:00",
                    updated_at="2026-07-08T08:00:00+00:00",
                    confirmed_at="2026-07-08T08:00:00+00:00",
                    confirmed_by="operator",
                )
            )
            session.commit()

        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        assert created.status_code == 201
        draft = created.json()
        draft_id = draft["record"]["project_matrix_draft_id"]

        defaults = client.get(f"/api/projects/P1/matrix-drafts/{draft_id}/step-quantities")
        assert defaults.status_code == 200
        default_item = defaults.json()["items"][0]
        assert default_item["test_points_per_sample"] == "3"
        assert default_item["readings_per_point"] == "2"
        assert default_item["total_readings"] == "6"
        assert default_item["source"] == "basic_information_confirmed"

        saved = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}/step-quantities",
            json={
                "items": [
                    {
                        "draft_group_id": default_item["draft_group_id"],
                        "draft_row_id": default_item["draft_row_id"],
                        "step_sequence": default_item["step_sequence"],
                        "step_suffix_note": default_item["step_suffix_note"],
                        "raw_token": default_item["raw_token"],
                        "test_points_per_sample": "5",
                        "readings_per_point": "4",
                        "contact_points_per_sample": "2",
                        "source": "matrix_step_override",
                        "review_required": False,
                        "review_reason": None,
                    }
                ]
            },
        )
        assert saved.status_code == 200
        saved_item = saved.json()["items"][0]
        assert saved_item["test_points_per_sample"] == "5"
        assert saved_item["readings_per_point"] == "4"
        assert saved_item["total_readings"] == "20"
        assert saved_item["source"] == "matrix_step_override"
    finally:
        engine.dispose()


def test_matrix_step_quantity_api_rejects_duplicate_no_suffix_payload(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]

        defaults = client.get(f"/api/projects/P1/matrix-drafts/{draft_id}/step-quantities")
        assert defaults.status_code == 200
        default_item = defaults.json()["items"][0]
        payload_item = {
            "draft_group_id": default_item["draft_group_id"],
            "draft_row_id": default_item["draft_row_id"],
            "step_sequence": default_item["step_sequence"],
            "step_suffix_note": default_item["step_suffix_note"],
            "raw_token": default_item["raw_token"],
            "test_points_per_sample": "5",
            "readings_per_point": "4",
            "contact_points_per_sample": "2",
            "source": "matrix_step_override",
            "review_required": False,
            "review_reason": None,
        }

        saved = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}/step-quantities",
            json={"items": [payload_item, payload_item]},
        )

        assert saved.status_code == 422
        assert "Duplicate Step quantity" in saved.json()["detail"]
    finally:
        engine.dispose()
