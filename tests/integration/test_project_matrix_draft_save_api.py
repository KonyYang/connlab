from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixImportCommand,
    SourceMatrixImportPersistenceService,
)
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


def test_project_matrix_draft_save_api_replaces_snapshot_and_keeps_source_immutable(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        assert created.status_code == 201
        created_payload = created.json()
        draft_id = created_payload["record"]["project_matrix_draft_id"]
        initial_updated_at = created_payload["record"]["updated_at"]
        with session_factory() as session:
            source_repo = SourceMatrixImportRepository(session)
            source_before = source_repo.get_snapshot_by_import(source_import_id)
            assert source_before is not None
            source_before_rows = len(source_before.rows)
            source_before_groups = len(source_before.groups)
            source_before_cells = len(source_before.cells)
        save_response = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json={
                "groups": [
                    {
                        "draft_group_id": created_payload["groups"][0]["draft_group_id"],
                        "source_group_snapshot_id": created_payload["groups"][0][
                            "source_group_snapshot_id"
                        ],
                        "group_order": 1,
                        "group_key": "g1",
                        "group_label": "1",
                        "is_selected": True,
                        "sample_quantity_expression": "10",
                        "sample_note": None,
                    },
                    {
                        "draft_group_id": created_payload["groups"][1]["draft_group_id"],
                        "source_group_snapshot_id": created_payload["groups"][1][
                            "source_group_snapshot_id"
                        ],
                        "group_order": 2,
                        "group_key": "g2",
                        "group_label": "2",
                        "is_selected": False,
                        "sample_quantity_expression": "8",
                        "sample_note": None,
                    },
                ],
                "rows": [
                    {
                        "draft_row_id": created_payload["rows"][0]["draft_row_id"],
                        "source_row_snapshot_id": created_payload["rows"][0][
                            "source_row_snapshot_id"
                        ],
                        "row_order": 1,
                        "test_item": "Visual Examination",
                        "source_section": "6.1",
                        "is_sample_row": False,
                    },
                    {
                        "draft_row_id": created_payload["rows"][1]["draft_row_id"],
                        "source_row_snapshot_id": created_payload["rows"][1][
                            "source_row_snapshot_id"
                        ],
                        "row_order": 2,
                        "test_item": "LLCR",
                        "source_section": "6.2",
                        "is_sample_row": False,
                    },
                ],
                "cells": [
                    {
                        "draft_row_id": created_payload["rows"][0]["draft_row_id"],
                        "draft_group_id": created_payload["groups"][0]["draft_group_id"],
                        "cell_value": "",
                    },
                    {
                        "draft_row_id": created_payload["rows"][1]["draft_row_id"],
                        "draft_group_id": created_payload["groups"][1]["draft_group_id"],
                        "cell_value": "7",
                    },
                ],
            },
        )
        assert save_response.status_code == 200
        saved_payload = save_response.json()
        assert saved_payload["record"]["project_matrix_draft_id"] == draft_id
        assert saved_payload["record"]["updated_at"] != initial_updated_at
        assert len(saved_payload["cells"]) == 1
        assert saved_payload["cells"][0]["cell_value"] == "7"
        list_response = client.get("/api/projects/P1/matrix-drafts")
        assert list_response.status_code == 200
        listed = list_response.json()
        assert listed[0]["project_matrix_draft_id"] == draft_id
        with session_factory() as session:
            source_repo = SourceMatrixImportRepository(session)
            source_after = source_repo.get_snapshot_by_import(source_import_id)
            assert source_after is not None
            assert len(source_after.rows) == source_before_rows
            assert len(source_after.groups) == source_before_groups
            assert len(source_after.cells) == source_before_cells
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


def _seed_project(project_id: str, tmp_path: Path) -> None:
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
                created_on=date(2026, 5, 22),
            )
        )
        session.commit()
    engine.dispose()


def _seed_source_import(project_id: str, tmp_path: Path) -> str:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        service = SourceMatrixImportPersistenceService(store=SourceMatrixImportRepository(session))
        import_id = service.persist_from_draft(
            PersistSourceMatrixImportCommand(
                project_id=project_id,
                draft_id="ptpd-1",
                source_document_path="C:/spec.docx",
                source_document_name="spec.docx",
                source_format=".docx",
                source_asset_id="asset-1",
                source_case_id="case-1",
                source_draft_id="draft-1",
                payload={
                    "groups": [
                        {"group_key": "g1", "group_label": "G1", "sample_quantity_expression": "5"},
                        {"group_key": "g2", "group_label": "G2", "sample_quantity_expression": "6"},
                    ],
                    "rows": [
                        {
                            "source_row_index": 3,
                            "test_item": "Visual",
                            "source_section": "6.1",
                            "group_tokens": {"G1": "1", "G2": ""},
                            "is_sample_row": False,
                        },
                        {
                            "source_row_index": 4,
                            "test_item": "LLCR",
                            "source_section": "6.2",
                            "group_tokens": {"G1": "", "G2": "2"},
                            "is_sample_row": False,
                        },
                    ],
                    "warnings": [],
                    "blockers": [],
                    "selected_group_keys_at_import": ["g2"],
                },
                created_at="2026-05-22T09:00:00+00:00",
            )
        )
        session.commit()
    engine.dispose()
    return import_id
