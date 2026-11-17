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



@pytest.mark.parametrize("managed", [False, True])
def test_first_project_save_creates_isolated_default_even_when_materials_library_is_offline(tmp_path, managed):
    from sqlalchemy import delete
    from backend.infrastructure.storage.models import ExternalResourceModel
    from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
    from backend.shared.config import Settings
    with prepared(tmp_path) as (client,sessions,_,_):
        project_root = tmp_path / "Projects" if managed else tmp_path / "new-default/Projects"
        isolated = Settings(tmp_path / "data", project_root, tmp_path / "templates",
            tmp_path / "connlab.sqlite3", output_root=tmp_path / "new-default",
            library_root=tmp_path if managed else None)
        app.dependency_overrides[deps.get_settings]=lambda:isolated
        with sessions() as session:
            session.execute(delete(ExternalResourceModel).where(ExternalResourceModel.resource_type==ExternalResourceType.PROJECT_OUTPUT_ROOT.value))
            MaterialReceiptRepository(session).configure(str(tmp_path/"offline-materials"))
            session.commit()
        assert not isolated.projects_dir.exists()
        result=create(client,"first-default")
        assert result["directory_available"]
        assert Path(result["official_project_folder_path"]).is_relative_to(isolated.projects_dir)
        with sessions() as session:
            assert deps.ExternalResourceRepository(session).get_by_type(ExternalResourceType.PROJECT_OUTPUT_ROOT).path==isolated.projects_dir
            assert MaterialReceiptRepository(session).settings()["root_path"]==str(tmp_path/"offline-materials")
        assert not (tmp_path/"offline-materials").exists()

        # A persisted binding that goes offline is not another first use.
        retained=isolated.projects_dir.with_name("retained-offline-copy")
        isolated.projects_dir.rename(retained)
        unavailable=client.get("/api/projects/P1/official-workspace/basic/preview")
        assert unavailable.status_code==200
        assert unavailable.json()["status"]=="blocked" and not unavailable.json()["directory_available"]
        rejected=client.post("/api/projects/P1/official-workspace/basic/create",json={"expected_context":unavailable.json()["expected_context"],"request_id":"offline-save"})
        assert rejected.status_code==409
        assert not isolated.projects_dir.exists() and retained.is_dir()
        with sessions() as session:
            assert deps.ExternalResourceRepository(session).get_by_type(ExternalResourceType.PROJECT_OUTPUT_ROOT).path==isolated.projects_dir


@pytest.mark.parametrize("environment", ["development", "release"])
@pytest.mark.parametrize("entrypoint", ["official-workspace/basic/preview", "public-folder-workflow/context", "official-workspace/preview"])
def test_description_rename_remains_usable_through_normal_folder_actions(tmp_path, monkeypatch, environment, entrypoint):
    from dataclasses import replace
    from hashlib import sha256
    from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway
    with prepared(tmp_path) as (client, sessions, _, _):
        settings = replace(app.dependency_overrides[deps.get_settings](), environment=environment)
        app.dependency_overrides[deps.get_settings] = lambda: settings
        original = Path(create(client)["official_project_folder_path"])
        nested = original / "Test results" / "中文资料"
        nested.mkdir()
        content = b"retained historical test data"
        (nested / "result.txt").write_bytes(content)
        with sessions() as session:
            deps.FileAssetRepository(session).create(FileAsset("placed", "P1", FileAssetType.ATTACHMENT,
                nested / "result.txt", sha256=sha256(content).hexdigest()))
            session.commit()
        renamed = original.with_name("DL-2026-09-002A 中文自定义描述")
        original.rename(renamed)
        first = client.get(f"/api/projects/P1/{entrypoint}")
        assert first.status_code == 200, first.text
        preview = client.get("/api/projects/P1/official-workspace/basic/preview")
        assert preview.status_code == 200, preview.text
        assert preview.json()["directory_available"], preview.json()
        assert preview.json()["official_project_folder_path"] == str(renamed)
        opened = []
        monkeypatch.setattr("backend.infrastructure.files.local_folder_open_gateway._windows_startfile", lambda path: opened.append(Path(path)))
        response = client.post("/api/projects/P1/folder/open-local")
        assert response.status_code == 200, response.text
        assert opened == [renamed]
        sync = client.post("/api/projects/P1/public-folder-workflow/sync/preview")
        assert sync.status_code == 200, sync.text
        assert sync.json()["local_official_folder_path"] == str(renamed)
        executed = client.post("/api/projects/P1/public-folder-workflow/sync/execute", json={
            "preview_hash": sync.json()["preview_hash"], "confirmed": True,
            "confirm_directory_creation": True, "confirm_existing_public_folder": True})
        assert executed.status_code == 200, executed.text
        assert executed.json()["status"] == "completed", executed.json()
        target = Path(executed.json()["preview"]["public_open_path"])
        assert (target / "Test results" / "中文资料" / "result.txt").read_bytes() == content
        with sessions() as session:
            assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1").official_folder_path == renamed
            assert deps.FileAssetRepository(session).get("placed").path == renamed / "Test results" / "中文资料" / "result.txt"
        from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
        runner = ProjectFolderGenerationRunner(sessions, settings)
        try:
            generation = runner.preview("P1")
            assert generation["workspace_preview"]["official_project_folder_path"] == str(renamed)
        finally:
            runner.pool.shutdown(wait=True)
        assert not original.exists()
        assert (renamed / "Test results" / "中文资料" / "result.txt").read_bytes() == content


@pytest.mark.parametrize("case", ["legacy_identity", "ambiguous", "replaced", "changed_root", "changed_ltr", "writer_busy", "generation_pending", "basic_pending"])
def test_automatic_description_rebind_does_not_claim_unverified_folders(tmp_path, case):
    import json
    import shutil
    from backend.infrastructure.files.generation_journal import GenerationJournal
    with prepared(tmp_path) as (client, sessions, output, _):
        original = Path(create(client)["official_project_folder_path"])
        manifest = original.parent / ".connlab" / "manifest.json"
        candidate = original.with_name("DL-2026-09-002A custom description")
        original.rename(candidate)
        if case == "legacy_identity":
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload.pop("official_folder_identity")
            manifest.write_text(json.dumps(payload), encoding="utf-8")
        elif case == "ambiguous":
            (candidate.parent / "DL-2026-09-002A second").mkdir()
        elif case == "replaced":
            retained = tmp_path / "retained-original"
            candidate.rename(retained)
            shutil.copytree(retained, candidate)
        elif case == "changed_root":
            other = tmp_path / "other-configured-root"
            other.mkdir()
            with sessions() as session:
                deps.ExternalResourceRepository(session).upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, other))
                session.commit()
        elif case == "changed_ltr":
            with sessions() as session:
                ltr = deps.LtrRecordRepository(session).list_by_project("P1")[0]
                from backend.infrastructure.storage.models import LtrRecordModel
                session.get(LtrRecordModel, ltr.ltr_id).ltr_number = "DL-2026-09-002B"
                session.commit()
        elif case in {"generation_pending", "basic_pending"}:
            name = "project_folder_generation" if case == "generation_pending" else "basic_project_workspace"
            GenerationJournal(tmp_path / "data" / name).create("P1", None, "unfinished")
        before = manifest.read_bytes()
        def check():
            preview = client.get("/api/projects/P1/official-workspace/basic/preview")
            assert preview.status_code in {200, 409}, preview.text
            if preview.status_code == 200:
                assert not preview.json()["directory_available"], preview.json()
            if case == "writer_busy":
                context = client.get("/api/projects/P1/public-folder-workflow/context")
                assert context.status_code == 409, context.text
            assert manifest.read_bytes() == before
            with sessions() as session:
                assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1").official_folder_path == original
            assert candidate.is_dir() and not original.exists()
        if case == "writer_busy":
            with GenerationJournal(tmp_path / "data/project_folder_generation").lock("P1"):
                check()
        else:
            check()


def test_description_rebind_resumes_after_manifest_update_in_a_fresh_process(tmp_path, monkeypatch):
    import json
    import os
    import subprocess
    import sys
    from backend.infrastructure.storage.repositories.official_workspace import ProjectOfficialWorkspaceRepository
    with prepared(tmp_path) as (client, sessions, _, _):
        original = Path(create(client)["official_project_folder_path"])
        renamed = original.with_name("DL-2026-09-002A interrupted custom description")
        original.rename(renamed)
        publish = ProjectOfficialWorkspaceRepository.publish_relocation
        def fail_index(*args, **kwargs):
            raise OSError("simulated index commit interruption")
        monkeypatch.setattr(ProjectOfficialWorkspaceRepository, "publish_relocation", fail_index)
        blocked = client.get("/api/projects/P1/official-workspace/basic/preview")
        assert blocked.status_code == 409, blocked.text
        assert "simulated index commit interruption" in blocked.json()["detail"]
        assert json.loads((renamed.parent / ".connlab/manifest.json").read_text(encoding="utf-8"))["official_project_folder_path"] == str(renamed)
        monkeypatch.setattr(ProjectOfficialWorkspaceRepository, "publish_relocation", publish)
        code = r"""
import json,sys
from pathlib import Path
from backend.shared.config import Settings
from backend.infrastructure.storage.database import register_models,create_database_engine,create_session_factory
from backend.api import dependencies as deps
root=Path(sys.argv[1]); settings=Settings(root/'data',root/'projects',root/'templates',root/'connlab.sqlite3')
register_models(); engine=create_database_engine(settings)
try:
 with create_session_factory(engine)() as session:
  result=deps.get_basic_project_workspace_service(session,settings).preview('P1')
  session.commit(); print(json.dumps(result))
finally: engine.dispose()
"""
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        recovered = subprocess.run([sys.executable, "-c", code, str(tmp_path)], cwd=Path(__file__).resolve().parents[2], env=env, capture_output=True, text=True, encoding="utf-8", timeout=40)
        assert recovered.returncode == 0, recovered.stderr
        result = json.loads(recovered.stdout.strip().splitlines()[-1])
        assert result["directory_available"] and result["official_project_folder_path"] == str(renamed)
        with sessions() as session:
            assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1").official_folder_path == renamed
        assert not original.exists() and renamed.is_dir()


def test_lookup_does_not_resume_a_newer_explicit_rename_after_waiting_for_the_writer(tmp_path, monkeypatch):
    from backend.infrastructure.files.generation_journal import GenerationJournal
    from backend.infrastructure.files.recoverable_output_publisher import file_identity
    from backend.infrastructure.storage.repositories.official_workspace import ProjectOfficialWorkspaceRepository
    with prepared(tmp_path) as (client, sessions, _, _):
        original = Path(create(client)["official_project_folder_path"])
        custom = original.with_name("DL-2026-09-002A retained custom description")
        original.rename(custom)
        settings = app.dependency_overrides[deps.get_settings]()
        publish = ProjectOfficialWorkspaceRepository.publish_relocation
        monkeypatch.setattr(ProjectOfficialWorkspaceRepository, "publish_relocation",
            lambda *args, **kwargs: (_ for _ in ()).throw(OSError("interrupted index")))
        assert client.get("/api/projects/P1/official-workspace/basic/preview").status_code == 409
        monkeypatch.setattr(ProjectOfficialWorkspaceRepository, "publish_relocation", publish)
        journal = GenerationJournal(settings.data_dir / "official_folder_relocation")
        first = journal.read("P1")
        assert first["strategy"] == "rebind_keep_custom" and first["status"] != "completed"
        acquire = GenerationJournal.lock
        injected = False
        @contextmanager
        def racing_lock(self, project_id):
            nonlocal injected
            if not injected and self.root == settings.data_dir / "project_folder_generation":
                injected = True
                with acquire(self, project_id):
                    with sessions() as other:
                        service = deps.get_official_folder_relocation_service(other, settings)
                        service.apply(project_id, "resume", first["context"])
                        current = ProjectOfficialWorkspaceRepository(other).get_by_project(project_id)
                        # The competing writer persisted this explicit move but stopped before moving.
                        pending = journal.create(project_id, "rename_to_confirmed", "new-explicit-move")
                        pending["effects"]["relocation"] = {
                            "source":str(custom), "target":str(original), "suggested":str(original),
                            "directory_identity":file_identity(custom), "record":current}
                        journal.save(pending)
            with acquire(self, project_id):
                yield
        monkeypatch.setattr(GenerationJournal, "lock", racing_lock)
        response = client.get("/api/projects/P1/official-workspace/basic/preview")
        assert response.status_code in {200, 409}, response.text
        assert custom.is_dir() and not original.exists()
        retained = journal.read("P1")
        assert retained["strategy"] == "rename_to_confirmed" and retained["status"] != "completed"
