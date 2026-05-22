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


def test_matrix_revision_flow_api_happy_path(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        base_draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed_base = client.post(
            f"/api/projects/P1/matrix-drafts/{base_draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed_base.status_code == 201
        base_confirmed_id = confirmed_base.json()["version"]["confirmed_matrix_id"]

        revision_create = client.post("/api/projects/P1/matrix-revisions")
        assert revision_create.status_code == 201
        revision_draft = revision_create.json()
        revision_draft_id = revision_draft["record"]["project_matrix_draft_id"]
        assert revision_draft["record"]["base_confirmed_matrix_id"] == base_confirmed_id
        assert revision_draft["record"]["source_import_id"] is None
        assert all(not row["is_sample_row"] for row in revision_draft["rows"])

        confirm_revision = client.post(
            f"/api/projects/P1/matrix-drafts/{revision_draft_id}/confirm-revision",
            json={"confirmed_by": "operator", "superseded_reason": "Update groups"},
        )
        assert confirm_revision.status_code == 201
        revision_confirmed = confirm_revision.json()
        assert revision_confirmed["version"]["confirmed_revision"] == 2
        assert revision_confirmed["version"]["status"] == "confirmed"

        stale_confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{revision_draft_id}/confirm-revision",
            json={"confirmed_by": "operator"},
        )
        assert stale_confirm.status_code == 409
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_revision_flow_api_uniqueness_and_validation(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id},
        )
        assert created.status_code == 201
        base_draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed_base = client.post(
            f"/api/projects/P1/matrix-drafts/{base_draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed_base.status_code == 201

        first_revision = client.post("/api/projects/P1/matrix-revisions")
        assert first_revision.status_code == 201
        second_revision = client.post("/api/projects/P1/matrix-revisions")
        assert second_revision.status_code == 409

        revision_draft = first_revision.json()
        update_missing_sample = client.put(
            f"/api/projects/P1/matrix-drafts/{revision_draft['record']['project_matrix_draft_id']}",
            json={
                "groups": [
                    {
                        "draft_group_id": group["draft_group_id"],
                        "source_group_snapshot_id": group["source_group_snapshot_id"],
                        "group_order": group["group_order"],
                        "group_key": group["group_key"],
                        "group_label": group["group_label"],
                        "is_selected": group["is_selected"],
                        "sample_quantity_expression": " " if index == 0 else "6",
                        "sample_note": group["sample_note"],
                    }
                    for index, group in enumerate(revision_draft["groups"])
                ],
                "rows": revision_draft["rows"],
                "cells": revision_draft["cells"],
            },
        )
        assert update_missing_sample.status_code == 200
        confirm_invalid = client.post(
            f"/api/projects/P1/matrix-drafts/{revision_draft['record']['project_matrix_draft_id']}/confirm-revision",
            json={"confirmed_by": "operator"},
        )
        assert confirm_invalid.status_code == 422
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
                        {
                            "source_row_index": 5,
                            "test_item": "Samples Quantity (PCS)",
                            "source_section": None,
                            "group_tokens": {"G1": "5", "G2": "6"},
                            "is_sample_row": True,
                        },
                    ],
                    "warnings": [],
                    "blockers": [],
                    "selected_group_keys_at_import": ["g1", "g2"],
                },
                created_at="2026-05-22T09:00:00+00:00",
            )
        )
        session.commit()
    engine.dispose()
    return import_id
