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


def test_project_output_records_api_create_and_status(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        draft_id = client.post(
            "/api/projects/P1/test-plan/drafts",
            json=_create_draft_payload(),
        ).json()["draft_id"]
        created = client.post(
            "/api/projects/P1/output-records",
            json={
                "output_kind": "section2_write_back",
                "status": "current",
                "source": "system_executed",
                "output_path": "C:/target.docx",
                "draft_id": draft_id,
            },
        )

        assert created.status_code == 201
        listed = client.get("/api/projects/P1/output-records")
        assert listed.status_code == 200
        assert listed.json()[0]["output_kind"] == "section2_write_back"
        summary = client.get("/api/projects/P1/output-records/status")
        assert summary.status_code == 200
        section2 = next(item for item in summary.json()["items"] if item["output_kind"] == "section2_write_back")
        assert section2["status"] == "current"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_output_status_authority_stays_reviewed_until_candidate_confirm(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        reviewed_response = client.post(
            "/api/projects/P1/test-plan/drafts",
            json={
                "source_document_path": "C:/spec.docx",
                "source_document_name": "spec.docx",
                "source_format": ".docx",
                "status": "reviewed",
                "payload": {
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
        assert reviewed_response.status_code == 201
        reviewed_id = reviewed_response.json()["draft_id"]

        revised = client.put(
            f"/api/projects/P1/test-plan/drafts/{reviewed_id}/matrix",
            json={
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
                ]
            },
        )
        assert revised.status_code == 200
        candidate_id = revised.json()["draft"]["draft_id"]
        assert revised.json()["draft"]["status"] == "draft"

        created = client.post(
            "/api/projects/P1/output-records",
            json={
                "output_kind": "section2_write_back",
                "status": "current",
                "source": "system_executed",
                "output_path": "C:/target.docx",
                "draft_id": reviewed_id,
            },
        )
        assert created.status_code == 201

        summary_before = client.get("/api/projects/P1/output-records/status")
        assert summary_before.status_code == 200
        assert summary_before.json()["active_draft_id"] == reviewed_id
        assert summary_before.json()["active_draft_version"] == 1

        confirmed = client.post(
            f"/api/projects/P1/test-plan/drafts/{candidate_id}/matrix/confirm"
        )
        assert confirmed.status_code == 200
        summary_after = client.get("/api/projects/P1/output-records/status")
        assert summary_after.status_code == 200
        assert summary_after.json()["active_draft_id"] == candidate_id
        assert summary_after.json()["active_draft_version"] == 2
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


def _create_draft_payload() -> dict[str, object]:
    return {
        "source_document_path": "C:/spec.docx",
        "source_document_name": "spec.docx",
        "source_format": ".docx",
        "payload": {"groups": [], "warnings": [], "blockers": []},
    }
