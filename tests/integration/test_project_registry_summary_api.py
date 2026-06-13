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


def test_project_registry_api_returns_summary_rows_and_project_identity_fields(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_registry_project(session_factory)

        registry = client.get("/api/projects/registry")
        projects = client.get("/api/projects")
        project_detail = client.get("/api/projects/P1")

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
                "display_project_id": "DL-2026-05-001",
                "display_project_id_kind": "registered",
                "has_registered_ltr": True,
                "temporary_project_id": None,
                "registered_ltr_number": "DL-2026-05-001",
                "temporary_source_asset_ids": [],
            }
        ]
        assert projects.status_code == 200
        assert "notes" not in projects.json()[0]
        assert project_detail.status_code == 200
        assert project_detail.json()["sample_description"] == "CoolPower connector samples"
        assert project_detail.json()["test_item"] == "Qualification bend testing"
        assert project_detail.json()["temporary_source_asset_ids"] == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_temporary_project_api_creates_planning_project_with_tmp_identity(
    tmp_path: Path,
) -> None:
    client, engine, _session_factory = _client(tmp_path)
    try:
        response = client.post(
            "/api/projects/temporary",
            json={
                "request_summary": "Connector feasibility discussion",
                "sample_description": "Planning connector sample",
                "test_item": "Duration estimate",
                "requestor": "Neo Xu",
                "source_asset_ids": ["ASSET1"],
                "notes": "Temporary project from email",
            },
        )

        assert response.status_code == 201
        created = response.json()
        assert created["project_id"]
        assert created["display_project_id"].startswith("TMP-")
        assert created["display_project_id_kind"] == "temporary"
        assert created["has_registered_ltr"] is False
        assert created["status"] == "draft"
        assert created["next_route"] == f"/projects/{created['project_id']}"

        registry = client.get("/api/projects/registry")
        assert registry.status_code == 200
        row = registry.json()[0]
        assert row["project_id"] == created["project_id"]
        assert row["display_project_id"] == created["display_project_id"]
        assert row["display_project_id_kind"] == "temporary"
        assert row["has_registered_ltr"] is False
        assert row["ltr_number"] is None
        assert row["sample_description"] == "Planning connector sample"
        assert row["test_item"] == "Duration estimate"
        assert row["notes"] == "Temporary project from email"
        assert row["temporary_source_asset_ids"] == ["ASSET1"]

        detail = client.get(f"/api/projects/{created['project_id']}")
        assert detail.status_code == 200
        assert detail.json()["test_item"] == "Duration estimate"
        assert detail.json()["temporary_notes"] == "Temporary project from email"
        assert detail.json()["temporary_source_asset_ids"] == ["ASSET1"]
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
                product_name="CoolPower connector samples",
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
