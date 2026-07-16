from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.application.contact_point_profile_lifecycle_service import (
    ContactPointProfileLifecycleService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
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
)
from backend.infrastructure.storage.repositories.contact_point_profile_authority import (
    ContactPointProfileAuthorityRepository,
)
from backend.shared.config import Settings


def test_confirmed_matrix_fee_draft_api_happy_path(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        _seed_active_confirmed_snapshot("P1", tmp_path)

        response = client.get("/api/projects/P1/confirmed-matrix/fee-draft")

        assert response.status_code == 200
        payload = response.json()
        assert payload["header"]["project_id"] == "P1"
        assert payload["header"]["pricing_rule_version_id"] == "fee_rules_v2026_07_16_r3"
        assert payload["header"]["pricing_effective_from"] == "2026-06-03"
        assert payload["draft_status"] == "ready"
        assert payload["groups"][0]["group_key"] == "g1"
        assert payload["groups"][0]["line_items"][0]["matched_rule_id"] == "fee_rule_visual_exam"
        assert (
            payload["groups"][0]["line_items"][0]["matched_rule_version_id"]
            == "fee_rules_v2026_07_16_r3"
        )
        assert payload["groups"][0]["line_items"][0]["spend_time"] == "0.5"
        assert payload["groups"][0]["line_items"][0]["unit_price"] == "10"
        assert payload["groups"][0]["line_items"][0]["testing_fee"] == "0"
        assert payload["groups"][0]["line_items"][0]["field_metadata"][0] == {
            "field": "spend_time",
            "state": "auto_filled",
            "message": None,
            "source": "Visual exam",
        }
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_confirmed_matrix_fee_draft_api_returns_404_when_no_active_confirmed(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.get("/api/projects/P1/confirmed-matrix/fee-draft")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_fee_draft_api_uses_confirmed_point_profile_for_llcr_units(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        _seed_llcr_snapshot("P1", tmp_path)
        _confirm_point_profile("P1", tmp_path)

        response = client.get("/api/projects/P1/confirmed-matrix/fee-draft")

        assert response.status_code == 200
        line = response.json()["groups"][0]["line_items"][0]
        assert line["units"] == "20"
        assert any(
            item["field"] == "units"
            and item["source"].startswith("Confirmed Project Point Profile: revision 1")
            for item in line["field_metadata"]
        )
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
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id=project_id,
                project_no=f"DL-2026-06-{project_id}",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 6, 4),
            )
        )
        session.commit()
    engine.dispose()


def _seed_active_confirmed_snapshot(project_id: str, tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        repo = ConfirmedMatrixAuthorityRepository(session)
        repo.create_snapshot(
            ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id="cmv-1",
                    project_id=project_id,
                    project_matrix_draft_id="pmd-1",
                    source_import_id="smi-1",
                    source_snapshot_id="sms-1",
                    confirmed_revision=1,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by="operator",
                    confirmed_at="2026-06-04T10:00:00+08:00",
                    sample_received_date="2026-06-03",
                ),
                groups=(
                    ConfirmedMatrixGroup(
                        confirmed_group_id="cmg-1",
                        confirmed_matrix_id="cmv-1",
                        draft_group_id="pmdg-1",
                        source_group_snapshot_id="smg-1",
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        sample_quantity_expression="5",
                    ),
                ),
                rows=(
                    ConfirmedMatrixRow(
                        confirmed_row_id="cmr-visual",
                        confirmed_matrix_id="cmv-1",
                        draft_row_id="pmdr-visual",
                        source_row_snapshot_id="smr-visual",
                        row_order=1,
                        test_item="Visual Examination",
                        source_section="6.1",
                        method="EIA-364-18",
                        condition="Visual Inspection",
                        requirement="No damage",
                        day_expression="2D",
                    ),
                ),
                cells=(
                    ConfirmedMatrixCell(
                        confirmed_cell_id="cmc-1",
                        confirmed_matrix_id="cmv-1",
                        confirmed_row_id="cmr-visual",
                        confirmed_group_id="cmg-1",
                        draft_row_id="pmdr-visual",
                        draft_group_id="pmdg-1",
                        cell_value="1",
                    ),
                ),
            )
        )
        session.commit()
    engine.dispose()


def _seed_llcr_snapshot(project_id: str, tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        repo = ConfirmedMatrixAuthorityRepository(session)
        repo.create_snapshot(
            ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id="cmv-llcr", project_id=project_id,
                    project_matrix_draft_id="pmd-1", source_import_id="smi-1",
                    source_snapshot_id="sms-1", confirmed_revision=1,
                    is_active_authority=True, status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by="operator", confirmed_at="2026-07-15T10:00:00+08:00",
                    sample_received_date="2026-06-03",
                ),
                groups=(ConfirmedMatrixGroup(
                    confirmed_group_id="cmg-llcr", confirmed_matrix_id="cmv-llcr",
                    draft_group_id="pmdg-1", source_group_snapshot_id="smg-1",
                    group_order=1, group_key="g1", group_label="G1",
                    sample_quantity_expression="5",
                ),),
                rows=(ConfirmedMatrixRow(
                    confirmed_row_id="cmr-llcr", confirmed_matrix_id="cmv-llcr",
                    draft_row_id="pmdr-llcr", source_row_snapshot_id="smr-1",
                    row_order=1, test_item="Contact Resistance (Low Level)",
                    source_section="6.1", method="EIA-364-06", condition="",
                    requirement="",
                ),),
                cells=(ConfirmedMatrixCell(
                    confirmed_cell_id="cmc-llcr", confirmed_matrix_id="cmv-llcr",
                    confirmed_row_id="cmr-llcr", confirmed_group_id="cmg-llcr",
                    draft_row_id="pmdr-llcr", draft_group_id="pmdg-1", cell_value="1",
                ),),
            )
        )
        session.commit()
    engine.dispose()


def _confirm_point_profile(project_id: str, tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ContactPointProfileLifecycleService(
            ContactPointProfileAuthorityRepository(session),
            clock=lambda: "2026-07-15T10:00:00+00:00",
        ).confirm_direct(
            project_id=project_id,
            expected_revision_id=None,
            expected_fingerprint=None,
            rows=[{"category_id": None, "prefix": "P", "point_expression": "1-4"}],
            actor="tester",
        )
        session.commit()
    engine.dispose()


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
