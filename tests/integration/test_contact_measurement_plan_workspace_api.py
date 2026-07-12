"""Typed read-only workspace API coverage for TASK_361C."""

from fastapi.testclient import TestClient

from backend.api.dependencies import get_contact_measurement_plan_workspace_read_service
from backend.api.main import app


def test_workspace_endpoint_returns_operator_context_from_read_service() -> None:
    app.dependency_overrides[get_contact_measurement_plan_workspace_read_service] = (
        lambda: _WorkspaceReadService()
    )
    try:
        with TestClient(app) as client:
            response = client.get("/api/projects/P1/contact-measurement-plan/workspace")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["revision"]["revision_sequence"] == 2
    assert payload["matrix_binding"]["current_matrix_revision"] == 4
    assert payload["targets"][0]["group_label"] == "Qualification group"
    assert payload["impacts"][0]["candidate"]["test_item"] == "LLCR"


class _WorkspaceReadService:
    def get_workspace(self, project_id: str) -> dict[str, object]:
        assert project_id == "P1"
        return {
            "status": "needs_review",
            "project_id": project_id,
            "active_confirmed_revision_id": "revision-confirmed",
            "editable_revision_id": "revision-draft",
            "editable_revision_state": "needs_review",
            "editable_revision_fingerprint": "fingerprint-2",
            "revision": {
                "revision_id": "revision-draft",
                "revision_sequence": 2,
                "state": "needs_review",
                "fingerprint": "fingerprint-2",
            },
            "matrix_binding": {
                "base_confirmed_matrix_id": "cmv-3",
                "base_matrix_revision": 3,
                "current_confirmed_matrix_id": "cmv-4",
                "current_matrix_revision": 4,
                "matrix_binding_fingerprint": "cmv-4:4",
            },
            "targets": [
                {
                    "stable_target_key": "cmp-target:v1|group:cg-1|row:cr-1|step:1|suffix:",
                    "group_label": "Qualification group",
                    "test_item": "LLCR",
                    "contact_kind": "llcr",
                    "step_sequence": 1,
                    "step_suffix_note": "",
                    "sample_quantity_expression": "2",
                    "eligible": True,
                    "included": True,
                    "exclusion_reason": None,
                    "is_override": False,
                    "coverage_state": "included",
                    "readings_per_sample": 2,
                    "target_review_state": "unchanged",
                    "target_review_reason": None,
                    "families": [],
                }
            ],
            "impacts": [
                {
                    "impact_subject_key": "cmp-candidate:v1|matrix:cmv-4|group:cg-1|row:cr-1|step:1|suffix:",
                    "category": "structural_review_required",
                    "severity": "review_required",
                    "resolution_state": "open",
                    "reason": "Review current target.",
                    "candidate": {
                        "group_label": "Qualification group",
                        "test_item": "LLCR",
                        "step_sequence": 1,
                        "step_suffix_note": "",
                    },
                }
            ],
            "summary": {
                "included_target_count": 1,
                "total_target_count": 1,
                "needs_review_count": 1,
                "readings_by_kind": {"llcr": 2, "cr_specified_current": None},
            },
            "diagnostics": ["Contact measurement changes require review."],
        }
