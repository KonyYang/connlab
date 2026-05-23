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
    ProjectMatrixDraftRepository,
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        payload = _request_payload(selected_group_keys=["g1"])
        response = client.post("/api/projects/P1/matrix-import/commit", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["commit_status"] == "created"
        assert body["selected_group_keys_committed"] == ["g1"]
        assert [group["group_key"] for group in body["project_matrix_draft"]["groups"]] == ["g1"]
        source_import_id = body["source_import_id"]
        source_snapshot_id = body["source_snapshot_id"]

        with session_factory() as session:
            source_repo = SourceMatrixImportRepository(session)
            draft_repo = ProjectMatrixDraftRepository(session)
            source_snapshot = source_repo.get_snapshot_by_import(source_import_id)
            assert source_snapshot is not None
            assert source_snapshot.snapshot_id == source_snapshot_id
            assert len(source_snapshot.groups) == 2
            assert len(source_snapshot.cells) == 2
            import_record = source_repo.get_import(source_import_id)
            assert import_record is not None
            assert import_record.task261_commit_fingerprint is not None
            found_by_fp = source_repo.get_import_by_project_and_fingerprint(
                project_id="P1",
                task261_commit_fingerprint=import_record.task261_commit_fingerprint,
            )
            assert found_by_fp is not None
            draft_record = draft_repo.get_by_project_and_source_import("P1", source_import_id)
            assert draft_record is not None
            draft_snapshot = draft_repo.get(draft_record.project_matrix_draft_id)
            assert draft_snapshot is not None
            assert [group.group_key for group in draft_snapshot.groups] == ["g1"]
            assert len(draft_snapshot.cells) == 1

        reused = client.post("/api/projects/P1/matrix-import/commit", json=payload)
        assert reused.status_code == 201
        reused_body = reused.json()
        assert reused_body["commit_status"] == "reused"
        assert reused_body["source_import_id"] == source_import_id
        assert (
            reused_body["project_matrix_draft"]["record"]["project_matrix_draft_id"]
            == body["project_matrix_draft"]["record"]["project_matrix_draft_id"]
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_matrix_import_commit_api_validates_selected_groups(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)

        empty = client.post(
            "/api/projects/P1/matrix-import/commit",
            json=_request_payload(selected_group_keys=[]),
        )
        assert empty.status_code == 422

        unknown = client.post(
            "/api/projects/P1/matrix-import/commit",
            json=_request_payload(selected_group_keys=["g3"]),
        )
        assert unknown.status_code == 422

        duplicate = client.post(
            "/api/projects/P1/matrix-import/commit",
            json=_request_payload(selected_group_keys=["g1", "g1"]),
        )
        assert duplicate.status_code == 422

        malformed_rows = client.post(
            "/api/projects/P1/matrix-import/commit",
            json={
                **_request_payload(selected_group_keys=["g1"]),
                "preview_payload": {
                    "groups": [
                        {"group_key": "g1", "group_label": "Group 1"},
                        {"group_key": "g2", "group_label": "Group 2"},
                    ],
                    "rows": [123],
                    "warnings": [],
                    "blockers": [],
                },
            },
        )
        assert malformed_rows.status_code == 422
        assert "rows list contains non-object entries" in malformed_rows.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _request_payload(*, selected_group_keys: list[str]) -> dict[str, object]:
    return {
        "source_document_path": "C:/spec.docx",
        "source_document_name": "spec.docx",
        "source_format": ".docx",
        "selected_group_keys": selected_group_keys,
        "preview_payload": {
            "groups": [
                {
                    "group_key": "g1",
                    "group_label": "Group 1",
                    "sample_quantity_expression": "5",
                },
                {
                    "group_key": "g2",
                    "group_label": "Group 2",
                    "sample_quantity_expression": "6",
                },
            ],
            "rows": [
                {
                    "source_row_index": 1,
                    "test_item": "Visual",
                    "source_section": "6.1",
                    "group_tokens": {"g1": "1", "g2": "2"},
                    "is_sample_row": False,
                }
            ],
            "warnings": [],
            "blockers": [],
        },
    }


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
                created_on=date(2026, 5, 23),
            )
        )
        session.commit()
    engine.dispose()
