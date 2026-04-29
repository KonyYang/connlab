from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import ProjectRepository
from backend.shared.config import Settings


def test_ltr_preview_api_is_blocked_before_confirmed_project_data(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-GATE-1",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        ).json()["project_id"]

        response = client.get(
            f"/api/projects/{project_id}/ltr/preview",
            params={"year": 2026, "month": 4},
        )

        assert response.status_code == 400
        assert "confirmed project data" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_folder_generate_api_is_blocked_before_ltr_registration(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-GATE-2",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        ).json()["project_id"]
        template = tmp_path / "template"
        template.mkdir()

        response = client.post(
            f"/api/projects/{project_id}/folder/generate",
            json={"template_path": str(template), "target_root": str(tmp_path)},
        )

        assert response.status_code == 400
        assert "registered LTR" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_closed_project_rejects_ltr_registration_api(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        project_id = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-GATE-3",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        ).json()["project_id"]
        _set_project_status(engine, project_id, tmp_path, ProjectStatus.CLOSED)

        response = client.post(
            f"/api/projects/{project_id}/ltr",
            json={"ltr_number": "LTR-GATE"},
        )

        assert response.status_code == 400
        assert "closed" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object]:
    """Create a test client backed by an isolated database."""
    engine = create_database_engine(
        Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
        )
    )
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session() -> Generator[Session, None, None]:
        """Yield a test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    return TestClient(app), engine


def _set_project_status(
    engine,
    project_id: str,
    tmp_path: Path,
    status: ProjectStatus,
) -> None:
    """Update project status in an isolated test database."""
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        repository = ProjectRepository(session)
        project = repository.get(project_id)
        assert project is not None
        repository.update(project.with_status(status))
        session.commit()
