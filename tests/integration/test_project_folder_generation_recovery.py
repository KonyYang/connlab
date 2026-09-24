"""New-process recovery through the real runner, SQLite and fake form generator."""

from pathlib import Path
import json
import os
import runpy
import subprocess
import sys
import shutil
import stat
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine

from backend.api import dependencies as deps
from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
from backend.domain import Project, ProjectStatus, FileAsset, FileAssetType, LtrRecord, LtrStatus
from backend.domain import ExternalResource, ExternalResourceType
from backend.application.official_project_workspace_service import OfficialWorkspacePreview, OfficialWorkspaceRecord
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.recoverable_workspace_publisher import RecoverableWorkspacePublisher
from backend.infrastructure.official_workspace_manifest import (
    OfficialWorkspaceManifest, OfficialWorkspaceManifestGateway, stable_folder_identity,
)
from backend.infrastructure.storage.database import Base, create_session_factory
from backend.shared.config import Settings
from backend.application.project_application_form_write_back_service import ProjectApplicationFormWriteBackService
from backend.infrastructure.files.project_folder_required_forms_gateway import ProjectFolderRequiredFormsFileGateway


def _settings(root):
    return Settings(data_dir=root / "data", projects_dir=root / "projects", templates_dir=root / "templates",
                    database_path=root / "fixture.sqlite")


def test_recoverable_backup_archives_only_active_ltr_child_under_history(tmp_path):
    workspace = tmp_path / "projects" / "DL-001"
    official = workspace / "DL-001 Original"
    official.mkdir(parents=True)
    (workspace / "Source Book").mkdir()
    (workspace / "History").mkdir()
    (workspace / "History" / "existing.txt").write_text("keep", encoding="utf-8")
    (official / "operator.txt").write_text("keep", encoding="utf-8")
    template = tmp_path / "template"
    template.mkdir()
    (template / "template.txt").write_text("new", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=workspace.parent,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="completed", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(official,),
    )
    journal = GenerationJournal(tmp_path / "journal")
    state = journal.create("P1", "backup_and_recreate", "fixture")

    class Repository:
        def save(self, record):
            return record

    result = RecoverableWorkspacePublisher(journal, state).create(
        preview, "backup_and_recreate", Repository()
    )

    archives = list((workspace / "History" / "Folders").glob("DL-001 Original [0-9]*"))
    assert len(archives) == 1
    assert (archives[0] / "operator.txt").read_text(encoding="utf-8") == "keep"
    assert (workspace / "History" / "existing.txt").read_text(encoding="utf-8") == "keep"
    assert (result.official_folder_path / "template.txt").read_text(encoding="utf-8") == "new"
    assert json.loads(result.record.manifest_path.read_text(encoding="utf-8"))[
        "official_folder_identity"
    ] == [result.official_folder_path.stat().st_dev, result.official_folder_path.stat().st_ino]


@pytest.mark.parametrize("legacy_manifest", [False, True])
def test_runner_update_in_place_reuses_verified_custom_folder_without_rebuilding(tmp_path, legacy_manifest):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    template = tmp_path / "template"
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "new-template-file.txt").write_text("new", encoding="utf-8")
    output = tmp_path / "output"
    output.mkdir()
    workspace = output / "DL-001"
    custom = workspace / "DL-001 Operator Custom"
    custom.mkdir(parents=True)
    (workspace / "Source Book").mkdir()
    operator_file = custom / "operator.txt"
    operator_file.write_text("keep", encoding="utf-8")
    manifest_path = workspace / ".connlab" / "manifest.json"
    record = OfficialWorkspaceRecord(
        "workspace-1", "P1", "DL-001", workspace, workspace / "Source Book",
        custom, manifest_path, template, "2026-09-25T00:00:00+00:00",
    )
    OfficialWorkspaceManifestGateway().write_adoption(manifest_path, OfficialWorkspaceManifest(
        1, "P1", "DL-001", str(workspace), str(workspace / "Source Book"),
        str(custom), str(template), record.created_at,
        None if legacy_manifest else stable_folder_identity(custom),
        "DL-001 Connector Qualification Testing",
    ))
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(
            project_id="P1", project_no="DL-001", product_name="Connector",
            requestor="Test", status=ProjectStatus.DRAFT,
        ))
        deps.LtrRecordRepository(session).create(LtrRecord(
            "ltr", "P1", "DL-001", LtrStatus.REGISTERED,
        ))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, output))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        deps.ProjectOfficialWorkspaceRepository(session).save(record)
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    runner.context = lambda _project_id: "fixture"
    runner.preview_context_matches = lambda *_args, **_kwargs: True
    state = runner.journal.create("P1", "update_in_place", "fixture")
    state.update(preview_context="fixture", preview_context_version=2)
    runner.journal.save(state)
    try:
        runner.run_step(state, "workspace")
        with sessions() as session:
            retained = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
        assert retained.official_folder_path == custom
        assert operator_file.read_text(encoding="utf-8") == "keep"
        assert not (custom / "new-template-file.txt").exists()
        assert not (workspace / "History").exists()
        assert state["workspace_directories"]["official_folder_path"]["identity"] == stable_folder_identity(custom)
    finally:
        runner.pool.shutdown()
        engine.dispose()


@pytest.mark.skipif(os.name != "nt", reason="Windows readonly deletion semantics")
@pytest.mark.parametrize("input_change", ["first_denial", "after_chmod", None])
def test_runner_revalidates_real_inputs_around_readonly_cleanup(tmp_path, monkeypatch, input_change):
    # Runner.context loads schedule storage lazily; register it before fixture DDL.
    from backend.infrastructure.storage import models_project_schedule  # noqa: F401

    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    source = tmp_path / "source.txt"
    source.write_text("approved input", encoding="utf-8")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(
            project_id="P1", project_no="DL-001", product_name="Fixture",
            requestor="Test", status=ProjectStatus.DRAFT,
        ))
        deps.FileAssetRepository(session).create(FileAsset(
            "attachment", "P1", FileAssetType.ATTACHMENT, source,
            original_name=source.name, source_role="supporting_attachment",
        ))
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    workspace = tmp_path / "workspace"
    official, template = workspace / "Official", tmp_path / "template"
    official.mkdir(parents=True)
    template.mkdir()
    (official / "old.txt").write_text("previous output", encoding="utf-8")
    (template / "new.txt").write_text("generated output", encoding="utf-8")
    preview = OfficialWorkspacePreview(
        project_id="P1", dl_number="DL-001", local_workspace_root=tmp_path,
        local_workspace_path=workspace, source_book_path=workspace / "Source Book",
        template_path=template, official_folder_path=official,
        manifest_path=workspace / ".connlab" / "manifest.json",
        template_root_mode="template_root", status="exists", blockers=(), warnings=(),
        planned_paths=(), conflict_paths=(official,),
    )
    target = None
    real_unlink, real_chmod = Path.unlink, Path.chmod
    attempts, attribute_changes = [], []
    try:
        state = runner.journal.create("P1", "overwrite_rebuild", runner.context("P1"))
        with sessions() as session:
            RecoverableWorkspacePublisher(runner.journal, state).create(
                preview, "overwrite_rebuild", deps.ProjectOfficialWorkspaceRepository(session)
            )
            session.commit()
        backup = Path(state["effects"]["workspace"]["backup"])
        target = backup / "old.txt"
        target.chmod(stat.S_IREAD)

        def unlink(path, *args, **kwargs):
            if path == target:
                attempts.append(path)
            try:
                return real_unlink(path, *args, **kwargs)
            except PermissionError:
                if path == target and input_change == "first_denial":
                    source.write_text("changed input", encoding="utf-8")
                raise

        def chmod(path, *args, **kwargs):
            result = real_chmod(path, *args, **kwargs)
            if path == target:
                attribute_changes.append(path)
                if input_change == "after_chmod":
                    source.write_text("changed input", encoding="utf-8")
            return result

        monkeypatch.setattr(Path, "unlink", unlink)
        monkeypatch.setattr(Path, "chmod", chmod)
        if input_change is not None:
            with pytest.raises(ValueError, match="Generation inputs changed"):
                runner.finalize(state)
            assert target.read_text(encoding="utf-8") == "previous output"
            assert len(attempts) == 1
            assert len(attribute_changes) == (1 if input_change == "after_chmod" else 0)
            assert bool(target.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY) == (
                input_change == "first_denial"
            )
            assert not runner.journal.read("P1")["effects"]["workspace"].get("overwrite_deleted")
        else:
            runner.finalize(state)
            assert not backup.exists()
            assert len(attempts) == 2
            assert len(attribute_changes) == 1
            assert runner.journal.read("P1")["effects"]["workspace"]["overwrite_deleted"] is True
        assert (official / "new.txt").read_text(encoding="utf-8") == "generated output"
    finally:
        if target is not None and target.exists():
            real_chmod(target, stat.S_IWRITE)
        runner.pool.shutdown()
        engine.dispose()


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
    # This fixture exercises one real form step, not an earlier workspace execution.
    state.update(step=3, completed_steps=[])
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
