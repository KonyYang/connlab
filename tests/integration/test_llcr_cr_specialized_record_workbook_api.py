from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import (
    get_llcr_cr_record_workbook_artifact_store,
    get_llcr_cr_record_workbook_generation_service,
    get_llcr_cr_record_workbook_preview_service,
)
from backend.api.main import app
from backend.application.confirmed_matrix_llcr_cr_record_generation_service import (
    LlcrCrRecordWorkbookGenerationService,
)
from backend.application.confirmed_matrix_llcr_cr_record_preview_service import (
    LlcrCrRecordWorkbookPreviewService,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
)
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)
from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
    LlcrCrSpecializedRecordWorkbookGateway,
)


def test_preview_generate_and_contained_download_use_confirmed_authority_only(tmp_path: Path) -> None:
    artifact_store = LlcrCrSpecializedRecordArtifactStore(tmp_path / "generated")
    preview_service = LlcrCrRecordWorkbookPreviewService(
        confirmed_store=_ConfirmedStore(_snapshot())
    )
    generation_service = LlcrCrRecordWorkbookGenerationService(
        preview_service=preview_service,
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        artifact_store=artifact_store,
    )
    app.dependency_overrides[get_llcr_cr_record_workbook_preview_service] = lambda: preview_service
    app.dependency_overrides[get_llcr_cr_record_workbook_generation_service] = lambda: generation_service
    app.dependency_overrides[get_llcr_cr_record_workbook_artifact_store] = lambda: artifact_store
    try:
        client = TestClient(app)
        preview = client.post(
            "/api/projects/project-1/confirmed-matrix/llcr-cr-record-workbook/preview"
        )
        assert preview.status_code == 200
        assert preview.json()["status"] == "ready"
        assert not list(tmp_path.rglob("*.xlsx"))

        generated = client.post(
            "/api/projects/project-1/confirmed-matrix/llcr-cr-record-workbook/generate",
            json={"preview_fingerprint": preview.json()["preview_fingerprint"]},
        )
        assert generated.status_code == 200
        payload = generated.json()
        assert "output_path" not in payload
        assert payload["download_url"].endswith(payload["artifact_id"])

        download = client.get(payload["download_url"])
        assert download.status_code == 200
        assert download.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    finally:
        app.dependency_overrides.clear()


def test_preview_reports_both_families_for_a_same_section_prefix_collision(tmp_path: Path) -> None:
    source = _snapshot()
    plan = source.step_quantities[0].contact_plan
    assert plan is not None
    collision_plan = replace(
        plan,
        readings_per_sample="2",
        families=(
            MatrixStepContactFamily(
                "hp",
                "HP",
                "1",
                "HP contact",
                "hp",
                True,
                False,
            ),
            MatrixStepContactFamily(
                "high-duplicate",
                "High Power duplicate",
                "1",
                "High Power duplicate contact",
                "hp",
                True,
                True,
            ),
        ),
    )
    collision_quantity = replace(source.step_quantities[0], contact_plan=collision_plan)
    preview_service = LlcrCrRecordWorkbookPreviewService(
        confirmed_store=_ConfirmedStore(replace(source, step_quantities=(collision_quantity,)))
    )
    artifact_store = LlcrCrSpecializedRecordArtifactStore(tmp_path / "generated")
    generation_service = LlcrCrRecordWorkbookGenerationService(
        preview_service=preview_service,
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        artifact_store=artifact_store,
    )
    app.dependency_overrides[get_llcr_cr_record_workbook_preview_service] = lambda: preview_service
    app.dependency_overrides[get_llcr_cr_record_workbook_generation_service] = lambda: generation_service
    app.dependency_overrides[get_llcr_cr_record_workbook_artifact_store] = lambda: artifact_store
    try:
        response = TestClient(app).post(
            "/api/projects/project-1/confirmed-matrix/llcr-cr-record-workbook/preview"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert not list(tmp_path.rglob("*.xlsx"))
    diagnostic = payload["diagnostics"][0]
    assert diagnostic["first_family_id"] == "hp"
    assert diagnostic["first_family_label"] == "HP"
    assert diagnostic["second_family_id"] == "high-duplicate"
    assert diagnostic["second_family_label"] == "High Power duplicate"


class _ConfirmedStore:
    def __init__(self, snapshot: ConfirmedMatrixSnapshot) -> None:
        self._snapshot = snapshot

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        return self._snapshot if project_id == self._snapshot.version.project_id else None


def _snapshot() -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id="cmv-1",
        project_id="project-1",
        project_matrix_draft_id="draft-1",
        source_import_id="import-1",
        source_snapshot_id="source-1",
        confirmed_revision=4,
        is_active_authority=True,
        status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by="operator",
        confirmed_at="2026-07-10T10:00:00+00:00",
    )
    group = ConfirmedMatrixGroup("group-1", "cmv-1", "draft-group-1", None, 1, "G1", "Group 1", "1")
    row = ConfirmedMatrixRow("row-1", "cmv-1", "draft-row-1", None, 1, "LLCR")
    plan = MatrixStepContactPlan(
        "llcr", "eligible", True, None, False, "1",
        (MatrixStepContactFamily("signal", "Signal", "1", "Signal contact", "SIG", True, False),),
    )
    quantity = ConfirmedMatrixStepQuantity(
        "quantity-1", "cmv-1", "group-1", "row-1", "draft-group-1", "draft-row-1",
        2, None, "2", None, None, None, "matrix_contact_plan", False, None,
        version.confirmed_at, plan,
    )
    return ConfirmedMatrixSnapshot(version=version, groups=(group,), rows=(row,), step_quantities=(quantity,))
