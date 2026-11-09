from contextlib import contextmanager
from datetime import date
from pathlib import Path
import runpy
import pytest

from backend.api.main import app
from backend.api import dependencies as deps
from backend.domain import ExternalResource, ExternalResourceType, LtrRecord, LtrStatus, FileAsset, FileAssetType


@contextmanager
def prepared(tmp_path):
    fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
    client, engine, sessions = fixture["_client"](tmp_path)
    try:
        fixture["_seed_project"]("P1", tmp_path)
        output, public = tmp_path / "output", tmp_path / "public"
        output.mkdir()
        (public / "Open projects" / "2026").mkdir(parents=True)
        with sessions() as session:
            deps.LtrRecordRepository(session).create(LtrRecord("ltr", "P1", "DL-2026-09-002A", LtrStatus.REGISTERED, registered_on=date(2026, 9, 1)))
            resources = deps.ExternalResourceRepository(session)
            resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, output))
            resources.upsert(ExternalResource("public", ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT, public))
            session.commit()
        yield client, sessions, output, public
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def create(client, request_id="create"):
    preview = client.get("/api/projects/P1/official-workspace/basic/preview")
    assert preview.status_code == 200, preview.text
    response = client.post("/api/projects/P1/official-workspace/basic/create", json={
        "expected_context": preview.json()["expected_context"], "request_id": request_id})
    assert response.status_code == 200, response.text
    return response.json()


def test_basic_api_creates_and_opens_without_authorities_templates_and_preserves_manual_files(tmp_path, monkeypatch):
    from backend.application.project_request_material_collection_service import ProjectRequestMaterialCollectionService
    with prepared(tmp_path) as (client, sessions, output, _):
        missing = tmp_path / "missing.pdf"
        source = tmp_path / "mail.msg"
        source.write_bytes(b"original mail")
        with sessions() as session:
            assets = deps.FileAssetRepository(session)
            assets.create(FileAsset("mail", "P1", FileAssetType.ATTACHMENT, source, original_name="mail.msg", source_role="email_source"))
            assets.create(FileAsset("missing", "P1", FileAssetType.ATTACHMENT, missing, original_name="missing.pdf", source_role="supporting_attachment"))
            session.commit()
        original = ProjectRequestMaterialCollectionService.collect_available
        observed = []
        def archive(self, project_id, *args):
            with sessions() as other:
                record = deps.ProjectOfficialWorkspaceRepository(other).get_by_project(project_id)
                assert record is not None and record.creation_kind == "basic"
                observed.append(record.official_folder_path)
            return original(self, project_id, *args)
        monkeypatch.setattr(ProjectRequestMaterialCollectionService, "collect_available", archive)
        result = create(client)
        folder = Path(result["official_project_folder_path"])
        assert result["directory_available"] and result["status"] == "completed"
        assert observed == [folder]
        assert (folder / "E-mail" / "mail.msg").read_bytes() == b"original mail"
        assert any("missing.pdf" in item for item in result["issues"])
        manual = folder / "Test results" / "operator.xlsx"
        manual.write_bytes(b"manual result")
        missing.write_bytes(b"late material")
        assert create(client, "retry")["official_project_folder_path"] == str(folder)
        assert (folder / "Submitted Material" / "missing.pdf").read_bytes() == b"late material"
        assert manual.read_bytes() == b"manual result"
        context = client.get("/api/projects/P1/public-folder-workflow/context").json()
        assert context["local_official_folder_available"] is True
        assert not any(folder.glob("*.xlsx"))


def test_basic_api_rejects_unknown_existing_without_confirmation(tmp_path):
    with prepared(tmp_path) as (client, _, _, _):
        endpoint = "/api/projects/P1/official-workspace/basic"
        preview = client.get(endpoint + "/preview").json()
        folder = Path(preview["official_project_folder_path"])
        folder.mkdir(parents=True)
        (folder / "colleague.txt").write_bytes(b"retain")
        preview = client.get(endpoint + "/preview").json()
        body = {"expected_context": preview["expected_context"], "request_id": "confirmed"}
        assert client.post(endpoint + "/create", json=body).status_code == 409
        body["confirm_existing"] = True
        assert client.post(endpoint + "/create", json=body).status_code == 200
        assert (folder / "colleague.txt").read_bytes() == b"retain"


def test_basic_pending_operation_blocks_legacy_writer_and_resumes_via_http(tmp_path, monkeypatch):
    from backend.infrastructure.files.basic_project_workspace_publisher import BasicProjectWorkspacePublisher
    with prepared(tmp_path) as (client, sessions, _, _):
        original = BasicProjectWorkspacePublisher.manifest
        monkeypatch.setattr(BasicProjectWorkspacePublisher, "manifest", lambda *_: (_ for _ in ()).throw(OSError("manifest disconnected")))
        endpoint = "/api/projects/P1/official-workspace/basic"
        preview = client.get(endpoint + "/preview").json()
        response = client.post(endpoint + "/create", json={"expected_context": preview["expected_context"], "request_id": "interrupted"})
        assert response.status_code == 409
        legacy = client.post("/api/projects/P1/official-workspace/create", json={})
        assert legacy.status_code == 409 and "basic" in legacy.json()["detail"].lower()
        monkeypatch.setattr(BasicProjectWorkspacePublisher, "manifest", original)
        recovery = client.get(endpoint + "/preview").json()
        assert recovery["status"] == "recovery_required"
        resumed = client.post(endpoint + "/resume", json={"operation_id": recovery["operation_id"]})
        assert resumed.status_code == 200, resumed.text
        assert resumed.json()["directory_available"]


def test_basic_api_uses_same_canonical_lock_and_preserves_other_writer(tmp_path):
    from backend.infrastructure.files.generation_journal import GenerationJournal
    with prepared(tmp_path) as (client, sessions, _, _):
        endpoint = "/api/projects/P1/official-workspace/basic"
        preview = client.get(endpoint + "/preview").json()
        journal = GenerationJournal(tmp_path / "data" / "project_folder_generation")
        with journal.lock("P1"):
            denied = client.post(endpoint + "/create", json={"expected_context": preview["expected_context"], "request_id": "concurrent"})
            assert denied.status_code == 409 and "running" in denied.json()["detail"]
        with sessions() as session:
            assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1") is None
        assert create(client)["directory_available"]
