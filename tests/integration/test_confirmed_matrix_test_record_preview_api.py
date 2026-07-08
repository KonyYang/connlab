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
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    Project,
    ProjectStatus,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ConfirmedMatrixAuthorityRepository,
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_confirmed_matrix_test_record_preview_api_happy_path(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        create_draft = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        assert create_draft.status_code == 201
        draft_id = create_draft.json()["record"]["project_matrix_draft_id"]
        confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirm.status_code == 201
        confirmed_id = confirm.json()["version"]["confirmed_matrix_id"]

        response = client.get(
            "/api/projects/P1/confirmed-matrix/test-record-preview"
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["project_id"] == "P1"
        assert payload["confirmed_matrix_id"] == confirmed_id
        assert payload["preview_status"] == "ready"
        assert [group["group_key"] for group in payload["groups"]] == ["g1"]
        assert payload["groups"][0]["sample_quantity_expression"] == "5"
        assert "source_section" not in payload["groups"][0]["steps"][0]
        assert payload["groups"][0]["steps"][0]["section"] == "6.1"
        assert payload["groups"][0]["steps"][0]["method"] == ""
        assert payload["groups"][0]["steps"][0]["condition"] == ""
        assert payload["groups"][0]["steps"][0]["requirement"] == ""
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirmed_matrix_test_record_preview_api_returns_step_quantity_metadata(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        _seed_active_snapshot_with_step_quantity("P1", tmp_path)

        response = client.get(
            "/api/projects/P1/confirmed-matrix/test-record-preview"
        )

        assert response.status_code == 200
        step = response.json()["groups"][0]["steps"][0]
        assert step["quantity"] == {
            "test_points_per_sample": "3",
            "readings_per_point": "2",
            "contact_points_per_sample": "6",
            "total_readings": "6",
            "status": "ready",
            "source": "matrix_step_override",
            "review_reason": None,
        }
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirmed_matrix_test_record_preview_api_returns_404_when_no_active_confirmed(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.get(
            "/api/projects/P1/confirmed-matrix/test-record-preview"
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirmed_matrix_test_record_preview_api_empty_active_authority(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        _seed_empty_active_confirmed_snapshot("P1", tmp_path)

        response = client.get(
            "/api/projects/P1/confirmed-matrix/test-record-preview"
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["project_id"] == "P1"
        assert payload["confirmed_matrix_id"] == "cmv-empty"
        assert payload["preview_status"] == "empty"
        assert payload["groups"] == []
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
                created_on=date(2026, 5, 23),
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
        service = SourceMatrixImportPersistenceService(
            store=SourceMatrixImportRepository(session)
        )
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
                        {
                            "group_key": "g1",
                            "group_label": "G1",
                            "sample_quantity_expression": "5",
                        },
                        {
                            "group_key": "g2",
                            "group_label": "G2",
                            "sample_quantity_expression": "6",
                        },
                    ],
                    "rows": [
                        {
                            "source_row_index": 3,
                            "test_item": "Visual",
                            "source_section": "6.1",
                            "method": "",
                            "condition": "",
                            "requirement": "",
                            "group_tokens": {"g1": "1", "g2": ""},
                            "is_sample_row": False,
                        },
                        {
                            "source_row_index": 4,
                            "test_item": "LLCR",
                            "source_section": "6.2",
                            "method": "",
                            "condition": "",
                            "requirement": "",
                            "group_tokens": {"g1": "2(a)", "g2": "3"},
                            "is_sample_row": False,
                        },
                        {
                            "source_row_index": 5,
                            "test_item": "Samples Quantity (PCS)",
                            "source_section": None,
                            "group_tokens": {"g1": "5", "g2": "6"},
                            "is_sample_row": True,
                        },
                    ],
                    "warnings": [],
                    "blockers": [],
                    "selected_group_keys_at_import": ["g1", "g2"],
                },
                created_at="2026-05-23T09:00:00+00:00",
            )
        )
        session.commit()
    engine.dispose()
    return import_id


def _seed_empty_active_confirmed_snapshot(project_id: str, tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        repo = ConfirmedMatrixAuthorityRepository(session)
        repo.create_snapshot(
            ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id="cmv-empty",
                    project_id=project_id,
                    project_matrix_draft_id="pmd-empty",
                    source_import_id="smi-empty",
                    source_snapshot_id="sms-empty",
                    confirmed_revision=1,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by="operator",
                    confirmed_at="2026-05-23T10:00:00+00:00",
                ),
                groups=(),
                rows=(),
                cells=(),
            )
        )
        session.commit()
    engine.dispose()


def _seed_active_snapshot_with_step_quantity(project_id: str, tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        repo = ConfirmedMatrixAuthorityRepository(session)
        row = ConfirmedMatrixRow(
            confirmed_row_id="cmr-llcr",
            confirmed_matrix_id="cmv-quantity",
            draft_row_id="pmdr-llcr",
            source_row_snapshot_id="smr-llcr",
            row_order=1,
            test_item="LLCR",
            source_section="6.2",
            method="M2",
            condition="C2",
            requirement="R2",
        )
        repo.create_snapshot(
            ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id="cmv-quantity",
                    project_id=project_id,
                    project_matrix_draft_id="pmd-quantity",
                    source_import_id="smi-quantity",
                    source_snapshot_id="sms-quantity",
                    confirmed_revision=1,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by="operator",
                    confirmed_at="2026-05-23T10:00:00+00:00",
                ),
                groups=(
                    ConfirmedMatrixGroup(
                        confirmed_group_id="cmg-1",
                        confirmed_matrix_id="cmv-quantity",
                        draft_group_id="pmdg-1",
                        source_group_snapshot_id="smg-1",
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        sample_quantity_expression="5",
                    ),
                ),
                rows=(row,),
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-1",
                        confirmed_matrix_id="cmv-quantity",
                        confirmed_row_id=row.confirmed_row_id,
                        confirmed_group_id="cmg-1",
                        draft_row_id=row.draft_row_id,
                        draft_group_id="pmdg-1",
                        cell_value="1",
                    ),
                ),
                step_quantities=(
                    ConfirmedMatrixStepQuantity(
                        confirmed_step_quantity_id="cmsq-1",
                        confirmed_matrix_id="cmv-quantity",
                        confirmed_group_id="cmg-1",
                        confirmed_row_id=row.confirmed_row_id,
                        draft_group_id="pmdg-1",
                        draft_row_id=row.draft_row_id,
                        step_sequence=1,
                        step_suffix_note=None,
                        raw_token="1",
                        test_points_per_sample="3",
                        readings_per_point="2",
                        contact_points_per_sample="6",
                        source="matrix_step_override",
                        review_required=False,
                        review_reason=None,
                        confirmed_at="2026-07-08T09:00:00+00:00",
                    ),
                ),
            )
        )
        session.commit()
    engine.dispose()
