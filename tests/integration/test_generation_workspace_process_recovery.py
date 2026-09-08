"""Hard process-exit windows around real workspace publication and SQLite indexing."""

from pathlib import Path
import os
import shutil
import subprocess
import sys

import pytest
from sqlalchemy import create_engine

from backend.api import dependencies as deps
from backend.api.project_folder_generation_composition import ProjectFolderGenerationRunner
from backend.application.project_basic_information_service import (
    ConfirmProjectBasicInformationCommand,
)
from backend.domain import Project, ProjectStatus, LtrRecord, LtrStatus, ExternalResource, ExternalResourceType, FileAsset, FileAssetType
from backend.infrastructure.files.recoverable_output_publisher import RecoverableOutputPublisher
from backend.infrastructure.storage.database import Base, create_session_factory
from backend.shared.config import Settings


def _settings(root):
    return Settings(data_dir=root / "data", projects_dir=root / "projects", templates_dir=root / "templates",
                    database_path=root / "fixture.sqlite")


def _confirm_basic_information(session):
    deps.get_project_basic_information_service(session).confirm(
        ConfirmProjectBasicInformationCommand(
            project_id="P1",
            values={
                "dl_number": "DL-001",
                "project_type": "NPD",
                "product_description": "Connector",
                "test_item": "Qualification Testing",
                "tests_to_be_performed": "Qualification Testing",
                "requested_by": "Test",
                "project_leader": "Engineer",
                "lab_performing_tests": "Dongguan",
            },
            confirmed_by="operator",
        )
    )


@pytest.mark.parametrize("replaced", ["local_workspace_path", "official_folder_path", "source_book_path", None])
@pytest.mark.parametrize("reuse_existing", [False, True])
def test_later_step_refuses_replaced_workspace_directories_but_allows_new_output_contents(tmp_path, replaced, reuse_existing):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    template, destination = tmp_path / "template", tmp_path / "output"
    destination.mkdir()
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    source = tmp_path / "application.docx"
    source.write_bytes(b"original application")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project("P1", "DL-001", "Connector", "Test", ProjectStatus.DRAFT))
        deps.LtrRecordRepository(session).create(LtrRecord("ltr", "P1", "DL-001", LtrStatus.REGISTERED))
        deps.FileAssetRepository(session).create(FileAsset("form", "P1", FileAssetType.APPLICATION_FORM,
            source, original_name=source.name, source_role="selected_application_form"))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, destination))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        _confirm_basic_information(session)
        session.commit()
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    service.dispatch = lambda callback: None
    try:
        service.start("P1", None, runner.preview_context("P1"), "request")
        state = runner.journal.read("P1")
        runner.run_step(state, "workspace")
        if reuse_existing:
            state.update(status="completed")
            runner.journal.save(state)
            service.start("P1", None, runner.preview_context("P1"), "reuse")
            state = runner.journal.read("P1")
            runner.run_step(state, "workspace")
        state.update(step=1, completed_steps=["workspace"])
        runner.journal.save(state)
        with sessions() as session:
            record = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
        if replaced:
            target = getattr(record, replaced)
            original = target.with_name(target.name + "-original")
            target.rename(original)
            shutil.copytree(original, target, copy_function=os.link)  # Preserve file identity too; only directories change.
            before = sorted(str(path.relative_to(target)) for path in target.rglob("*"))
            with pytest.raises(ValueError, match="directory|workspace"):
                runner.run_step(state, "materials")
            assert sorted(str(path.relative_to(target)) for path in target.rglob("*")) == before
        else:
            (record.official_folder_path / "generated-earlier.txt").write_bytes(b"legitimate evolving output")
            runner.run_step(state, "materials")
            assert (record.official_folder_path / "Submitted Material" / source.name).read_bytes() == source.read_bytes()
    finally:
        runner.pool.shutdown()
        engine.dispose()


def _child(root, mode):
    settings = _settings(root)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    runner = ProjectFolderGenerationRunner(create_session_factory(engine), settings)
    state = runner.journal.read("P1")
    if mode == "copy":
        original = shutil.copy2
        original_tree = shutil.copytree
        def interrupted_copy(*args, **kwargs):
            result = original(*args, **kwargs)
            os._exit(31)
        def interrupted_tree(source, target):
            shutil.copytree = original_tree
            return original_tree(source, target, copy_function=interrupted_copy)
        shutil.copytree = interrupted_tree
    if mode in {"move", "backup"}:
        original = Path.rename
        def interrupted_move(path, target):
            result = original(path, target)
            if (mode == "move" and Path(target).name == "DL-001") or (mode == "backup" and path.name == "DL-001"):
                os._exit(32)
            return result
        Path.rename = interrupted_move
    if mode == "manifest":
        original = RecoverableOutputPublisher.publish_file
        def interrupted_manifest(self, key, *args, **kwargs):
            result = original(self, key, *args, **kwargs)
            if key == "manifest":
                os._exit(33)
            return result
        RecoverableOutputPublisher.publish_file = interrupted_manifest
    runner.run_step(state, "workspace")
    runner.pool.shutdown()
    engine.dispose()
    if mode == "db":
        os._exit(34)


@pytest.mark.parametrize("window,exit_code", [("copy", 31), ("move", 32), ("manifest", 33), ("db", 34), ("backup", 32)])
def test_fresh_process_recovers_workspace_without_replaying_conflict_or_copy(tmp_path, window, exit_code):
    settings = _settings(tmp_path)
    engine = create_engine(f"sqlite:///{settings.database_path.as_posix()}")
    Base.metadata.create_all(engine)
    sessions = create_session_factory(engine)
    template, destination = tmp_path / "template", tmp_path / "output"
    destination.mkdir()
    for name in ("E-mail", "Submitted Material", "Photos", "Test results/Final Examination"):
        (template / name).mkdir(parents=True)
    (template / "template.txt").write_text("fixture bytes", encoding="utf-8")
    with sessions() as session:
        deps.ProjectRepository(session).create(Project(project_id="P1", project_no="DL-001", product_name="Connector", requestor="Test", status=ProjectStatus.DRAFT))
        deps.LtrRecordRepository(session).create(LtrRecord(ltr_id="ltr", project_id="P1", ltr_number="DL-001", status=LtrStatus.REGISTERED))
        resources = deps.ExternalResourceRepository(session)
        resources.upsert(ExternalResource("root", ExternalResourceType.PROJECT_OUTPUT_ROOT, destination))
        resources.upsert(ExternalResource("template", ExternalResourceType.PROJECT_FOLDER_TEMPLATE, template))
        _confirm_basic_information(session)
        session.commit()
    if window == "backup":
        (destination / "DL-001").mkdir()
        (destination / "DL-001" / "foreign.txt").write_bytes(b"must survive")
    runner = ProjectFolderGenerationRunner(sessions, settings)
    service = runner.service()
    service.dispatch = lambda callback: None
    service.start("P1", "backup_and_recreate" if window == "backup" else None, runner.preview_context("P1"), "request")
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[2]))
    def run(mode):
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), str(tmp_path), mode],
                              env=env, capture_output=True, text=True, timeout=40)
    crashed = run(window)
    assert crashed.returncode == exit_code, crashed.stdout + crashed.stderr
    orphan_stages = list((destination / ".connlab").rglob("template.txt")) if window == "copy" else []
    if window == "copy":
        assert "workspace" not in runner.journal.read("P1")["effects"]
        assert orphan_stages
    recovered = run("recover")
    assert recovered.returncode == 0, recovered.stdout + recovered.stderr
    with sessions() as session:
        record = deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1")
        identity = record.workspace_id
    before = (record.official_folder_path / "template.txt").stat().st_mtime_ns
    recovered_again = run("recover")
    assert recovered_again.returncode == 0, recovered_again.stdout + recovered_again.stderr
    with sessions() as session:
        assert deps.ProjectOfficialWorkspaceRepository(session).get_by_project("P1").workspace_id == identity
    assert (record.official_folder_path / "template.txt").read_bytes() == b"fixture bytes"
    assert (record.official_folder_path / "template.txt").stat().st_mtime_ns == before
    assert record.manifest_path.is_file()
    assert record.source_book_path.is_dir()
    for orphan in orphan_stages:
        assert orphan.read_bytes() == b"fixture bytes"  # Never delete an unjournaled attempt.
    if window == "backup":
        effect = runner.journal.read("P1")["effects"]["workspace"]
        assert (Path(effect["backup"]) / "foreign.txt").read_bytes() == b"must survive"
        assert len(list(destination.glob("*.connlab-backup-*"))) == 1
    runner.pool.shutdown()
    engine.dispose()


if __name__ == "__main__":
    _child(Path(sys.argv[1]), sys.argv[2])
