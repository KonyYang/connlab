from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.shared.config import Settings


def test_project_api_create_list_get_with_temp_db(tmp_path: Path) -> None:
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
        create_response = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-001",
                "product_name": "Connector",
                "requestor": "Alice",
                "business_unit": "BU-1",
            },
        )

        assert create_response.status_code == 201
        created = create_response.json()
        assert created["project_no"] == "PRJ-001"
        assert created["status"] == "draft"

        list_response = client.get("/api/projects")
        detail_response = client.get(f"/api/projects/{created['project_id']}")
        missing_response = client.get("/api/projects/missing")

        assert list_response.status_code == 200
        assert list_response.json() == [created]
        assert detail_response.status_code == 200
        assert detail_response.json() == created
        assert missing_response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
