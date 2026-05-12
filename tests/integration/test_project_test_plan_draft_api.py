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


def test_project_test_plan_draft_api_create_list_get_update_and_supersede(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        create_response = client.post(
            "/api/projects/P1/test-plan/drafts",
            json=_create_payload("Group 1"),
        )
        assert create_response.status_code == 201
        first = create_response.json()
        assert first["project_id"] == "P1"
        assert first["status"] == "draft"
        assert first["version"] == 1
        assert first["payload"]["groups"][0]["group_label"] == "Group 1"

        update_response = client.put(
            f"/api/projects/P1/test-plan/drafts/{first['draft_id']}",
            json={"status": "reviewed", "payload": _payload("Reviewed Group")},
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "reviewed"
        assert update_response.json()["reviewed_at"] is not None

        second_response = client.post(
            "/api/projects/P1/test-plan/drafts",
            json=_create_payload("Group 2"),
        )
        assert second_response.status_code == 201
        assert second_response.json()["version"] == 2

        get_first = client.get(f"/api/projects/P1/test-plan/drafts/{first['draft_id']}")
        list_response = client.get("/api/projects/P1/test-plan/drafts")

        assert get_first.status_code == 200
        assert get_first.json()["status"] == "superseded"
        assert list_response.status_code == 200
        assert len(list_response.json()) == 2
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_project_test_plan_draft_api_rejects_unknown_and_cross_project(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        _create_project("P2", tmp_path)
        missing = client.post(
            "/api/projects/UNKNOWN/test-plan/drafts",
            json=_create_payload("Group 1"),
        )
        create_response = client.post(
            "/api/projects/P1/test-plan/drafts",
            json=_create_payload("Group 1"),
        )
        draft_id = create_response.json()["draft_id"]
        cross = client.get(f"/api/projects/P2/test-plan/drafts/{draft_id}")

        assert missing.status_code == 404
        assert "Project not found" in missing.json()["detail"]
        assert cross.status_code == 404
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


def _create_project(project_id: str, tmp_path: Path) -> None:
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
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 5, 12),
            )
        )
        session.commit()
    engine.dispose()


def _create_payload(group_label: str) -> dict[str, object]:
    return {
        "source_document_path": "C:/spec.docx",
        "source_document_name": "spec.docx",
        "source_format": ".docx",
        "source_case_id": "CASE1",
        "source_draft_id": "DRAFT1",
        "payload": _payload(group_label),
    }


def _payload(group_label: str) -> dict[str, object]:
    return {
        "groups": [
            {
                "group_key": "group_1",
                "group_label": group_label,
                "source_table_index": 21,
                "steps": [{"sequence": 1, "test_item": "Examination"}],
            }
        ],
        "warnings": [],
        "blockers": [],
    }
