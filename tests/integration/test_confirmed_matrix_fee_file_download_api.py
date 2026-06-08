from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.dependencies import (
    get_confirmed_matrix_fee_evaluation_export_service,
    get_settings,
)
from backend.api.main import app
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftNotFoundError,
)
from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ConfirmedMatrixFeeEvaluationExportNotFoundError,
    ConfirmedMatrixFeeEvaluationExportTimeoutError,
    ExportConfirmedMatrixFeeEvaluationCommand,
    ExportConfirmedMatrixFeeEvaluationResult,
)
from backend.application.fee_evaluation_export_lineage import (
    FeeEvaluationExportLineTrace,
)
from backend.shared.config import Settings


def test_fee_file_download_route_returns_generated_xls_and_uses_matrix_basic_fill(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    service = _FakeDownloadExportService()
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: service
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/file/generate"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.content == b"fee workbook"
    assert response.headers["content-type"].startswith("application/vnd.ms-excel")
    assert "fee-P1.xls" in response.headers["content-disposition"]

    command = service.commands[0]
    assert command.project_id == "P1"
    assert command.fill_mode == "matrix_basic"
    assert command.allow_review_required is True
    assert command.overwrite is True
    assert command.output_file_name is None
    assert command.output_dir == settings.data_dir / "generated_fee_files"
    assert command.template_path == Path(
        "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls"
    )


def test_fee_file_download_route_accepts_edited_payload(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    service = _FakeDownloadExportService()
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: service
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/file/generate",
            json={
                "rows": [
                    {
                        "source_line_id": "cmv-1:g1:cmr-1:1:0",
                        "confirmed_group_id": "cmg-1",
                        "confirmed_row_id": "cmr-1",
                        "step_token": "1",
                        "step_index": 0,
                        "spend_time": "1.5",
                        "unit_price": "20",
                        "unit_type": "per sample",
                        "units": "2",
                        "base_fee": "5",
                        "discount": "10%",
                        "testing_fee": "41",
                        "notes": "operator note",
                    }
                ],
                "manual_rows": [
                    {
                        "row_kind": "report_preparation",
                        "spend_time": "0.5",
                        "unit_price": "100",
                        "unit_type": "per report",
                        "units": "1",
                        "base_fee": "0",
                        "discount": "0%",
                        "testing_fee": "100",
                        "notes": "",
                    }
                ],
                "summary": {
                    "condition_confirmation_spend_time": "0.25",
                    "external_cost": "150",
                    "external_cost_note": "tooling",
                    "lab_manpower_hourly_rate": "200",
                },
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    command = service.commands[0]
    assert command.edited_values is not None
    assert command.edited_values.rows[0].notes == "operator note"
    assert command.edited_values.manual_rows[0].row_kind == "report_preparation"
    assert command.edited_values.summary.external_cost_note == "tooling"


def test_fee_file_download_route_rejects_duplicate_edited_row_identity(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = _FakeDownloadExportService
    app.dependency_overrides[get_settings] = lambda: settings
    row = {
        "source_line_id": "cmv-1:g1:cmr-1:1:0",
        "confirmed_group_id": "cmg-1",
        "confirmed_row_id": "cmr-1",
        "step_token": "1",
        "step_index": 0,
        "spend_time": "1",
        "unit_price": "20",
        "unit_type": "per sample",
        "units": "1",
        "base_fee": "0",
        "discount": "0%",
        "testing_fee": "20",
        "notes": "",
    }
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/file/generate",
            json={
                "rows": [row, row],
                "summary": {
                    "condition_confirmation_spend_time": "0",
                    "external_cost": "0",
                    "external_cost_note": "",
                    "lab_manpower_hourly_rate": "200",
                },
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_fee_file_download_route_rejects_service_path_outside_generated_fee_dir(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    outside = tmp_path / "outside.xls"
    outside.write_bytes(b"not a fee cache file")
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: _PathReturningExportService(outside)
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/file/generate"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert "generated Fee file path" in response.json()["detail"]


def test_fee_file_download_route_rejects_non_xls_generated_path(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    generated_dir = settings.data_dir / "generated_fee_files"
    generated_dir.mkdir(parents=True)
    generated = generated_dir / "fee-P1.xlsx"
    generated.write_bytes(b"xlsx")
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: _PathReturningExportService(generated)
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/file/generate"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert ".xls" in response.json()["detail"]


def test_fee_file_download_route_maps_missing_authority_to_404(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: _FailingDownloadExportService(
        ConfirmedMatrixFeeEvaluationExportNotFoundError("No active Confirmed Matrix.")
    )
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/file/generate"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "No active Confirmed Matrix" in response.json()["detail"]


def test_fee_file_download_route_maps_timeout_to_structured_503(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: _FailingDownloadExportService(
        ConfirmedMatrixFeeEvaluationExportTimeoutError(
            "Fee file generation timed out after 90 seconds.",
            elapsed_seconds=90.0,
            manual_cleanup_warning="Close Excel manually if it is still open.",
        )
    )
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/file/generate"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "timed out" in detail["message"]
    assert detail["elapsed_seconds"] == 90.0
    assert "Close Excel" in detail["manual_cleanup_warning"]


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "data" / "connlab.sqlite3",
    )


class _FakeDownloadExportService:
    def __init__(self) -> None:
        self.commands: list[ExportConfirmedMatrixFeeEvaluationCommand] = []

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        self.commands.append(command)
        assert command.output_dir is not None
        command.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = command.output_dir / f"fee-{command.project_id}.xls"
        output_path.write_bytes(b"fee workbook")
        return _result(command.project_id, output_path)


class _PathReturningExportService:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        return _result(command.project_id, self.output_path)


class _FailingDownloadExportService:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        raise self.exc


def _result(project_id: str, output_path: Path) -> ExportConfirmedMatrixFeeEvaluationResult:
    return ExportConfirmedMatrixFeeEvaluationResult(
        project_id=project_id,
        output_path=output_path,
        output_format=output_path.suffix.lstrip("."),
        status="exported",
        confirmed_matrix_id="cmv-1",
        confirmed_revision=1,
        pricing_rule_version_id="fee_rules_v2026_06_03",
        pricing_effective_from=None,
        prepared_by="Lab User",
        approved_by=None,
        output_record_id="por-1",
        line_traceability=(
            FeeEvaluationExportLineTrace(
                line_id="line-1",
                group_key="visual",
                group_label="Visual",
                confirmed_group_id="group-1",
                confirmed_row_id="row-1",
                source_row_id="source-row-1",
                row_order=1,
                matched_rule_id="fee_rule_visual",
                matched_rule_version_id="fee_rules_v2026_06_03",
                step_tokens=("1",),
                cell_value="1 X",
            ),
        ),
        warnings=(),
    )
