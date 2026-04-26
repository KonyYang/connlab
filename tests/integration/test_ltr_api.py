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


def test_ltr_api_register_retrieve_search_and_prevent_duplicate(
    tmp_path: Path,
) -> None:
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
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    try:
        project_response = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-001",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        )
        project_id = project_response.json()["project_id"]

        register_response = client.post(
            f"/api/projects/{project_id}/ltr",
            json={
                "ltr_number": "LTR-001",
                "requested_by": "Alice",
                "requested_date": "2026-04-26",
                "notes": "Initial registration",
            },
        )
        assert register_response.status_code == 201
        registered = register_response.json()
        assert registered["ltr_number"] == "LTR-001"
        assert registered["status"] == "registered"

        list_response = client.get(f"/api/projects/{project_id}/ltr")
        search_response = client.get("/api/ltr-records", params={"query": "LTR-001"})
        duplicate_response = client.post(
            f"/api/projects/{project_id}/ltr",
            json={"ltr_number": "LTR-002"},
        )

        assert list_response.status_code == 200
        assert list_response.json() == [registered]
        assert search_response.status_code == 200
        assert search_response.json() == [registered]
        assert duplicate_response.status_code == 409

        with session_factory() as session:
            project = ProjectRepository(session).get(project_id)
            assert project is not None
            assert project.status is ProjectStatus.LTR_REGISTERED
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
