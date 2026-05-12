from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from docx import Document
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


def test_record_fee_document_generation_api_generates_test_record_docx(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        draft_id = client.post(
            "/api/projects/P1/test-plan/drafts",
            json=_create_draft_payload(),
        ).json()["draft_id"]

        template = tmp_path / "record_template.docx"
        Document().save(template)

        response = client.post(
            f"/api/projects/P1/test-plan/drafts/{draft_id}/record-fee-documents/generate",
            json={
                "output_dir": str(tmp_path),
                "test_record_template_path": str(template),
                "include_test_record": True,
                "include_fee_evaluation": False,
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["generated_files"][0]["kind"] == "test_record"
        assert body["generated_files"][0]["status"] == "generated"
        assert Path(body["generated_files"][0]["output_path"]).exists()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_record_fee_document_generation_api_rejects_disabled_outputs(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        response = client.post(
            "/api/projects/P1/test-plan/drafts/D1/record-fee-documents/generate",
            json={
                "output_dir": str(tmp_path),
                "include_test_record": False,
                "include_fee_evaluation": False,
            },
        )

        assert response.status_code == 400
        assert "At least one output" in response.json()["detail"]
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
        "payload": {
            "groups": [
                {
                    "group_key": "group_1",
                    "group_label": "Group 1",
                    "source_table_index": 21,
                    "steps": [
                        {
                            "sequence": 1,
                            "test_item": "LLCR",
                            "condition_summary": "After conditioning",
                            "method_summary": "Measure LLCR",
                            "reference_standard": "EIA-364-23",
                            "judgement_criteria": "20 mOhm max",
                            "estimated_duration_days": 1,
                            "source_section": "5.4",
                            "source_table_index": 21,
                            "source_row_index": 5,
                        }
                    ],
                }
            ],
            "warnings": [],
            "blockers": [],
        },
    }
