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


def test_matrix_edit_api_update_validate_confirm_flow(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        draft_id = _create_draft(client)

        updated = client.put(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix",
            json={
                "groups": [
                    {
                        "group_key": "group_1",
                        "group_label": "Group 1",
                        "steps": [
                            {
                                "raw_token": "1 2",
                                "test_item": "Visual examination",
                                "method_summary": "Method A",
                                "judgement_criteria": "No crack",
                                "condition_summary": "Ambient",
                            }
                        ],
                    }
                ]
            },
        )
        assert updated.status_code == 200
        assert updated.json()["validation"]["blockers"] == []
        assert updated.json()["validation"]["step_count"] == 2

        validated = client.post(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix/validate"
        )
        assert validated.status_code == 200
        assert validated.json()["validation"]["group_count"] == 1
        assert validated.json()["validation"]["blockers"] == []

        confirmed = client.post(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix/confirm"
        )
        assert confirmed.status_code == 200
        assert confirmed.json()["draft"]["status"] == "reviewed"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_edit_api_confirm_rejects_validation_blockers(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        draft_id = _create_draft(
            client,
            payload={
                "groups": [
                    {
                        "group_key": "group_1",
                        "group_label": "Group 1",
                        "steps": [
                            {
                                "raw_token": "2",
                                "test_item": "Visual examination",
                                "method_summary": "Method A",
                                "judgement_criteria": "No crack",
                            }
                        ],
                    }
                ],
                "warnings": [],
                "blockers": [],
            },
        )

        response = client.post(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix/confirm"
        )
        assert response.status_code == 400
        assert "cannot be confirmed" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_edit_api_update_reviewed_draft_creates_new_version(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        draft_id = _create_draft(client)
        confirmed = client.post(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix/confirm"
        )
        assert confirmed.status_code == 200
        assert confirmed.json()["draft"]["status"] == "reviewed"

        revised = client.put(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix",
            json={
                "groups": [
                    {
                        "group_key": "group_1",
                        "group_label": "Group 1",
                        "steps": [
                            {
                                "raw_token": "1",
                                "test_item": "Revised item",
                                "method_summary": "Method B",
                                "judgement_criteria": "Pass",
                            }
                        ],
                    }
                ]
            },
        )
        assert revised.status_code == 200
        assert revised.json()["created_new_draft"] is True
        assert revised.json()["draft"]["status"] == "draft"
        assert revised.json()["draft"]["version"] == 2
        original = client.get(f"/api/projects/P1/test-plan/drafts/{draft_id}")
        assert original.status_code == 200
        assert original.json()["status"] == "reviewed"

        confirmed_revised = client.post(
            f"/api/projects/P1/test-plan/drafts/{revised.json()['draft']['draft_id']}/matrix/confirm"
        )
        assert confirmed_revised.status_code == 200
        original_after_confirm = client.get(f"/api/projects/P1/test-plan/drafts/{draft_id}")
        assert original_after_confirm.status_code == 200
        assert original_after_confirm.json()["status"] == "superseded"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_edit_api_confirm_allows_warning_only_missing_method_requirement(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        draft_id = _create_draft(
            client,
            payload={
                "groups": [
                    {
                        "group_key": "group_1",
                        "group_label": "Group 1",
                        "steps": [{"raw_token": "1", "test_item": "Visual examination"}],
                    }
                ],
                "warnings": [],
                "blockers": [],
            },
        )
        response = client.post(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix/confirm"
        )
        assert response.status_code == 200
        assert response.json()["draft"]["status"] == "reviewed"
        assert response.json()["validation"]["blockers"] == []
        assert any(
            "method is missing" in item for item in response.json()["validation"]["warnings"]
        )
        assert any(
            "requirement is missing"
            in item
            for item in response.json()["validation"]["warnings"]
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_edit_api_confirm_blocks_when_group_identity_missing(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        draft_id = _create_draft(
            client,
            payload={
                "groups": [
                    {
                        "steps": [{"raw_token": "1", "test_item": "Visual examination"}],
                    }
                ],
                "warnings": [],
                "blockers": [],
            },
        )
        response = client.post(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/matrix/confirm"
        )
        assert response.status_code == 400
        assert "cannot be confirmed" in response.json()["detail"]
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


def _create_draft(
    client: TestClient,
    *,
    payload: dict[str, object] | None = None,
) -> str:
    response = client.post(
        "/api/projects/P1/test-plan/drafts",
        json={
            "source_document_path": "C:/spec.docx",
            "source_document_name": "spec.docx",
            "source_format": ".docx",
            "payload": payload
            or {
                "groups": [
                    {
                        "group_key": "group_1",
                        "group_label": "Group 1",
                        "steps": [
                            {
                                "raw_token": "1",
                                "test_item": "Visual examination",
                                "method_summary": "Method A",
                                "judgement_criteria": "No crack",
                            }
                        ],
                    }
                ],
                "warnings": [],
                "blockers": [],
            },
        },
    )
    assert response.status_code == 201
    return response.json()["draft_id"]
