from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import delete
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
from backend.infrastructure.storage.models_matrix_source import SourceMatrixSnapshotModel
from backend.infrastructure.storage.repositories import (
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_matrix_editor_session_seed_handles_missing_source_snapshot(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201

        with session_factory() as session:
            session.execute(delete(SourceMatrixSnapshotModel))
            session.commit()

        seed = client.get("/api/projects/P1/matrix-editor/session")
        assert seed.status_code == 200
        payload = seed.json()
        assert payload["source_status"] == "unavailable"
        assert (
            payload["source_unavailable_message"]
            == "Original source Matrix is unavailable. Use Import Matrix to reselect groups."
        )
        assert payload["editor_draft"] is not None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_session_confirm_no_change_returns_http200_no_change(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201

        seed = client.get("/api/projects/P1/matrix-editor/session")
        assert seed.status_code == 200
        seed_payload = seed.json()
        assert seed_payload["active_confirmed_matrix_id"] is not None
        editor_draft = seed_payload["editor_draft"]
        assert editor_draft is not None

        response = client.post(
            "/api/projects/P1/matrix-editor/session/confirm",
            json={
                "expected_active_confirmed_matrix_id": seed_payload["active_confirmed_matrix_id"],
                "expected_active_confirmed_revision": seed_payload["active_confirmed_revision"],
                "source_document_path": seed_payload["source_preview_payload"]["source_document_path"]
                if seed_payload["source_preview_payload"]
                else None,
                "source_document_name": seed_payload["source_preview_payload"]["source_document_name"]
                if seed_payload["source_preview_payload"]
                else None,
                "source_format": seed_payload["source_preview_payload"]["source_format"]
                if seed_payload["source_preview_payload"]
                else None,
                "confirmed_by": "operator",
                "groups": editor_draft["groups"],
                "rows": editor_draft["rows"],
                "cells": editor_draft["cells"],
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["publish_status"] == "no_change"
        assert payload["message"] == "No Matrix changes to confirm."
        assert payload["confirmed_snapshot"] is None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_session_confirm_publishes_schedule_planning_fields(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201

        seed = client.get("/api/projects/P1/matrix-editor/session")
        assert seed.status_code == 200
        seed_payload = seed.json()
        editor_draft = seed_payload["editor_draft"]
        assert editor_draft is not None
        rows = [
            {**row, "day_expression": "0.5x"}
            if row["test_item"] == "Visual Examination"
            else row
            for row in editor_draft["rows"]
        ]

        response = client.post(
            "/api/projects/P1/matrix-editor/session/confirm",
            json={
                "expected_active_confirmed_matrix_id": seed_payload["active_confirmed_matrix_id"],
                "expected_active_confirmed_revision": seed_payload["active_confirmed_revision"],
                "source_document_path": seed_payload["source_preview_payload"]["source_document_path"],
                "source_document_name": seed_payload["source_preview_payload"]["source_document_name"],
                "source_format": seed_payload["source_preview_payload"]["source_format"],
                "source_import_id": seed_payload["active_source_import_id"],
                "source_snapshot_id": seed_payload["active_source_snapshot_id"],
                "confirmed_by": "operator",
                "pre_test_buffer_days": "1",
                "post_test_buffer_days": "1",
                "sample_received_date": "2026-06-01",
                "planned_test_start_date": "2026-06-02",
                "planned_test_complete_date": "2026-06-03",
                "estimated_completion_date": "2026-06-04",
                "groups": editor_draft["groups"],
                "rows": rows,
                "cells": editor_draft["cells"],
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["publish_status"] == "published"
        version = payload["confirmed_snapshot"]["version"]
        assert version["pre_test_buffer_days"] == "1"
        assert version["post_test_buffer_days"] == "1"
        assert version["sample_received_date"] == "2026-06-01"
        assert version["planned_test_start_date"] == "2026-06-02"
        assert version["planned_test_complete_date"] == "2026-06-03"
        assert version["estimated_completion_date"] == "2026-06-04"
        assert payload["confirmed_snapshot"]["rows"][0]["day_expression"] == "0.5x"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_session_confirm_rejects_invalid_schedule(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201

        seed = client.get("/api/projects/P1/matrix-editor/session")
        assert seed.status_code == 200
        seed_payload = seed.json()
        editor_draft = seed_payload["editor_draft"]
        assert editor_draft is not None
        rows = [
            {**row, "day_expression": "3"}
            if row["test_item"] == "Visual Examination"
            else row
            for row in editor_draft["rows"]
        ]

        response = client.post(
            "/api/projects/P1/matrix-editor/session/confirm",
            json={
                "expected_active_confirmed_matrix_id": seed_payload["active_confirmed_matrix_id"],
                "expected_active_confirmed_revision": seed_payload["active_confirmed_revision"],
                "source_document_path": seed_payload["source_preview_payload"]["source_document_path"],
                "source_document_name": seed_payload["source_preview_payload"]["source_document_name"],
                "source_format": seed_payload["source_preview_payload"]["source_format"],
                "source_import_id": seed_payload["active_source_import_id"],
                "source_snapshot_id": seed_payload["active_source_snapshot_id"],
                "confirmed_by": "operator",
                "pre_test_buffer_days": "0",
                "post_test_buffer_days": "0",
                "sample_received_date": "2026-06-01",
                "planned_test_start_date": "2026-06-01",
                "planned_test_complete_date": "2026-06-02",
                "estimated_completion_date": "2026-06-02",
                "groups": editor_draft["groups"],
                "rows": rows,
                "cells": editor_draft["cells"],
            },
        )

        assert response.status_code == 422
        assert "planned_test_complete_date is earlier" in response.text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_session_confirm_after_source_change_updates_active_lineage(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_a = _seed_source_import("P1", tmp_path)
        draft_a = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_a, "selected_group_keys": ["g1", "g2"]},
        )
        assert draft_a.status_code == 201
        draft_a_id = draft_a.json()["record"]["project_matrix_draft_id"]
        confirmed_a = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_a_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed_a.status_code == 201

        source_import_b = _seed_source_import(
            "P1",
            tmp_path,
            source_document_name="spec_b.docx",
            groups=(
                {"group_key": "g1", "group_label": "1", "sample_quantity_expression": "7"},
                {"group_key": "g2", "group_label": "2", "sample_quantity_expression": "8"},
                {"group_key": "g3", "group_label": "3", "sample_quantity_expression": "9"},
            ),
        )
        draft_b = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_b, "selected_group_keys": ["g1", "g3"]},
        )
        assert draft_b.status_code == 201
        draft_b_payload = draft_b.json()
        draft_b_id = draft_b_payload["record"]["project_matrix_draft_id"]

        draft_b_detail = client.get(f"/api/projects/P1/matrix-drafts/{draft_b_id}")
        assert draft_b_detail.status_code == 200
        session_seed = client.get("/api/projects/P1/matrix-editor/session")
        assert session_seed.status_code == 200
        seed_payload = session_seed.json()

        response = client.post(
            "/api/projects/P1/matrix-editor/session/confirm",
            json={
                "expected_active_confirmed_matrix_id": seed_payload["active_confirmed_matrix_id"],
                "expected_active_confirmed_revision": seed_payload["active_confirmed_revision"],
                "source_document_path": "C:/spec_b.docx",
                "source_document_name": "spec_b.docx",
                "source_format": ".docx",
                "source_import_id": source_import_b,
                "source_snapshot_id": draft_b_payload["record"]["source_snapshot_id"],
                "confirmed_by": "operator",
                "groups": draft_b_detail.json()["groups"],
                "rows": draft_b_detail.json()["rows"],
                "cells": draft_b_detail.json()["cells"],
            },
        )
        assert response.status_code == 200
        confirm_payload = response.json()
        assert confirm_payload["publish_status"] == "published"

        active_after = client.get("/api/projects/P1/confirmed-matrix/active-snapshot")
        assert active_after.status_code == 200
        active_version = active_after.json()["version"]
        assert active_version["source_import_id"] == source_import_b
        assert active_version["source_snapshot_id"] == draft_b_payload["record"]["source_snapshot_id"]

        seed_after = client.get("/api/projects/P1/matrix-editor/session")
        assert seed_after.status_code == 200
        seed_after_payload = seed_after.json()["source_preview_payload"]
        groups_after = seed_after_payload["groups"]
        assert [group["group_key"] for group in groups_after] == ["g1", "g2", "g3"]
        first_group_steps = groups_after[0]["steps"]
        assert first_group_steps
        assert first_group_steps[0]["method_summary"] == "EIA-364-18B"
        assert first_group_steps[0]["condition_summary"] == "10x min magnification"
        assert first_group_steps[0]["judgement_criteria"] == "No detrimental condition"
        assert first_group_steps[0]["source_note"] == "Visual note from source B"
        assert first_group_steps[0]["source_item_section_note"] == "Section note from source B"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_session_confirm_allows_stale_expected_when_source_is_unchanged(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201

        seed = client.get("/api/projects/P1/matrix-editor/session")
        assert seed.status_code == 200
        stale_seed = seed.json()
        editor_draft = stale_seed["editor_draft"]
        assert editor_draft is not None

        first_session_payload = {
            "expected_active_confirmed_matrix_id": stale_seed["active_confirmed_matrix_id"],
            "expected_active_confirmed_revision": stale_seed["active_confirmed_revision"],
            "source_document_path": stale_seed["source_preview_payload"]["source_document_path"],
            "source_document_name": stale_seed["source_preview_payload"]["source_document_name"],
            "source_format": stale_seed["source_preview_payload"]["source_format"],
            "source_import_id": stale_seed["active_source_import_id"],
            "source_snapshot_id": stale_seed["active_source_snapshot_id"],
            "confirmed_by": "operator",
            "groups": editor_draft["groups"],
            "rows": editor_draft["rows"],
            "cells": [
                {**cell, "cell_value": "2"}
                if index == 0
                else cell
                for index, cell in enumerate(editor_draft["cells"])
            ],
        }
        first_confirm = client.post(
            "/api/projects/P1/matrix-editor/session/confirm",
            json=first_session_payload,
        )
        assert first_confirm.status_code == 200
        assert first_confirm.json()["publish_status"] == "published"

        stale_expected_payload = {
            **first_session_payload,
            "cells": [
                {**cell, "cell_value": "3"}
                if index == 0
                else cell
                for index, cell in enumerate(editor_draft["cells"])
            ],
        }
        response = client.post(
            "/api/projects/P1/matrix-editor/session/confirm",
            json=stale_expected_payload,
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["publish_status"] == "published"
        assert payload["confirmed_snapshot"]["version"]["confirmed_revision"] == 3
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_editor_session_confirm_rejects_selected_group_sample_without_digit(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        created = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1", "g2"]},
        )
        assert created.status_code == 201
        draft_id = created.json()["record"]["project_matrix_draft_id"]
        confirmed = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirmed.status_code == 201

        seed = client.get("/api/projects/P1/matrix-editor/session")
        assert seed.status_code == 200
        payload = seed.json()
        editor_draft = payload["editor_draft"]
        assert editor_draft is not None
        groups = editor_draft["groups"]
        groups[0]["sample_quantity_expression"] = "sample only"

        response = client.post(
            "/api/projects/P1/matrix-editor/session/confirm",
            json={
                "expected_active_confirmed_matrix_id": payload["active_confirmed_matrix_id"],
                "expected_active_confirmed_revision": payload["active_confirmed_revision"],
                "source_document_path": payload["source_preview_payload"]["source_document_path"],
                "source_document_name": payload["source_preview_payload"]["source_document_name"],
                "source_format": payload["source_preview_payload"]["source_format"],
                "source_import_id": payload["active_source_import_id"],
                "source_snapshot_id": payload["active_source_snapshot_id"],
                "confirmed_by": "operator",
                "groups": groups,
                "rows": editor_draft["rows"],
                "cells": editor_draft["cells"],
            },
        )
        assert response.status_code == 422
        assert "Sample quantity is required for selected groups: 1." in response.text
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


def _seed_source_import(
    project_id: str,
    tmp_path: Path,
    *,
    source_document_name: str = "spec.docx",
    groups: tuple[dict[str, object], ...] | None = None,
) -> str:
    group_entries = list(
        groups
        if groups is not None
        else (
            {"group_key": "g1", "group_label": "1", "sample_quantity_expression": "5"},
            {"group_key": "g2", "group_label": "2", "sample_quantity_expression": "6"},
        )
    )
    group_entries_with_steps = []
    for index, group in enumerate(group_entries, start=1):
        entry = dict(group)
        group_label = str(entry.get("group_label", ""))
        entry.setdefault(
            "steps",
            [
                {
                    "sequence": index,
                    "raw_token": str(index),
                    "suffix_note": "(a)" if index == 1 else None,
                    "test_item": "Visual Examination",
                    "source_section": "1.1",
                    "source_note": "Visual note from source B" if index == 1 else None,
                    "source_note_origin": "step" if index == 1 else None,
                    "source_item_section_note": "Section note from source B" if index == 1 else None,
                    "condition_summary": "10x min magnification",
                    "method_summary": "EIA-364-18B",
                    "reference_standard": "EIA-364-18B",
                    "judgement_criteria": "No detrimental condition",
                    "estimated_duration_hint": None,
                    "duration_source": None,
                    "duration_status": "missing",
                    "source_table_index": 0,
                    "source_row_index": 3,
                    "warnings": [],
                }
            ],
        )
        group_entries_with_steps.append(entry)

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
                source_document_name=source_document_name,
                source_format=".docx",
                source_asset_id="asset-1",
                source_case_id="case-1",
                source_draft_id="draft-1",
                payload={
                    "groups": list(
                        group_entries_with_steps
                    ),
                    "rows": [
                        {
                            "source_row_index": 3,
                            "test_item": "Visual Examination",
                            "source_section": "1.1",
                            "group_tokens": {
                                str(group.get("group_label", "")): "1" if index == 0 else ""
                                for index, group in enumerate(
                                    group_entries
                                )
                            },
                            "is_sample_row": False,
                        },
                        {
                            "source_row_index": 4,
                            "test_item": "Samples Quantity (PCS)",
                            "source_section": None,
                            "group_tokens": {
                                str(group.get("group_label", "")): str(group.get("sample_quantity_expression", ""))
                                for group in (
                                    group_entries
                                )
                            },
                            "is_sample_row": True,
                        },
                    ],
                    "warnings": [],
                    "blockers": [],
                    "selected_group_keys_at_import": [
                        str(group.get("group_key", ""))
                        for group in (
                            group_entries
                        )
                    ],
                },
                created_at="2026-05-22T09:00:00+00:00",
            )
        )
        session.commit()
    engine.dispose()
    return import_id
