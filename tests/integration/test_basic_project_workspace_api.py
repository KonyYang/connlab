from contextlib import contextmanager
from datetime import date
from pathlib import Path
import runpy
import shutil
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


@pytest.mark.parametrize("case", ["legacy_identity", "ambiguous", "replaced", "changed_ltr", "writer_busy", "generation_pending", "basic_pending"])
@pytest.mark.parametrize("change_default", [False, True])
def test_automatic_description_rebind_does_not_claim_unverified_folders(tmp_path, case, change_default):
    import json
    import shutil
    from backend.infrastructure.files.generation_journal import GenerationJournal
    with prepared(tmp_path) as (client, sessions, output, _):
        original = Path(create(client)["official_project_folder_path"])
        manifest = original.parent / ".connlab" / "manifest.json"
        candidate = original.with_name("DL-2026-09-002A custom description")
        original.rename(candidate)
        if change_default:
            new_root = tmp_path / "new-default"
            new_root.mkdir()
            with sessions() as session:
                deps.ExternalResourceRepository(session).upsert(
                    ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, new_root))
                session.commit()
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


@pytest.mark.parametrize("environment", ["development", "release"])
@pytest.mark.parametrize("default_state", ["available", "offline"])
@pytest.mark.parametrize("rename", [False, True])
def test_registered_workspace_survives_default_location_change(tmp_path, monkeypatch, environment, default_state, rename):
    from dataclasses import replace
    from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
    from backend.application.project_folder_open_service import ProjectFolderOpenResult
    from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway

    with prepared(tmp_path) as (client, sessions, output, _):
        settings = replace(app.dependency_overrides[deps.get_settings](), environment=environment)
        app.dependency_overrides[deps.get_settings] = lambda: settings
        original = Path(create(client)["official_project_folder_path"])
        # Search reads the explicit library index, not a live directory scan.
        from backend.api.routes_project_library import get_library_search_service
        with sessions() as session:
            get_library_search_service(session).refresh()
            session.commit()
        manual = original / "Test results" / "manual.txt"
        manual.write_bytes(b"operator-owned content")
        expected = original
        if rename:
            expected = original.with_name("DL-2026-09-002A revised description")
            original.rename(expected)
        new_root = tmp_path / "new-default"
        if default_state == "available":
            new_root.mkdir()
        with sessions() as session:
            deps.ExternalResourceRepository(session).upsert(
                ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, new_root))
            session.commit()

        basic = client.get("/api/projects/P1/official-workspace/basic/preview")
        assert basic.status_code == 200, basic.text
        assert basic.json()["status"] == "available", basic.text
        assert basic.json()["official_project_folder_path"] == str(expected)
        workspace = client.get("/api/projects/P1/official-workspace/preview")
        assert workspace.status_code == 200, workspace.text
        assert workspace.json()["status"] == "completed", workspace.text
        assert workspace.json()["official_project_folder_path"] == str(expected)
        assert create(client, "after-default-change")["official_project_folder_path"] == str(expected)

        opened = []
        monkeypatch.setattr(LocalFolderOpenGateway, "open_directory", lambda self, path: opened.append(path) or
            ProjectFolderOpenResult("", "opened", "opened", path))
        response = client.post("/api/projects/P1/folder/open-local")
        assert response.status_code == 200, response.text
        assert opened == [expected]
        catalog = client.get("/api/project-library/search").json()["projects"]
        entry = next(row for row in catalog if row["project_id"] == "P1")
        assert entry["available"] and entry["folder_path"] == str(expected.parent)
        session_id = client.post("/api/material-receipts/copy-context/session").json()["session_id"]
        target = client.post("/api/material-receipts/copy-context", json={
            "session_id": session_id, "intent": 1, "project_id": "P1"})
        assert target.status_code == 200, target.text
        assert target.json()["target"]["folder_path"] == str(expected.parent)
        runner = ProjectFolderGenerationRunner(sessions, settings)
        try:
            generated = runner.preview("P1")
            assert generated["workspace_preview"]["official_project_folder_path"] == str(expected)
        finally:
            runner.pool.shutdown(wait=True)
        assert (expected / "Test results" / "manual.txt").read_bytes() == b"operator-owned content"
        assert not (new_root / "DL-2026-09-002A").exists()
        assert new_root.exists() == (default_state == "available")

        fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
        fixture["_seed_project"]("P2", tmp_path)
        with sessions() as session:
            deps.LtrRecordRepository(session).create(LtrRecord("ltr2", "P2", "DL-2026-09-003", LtrStatus.REGISTERED))
            session.commit()
        second = client.get("/api/projects/P2/official-workspace/basic/preview")
        assert second.status_code == 200, second.text
        if default_state == "offline":
            assert second.json()["status"] == "blocked"
            assert not new_root.exists()
        else:
            created = client.post("/api/projects/P2/official-workspace/basic/create", json={
                "expected_context": second.json()["expected_context"], "request_id": "new-project"})
            assert created.status_code == 200, created.text
            assert Path(created.json()["official_project_folder_path"]).is_relative_to(new_root)


def test_missing_registered_workspace_does_not_fall_back_to_new_default(tmp_path):
    with prepared(tmp_path) as (client, sessions, output, _):
        original = Path(create(client)["official_project_folder_path"])
        old_workspace = original.parent
        old_workspace.rename(tmp_path / "retained-workspace")
        new_root = tmp_path / "new-default"
        new_root.mkdir()
        with sessions() as session:
            deps.ExternalResourceRepository(session).upsert(
                ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, new_root))
            session.commit()
        preview = client.get("/api/projects/P1/official-workspace/preview")
        assert preview.status_code == 200, preview.text
        assert preview.json()["status"] in {"blocked", "inconsistent"}, preview.text
        assert preview.json()["official_project_folder_path"] == str(original), preview.text
        assert not list(new_root.iterdir())
        with sessions() as session:
            assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1").official_folder_path == original

@pytest.mark.parametrize("strategy", ["relink", "recreate"])
def test_resolve_missing_workspace_through_project_actions(tmp_path, strategy):
    with prepared(tmp_path) as (client, sessions, original_root, _):
        old_folder = Path(create(client)["official_project_folder_path"])
        manual_name = "operator notes.txt"
        (old_folder / manual_name).write_text("manual work", encoding="utf-8")
        fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
        fixture["_seed_project"]("P2", tmp_path)
        with sessions() as session:
            deps.LtrRecordRepository(session).create(LtrRecord("ltr2", "P2", "DL-2026-09-003", LtrStatus.REGISTERED))
            deps.FileAssetRepository(session).create(
                FileAsset("historical", "P1", FileAssetType.ATTACHMENT, old_folder / manual_name))
            session.commit()
        second = "/api/projects/P2/official-workspace/basic"
        second_context = client.get(second + "/preview").json()["expected_context"]
        second_created = client.post(second + "/create", json={"expected_context": second_context, "request_id": "create-p2"})
        assert second_created.status_code == 200, second_created.text
        other_folder = Path(second_created.json()["official_project_folder_path"])
        new_parent = tmp_path / "selected"
        new_parent.mkdir()
        restored = original_root.rename(tmp_path / "restored")
        saved_copy = restored / old_folder.relative_to(original_root)
        base = "/api/projects/P1/official-workspace"
        basic = client.get(base + "/basic/preview").json()
        assert basic["resolution_required"] and basic["registered_folder_path"] == str(old_folder)
        if strategy == "relink":
            backup_workspace = shutil.copytree(saved_copy.parent, new_parent / saved_copy.parent.name)
            target = backup_workspace / saved_copy.name
        else:
            target = new_parent
        body = {"strategy": strategy, "path": str(target)}
        preview = client.post(base + "/resolution/preview", json=body)
        assert preview.status_code == 200, preview.text
        assert preview.json()["old_path"] == str(old_folder)
        if strategy == "recreate":
            assert not list(new_parent.iterdir())
        apply = {**body, "expected_context": preview.json()["expected_context"], "request_id": "resolve-one"}
        response = client.post(base + "/resolution/apply", json=apply)
        assert response.status_code == 200, response.text
        assert response.json()["directory_available"]
        destination = Path(response.json()["official_project_folder_path"])
        assert str(destination) == preview.json()["target_path"]
        assert (destination / manual_name).exists() == (strategy == "relink")
        assert (saved_copy / manual_name).read_text(encoding="utf-8") == "manual work"
        assert not old_folder.exists()
        refreshed = client.get(base + "/basic/preview").json()
        assert refreshed["directory_available"] and not refreshed.get("resolution_required")
        assert Path(refreshed["official_project_folder_path"]) == destination
        with sessions() as session:
            assert deps.FileAssetRepository(session).get("historical").path == old_folder / manual_name
            assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P2").official_folder_path == other_folder
        assert client.get(second + "/preview").json()["resolution_required"]
        replay = client.post(base + "/resolution/apply", json=apply)
        assert replay.status_code == 200 and replay.json()["operation_id"] == response.json()["operation_id"]


def test_resolve_rechecks_default_location_before_applying(tmp_path):
    with prepared(tmp_path) as (client, sessions, original_root, _):
        old_folder = Path(create(client)["official_project_folder_path"])
        original_root.rename(tmp_path / "offline-copy")
        endpoint = "/api/projects/P1/official-workspace/resolution"
        body = {"strategy": "recreate"}
        assert client.post(endpoint + "/preview", json=body).status_code == 409
        assert not original_root.exists()

        current_default = tmp_path / "new-default"
        current_default.mkdir()
        def set_default(path):
            with sessions() as session:
                deps.ExternalResourceRepository(session).upsert(
                    ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, path))
                session.commit()
        set_default(current_default)
        preview = client.post(endpoint + "/preview", json=body)
        assert preview.status_code == 200, preview.text
        assert Path(preview.json()["target_path"]).is_relative_to(current_default)
        assert tuple(current_default.iterdir()) == ()
        changed_default = tmp_path / "latest-default"
        changed_default.mkdir()
        set_default(changed_default)
        apply = {**body, "expected_context": preview.json()["expected_context"], "request_id": "default-location"}
        assert client.post(endpoint + "/apply", json=apply).status_code == 409
        assert tuple(current_default.iterdir()) == tuple(changed_default.iterdir()) == ()
        with sessions() as session:
            assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1").official_folder_path == old_folder


def test_interrupted_resolution_can_keep_reconnected_folder(tmp_path, monkeypatch):
    with prepared(tmp_path) as (client, sessions, root, _):
        old_folder = Path(create(client)["official_project_folder_path"])
        offline = root.rename(tmp_path / "offline-copy")
        destination = tmp_path / "alternative"
        destination.mkdir()
        endpoint = "/api/projects/P1/official-workspace"
        choice = {"strategy": "recreate", "path": str(destination)}
        review = client.post(endpoint + "/resolution/preview", json=choice).json()
        def unavailable(*args):
            raise OSError("isolated binding interruption")
        with monkeypatch.context() as patch:
            patch.setattr(deps.ProjectOfficialWorkspaceRepository, "save", unavailable)
            result = client.post(endpoint + "/resolution/apply", json={
                **choice, "expected_context": review["expected_context"], "request_id": "interrupted"})
            assert result.status_code == 409, result.text
        offline.rename(root)
        pending = client.get(endpoint + "/basic/preview").json()["resolution_operation_id"]
        assert pending
        result = client.post(endpoint + "/resolution/abandon", json={"operation_id": pending})
        assert result.status_code == 200, result.text
        assert result.json()["status"] == "abandoned" and result.json()["directory_available"]
        refreshed = client.get(endpoint + "/basic/preview").json()
        assert refreshed["directory_available"] and not refreshed["resolution_operation_id"]
        assert Path(refreshed["official_project_folder_path"]) == old_folder
        assert Path(review["target_path"]).is_dir()
