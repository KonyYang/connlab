from __future__ import annotations

import json
from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    LtrRecordRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_project_registry_api_returns_summary_rows_without_extending_project_dto(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_registry_project(session_factory)

        registry = client.get("/api/projects/registry")
        projects = client.get("/api/projects")

        assert registry.status_code == 200
        assert registry.json() == [
            {
                "project_id": "P1",
                "ltr_number": "DL-2026-05-001",
                "sample_description": "CoolPower connector samples",
                "test_item": "Qualification bend testing",
                "requestor": "Neo Xu",
                "business_unit": "Power Solutions",
                "status": "ltr_registered",
                "progress": 70,
                "notes": None,
            }
        ]
        assert projects.status_code == 200
        assert "sample_description" not in projects.json()[0]
        assert "test_item" not in projects.json()[0]
        assert "notes" not in projects.json()[0]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path):
    """Create an isolated API client."""
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
    return TestClient(app), engine, session_factory


def _seed_registry_project(session_factory) -> None:
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no=None,
                product_name="Legacy Product Name",
                requestor="Neo Xu",
                business_unit="Power Solutions",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 6, 7),
            )
        )
        LtrRecordRepository(session).create(
            LtrRecord(
                ltr_id="LTR1",
                project_id="P1",
                ltr_number="DL-2026-05-001",
                status=LtrStatus.REGISTERED,
                registered_on=date(2026, 6, 7),
                notes=json.dumps(
                    {
                        "commit_mode": "external_ltr_workbook",
                        "operator_note": json.dumps(
                            {
                                "source": "new_project_setup_confirmation",
                                "sample_description": "CoolPower connector samples",
                                "test_item": "Qualification bend testing",
                            },
                            sort_keys=True,
                        ),
                    },
                    sort_keys=True,
                ),
            )
        )
        session.commit()
