from fastapi.testclient import TestClient

from backend.api.dependencies import (
    get_draft_measurement_plan_workbook_generation_service,
    get_draft_measurement_plan_workbook_preview_service,
)
from backend.api.main import app
from backend.application.draft_measurement_plan_workbook_preview_service import (
    DraftMeasurementPlanWorkbookPreviewError,
)
from backend.application.draft_measurement_plan_workbook_projection import (
    build_draft_measurement_plan_workbook_projection,
)
from backend.application.draft_measurement_plan_workbook_generation_service import (
    DraftMeasurementPlanWorkbookGenerationResult,
)
from pathlib import Path


def test_draft_preview_route_returns_typed_review_material_without_write() -> None:
    app.dependency_overrides[get_draft_measurement_plan_workbook_preview_service] = lambda: _PreviewService()
    try:
        with TestClient(app) as client:
            response = client.post("/api/projects/P1/contact-measurement-plan/revisions/draft-1/draft-workbook/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["output_label"] == "DRAFT"
    assert payload["generate_allowed"] is True
    assert payload["row_count"] == 1


def test_draft_preview_route_returns_stale_409_for_non_current_revision() -> None:
    app.dependency_overrides[get_draft_measurement_plan_workbook_preview_service] = lambda: _StalePreviewService()
    try:
        with TestClient(app) as client:
            response = client.post("/api/projects/P1/contact-measurement-plan/revisions/old/draft-workbook/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "draft_workbook_stale"


def test_draft_generate_route_exposes_nonfatal_cleanup_warning() -> None:
    app.dependency_overrides[get_draft_measurement_plan_workbook_generation_service] = lambda: _GenerationService()
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/projects/P1/contact-measurement-plan/revisions/draft-1/draft-workbook/generate",
                json={"preview_fingerprint": "preview"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["cleanup_warning"] == "Older draft artifacts could not be cleaned up."


class _PreviewService:
    def preview(self, project_id: str, revision_id: str):
        assert (project_id, revision_id) == ("P1", "draft-1")
        return build_draft_measurement_plan_workbook_projection(_workspace())


class _StalePreviewService:
    def preview(self, project_id: str, revision_id: str):
        raise DraftMeasurementPlanWorkbookPreviewError("Editable measurement plan changed. Reload before previewing.")


class _GenerationService:
    def generate(self, project_id: str, revision_id: str, preview_fingerprint: str):
        return DraftMeasurementPlanWorkbookGenerationResult(
            project_id, revision_id, "a" * 32, "draft.xlsx", Path("draft.xlsx"), "DRAFT",
            "Older draft artifacts could not be cleaned up.",
        )


def _workspace() -> dict[str, object]:
    return {
        "project_id": "P1", "editable_revision_id": "draft-1", "editable_revision_state": "draft", "editable_revision_fingerprint": "f", "revision": {"revision_id": "draft-1", "revision_sequence": 1},
        "matrix_binding": {"base_confirmed_matrix_id": "matrix-1", "base_matrix_revision": 1, "matrix_binding_fingerprint": "matrix"},
        "targets": [{"contact_kind": "llcr", "eligible": True, "included": True, "group_label": "Group", "step_sequence": 1, "step_suffix_note": "", "sample_quantity_expression": "1", "readings_per_sample": 1, "families": [{"included": True, "count_per_sample": 1, "record_label": "High Power", "record_prefix": "HP"}]}],
        "impacts": [],
    }
