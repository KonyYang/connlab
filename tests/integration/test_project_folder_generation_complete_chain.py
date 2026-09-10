"""One public Start completes the real services on isolated SQLite/files; Office is fake."""

from pathlib import Path
import runpy
from types import SimpleNamespace
from hashlib import sha256
import pytest

from backend.api import dependencies as deps
from backend.api.main import app
from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
from backend.domain import ApplicationForm, ExternalResource, ExternalResourceType, FileAsset, FileAssetType, LtrRecord, LtrStatus
from backend.infrastructure.office import OfficeFacade
from backend.infrastructure.office.models import FeeEvaluationWorkbookWriteResult


def _ok(response):
    assert response.status_code in (200, 201, 202), response.text
    return response.json()


@pytest.mark.parametrize("include_email", [True, False])
def test_one_start_completes_all_real_steps_and_reconnect_never_rewrites_outputs(tmp_path, monkeypatch, include_email):
    fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
    client, engine, sessions = fixture["_client"](tmp_path)
    settings = app.dependency_overrides[deps.get_settings]()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    callbacks = []
    service.dispatch = callbacks.append
    app.dependency_overrides[deps.get_project_folder_generation_service] = lambda: service
    try:
        fixture["_seed_project"]("P1", tmp_path)
        source_id = fixture["_seed_source_import"]("P1", tmp_path)
        draft = _ok(client.post("/api/projects/P1/matrix-drafts", json={
            "source_import_id": source_id, "selected_group_keys": ["g1", "g2"]}))
        _ok(client.post(f"/api/projects/P1/matrix-drafts/{draft['record']['project_matrix_draft_id']}/confirm",
                        json={"confirmed_by": "operator"}))
        source = tmp_path / "application.docx"
        source.write_bytes(b"original submitted application")
        template, output = tmp_path / "template", tmp_path / "output"
        output.mkdir()
        for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
            (template / name).mkdir(parents=True)
        for name in ("E-4243_D Customer Feedback Form.xlsx", "FDQF-E-176 Testing Fee Evaluation.xls",
                     "FDQF-E-036 Test Record.docx"):
            (template / name).write_bytes(b"controlled template")
        with sessions() as session:
            deps.LtrRecordRepository(session).create(LtrRecord("ltr", "P1", "DL-2026-05-P1", LtrStatus.REGISTERED))
            deps.ApplicationFormRepository(session).create(ApplicationForm("form", "P1", "F1", "1", "Alice"))
            deps.FileAssetRepository(session).create(FileAsset("app", "P1", FileAssetType.APPLICATION_FORM,
                source, original_name=source.name, source_role="selected_application_form",
                sha256=sha256(source.read_bytes()).hexdigest()))
            if include_email:
                email = tmp_path / "request.msg"
                email.write_bytes(b"request email")
                deps.FileAssetRepository(session).create(FileAsset("email", "P1", FileAssetType.ATTACHMENT,
                    email, original_name=email.name, source_role="email_source",
                    sha256=sha256(email.read_bytes()).hexdigest()))
            resources = deps.ExternalResourceRepository(session)
            resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, output))
            resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
            session.commit()
        _ok(client.post("/api/projects/P1/basic-information/confirm", json={"confirmed_by": "operator", "values": {
            "dl_number": "DL-2026-05-P1", "project_type": "NPD", "product_description": "Connector",
            "tests_to_be_performed": "Qualification Testing", "requested_by": "Alice", "project_leader": "Engineer",
            "test_item": "Qualification Testing",
            "lab_performing_tests": "Dongguan", "date_lab_received_samples": "2026-09-05",
            "condition_of_samples_when_received": "Acceptable"}}))
        schedule = _ok(client.get("/api/projects/P1/project-schedule"))
        _ok(client.post("/api/projects/P1/project-schedule/confirm", json={
            "actor": "operator",
            "expected_revision_id": (
                schedule["confirmed_revision"]["revision_id"]
                if schedule["confirmed_revision"] else None
            ),
            "expected_fingerprint": (
                schedule["confirmed_revision"]["fingerprint"]
                if schedule["confirmed_revision"] else None
            ),
            "post_test_buffer_days": "0",
            "test_start_date": "2026-09-06",
            "test_complete_date": "2026-09-15",
            "estimated_completion_date": "2026-09-15",
        }))
        pricing = _ok(client.put("/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
                                 json={"rows": [], "summary": {}}))
        _ok(client.post("/api/projects/P1/confirmed-fee/versions", json={
            "confirmed_by": "operator", "expected_pricing_draft_edit_id": pricing["saved_draft_edit_id"],
            "expected_generation": pricing["saved_generation"],
            "expected_payload_fingerprint": pricing["saved_payload_fingerprint"],
            "expected_validation_token": pricing["saved_validation_token"],
            "summary": {key: "0" for key in ("testing_fee_total", "working_hours", "lab_manpower_cost", "external_cost", "grand_cost")}}))

        staged_paths = []

        def write_document(self, **kwargs):
            path = kwargs["output_path"]
            staged_paths.append(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fake Office record with confirmed Matrix")
            return path

        def write_fee(self, **kwargs):
            path = write_document(self, **kwargs)
            return FeeEvaluationWorkbookWriteResult(output_path=path, status="generated")

        def write_feedback(self, **kwargs):
            return write_document(self, **kwargs), ()

        def write_application(self, path, fields):
            assert path != source
            path.write_bytes(b"completed Application Form")
            return SimpleNamespace(changed_fields=tuple(fields), unchanged_fields=(), warnings=())

        monkeypatch.setattr(deps.TestRecordDocumentGateway, "generate_from_confirmed_matrix", write_document)
        monkeypatch.setattr(deps.FeeEvaluationWorkbookGateway, "generate_matrix_basic_fill", write_fee)
        monkeypatch.setattr(deps.CustomerFeedbackWorkbookGateway, "generate", write_feedback)
        monkeypatch.setattr(OfficeFacade, "write_word_application_form_fields_with_owned_session", write_application)

        url = "/api/projects/P1/project-folder/generation"
        preview = _ok(client.get(url + "/preview"))
        request = {"expected_context": preview["expected_context"], "request_id": "whole-chain"}
        started = _ok(client.post(url + "/start", json=request))
        assert len(callbacks) == 1
        callbacks.pop()()  # One backend job runs all services; no further frontend write requests.
        completed = _ok(client.get(url))
        assert completed["status"] == "completed", completed
        assert completed["completed_steps"] == ["workspace", "materials", "check", "customer_feedback_form",
                                                  "fee_form", "test_record", "test_status", "application_form"]
        # Regenerable Office inputs must not inherit the durable journal's deep hash path.
        assert staged_paths
        for path in staged_paths:
            relative_parent = path.parent.relative_to(settings.data_dir)
            assert len(str(relative_parent)) < 100, relative_parent
            assert started["operation_id"] in relative_parent.parts
        with sessions() as session:
            records = deps.get_project_output_record_service(session).list_records("P1")
            assert len(records) == 5
            files = {Path(record.output_path): (Path(record.output_path).read_bytes(), Path(record.output_path).stat().st_mtime_ns)
                     for record in records}
            workspace = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
            assert workspace.official_folder_path.is_dir()
            assert workspace.official_folder_path.name == "DL-2026-05-P1 Connector Qualification Testing"
            collected = deps.ProjectRequestMaterialCollectionRepository(session).latest_by_project("P1")
            assert collected is not None
        assert source.read_bytes() == b"original submitted application"
        assert _ok(client.post(url + "/start", json=request))["operation_id"] == started["operation_id"]
        assert _ok(client.post(url + "/resume", json={"operation_id": started["operation_id"]}))["status"] == "completed"
        assert not callbacks
        assert files == {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in files}
    finally:
        app.dependency_overrides.clear()
        runner.pool.shutdown()
        engine.dispose()
