from pathlib import Path

import pytest

from backend.application.draft_measurement_plan_workbook_generation_service import (
    DraftMeasurementPlanWorkbookGenerationError,
    DraftMeasurementPlanWorkbookGenerationService,
)
from backend.application.draft_measurement_plan_workbook_preview_service import (
    DraftMeasurementPlanWorkbookPreviewService,
)
from backend.infrastructure.files.draft_measurement_plan_workbook_artifact_store import (
    DraftMeasurementPlanWorkbookArtifactStore,
)
from backend.infrastructure.office.draft_measurement_plan_workbook_gateway import (
    DraftMeasurementPlanWorkbookGateway,
)


def test_generation_requires_current_preview_fingerprint_before_writing(tmp_path: Path) -> None:
    workspace = _workspace()
    preview_service = DraftMeasurementPlanWorkbookPreviewService(lambda _: workspace)
    service = DraftMeasurementPlanWorkbookGenerationService(
        preview_service=preview_service,
        workbook_gateway=DraftMeasurementPlanWorkbookGateway(),
        artifact_store=DraftMeasurementPlanWorkbookArtifactStore(tmp_path),
    )

    with pytest.raises(DraftMeasurementPlanWorkbookGenerationError, match="Preview again"):
        service.generate("P-1", "draft-1", "stale")

    assert not list(tmp_path.rglob("*.xlsx"))


def test_generation_manifest_carries_source_review_and_layout_metadata(tmp_path: Path) -> None:
    workspace = _workspace()
    preview_service = DraftMeasurementPlanWorkbookPreviewService(lambda _: workspace)
    store = DraftMeasurementPlanWorkbookArtifactStore(tmp_path)
    service = DraftMeasurementPlanWorkbookGenerationService(
        preview_service=preview_service,
        workbook_gateway=DraftMeasurementPlanWorkbookGateway(),
        artifact_store=store,
    )
    preview = preview_service.preview("P-1", "draft-1")

    result = service.generate("P-1", "draft-1", preview.preview_fingerprint or "")
    metadata = store.resolve(project_id="P-1", artifact_id=result.artifact_id).metadata

    assert metadata["revision_fingerprint"] == "f"
    assert metadata["matrix_binding_fingerprint"] == "matrix"
    assert metadata["layout_version"] == "LLCR_CR_RECORD_LAYOUT_V1"
    assert metadata["generated_at_utc"]


def _workspace() -> dict[str, object]:
    return {
        "project_id": "P-1", "editable_revision_id": "draft-1", "editable_revision_state": "draft", "editable_revision_fingerprint": "f", "revision": {"revision_id": "draft-1", "revision_sequence": 1},
        "matrix_binding": {"base_confirmed_matrix_id": "matrix-1", "base_matrix_revision": 1, "matrix_binding_fingerprint": "matrix"},
        "targets": [{"contact_kind": "llcr", "eligible": True, "included": True, "group_label": "Group", "step_sequence": 1, "step_suffix_note": "", "sample_quantity_expression": "1", "readings_per_sample": 1, "families": [{"included": True, "count_per_sample": 1, "record_label": "High Power", "record_prefix": "HP"}]}],
        "impacts": [],
    }
