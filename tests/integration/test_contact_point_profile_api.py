from fastapi.testclient import TestClient

from backend.api.dependencies import (
    get_contact_point_profile_lifecycle_service,
    get_contact_point_profile_read_service,
)
from backend.api.main import app
from backend.application.contact_point_profile_lifecycle_service import ContactPointProfileLifecycleError


def test_point_profile_workspace_and_summary_are_project_only_typed_reads() -> None:
    app.dependency_overrides[get_contact_point_profile_read_service] = lambda: _ReadService()
    try:
        with TestClient(app) as client:
            workspace = client.get("/api/projects/P1/contact-point-profile/workspace")
            summary = client.get("/api/projects/P1/contact-point-profile/summary")
    finally:
        app.dependency_overrides.clear()

    assert workspace.status_code == 200
    assert workspace.json()["editable_revision"]["points_per_sample"] == 33
    assert "targets" not in workspace.json()
    assert summary.json()["confirmed_revision"] is not None
    assert summary.json()["has_unconfirmed_draft"] is True


def test_point_profile_draft_write_returns_typed_stale_conflict() -> None:
    app.dependency_overrides[get_contact_point_profile_lifecycle_service] = lambda: _StaleLifecycle()
    try:
        with TestClient(app) as client:
            response = client.put(
                "/api/projects/P1/contact-point-profile/draft",
                json={
                    "actor": "operator",
                    "expected_revision_id": "revision-1",
                    "expected_revision_fingerprint": "old",
                    "categories": [],
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "contact_point_profile_stale"


class _ReadService:
    def get_workspace(self, project_id: str):
        return {
            "status": "draft", "project_id": project_id,
            "editable_revision": _revision("draft", 2),
            "confirmed_revision": _revision("confirmed", 1),
            "has_unconfirmed_draft": True, "legacy_uniform_suggestion": None,
            "diagnostics": [],
        }

    def get_summary(self, project_id: str):
        return {
            "status": "confirmed", "project_id": project_id,
            "confirmed_revision": _revision("confirmed", 1),
            "points_per_sample": 33, "has_unconfirmed_draft": True, "diagnostics": [],
        }


class _StaleLifecycle:
    def save_draft(self, *args, **kwargs):
        raise ContactPointProfileLifecycleError("Point Profile draft is stale.")


def _revision(state: str, sequence: int):
    return {
        "revision_id": f"revision-{sequence}", "revision_sequence": sequence,
        "state": state, "fingerprint": "fingerprint", "created_at": "2026-07-14T00:00:00Z",
        "confirmed_at": "2026-07-14T00:00:00Z" if state == "confirmed" else None,
        "categories": [
            {"category_id": "ppc-1", "category_ordinal": 0, "label": "HP", "count_per_sample": 4, "record_prefix": "HP", "included": True},
            {"category_id": "ppc-2", "category_ordinal": 1, "label": "LP", "count_per_sample": 5, "record_prefix": "LP", "included": True},
            {"category_id": "ppc-3", "category_ordinal": 2, "label": "Signal", "count_per_sample": 24, "record_prefix": "SIG", "included": True},
        ],
        "points_per_sample": 33,
    }
