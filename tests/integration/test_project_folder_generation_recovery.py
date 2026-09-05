"""New-process recovery through the real runner, SQLite and fake form generator."""

from pathlib import Path
import os
import runpy
import subprocess
import sys
import shutil
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine

from backend.api import dependencies as deps
from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
from backend.domain import Project, ProjectStatus, FileAsset, FileAssetType
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.storage.database import Base, create_session_factory
from backend.shared.config import Settings
from backend.application.project_application_form_write_back_service import ProjectApplicationFormWriteBackService
from backend.infrastructure.files.project_folder_required_forms_gateway import ProjectFolderRequiredFormsFileGateway


def _settings(root):
    return Settings(data_dir=root / "data", projects_dir=root / "projects", templates_dir=root / "templates",
                    database_path=root / "fixture.sqlite")


@pytest.mark.parametrize("missing_attachment", [False, True])
def test_materials_step_commits_warning_only_collection_but_rejects_unresolved_sources(tmp_path, missing_attachment):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    workspace, official = tmp_path / "workspace", tmp_path / "workspace" / "Official"
    official.mkdir(parents=True)
    source = tmp_path / "application.docx"
    source.write_bytes(b"submitted form")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Fixture", requestor="Test", status=ProjectStatus.DRAFT))
        deps.ProjectOfficialWorkspaceRepository(session).save(OfficialWorkspaceRecord(
            workspace_id="workspace", project_id="P1", dl_number="DL-001", local_workspace_path=workspace,
            source_book_path=workspace / "Source Book", official_folder_path=official,
            manifest_path=workspace / ".connlab" / "manifest.json", template_source_path=tmp_path / "template", created_at="2026-09-05T00:00:00+00:00"))
        deps.FileAssetRepository(session).create(FileAsset("app", "P1", FileAssetType.APPLICATION_FORM,
            source, original_name=source.name, source_role="selected_application_form"))
        if missing_attachment:
            deps.FileAssetRepository(session).create(FileAsset("attachment", "P1", FileAssetType.ATTACHMENT,
                tmp_path / "missing.pdf", original_name="missing.pdf", source_role="supporting_attachment"))
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    runner.context = lambda _: "fixture authority"
    state = runner.journal.create("P1", None, "fixture authority")
    try:
        if missing_attachment:
            with pytest.raises(ValueError, match="material|source"):
                runner.run_step(state, "materials")
        else:
            runner.run_step(state, "materials")
            with sessions() as session:
                collection = deps.ProjectRequestMaterialCollectionRepository(session).latest_by_project("P1")
                assert collection.collection_id == state["operation_id"]
                assert "Request email missing" in collection.warnings
            target = official / "Submitted Material" / source.name
            before = target.stat().st_mtime_ns
            runner.run_step(state, "materials")
            assert target.stat().st_mtime_ns == before
    finally:
        runner.pool.shutdown()
        engine.dispose()


def _child(root, mode):
    settings = _settings(root)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    sessions = create_session_factory(engine)
    fixtures = runpy.run_path(str(Path(__file__).parents[1] / "unit" / "test_project_folder_required_forms_service.py"))
    runner = ProjectFolderGenerationRunner(sessions, settings)
    state = runner.journal.read("P1")
    runner.context = lambda _: "fixture authority"
    generator = fixtures["_Generator"](root)
    if mode == "recover":
        def reject_repeat(**kwargs):
            raise AssertionError("Recovery regenerated a published form")
        generator.generate = reject_repeat
    deps.get_project_folder_required_forms_service = lambda session, settings: fixtures["_service"](
        root, output_service=deps.get_project_output_record_service(session), generator=generator)
    if mode == "before_db":
        from backend.application.project_output_record_service import ProjectOutputRecordService
        ProjectOutputRecordService.register_output = lambda *args, **kwargs: os._exit(23)
    runner.run_step(state, "customer_feedback_form")
    runner.pool.shutdown()
    engine.dispose()
    if mode == "after_db":
        os._exit(24)


def _application_child(root, mode):
    settings = _settings(root)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    runner = ProjectFolderGenerationRunner(create_session_factory(engine), settings)
    state = runner.journal.read("P1")
    runner.context = lambda _: "fixture authority"
    fixtures = runpy.run_path(str(Path(__file__).parents[1] / "unit" / "test_project_application_form_write_back_service.py"))
    official, source = root / "official", root / "source.docx"
    target = official / "Submitted Material" / "application.docx"
    class FakeOffice:
        def write_word_application_form_fields_with_owned_session(self, staged, fields):
            assert staged != target
            assert target.read_bytes() == source.read_bytes()
            if mode == "app_recover":
                raise AssertionError("Recovery repeated Office edits")
            staged.write_bytes(b"partial fake Office edit" if mode == "app_office" else b"complete fake Office result")
            if mode == "app_office":
                os._exit(41)
            return SimpleNamespace(changed_fields=(), unchanged_fields=(), warnings=())
    deps.get_project_application_form_write_back_service = lambda session, settings: ProjectApplicationFormWriteBackService(
        project_store=fixtures["_ProjectStore"](), workspace_store=fixtures["_WorkspaceStore"](official),
        application_form_store=fixtures["_ApplicationFormStore"](), file_asset_store=fixtures["_FileAssetStore"](source),
        basic_information_reader=fixtures["_BasicInformationReader"](fixtures["_basic_information"]()),
        output_record_service=deps.get_project_output_record_service(session),
        file_gateway=ProjectFolderRequiredFormsFileGateway(), office=FakeOffice(),
    )
    if mode == "app_before_db":
        from backend.application.project_output_record_service import ProjectOutputRecordService
        ProjectOutputRecordService.register_output = lambda *args, **kwargs: os._exit(42)
    runner.run_step(state, "application_form")
    runner.pool.shutdown()
    engine.dispose()
    if mode == "app_after_db":
        os._exit(43)


@pytest.mark.parametrize("window,exit_code", [("before_db", 23), ("after_db", 24)])
def test_new_process_recovers_published_output_and_committed_record_without_regeneration(tmp_path, window, exit_code):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Fixture",
                                                     requestor="Test", status=ProjectStatus.DRAFT))
        session.commit()
    journal = GenerationJournal(settings.data_dir / "project_folder_generation")
    state = journal.create("P1", None, "fixture authority")
    state.update(step=3, completed_steps=["workspace", "materials", "check"])
    journal.save(state)
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[2]))
    def run(mode):
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), str(tmp_path), mode],
                              env=env, capture_output=True, text=True, timeout=40)
    crashed = run(window)
    assert crashed.returncode == exit_code, crashed.stdout + crashed.stderr
    state = journal.read("P1")
    effect = state["effects"]["customer_feedback_form:customer_feedback_form"]
    target = Path(effect["target"])
    original_bytes, original_mtime = target.read_bytes(), target.stat().st_mtime_ns
    recovered = run("recover")
    assert recovered.returncode == 0, recovered.stdout + recovered.stderr
    recovered_again = run("recover")
    assert recovered_again.returncode == 0, recovered_again.stdout + recovered_again.stderr
    with sessions() as session:
        records = deps.get_project_output_record_service(session).list_records("P1")
        assert len(records) == 1
        assert records[0].output_path == str(target)
    assert target.read_bytes() == original_bytes
    assert target.stat().st_mtime_ns == original_mtime
    engine.dispose()


@pytest.mark.parametrize("window,exit_code", [("app_office", 41), ("app_before_db", 42), ("app_after_db", 43)])
def test_application_form_process_crash_never_edits_final_in_place_or_repeats_committed_office(tmp_path, window, exit_code):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Fixture", requestor="Test", status=ProjectStatus.DRAFT))
        session.commit()
    source, target = tmp_path / "source.docx", tmp_path / "official" / "Submitted Material" / "application.docx"
    source.write_bytes(b"original source bytes")
    target.parent.mkdir(parents=True)
    shutil.copy2(source, target)
    journal = GenerationJournal(settings.data_dir / "project_folder_generation")
    journal.create("P1", None, "fixture authority")
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[2]))
    def run(mode):
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), str(tmp_path), mode], env=env,
                              capture_output=True, text=True, timeout=40)
    crashed = run(window)
    assert crashed.returncode == exit_code, crashed.stdout + crashed.stderr
    if window == "app_office":
        assert target.read_bytes() == b"original source bytes"
        assert set(path.name for path in target.parent.iterdir()) == {"application.docx"}
        recovered = run("app_finish")
    else:
        assert target.read_bytes() == b"complete fake Office result"
        recovered = run("app_recover")
    assert recovered.returncode == 0, recovered.stdout + recovered.stderr
    before = target.stat().st_mtime_ns
    recovered_again = run("app_recover")
    assert recovered_again.returncode == 0, recovered_again.stdout + recovered_again.stderr
    assert target.read_bytes() == b"complete fake Office result"
    assert target.stat().st_mtime_ns == before
    assert source.read_bytes() == b"original source bytes"
    with sessions() as session:
        assert len(deps.get_project_output_record_service(session).list_records("P1")) == 1
    engine.dispose()


if __name__ == "__main__":
    (_application_child if sys.argv[2].startswith("app_") else _child)(Path(sys.argv[1]), sys.argv[2])
