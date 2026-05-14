from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import Project, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import ProjectRepository
from backend.shared.config import Settings


def test_approval_package_preview_and_execute_api(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", ProjectStatus.FOLDER_CREATED, tmp_path)
        folder = tmp_path / "project"
        folder.mkdir()
        (folder / "Submitted Material").mkdir()
        (folder / "E-mail").mkdir()
        app_form = tmp_path / "request.docx"
        app_form.write_text("req", encoding="utf-8")
        test_record = tmp_path / "record.docx"
        test_record.write_text("record", encoding="utf-8")
        msg = tmp_path / "mail.msg"
        msg.write_text("mail", encoding="utf-8")

        payload = {
            "project_folder_path": str(folder),
            "completed_application_form_path": str(app_form),
            "test_record_output_path": str(test_record),
            "evidence_source_paths": [str(msg)],
            "overwrite": False,
        }
        preview = client.post("/api/projects/P1/approval-package/preview", json=payload)
        execute = client.post("/api/projects/P1/approval-package/execute", json=payload)

        assert preview.status_code == 200
        assert preview.json()["mode"] == "preview"
        assert execute.status_code == 201
        assert execute.json()["mode"] == "execute"
        assert (folder / "Submitted Material" / "request.docx").exists()
        assert (folder / "Submitted Material" / "record.docx").exists()
        assert (folder / "E-mail" / "mail.msg").exists()
        status_response = client.get("/api/projects/P1/output-records/status")
        assert status_response.status_code == 200
        approval = next(
            item for item in status_response.json()["items"] if item["output_kind"] == "approval_package"
        )
        assert approval["status"] in {"manual", "current"}
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_approval_package_execute_lifecycle_blocked_when_not_folder_created(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", ProjectStatus.LTR_REGISTERED, tmp_path)
        folder = tmp_path / "project"
        folder.mkdir()
        app_form = tmp_path / "request.docx"
        app_form.write_text("req", encoding="utf-8")
        test_record = tmp_path / "record.docx"
        test_record.write_text("record", encoding="utf-8")
        response = client.post(
            "/api/projects/P1/approval-package/execute",
            json={
                "project_folder_path": str(folder),
                "completed_application_form_path": str(app_form),
                "test_record_output_path": str(test_record),
                "overwrite": False,
            },
        )

        assert response.status_code == 400
        assert "requires a generated project folder first" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object]:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
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

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), engine


def _create_project(project_id: str, status: ProjectStatus, tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id=project_id,
                project_no=f"DL-2026-05-{project_id}",
                product_name="Connector",
                requestor="Alice",
                status=status,
                created_on=date(2026, 5, 12),
            )
        )
        session.commit()
    engine.dispose()
