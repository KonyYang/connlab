from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from openpyxl import load_workbook

from backend.api.dependencies import (
    get_matrix_editor_llcr_cr_record_generation_service,
    get_matrix_editor_llcr_cr_record_publication_service,
)
from backend.application.confirmed_matrix_llcr_cr_record_generation_service import (
    MatrixEditorLlcrCrPublicationPreview, MatrixEditorLlcrCrPublicationResult,
)
from backend.api.main import app
from backend.application.matrix_editor_llcr_cr_record_generation_service import (
    MatrixEditorLlcrCrRecordGenerationService,
)
from backend.infrastructure.files.llcr_cr_specialized_record_artifact_store import (
    LlcrCrSpecializedRecordArtifactStore,
)
from backend.infrastructure.office.llcr_cr_specialized_record_workbook_gateway import (
    LlcrCrSpecializedRecordWorkbookGateway,
)
from backend.domain.enums import LtrStatus


def test_matrix_editor_llcr_download_uses_current_ui_draft_without_confirmed_matrix(
    tmp_path: Path,
) -> None:
    response = _post_current_ui_draft(tmp_path, "5", None)

    assert response.status_code == 200
    assert "Unconfirmed" in response.headers["content-disposition"]
    output = tmp_path / "matrix-editor-llcr-preview.xlsx"
    output.write_bytes(response.content)
    workbook = load_workbook(output, data_only=False)
    assert workbook.sheetnames == ["Summary", "SIG"]
    sheet = workbook["SIG"]
    assert sheet["F1"].value == "DL-2026-05-999"
    assert sheet["F5"].value == "20 mV, 100 mA"
    assert sheet["D9"].value == "1#"
    assert sheet["K9"].value == "unit:mΩ"


def test_matrix_editor_llcr_download_accepts_footnoted_sample_quantity(
    tmp_path: Path,
) -> None:
    response = _post_current_ui_draft(
        tmp_path,
        "3(a)",
        "(a) Male connector and Female connector",
    )

    assert response.status_code == 200
    output = tmp_path / "matrix-editor-llcr-footnoted-preview.xlsx"
    output.write_bytes(response.content)
    sheet = load_workbook(output, data_only=False)["SIG"]
    assert [sheet.cell(9, column).value for column in range(4, 7)] == [
        "1#",
        "2#",
        "3#",
    ]
    assert sheet["I9"].value == "unit:mΩ"


def test_matrix_editor_llcr_download_preserves_explicit_point_ids_and_order(
    tmp_path: Path,
) -> None:
    response = _post_current_ui_draft(
        tmp_path,
        "1",
        None,
        point_expression="1,24,35,2,7,10",
        point_category="HP",
    )

    assert response.status_code == 200
    output = tmp_path / "matrix-editor-llcr-explicit-points.xlsx"
    output.write_bytes(response.content)
    sheet = load_workbook(output, data_only=False)["HP"]
    assert [sheet.cell(row, 3).value for row in range(10, 16)] == [
        "1", "24", "35", "2", "7", "10",
    ]


def test_draft_llcr_step_exception_marks_untested_cells_without_formulas(
    tmp_path: Path,
) -> None:
    response = _post_current_ui_draft(tmp_path, "1", None, point_overrides=[{
        "draft_group_id": "group-id", "draft_row_id": "row-id",
        "step_sequence": 6, "step_suffix_note": "",
        "categories": [{"prefix": "SIG", "point_expression": "2"}],
    }])

    assert response.status_code == 200
    output = tmp_path / "step-subset.xlsx"
    output.write_bytes(response.content)
    workbook = load_workbook(output, data_only=False)
    try:
        sheet = workbook["SIG"]
        assert [sheet.cell(row, 3).value for row in range(10, 14)] == ["1", "2", "1", "2"]
        assert sheet["D12"].value is None
        assert sheet["J12"].value is None
        assert sheet["K12"].value is None
        assert sheet["D12"].fill.fgColor.rgb == "00E7E6E6"
        assert sheet["J13"].data_type == "f"
    finally:
        workbook.close()


def test_draft_cr_step_exception_marks_untested_cells_without_formulas(
    tmp_path: Path,
) -> None:
    response = _post_current_ui_draft(
        tmp_path, "1", None, record_type="cr", test_item="Contact Resistance (Power)",
        point_overrides=[{
            "draft_group_id": "group-id", "draft_row_id": "row-id",
            "step_sequence": 6, "step_suffix_note": "",
            "categories": [{"prefix": "SIG", "point_expression": "2"}],
        }],
    )

    assert response.status_code == 200
    output = tmp_path / "cr-step-subset.xlsx"
    output.write_bytes(response.content)
    workbook = load_workbook(output, data_only=False)
    try:
        sheet = workbook["SIG"]
        assert sheet["D12"].value is None
        assert sheet["J12"].value is None
        assert sheet["D12"].fill.fgColor.rgb == "00E7E6E6"
        assert sheet["J13"].data_type == "f"
    finally:
        workbook.close()


def test_publication_preview_and_publish_routes_preserve_reviewed_contract(tmp_path: Path) -> None:
    class _Publication:
        def preview(self, command):
            assert command.draft.project_id == "P1"
            return MatrixEditorLlcrCrPublicationPreview(
                project_id="P1", mode="official", status="conflict",
                authority_status="confirmed", target_path=tmp_path / "Test results" / "form.xlsx",
                existing_file=True, blockers=(), preview_token="review-token",
            )

        def publish(self, command):
            assert command.preview_token == "review-token"
            assert command.conflict_action == "archive"
            return MatrixEditorLlcrCrPublicationResult(
                project_id="P1", file_name="form.xlsx",
                target_path=tmp_path / "Test results" / "form.xlsx",
                archive_path=tmp_path / "History" / "form.xlsx",
            )

    app.dependency_overrides[get_matrix_editor_llcr_cr_record_publication_service] = lambda: _Publication()
    request = {
        "source": "matrix_editor_current_ui_state", "record_type": "llcr",
        "groups": [], "rows": [], "point_overrides": [],
    }
    try:
        client = TestClient(app)
        preview = client.post("/api/projects/P1/matrix-editor/llcr-cr-record-publication/preview", json=request)
        published = client.post("/api/projects/P1/matrix-editor/llcr-cr-record-publication/publish",
                                json={**request, "preview_token": "review-token", "conflict_action": "archive"})
    finally:
        app.dependency_overrides.clear()
    assert preview.status_code == 200
    assert preview.json()["preview_token"] == "review-token"
    assert preview.json()["mode"] == "official"
    assert published.status_code == 200
    assert published.json()["archive_path"] == str(tmp_path / "History" / "form.xlsx")


def test_draft_download_with_stale_preview_token_is_rejected(tmp_path: Path) -> None:
    class _Publication:
        def validate_download(self, command, token):
            assert command.draft.project_id == "P1"
            assert token == "stale-token"
            raise ValueError("download preview changed")

    app.dependency_overrides[get_matrix_editor_llcr_cr_record_publication_service] = lambda: _Publication()
    try:
        response = TestClient(app).post(
            "/api/projects/P1/matrix-editor/llcr-cr-record-draft/generate",
            json={"source": "matrix_editor_current_ui_state", "record_type": "llcr",
                  "groups": [], "rows": [], "preview_token": "stale-token"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422
    assert "changed" in response.json()["detail"]


def test_publication_permission_failure_returns_recovery_instruction() -> None:
    class _Publication:
        def publish(self, _command):
            raise PermissionError(5, "Access denied to measured form")

    app.dependency_overrides[get_matrix_editor_llcr_cr_record_publication_service] = lambda: _Publication()
    try:
        response = TestClient(app).post(
            "/api/projects/P1/matrix-editor/llcr-cr-record-publication/publish",
            json={"source": "matrix_editor_current_ui_state", "record_type": "llcr",
                  "groups": [], "rows": [], "preview_token": "reviewed",
                  "conflict_action": "archive"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 409
    assert "Access denied" in response.json()["detail"]
    assert "Retry this reviewed action" in response.json()["detail"]


def _post_current_ui_draft(
    tmp_path: Path,
    sample_quantity_expression: str,
    sample_note: str | None,
    *,
    point_expression: str = "1-2",
    point_category: str = "SIG",
    point_overrides: list[dict] | None = None,
    record_type: str = "llcr",
    test_item: str = "Contact Resistance (Low Level)",
):
    generation = MatrixEditorLlcrCrRecordGenerationService(
        point_profile_adapter=_PointProfileAdapter(),
        workbook_gateway=LlcrCrSpecializedRecordWorkbookGateway(),
        artifact_store=LlcrCrSpecializedRecordArtifactStore(tmp_path / "generated"),
        ltr_store=_LtrStore(),
    )
    app.dependency_overrides[
        get_matrix_editor_llcr_cr_record_generation_service
    ] = lambda: generation
    try:
        response = TestClient(app).post(
            "/api/projects/P1/matrix-editor/llcr-cr-record-draft/generate",
            json={
                "source": "matrix_editor_current_ui_state",
                "record_type": record_type,
                "point_profile": {
                    "categories": [{
                        "prefix": point_category, "point_expression": point_expression,
                        "cr_selected": True,
                    }],
                    "delta_r_enabled": True,
                },
                "point_overrides": point_overrides or [],
                "groups": [
                    {
                        "group_key": "group_6",
                        "draft_group_id": "group-id",
                        "group_label": "6",
                        "sample_quantity_expression": sample_quantity_expression,
                        "sample_note": sample_note,
                    }
                ],
                "rows": [
                    {
                        "test_item": test_item,
                        "draft_row_id": "row-id",
                        "section": "6.1",
                        "method": "EIA-364-23D",
                        "condition": "20 mV, 100 mA",
                        "requirement": "Initial <= 0.25 mOhm",
                        "group_values": {"group_6": "2,6"},
                    }
                ],
            },
        )
    finally:
        app.dependency_overrides.clear()
    return response


class _LtrStore:
    def list_by_project(self, project_id: str):
        assert project_id == "P1"
        return [
            SimpleNamespace(
                ltr_number="DL-2026-05-999",
                status=LtrStatus.REGISTERED,
                registered_on="2026-05-20",
            )
        ]


class _PointProfileAdapter:
    def get_effective(self, project_id: str):
        raise AssertionError("Draft download must not read the independent Point Profile authority.")
