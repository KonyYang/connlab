"""Real persisted authority and temporary-file publication, with Office at its seam."""

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import json

import pytest
from fastapi.testclient import TestClient

from backend.api import dependencies as deps
from backend.api.main import app
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_basic_information_service import ProjectBasicInformationRecord
from backend.domain import ConfirmedMatrixStatus, ExternalResource, ExternalResourceType, ExternalResourceValidationStatus
from backend.domain.confirmed_matrix_authority_models import ConfirmedMatrixDurationAuthority
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifest, OfficialWorkspaceManifestGateway
from backend.infrastructure.storage.database import create_database_engine, create_session_factory, init_db
from backend.infrastructure.storage.models import ProjectBasicInformationRecordModel, ProjectModel
from backend.infrastructure.storage.models_confirmed_matrix_authority import ConfirmedMatrixVersionModel
from backend.infrastructure.storage.repositories import ConfirmedMatrixAuthorityRepository, ExternalResourceRepository, ProjectBasicInformationRepository
from backend.infrastructure.storage.repositories.official_workspace import ProjectOfficialWorkspaceRepository
from backend.infrastructure.storage.repositories.result_dataset import ResultDatasetRepository
from backend.shared.config import Settings
from tests.unit.test_confirmed_matrix_authority_repository import _build_confirmed_snapshot, _seed_project, _seed_project_matrix_draft, _seed_source_snapshot


BASE = "/api/projects/P1/report-workspace/internal-report"


class ReportWriter:
    """Substitute the external Word boundary; all application/file/DB paths are real."""
    def __init__(self):
        self.after_write = None
        self.failure = None
        self.reports = []

    def generate(self, *, template_path, output_path, report):
        self.reports.append(report)
        output_path.write_bytes(b"fresh approved template report")
        if self.after_write:
            self.after_write()
        if self.failure:
            raise self.failure
        return output_path


@pytest.fixture
def lab(tmp_path, monkeypatch):
    settings = Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects",
                        templates_dir=tmp_path / "templates", database_path=tmp_path / "connlab.sqlite3")
    settings.data_dir.mkdir()
    settings.templates_dir.mkdir()
    template = settings.templates_dir / "E-3707_H Laboratory Test Report.docx"
    template.write_bytes(b"approved template")
    engine = create_database_engine(settings)
    init_db(engine)
    factory = create_session_factory(engine)
    with factory() as session:
        _seed_project(session)
        source_id, source = _seed_source_snapshot(session)
        draft = _seed_project_matrix_draft(session, source_id, source)
        matrix = _build_confirmed_snapshot(confirmed_matrix_id="cmv-1", draft=draft, status=ConfirmedMatrixStatus.CONFIRMED)
        matrix = replace(matrix, version=replace(matrix.version, planned_test_start_date="2026-06-01",
                         planned_test_complete_date="2026-06-10", estimated_completion_date="2026-06-12", post_test_buffer_days="2"))
        matrix = replace(matrix, duration_authorities=(ConfirmedMatrixDurationAuthority(
            "duration-1", "cmv-1", matrix.groups[0].confirmed_group_id, matrix.rows[0].confirmed_row_id,
            1, "", Decimal("2.5"), "hours", Decimal("2.5"), "manual", "duration", source_id,
            "source-fp", "lineage-fp", "1", "usable", None, None, "2026-06-01", "2026-06-01",
        ),))
        ConfirmedMatrixAuthorityRepository(session).create_snapshot(matrix)
        basic = ProjectBasicInformationRecord("basic-1", "P1", "confirmed", 1,
            {"dl_number": "DL-2026-05-001", "product_description": "Latest Connector", "test_item": "Qualification Testing",
             "applicable_specifications": "Approved Spec", "date_lab_received_samples": "2026-05-30"},
            "source-signature-1", "2026-06-01", "2026-06-01", "2026-06-01", "Operator")
        ProjectBasicInformationRepository(session).create_confirmed(basic)
        ExternalResourceRepository(session).upsert(ExternalResource("templates", ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
            settings.templates_dir, True, ExternalResourceValidationStatus.VALID))
        session.commit()

    def get_session():
        with factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[deps.get_session] = get_session
    app.dependency_overrides[deps.get_settings] = lambda: settings
    writer = ReportWriter()
    monkeypatch.setattr(deps, "TestReportDocumentGateway", lambda: writer)
    client = TestClient(app, raise_server_exceptions=False)
    yield {"settings": settings, "factory": factory, "client": client, "writer": writer, "template": template, "basic": basic, "root": tmp_path}
    app.dependency_overrides.clear()
    engine.dispose()


def official_report(lab):
    local = lab["root"] / "projects" / "DL-2026-05-001"
    official = local / "Old Connector Qualification Testing"
    official.mkdir(parents=True)
    manifest = local / ".connlab" / "manifest.json"
    record = OfficialWorkspaceRecord("workspace-1", "P1", "DL-2026-05-001", local, local / "Source Book", official, manifest, lab["settings"].templates_dir, "2026-06-01")
    OfficialWorkspaceManifestGateway().write(manifest, OfficialWorkspaceManifest(1, "P1", record.dl_number,
        str(local), str(record.source_book_path), str(official), str(record.template_source_path), record.created_at))
    with lab["factory"]() as session:
        ProjectOfficialWorkspaceRepository(session).save(record)
        ExternalResourceRepository(session).upsert(ExternalResource("project-root", ExternalResourceType.PROJECT_OUTPUT_ROOT,
            lab["root"] / "projects", True, ExternalResourceValidationStatus.VALID))
        session.commit()
    current = official / "DL-2026-05-001 Old Connector Qualification Testing Report_Rev_A.docx"
    current.write_bytes(b"operator manual results, equipment and photos")
    return current, local


def preview(lab):
    response = lab["client"].get(BASE + "/generation-preview")
    assert response.status_code == 200
    assert response.json()["status"] == "ready", response.text
    return response.json()


def generate(lab, reviewed, confirmed=False):
    return lab["client"].post(BASE + "/generate", json={"preview_token": reviewed["preview_token"], "archive_and_regenerate": confirmed})


def test_initializes_managed_report_from_latest_authority_and_rejects_duplicate_preview(lab):
    reviewed = preview(lab)
    assert reviewed["requires_confirmation"] is False
    assert not lab["writer"].reports
    response = generate(lab, reviewed)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["file_name"] == "DL-2026-05-001 Latest Connector Qualification Testing Report_Rev_A_Draft.docx"
    current = lab["client"].get("/api/projects/P1/report-workspace/current-report").json()
    assert current["file_path"] == result["file_path"]
    assert current["mode"] == "managed_draft"
    assert generate(lab, reviewed).status_code == 409
    workspace = lab["client"].get("/api/projects/P1/report-workspace").json()
    assert len(workspace["report_revisions"]) == 1
    assert workspace["latest_report_revision"]["result_dataset_id"] is None
    with lab["factory"]() as session:
        assert session.get(ProjectModel, "P1").registry_revision == 1


def test_archives_manual_report_and_renames_from_latest_basic_information(lab):
    current, local = official_report(lab)
    reviewed = preview(lab)
    assert reviewed["requires_confirmation"]
    assert generate(lab, reviewed).status_code == 409
    assert not lab["writer"].reports
    assert current.read_bytes().startswith(b"operator manual")
    response = generate(lab, reviewed, True)
    assert response.status_code == 200, response.text
    result = response.json()
    assert Path(result["archive_path"]).parent == local / "History" / "Report"
    assert Path(result["archive_path"]).read_bytes() == b"operator manual results, equipment and photos"
    assert not current.exists()
    assert result["file_name"] == "DL-2026-05-001 Latest Connector Qualification Testing Report_Rev_A.docx"
    assert list(current.parent.glob("*.docx")) == [Path(result["file_path"])]
    assert generate(lab, reviewed, True).status_code == 409


@pytest.mark.parametrize("change", ["basic", "basic_values", "matrix", "template", "report", "workspace"])
def test_authority_changes_during_word_generation_preserve_the_current_report(lab, change):
    current, local = official_report(lab)
    original = current.read_bytes()
    reviewed = preview(lab)

    def change_source():
        if change == "basic":
            with lab["factory"]() as session:
                basic = replace(lab["basic"], record_id="basic-2", version=2, values={**lab["basic"].values, "product_description": "New authority"})
                ProjectBasicInformationRepository(session).create_confirmed(basic)
                session.commit()
        elif change == "basic_values":
            with lab["factory"]() as session:
                row = session.get(ProjectBasicInformationRecordModel, "basic-1")
                row.values_json = json.dumps({**lab["basic"].values, "product_description": "Changed same record"})
                session.commit()
        elif change == "matrix":
            with lab["factory"]() as session:
                row = session.get(ConfirmedMatrixVersionModel, "cmv-1")
                row.confirmed_revision = 2
                session.commit()
        elif change == "template":
            lab["template"].write_bytes(b"new template")
        elif change == "report":
            current.write_bytes(b"new manual edit")
        else:
            with lab["factory"]() as session:
                record = ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
            record.manifest_path.write_text('{"project_id": "foreign"}', encoding="utf-8")

    lab["writer"].after_write = change_source
    response = generate(lab, reviewed, True)
    assert response.status_code == 409, response.text
    assert current.read_bytes() == (b"new manual edit" if change == "report" else original)
    assert not (local / "History").exists()
    assert list(current.parent.glob("*.docx")) == [current]
    assert not list((lab["settings"].data_dir / "internal_report_staging").iterdir())


def test_metadata_commit_failure_restores_old_report_without_orphan_history(lab, monkeypatch):
    current, local = official_report(lab)
    reviewed = preview(lab)
    monkeypatch.setattr(ResultDatasetRepository, "commit", lambda self: (_ for _ in ()).throw(RuntimeError("metadata unavailable")))
    response = generate(lab, reviewed, True)
    assert response.status_code == 500
    assert "preview again" in response.json()["detail"]
    assert current.read_bytes().startswith(b"operator manual")
    assert list(current.parent.glob("*.docx")) == [current]
    assert not (local / "History").exists()
    with lab["factory"]() as session:
        assert ResultDatasetRepository(session).list_report_revisions("P1") == ()
        assert session.get(ProjectModel, "P1").registry_revision == 0


def test_pending_folder_operation_blocks_every_retained_report_writer(lab):
    journal = GenerationJournal(lab["settings"].data_dir / "project_folder_generation")
    journal.create("P1", None, "test operation")
    endpoints = [(BASE + "/generate", {"preview_token": "a" * 64}),
        ("/api/projects/P1/report-workspace/initial-drafts", {}),
        ("/api/projects/P1/report-workspace/llcr-drafts", {"dataset_id": "dataset"}),
        ("/api/projects/P1/report-workspace/current-report/publish", {"expected_report_sha256": "a" * 64}),
        ("/api/projects/P1/report-workspace/current-report/llcr", {"dataset_id": "dataset", "expected_report_sha256": "a" * 64}),
        ("/api/projects/P1/report-workspace/current-report/equipment", {"expected_report_sha256": "a" * 64, "expected_source_sha256": "a" * 64, "expected_catalog_sha256": "a" * 64})]
    for endpoint, body in endpoints:
        response = lab["client"].post(endpoint, json=body)
        assert response.status_code == 409, (endpoint, response.text)
        assert "unfinished" in response.json()["detail"]
    assert not lab["writer"].reports


def test_cached_request_authority_does_not_override_fresh_confirmed_values(lab):
    with lab["factory"]() as cached:
        # Keep a strong reference: SQLAlchemy otherwise releases this cached row.
        old_row = cached.get(ProjectBasicInformationRecordModel, "basic-1")
        assert old_row is not None
        with lab["factory"]() as changed:
            row = changed.get(ProjectBasicInformationRecordModel, "basic-1")
            row.values_json = json.dumps({**lab["basic"].values, "product_description": "Fresh confirmed description"})
            changed.commit()

        def cached_session():
            yield cached

        app.dependency_overrides[deps.get_session] = cached_session
        reviewed = preview(lab)
        assert "Fresh confirmed description" in reviewed["target_path"]
        response = generate(lab, reviewed)
        assert response.status_code == 200, response.text
        assert "Fresh confirmed description" in response.json()["file_name"]
        assert lab["writer"].reports[0].product_name == "Fresh confirmed description"


def test_writer_failure_leaves_manual_report_and_history_untouched(lab):
    current, local = official_report(lab)
    reviewed = preview(lab)
    lab["writer"].failure = RuntimeError("Word output validation failed")
    response = generate(lab, reviewed, True)
    assert response.status_code == 409
    assert "approved template" in response.json()["detail"]
    assert current.read_bytes().startswith(b"operator manual")
    assert not (local / "History").exists()
    assert not list((lab["settings"].data_dir / "internal_report_staging").iterdir())


def test_identical_regeneration_archives_and_invalidates_the_used_preview(lab):
    current, local = official_report(lab)
    initialized = generate(lab, preview(lab), True)
    assert initialized.status_code == 200
    current = Path(initialized.json()["file_path"])
    reviewed = preview(lab)
    response = generate(lab, reviewed, True)
    assert response.status_code == 200, response.text
    assert Path(response.json()["archive_path"]).read_bytes() == current.read_bytes()
    assert generate(lab, reviewed, True).status_code == 409
    assert len(list((local / "History" / "Report").glob("*.docx"))) == 2
    with lab["factory"]() as session:
        assert session.get(ProjectModel, "P1").registry_revision == 2
    workspace = lab["client"].get("/api/projects/P1/report-workspace").json()
    archived_revision = workspace["report_revisions"][0]
    download = lab["client"].get(archived_revision["download_url"])
    assert download.status_code == 200
    assert download.content == b"fresh approved template report"


def test_overlapping_report_writer_cannot_enter_generation(lab):
    reviewed = preview(lab)
    journal = GenerationJournal(lab["settings"].data_dir / "project_folder_generation")
    with journal.lock("P1"):
        response = generate(lab, reviewed)
    assert response.status_code == 409
    assert "already running" in response.json()["detail"]
    assert not lab["writer"].reports


def test_legacy_initial_generation_cannot_silently_duplicate_an_existing_official_report(lab):
    current, _ = official_report(lab)
    response = lab["client"].post("/api/projects/P1/report-workspace/initial-drafts", json={})
    assert response.status_code == 422
    assert "Archive and regenerate" in response.json()["detail"]
    assert list(current.parent.glob("*.docx")) == [current]
    assert not lab["writer"].reports


def test_no_report_preview_cannot_publish_over_an_operator_report_created_during_generation(lab):
    reviewed = preview(lab)
    foreign = Path(reviewed["target_path"])

    def create_operator_report():
        foreign.parent.mkdir(parents=True, exist_ok=True)
        foreign.write_bytes(b"operator report")

    lab["writer"].after_write = create_operator_report
    response = generate(lab, reviewed)
    assert response.status_code == 409
    assert foreign.read_bytes() == b"operator report"
    assert not (foreign.parent / "History").exists()


@pytest.mark.parametrize("state", ["missing_template", "ambiguous_template", "missing_basic", "missing_matrix", "missing_folder", "ambiguous_reports"])
def test_generation_preview_has_actionable_blockers_without_writing(lab, state):
    if state == "missing_template":
        lab["template"].unlink()
    elif state == "ambiguous_template":
        lab["template"].with_name("E-3707_H Duplicate.docx").write_bytes(b"other template")
    elif state in {"missing_basic", "missing_matrix"}:
        with lab["factory"]() as session:
            if state == "missing_basic":
                session.get(ProjectBasicInformationRecordModel, "basic-1").status = "draft"
            else:
                session.get(ConfirmedMatrixVersionModel, "cmv-1").is_active_authority = False
            session.commit()
    else:
        current, _ = official_report(lab)
        if state == "missing_folder":
            current.parent.rename(current.parent.with_name("operator renamed folder"))
        else:
            current.with_name("DL-2026-05-001 Other Report_Rev_A.docx").write_bytes(b"other manual report")
    response = lab["client"].get(BASE + "/generation-preview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["preview_token"] is None
    assert payload["blockers"]
    assert not lab["writer"].reports
    assert not (lab["settings"].data_dir / "internal_report_staging").exists()
