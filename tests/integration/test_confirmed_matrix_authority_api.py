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
    SourceMatrixImportRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_confirm_project_matrix_draft_api_happy_path_and_immutability(tmp_path: Path) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        draft = created.json()
        draft_id = draft["record"]["project_matrix_draft_id"]
        with session_factory() as session:
            source_repo = SourceMatrixImportRepository(session)
            source_before = source_repo.get_snapshot_by_import(source_import_id)
            assert source_before is not None
            source_counts_before = (
                len(source_before.rows),
                len(source_before.groups),
                len(source_before.cells),
            )
        saved = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json={
                "groups": [
                    {
                        "draft_group_id": draft["groups"][0]["draft_group_id"],
                        "source_group_snapshot_id": draft["groups"][0]["source_group_snapshot_id"],
                        "group_order": 1,
                        "group_key": "g1",
                        "group_label": "1",
                        "is_selected": True,
                        "sample_quantity_expression": "5",
                        "sample_note": None,
                    },
                    {
                        "draft_group_id": draft["groups"][1]["draft_group_id"],
                        "source_group_snapshot_id": draft["groups"][1]["source_group_snapshot_id"],
                        "group_order": 2,
                        "group_key": "g2",
                        "group_label": "2",
                        "is_selected": True,
                        "sample_quantity_expression": "6",
                        "sample_note": None,
                    },
                ],
                "rows": [
                    {
                        "draft_row_id": draft["rows"][0]["draft_row_id"],
                        "source_row_snapshot_id": draft["rows"][0]["source_row_snapshot_id"],
                        "row_order": 1,
                        "test_item": "Visual",
                        "source_section": "6.1",
                        "method": "M1",
                        "condition": "C1",
                        "requirement": "R1",
                        "is_sample_row": False,
                    },
                    {
                        "draft_row_id": draft["rows"][1]["draft_row_id"],
                        "source_row_snapshot_id": draft["rows"][1]["source_row_snapshot_id"],
                        "row_order": 2,
                        "test_item": "LLCR",
                        "source_section": "6.2",
                        "method": "M2",
                        "condition": "C2",
                        "requirement": "R2",
                        "is_sample_row": False,
                    },
                    {
                        "draft_row_id": draft["rows"][2]["draft_row_id"],
                        "source_row_snapshot_id": draft["rows"][2]["source_row_snapshot_id"],
                        "row_order": 3,
                        "test_item": "Samples Quantity (PCS)",
                        "source_section": None,
                        "method": None,
                        "condition": None,
                        "requirement": None,
                        "is_sample_row": True,
                    },
                ],
                "cells": [
                    {
                        "draft_row_id": draft["rows"][0]["draft_row_id"],
                        "draft_group_id": draft["groups"][0]["draft_group_id"],
                        "cell_value": "1",
                    },
                    {
                        "draft_row_id": draft["rows"][1]["draft_row_id"],
                        "draft_group_id": draft["groups"][1]["draft_group_id"],
                        "cell_value": "2",
                    },
                    {
                        "draft_row_id": draft["rows"][2]["draft_row_id"],
                        "draft_group_id": draft["groups"][0]["draft_group_id"],
                        "cell_value": "5",
                    },
                ],
            },
        )
        assert saved.status_code == 200
        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201
        payload = confirmed.json()
        assert payload["version"]["project_id"] == "P1"
        assert payload["version"]["project_matrix_draft_id"] == draft_id
        assert payload["version"]["confirmed_revision"] == 1
        assert payload["version"]["status"] == "confirmed"
        assert len(payload["groups"]) == 2
        assert len(payload["rows"]) == 2
        assert len(payload["cells"]) == 2

        draft_after = client.get(f"/api/projects/P1/matrix-drafts/{draft_id}")
        assert draft_after.status_code == 200
        assert len(draft_after.json()["rows"]) == 3

        with session_factory() as session:
            source_repo = SourceMatrixImportRepository(session)
            source_after = source_repo.get_snapshot_by_import(source_import_id)
            assert source_after is not None
            assert (
                len(source_after.rows),
                len(source_after.groups),
                len(source_after.cells),
            ) == source_counts_before
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirm_project_matrix_draft_api_conflict_when_active_exists(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]

        first = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert first.status_code == 201
        second = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert second.status_code == 409
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirm_project_matrix_draft_api_validation_errors(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id},
        )
        assert created.status_code == 201
        draft = created.json()
        draft_id = draft["record"]["project_matrix_draft_id"]

        save_all_unselected = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json={
                "groups": [
                    {
                        "draft_group_id": group["draft_group_id"],
                        "source_group_snapshot_id": group["source_group_snapshot_id"],
                        "group_order": group["group_order"],
                        "group_key": group["group_key"],
                        "group_label": group["group_label"],
                        "is_selected": False,
                        "sample_quantity_expression": "5",
                        "sample_note": None,
                    }
                    for group in draft["groups"]
                ],
                "rows": draft["rows"],
                "cells": draft["cells"],
            },
        )
        assert save_all_unselected.status_code == 200
        no_selected = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert no_selected.status_code == 422

        save_blank_samples = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json={
                "groups": [
                    {
                        "draft_group_id": draft["groups"][0]["draft_group_id"],
                        "source_group_snapshot_id": draft["groups"][0]["source_group_snapshot_id"],
                        "group_order": 1,
                        "group_key": "g1",
                        "group_label": "1",
                        "is_selected": True,
                        "sample_quantity_expression": " ",
                        "sample_note": None,
                    },
                    {
                        "draft_group_id": draft["groups"][1]["draft_group_id"],
                        "source_group_snapshot_id": draft["groups"][1]["source_group_snapshot_id"],
                        "group_order": 2,
                        "group_key": "g2",
                        "group_label": "2",
                        "is_selected": True,
                        "sample_quantity_expression": "6",
                        "sample_note": None,
                    },
                ],
                "rows": draft["rows"],
                "cells": draft["cells"],
            },
        )
        assert save_blank_samples.status_code == 200
        missing_samples_confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert missing_samples_confirm.status_code == 422
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
