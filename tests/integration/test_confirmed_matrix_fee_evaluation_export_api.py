from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import (
    get_confirmed_matrix_fee_evaluation_export_service,
    get_session,
    get_settings,
)
from backend.api.main import app
from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftService,
)
from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ConfirmedMatrixFeeEvaluationExportNotFoundError,
    ConfirmedMatrixFeeEvaluationExportUnavailableError,
    ExportConfirmedMatrixFeeEvaluationCommand,
    ExportConfirmedMatrixFeeEvaluationResult,
    FeeEvaluationExportLineTrace,
    ConfirmedMatrixFeeEvaluationExportService,
)
from backend.application.project_output_record_service import (
    ProjectOutputRecordService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
    Project,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
    ProjectStatus,
    ProjectTestPlanDraft,
    ProjectTestPlanDraftStatus,
)
from backend.infrastructure.office.models import FeeEvaluationWorkbookWriteResult
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ConfirmedMatrixAuthorityRepository,
    ProjectOutputRecordRepository,
    ProjectRepository,
    ProjectTestPlanDraftRepository,
)
from backend.shared.config import Settings


def test_confirmed_matrix_fee_evaluation_export_api_returns_result(
    tmp_path: Path,
) -> None:
    service = _FakeExportService()
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/export",
            json={
                "template_path": str(tmp_path / "template.xls"),
                "output_dir": str(tmp_path),
                "output_file_name": "fee.xlsx",
                "overwrite": True,
                "fill_mode": "matrix_basic",
                "allow_review_required": True,
                "prepared_by": "Operator",
                "approved_by": "Lead",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "P1"
    assert payload["output_path"].endswith("fee.xlsx")
    assert payload["output_format"] == "xlsx"
    assert payload["confirmed_matrix_id"] == "cmv-1"
    assert payload["pricing_rule_version_id"] == "fee_rules_v2026_06_03"
    assert payload["output_record_id"] == "por-1"
    assert payload["line_traceability"][0]["confirmed_row_id"] == "cmr-1"
    assert payload["line_traceability"][0]["matched_rule_id"] == "fee_rule_visual"
    assert payload["line_traceability"][0]["cell_value"] == "1 X"
    assert service.commands[0].template_path == tmp_path / "template.xls"
    assert service.commands[0].approved_by == "Lead"
    assert service.commands[0].fill_mode == "matrix_basic"


def test_confirmed_matrix_fee_evaluation_export_api_maps_not_ready_to_400(
    tmp_path: Path,
) -> None:
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: _FailingExportService(
        ConfirmedMatrixFeeEvaluationExportError("Fee draft requires review before export.")
    )
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/export",
            json={
                "template_path": str(tmp_path / "template.xls"),
                "output_dir": str(tmp_path),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "requires review" in response.json()["detail"]


def test_confirmed_matrix_fee_evaluation_export_api_maps_missing_path_to_404(
    tmp_path: Path,
) -> None:
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: _FailingExportService(
        ConfirmedMatrixFeeEvaluationExportNotFoundError("Template does not exist.")
    )
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/export",
            json={
                "template_path": str(tmp_path / "missing.xls"),
                "output_dir": str(tmp_path),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert "Template does not exist" in response.json()["detail"]


def test_confirmed_matrix_fee_evaluation_export_api_maps_unavailable_to_503(
    tmp_path: Path,
) -> None:
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = lambda: _FailingExportService(
        ConfirmedMatrixFeeEvaluationExportUnavailableError(
            "Excel COM automation is required."
        )
    )
    try:
        response = TestClient(app).post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/export",
            json={
                "template_path": str(tmp_path / "template.xls"),
                "output_dir": str(tmp_path),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "Excel COM automation" in response.json()["detail"]


def test_confirmed_matrix_fee_evaluation_export_api_registers_output_status(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project_and_draft("P1", tmp_path, draft_id="D1", version=1)
        _seed_active_confirmed_snapshot("P1", tmp_path)
        template = tmp_path / "template.xls"
        template.write_text("template", encoding="utf-8")
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        response = client.post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/export",
            json={
                "template_path": str(template),
                "output_dir": str(output_dir),
                "allow_review_required": True,
            },
        )

        assert response.status_code == 200
        summary = client.get("/api/projects/P1/output-records/status")
        assert summary.status_code == 200
        fee_item = next(
            item
            for item in summary.json()["items"]
            if item["output_kind"] == "fee_evaluation"
        )
        assert fee_item["status"] == "current"
        assert fee_item["draft_id"] == "D1"
        assert _latest_fee_output_note("P1", tmp_path) is not None
        assert "confirmed_matrix_id=cmv-1" in (_latest_fee_output_note("P1", tmp_path) or "")
        assert "fee_rule_version_id=fee_rules_v2026_06_03" in (
            _latest_fee_output_note("P1", tmp_path) or ""
        )

        _seed_project_test_plan_draft("P1", tmp_path, draft_id="D2", version=2)
        stale_summary = client.get("/api/projects/P1/output-records/status")
        stale_fee_item = next(
            item
            for item in stale_summary.json()["items"]
            if item["output_kind"] == "fee_evaluation"
        )
        assert stale_fee_item["status"] == "stale"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirmed_matrix_fee_evaluation_export_api_rejects_no_active_confirmed_matrix(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project_and_draft("P1", tmp_path, draft_id="D1", version=1)
        template = tmp_path / "template.xls"
        template.write_text("template", encoding="utf-8")

        response = client.post(
            "/api/projects/P1/confirmed-matrix/fee-evaluation/export",
            json={
                "template_path": str(template),
                "output_dir": str(tmp_path),
                "allow_review_required": True,
            },
        )

        assert response.status_code == 404
        assert "Active confirmed matrix" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


class _FakeExportService:
    def __init__(self) -> None:
        self.commands: list[ExportConfirmedMatrixFeeEvaluationCommand] = []

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        self.commands.append(command)
        return ExportConfirmedMatrixFeeEvaluationResult(
            project_id=command.project_id,
            output_path=(command.output_dir or Path(".")) / "fee.xlsx",
            output_format="xlsx",
            status="generated",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            pricing_rule_version_id="fee_rules_v2026_06_03",
            pricing_effective_from="2026-06-03",
            prepared_by=command.prepared_by,
            approved_by=command.approved_by,
            output_record_id="por-1",
            line_traceability=(
                FeeEvaluationExportLineTrace(
                    line_id="line-1",
                    group_key="g1",
                    group_label="G1",
                    confirmed_group_id="cmg-1",
                    confirmed_row_id="cmr-1",
                    source_row_id="smr-1",
                    row_order=1,
                    matched_rule_id="fee_rule_visual",
                    matched_rule_version_id="fee_rules_v2026_06_03",
                    step_tokens=("1",),
                    cell_value="1 X",
                ),
            ),
            warnings=("Approval remains manual.",),
        )


class _FailingExportService:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        raise self.error


class _ApiWriter:
    def generate_from_draft(
        self,
        *,
        template_path: Path,
        output_path: Path,
        draft: object,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        output_path.write_text("generated", encoding="utf-8")
        return FeeEvaluationWorkbookWriteResult(
            output_path=output_path,
            status="generated",
            warnings=(),
        )

    def generate_matrix_basic_fill(
        self,
        *,
        template_path: Path,
        output_path: Path,
        basic_fill: object,
        review_required: bool,
        prepared_by: str | None,
        approved_by: str | None,
    ) -> FeeEvaluationWorkbookWriteResult:
        output_path.write_text("generated-basic", encoding="utf-8")
        return FeeEvaluationWorkbookWriteResult(
            output_path=output_path,
            status="generated",
            warnings=("Matrix basic fill only.",),
        )


def _client(tmp_path: Path) -> tuple[TestClient, object, object]:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def override_export_service(
        session: Session = Depends(get_session),
    ) -> ConfirmedMatrixFeeEvaluationExportService:
        confirmed_store = ConfirmedMatrixAuthorityRepository(session)
        return ConfirmedMatrixFeeEvaluationExportService(
            fee_draft_service=ConfirmedMatrixFeeDraftService(
                confirmed_store=confirmed_store,
            ),
            confirmed_store=confirmed_store,
            project_output_service=ProjectOutputRecordService(
                project_store=ProjectRepository(session),
                draft_store=ProjectTestPlanDraftRepository(session),
                output_store=ProjectOutputRecordRepository(session),
            ),
            workbook_writer=_ApiWriter(),
        )

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[
        get_confirmed_matrix_fee_evaluation_export_service
    ] = override_export_service
    return TestClient(app), engine, session_factory


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )


def _seed_project_and_draft(
    project_id: str,
    tmp_path: Path,
    *,
    draft_id: str,
    version: int,
) -> None:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id=project_id,
                project_no=f"DL-2026-06-{project_id}",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 6, 4),
            )
        )
        ProjectTestPlanDraftRepository(session).create(
            _project_test_plan_draft(project_id, draft_id=draft_id, version=version)
        )
        session.commit()
    engine.dispose()


def _seed_project_test_plan_draft(
    project_id: str,
    tmp_path: Path,
    *,
    draft_id: str,
    version: int,
) -> None:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectTestPlanDraftRepository(session).create(
            _project_test_plan_draft(project_id, draft_id=draft_id, version=version)
        )
        session.commit()
    engine.dispose()


def _project_test_plan_draft(
    project_id: str,
    *,
    draft_id: str,
    version: int,
) -> ProjectTestPlanDraft:
    return ProjectTestPlanDraft(
        draft_id=draft_id,
        project_id=project_id,
        source_document_path="C:/spec.docx",
        source_document_name="spec.docx",
        source_format="docx",
        status=ProjectTestPlanDraftStatus.REVIEWED,
        version=version,
        payload_json='{"groups": [], "warnings": [], "blockers": []}',
        created_at=f"2026-06-04T0{version}:00:00+00:00",
        updated_at=f"2026-06-04T0{version}:00:00+00:00",
        source_asset_id=None,
        source_case_id=None,
        source_draft_id=None,
        reviewed_at=f"2026-06-04T0{version}:00:00+00:00",
    )


def _seed_active_confirmed_snapshot(project_id: str, tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        row = ConfirmedMatrixRow(
            confirmed_row_id="cmr-visual",
            confirmed_matrix_id="cmv-1",
            draft_row_id="pmdr-visual",
            source_row_snapshot_id="smr-visual",
            row_order=1,
            test_item="Visual Examination",
            source_section="6.1",
            method="EIA-364-18",
            condition="Visual Inspection",
            requirement="No damage",
        )
        ConfirmedMatrixAuthorityRepository(session).create_snapshot(
            ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id="cmv-1",
                    project_id=project_id,
                    project_matrix_draft_id="pmd-1",
                    source_import_id="smi-1",
                    source_snapshot_id="sms-1",
                    confirmed_revision=1,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by="operator",
                    confirmed_at="2026-06-04T10:00:00+08:00",
                    sample_received_date="2026-06-03",
                ),
                groups=(
                    ConfirmedMatrixGroup(
                        confirmed_group_id="cmg-1",
                        confirmed_matrix_id="cmv-1",
                        draft_group_id="pmdg-1",
                        source_group_snapshot_id="smg-1",
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        sample_quantity_expression="5",
                    ),
                ),
                rows=(row,),
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-1",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id=row.confirmed_row_id,
                        confirmed_group_id="cmg-1",
                        draft_row_id=row.draft_row_id,
                        draft_group_id="pmdg-1",
                        cell_value="1",
                    ),
                ),
            )
        )
        session.commit()
    engine.dispose()


def _latest_fee_output_note(project_id: str, tmp_path: Path) -> str | None:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        records = ProjectOutputRecordRepository(session).list_by_project(project_id)
        fee_records = [
            record
            for record in records
            if record.output_kind is ProjectOutputKind.FEE_EVALUATION
        ]
        note = fee_records[-1].note if fee_records else None
    engine.dispose()
    return note
