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
    ConfirmedMatrixAuthorityRepository,
    ProjectMatrixDraftRepository,
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


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


def _seed_project(project_id: str, session_factory: object) -> None:
    with session_factory() as session:  # type: ignore[operator]
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


def _commit_payload() -> dict[str, object]:
    return {
        "source_document_path": "C:/spec.docx",
        "source_document_name": "spec.docx",
        "source_format": ".docx",
        "selected_group_keys": ["g1", "g3"],
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
                {
                    "group_key": "g3",
                    "group_label": "Group 3",
                    "sample_quantity_expression": "7",
                },
            ],
            "rows": [
                {
                    "source_row_index": 1,
                    "test_item": "Visual",
                    "source_section": "6.1",
                    "method": "",
                    "condition": "",
                    "requirement": "",
                    "group_tokens": {"g1": "1", "g2": "2", "g3": "3"},
                    "is_sample_row": False,
                },
                {
                    "source_row_index": 2,
                    "test_item": "LLCR",
                    "source_section": "6.2",
                    "method": "",
                    "condition": "",
                    "requirement": "",
                    "group_tokens": {"g1": "4(a)", "g2": "5", "g3": "6,7"},
                    "is_sample_row": False,
                },
                {
                    "source_row_index": 3,
                    "test_item": "Samples Quantity (PCS)",
                    "source_section": None,
                    "group_tokens": {"g1": "5", "g2": "6", "g3": "7"},
                    "is_sample_row": True,
                },
            ],
            "warnings": [],
            "blockers": [],
        },
    }


def _assert_lineage_and_authority(
    *,
    session_factory: object,
    source_import_id: str,
    draft_id: str,
    confirmed_id: str,
) -> None:
    with session_factory() as session:  # type: ignore[operator]
        source = SourceMatrixImportRepository(session).get_snapshot_by_import(source_import_id)
        assert source is not None
        assert [group.group_key for group in source.groups] == ["g1", "g2", "g3"]

        draft = ProjectMatrixDraftRepository(session).get(draft_id)
        assert draft is not None
        assert [group.group_key for group in draft.groups] == ["g1", "g3"]
        assert "g2" not in {group.group_key for group in draft.groups}

        confirmed = ConfirmedMatrixAuthorityRepository(session).get(confirmed_id)
        assert confirmed is not None
        assert [group.group_key for group in confirmed.groups] == ["g1", "g3"]
        assert "g2" not in {group.group_key for group in confirmed.groups}


def test_matrix_to_test_record_smoke_flow_preserves_source_and_excludes_unselected(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", session_factory)

        commit = client.post("/api/projects/P1/matrix-import/commit", json=_commit_payload())
        assert commit.status_code == 201
        commit_body = commit.json()
        assert commit_body["selected_group_keys_committed"] == ["g1", "g3"]
        assert [group["group_key"] for group in commit_body["project_matrix_draft"]["groups"]] == [
            "g1",
            "g3",
        ]
        source_import_id = commit_body["source_import_id"]
        draft_id = commit_body["project_matrix_draft"]["record"]["project_matrix_draft_id"]

        confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirm.status_code == 201
        confirmed_body = confirm.json()
        confirmed_id = confirmed_body["version"]["confirmed_matrix_id"]
        assert [group["group_key"] for group in confirmed_body["groups"]] == ["g1", "g3"]

        preview = client.get("/api/projects/P1/confirmed-matrix/test-record-preview")
        assert preview.status_code == 200
        preview_body = preview.json()
        assert preview_body["project_id"] == "P1"
        assert preview_body["confirmed_matrix_id"] == confirmed_id
        assert preview_body["preview_status"] == "ready"
        assert [group["group_key"] for group in preview_body["groups"]] == ["g1", "g3"]
        assert "g2" not in {group["group_key"] for group in preview_body["groups"]}

        samples = {
            group["group_key"]: group["sample_quantity_expression"]
            for group in preview_body["groups"]
        }
        assert samples == {"g1": "5", "g3": "7"}

        steps_by_group = {
            group["group_key"]: [step["raw_token"] for step in group["steps"]]
            for group in preview_body["groups"]
        }
        assert steps_by_group["g1"] == ["1", "4(a)"]
        assert steps_by_group["g3"] == ["3", "6", "7"]

        first_step = preview_body["groups"][0]["steps"][0]
        assert first_step["section"] == "6.1"
        assert "source_section" not in first_step

        _assert_lineage_and_authority(
            session_factory=session_factory,
            source_import_id=source_import_id,
            draft_id=draft_id,
            confirmed_id=confirmed_id,
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
