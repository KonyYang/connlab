from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import LtrRecord, LtrStatus, Project, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    LtrRecordRepository,
    ProjectCleanupAuditRecordRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_project_ltr_cleanup_dry_run_api_reports_dirty_records(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    client = TestClient(app)
    try:
        _seed_dirty_records(session_factory)

        response = client.get("/api/cleanup/project-ltr/dry-run")

        assert response.status_code == 200
        payload = response.json()
        assert payload["total_projects"] == 2
        assert payload["total_ltr_records"] == 1
        issue_types = {issue["issue_type"] for issue in payload["issues"]}
        assert "project_without_registered_ltr" in issue_types
        assert "invalid_registered_ltr_number" in issue_types
        invalid = [
            issue for issue in payload["issues"]
            if issue["issue_type"] == "invalid_registered_ltr_number"
        ][0]
        assert invalid["ltr_number"] == "DL-2026-04-080341"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_no_ltr_project_cleanup_execute_api_cancels_only_eligible_projects(
    tmp_path: Path,
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    settings.ensure_directories()
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
    client = TestClient(app)
    try:
        _seed_cleanup_execution_records(session_factory)

        response = client.post(
            "/api/cleanup/project-ltr/no-ltr-projects/execute",
            json={
                "project_ids": ["P-NO-LTR", "P-HAS-LTR"],
                "reason": "Historical test cleanup.",
                "operator": "pytest",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["cancelled_count"] == 1
        assert payload["skipped_count"] == 0
        assert payload["changed"][0]["project_id"] == "P-NO-LTR"
        assert payload["changed"][0]["previous_status"] == "confirmed"
        assert payload["changed"][0]["new_status"] == "cancelled"
        assert payload["rejected"][0]["project_id"] == "P-HAS-LTR"

        with session_factory() as session:
            projects = ProjectRepository(session)
            audits = ProjectCleanupAuditRecordRepository(session)
            assert projects.get("P-NO-LTR").status is ProjectStatus.CANCELLED
            assert projects.get("P-HAS-LTR").status is ProjectStatus.LTR_REGISTERED
            audit_records = audits.list()
            assert len(audit_records) == 1
            assert audit_records[0].project_id == "P-NO-LTR"
            assert audit_records[0].reason == "Historical test cleanup."
            assert audit_records[0].operator == "pytest"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _seed_dirty_records(session_factory) -> None:
    with session_factory() as session:
        projects = ProjectRepository(session)
        ltrs = LtrRecordRepository(session)
        projects.create(
            Project(
                project_id="P-NO-LTR",
                project_no=None,
                product_name="No LTR Project",
                requestor="Alice",
                status=ProjectStatus.CONFIRMED,
            )
        )
        projects.create(
            Project(
                project_id="P-BAD-LTR",
                project_no=None,
                product_name="Bad LTR Project",
                requestor="Bob",
                status=ProjectStatus.LTR_REGISTERED,
            )
        )
        ltrs.create(
            LtrRecord(
                ltr_id="L-BAD",
                project_id="P-BAD-LTR",
                ltr_number="DL-2026-04-080341",
                status=LtrStatus.REGISTERED,
            )
        )
        session.commit()


def _seed_cleanup_execution_records(session_factory) -> None:
    with session_factory() as session:
        projects = ProjectRepository(session)
        ltrs = LtrRecordRepository(session)
        projects.create(
            Project(
                project_id="P-NO-LTR",
                project_no=None,
                product_name="No LTR Project",
                requestor="Alice",
                status=ProjectStatus.CONFIRMED,
            )
        )
        projects.create(
            Project(
                project_id="P-HAS-LTR",
                project_no=None,
                product_name="Registered Project",
                requestor="Bob",
                status=ProjectStatus.LTR_REGISTERED,
            )
        )
        ltrs.create(
            LtrRecord(
                ltr_id="LTR-REGISTERED",
                project_id="P-HAS-LTR",
                ltr_number="DL-2026-04-099",
                status=LtrStatus.REGISTERED,
            )
        )
        session.commit()
