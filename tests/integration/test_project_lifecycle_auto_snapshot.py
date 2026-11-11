from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.api.project_registry_access_guard import _commit_project_writes
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import (
    LtrRecordModel,
    ProjectModel,
    ProjectOfficialWorkspaceRecordModel,
)
from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
from backend.shared.config import Settings


def test_committed_project_write_refreshes_the_portable_snapshot(tmp_path):
    root = tmp_path / "library"
    project_root = root / "Projects" / "DL-2026-11-013"
    business = project_root / "DL-2026-11-013 Connector"
    source_book = project_root / "Source Book"
    business.mkdir(parents=True)
    source_book.mkdir()
    (project_root / ".connlab").mkdir()
    (business / "result.txt").write_text("evidence", encoding="utf-8")
    settings = Settings(root / "Data", root / "Projects", root / "Templates", root / "Data" / "connlab.sqlite3", library_root=root)
    settings.ensure_directories()
    engine = create_engine(f"sqlite:///{settings.database_path}")
    init_db(engine)
    try:
        with Session(engine) as session:
            session.add(ProjectModel(
                project_id="project-1", project_no="DL-2026-11-013", product_name="Before",
                requestor="Lab", status="draft", registry_state="active", registry_revision=0,
            ))
            session.add(LtrRecordModel(
                ltr_id="ltr-1", project_id="project-1", ltr_number="DL-2026-11-013",
                status="registered", is_current_owner=True,
            ))
            session.add(ProjectLibraryMemberModel(
                member_id="member-1", project_id="project-1", ltr_number="DL-2026-11-013",
                title="Connector", folder_path=str(project_root), source_path=str(project_root),
                source_project_id=None, revision=1, batch_id=None, created_at="2026-11-11T00:00:00Z",
            ))
            session.add(ProjectOfficialWorkspaceRecordModel(
                workspace_id="workspace-1", project_id="project-1", dl_number="DL-2026-11-013",
                local_workspace_path=str(project_root), source_book_path=str(source_book),
                official_folder_path=str(business), manifest_path=str(project_root / ".connlab" / "manifest.json"),
                template_source_path=None, created_at="2026-11-11T00:00:00Z",
            ))
            session.commit()

            with _commit_project_writes(session, {"project-1": 0}, settings):
                session.get(ProjectModel, "project-1").product_name = "After"

            snapshot = project_root / ".connlab" / "portable" / "snapshot.json"
            assert snapshot.is_file()
            first = snapshot.read_bytes()

            with _commit_project_writes(session, {"project-1": 1}, settings):
                session.get(ProjectModel, "project-1").product_name = "After again"

            assert snapshot.read_bytes() != first
    finally:
        engine.dispose()


def test_snapshot_setup_failure_does_not_undo_the_committed_business_write(tmp_path, monkeypatch):
    settings = Settings(
        tmp_path / "Data",
        tmp_path / "Projects",
        tmp_path / "Templates",
        tmp_path / "Data" / "connlab.sqlite3",
    )
    settings.ensure_directories()
    engine = create_engine(f"sqlite:///{settings.database_path}")
    init_db(engine)
    try:
        with Session(engine) as session:
            session.add(ProjectModel(
                project_id="project-1", product_name="Before", requestor="Lab",
                status="draft", registry_state="active", registry_revision=0,
            ))
            session.commit()

            def fail_refresh(*_args, **_kwargs):
                raise RuntimeError("snapshot setup unavailable")

            monkeypatch.setattr(
                "backend.api.project_registry_access_guard.AutomaticPortableSnapshotService.refresh",
                fail_refresh,
            )
            with _commit_project_writes(session, {"project-1": 0}, settings):
                session.get(ProjectModel, "project-1").product_name = "Committed"

            session.expire_all()
            assert session.get(ProjectModel, "project-1").product_name == "Committed"
    finally:
        engine.dispose()
