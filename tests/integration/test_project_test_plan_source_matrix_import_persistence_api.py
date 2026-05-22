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
from backend.infrastructure.storage.repositories import (
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_project_test_plan_draft_create_persists_source_matrix_import_snapshot(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        response = client.post(
            "/api/projects/P1/test-plan/drafts",
            json={
                "source_document_path": "C:/spec.docx",
                "source_document_name": "spec.docx",
                "source_format": ".docx",
                "payload": {
                    "groups": [
                        {
                            "group_key": "g1",
                            "group_label": "G1",
                            "source_table_index": 21,
                            "sample_size": 5,
                            "steps": [
                                {
                                    "raw_token": "1",
                                    "sequence": 1,
                                    "test_item": "Visual",
                                    "source_section": "6.1",
                                    "source_row_index": 10,
                                    "source_table_index": 21,
                                }
                            ],
                        },
                        {
                            "group_key": "g2",
                            "group_label": "G2",
                            "source_table_index": 21,
                            "sample_size": 5,
                            "steps": [
                                {
                                    "raw_token": "2",
                                    "sequence": 2,
                                    "test_item": "LLCR",
                                    "source_section": "6.2",
                                    "source_row_index": 11,
                                    "source_table_index": 21,
                                }
                            ],
                        },
                    ],
                    "rows": [
                        {
                            "source_row_index": 10,
                            "test_item": "Visual",
                            "source_section": "6.1",
                            "group_tokens": {"G1": "1", "G2": ""},
                            "is_sample_row": False,
                        },
                        {
                            "source_row_index": 11,
                            "test_item": "LLCR",
                            "source_section": "6.2",
                            "group_tokens": {"G1": "", "G2": "2"},
                            "is_sample_row": False,
                        },
                    ],
                    "warnings": ["warn-1"],
                    "blockers": [],
                    "source_metadata": {
                        "source_spec_number": "GS-12-1507",
                        "source_spec_revision": "Rev7",
                        "parse_time": "2026-05-22T08:00:00+00:00",
                        "parser_version": "parser-v3",
                        "payload_schema_version": "2.0",
                    },
                    "selected_group_keys_at_import": ["g1"],
                },
            },
        )
        assert response.status_code == 201
        created_draft_id = response.json()["draft_id"]

        with session_factory() as session:
            repo = SourceMatrixImportRepository(session)
            imports = repo.list_imports_by_project("P1")
            assert len(imports) == 1
            import_record = imports[0]
            assert import_record.draft_id == created_draft_id
            assert import_record.payload_schema_version == "2.0"
            assert import_record.parser_version == "parser-v3"
            assert import_record.source_spec_number == "GS-12-1507"
            assert list(import_record.selected_group_keys_at_import) == ["g1"]
            snapshot = repo.get_snapshot_by_import(import_record.import_id)
            assert snapshot is not None
            assert len(snapshot.groups) == 2
            assert len(snapshot.rows) == 2
            assert len(snapshot.cells) == 2
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_project_test_plan_draft_create_manual_format_does_not_persist_source_matrix_import(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        response = client.post(
            "/api/projects/P1/test-plan/drafts",
            json={
                "source_document_path": "manual://project-matrix",
                "source_document_name": "Manual Matrix",
                "source_format": "manual",
                "payload": {"groups": [], "warnings": [], "blockers": []},
            },
        )
        assert response.status_code == 201
        with session_factory() as session:
            repo = SourceMatrixImportRepository(session)
            assert repo.list_imports_by_project("P1") == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object, object]:
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
    return TestClient(app), engine, session_factory


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
