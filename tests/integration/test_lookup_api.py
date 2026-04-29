from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import (
    ApplicationForm,
    FileAsset,
    FileAssetType,
    LtrRecord,
    LtrStatus,
    Project,
    ProjectStatus,
    SampleInfo,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    FileAssetRepository,
    LtrRecordRepository,
    ProjectRepository,
    SampleInfoRepository,
)
from backend.shared.config import Settings


def test_lookup_api_search_sample_and_testing_summary(tmp_path: Path) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project(session_factory)

        by_ltr = client.get("/api/projects/lookup", params={"query": "DL-2026-04-001"})
        by_part = client.get("/api/projects/lookup", params={"query": "PN-100"})
        sample = client.get("/api/projects/P1/sample-summary")
        testing = client.get("/api/projects/P1/testing-summary")

        assert by_ltr.status_code == 200
        assert by_ltr.json()[0]["matched_fields"] == ["ltr_number"]
        assert by_part.status_code == 200
        assert by_part.json()[0]["matched_fields"] == ["sample.part_number"]
        assert sample.status_code == 200
        assert sample.json()["samples"][0]["part_number"] == "PN-100"
        assert sample.json()["ltr_numbers"] == ["DL-2026-04-001"]
        assert testing.status_code == 200
        assert testing.json()["requested_testing"] == "Salt spray per customer spec"
        assert testing.json()["applicable_specifications"] == ["customer_spec.pdf"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_lookup_api_returns_404_for_missing_project(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        response = client.get("/api/projects/missing/sample-summary")

        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path):
    """Create an isolated lookup API client."""
    engine = create_database_engine(
        Settings(
            data_dir=tmp_path / "data",
            projects_dir=tmp_path / "projects",
            templates_dir=tmp_path / "templates",
            database_path=tmp_path / "connlab.sqlite3",
        )
    )
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session() -> Generator[Session, None, None]:
        """Yield a test database session."""
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    return TestClient(app), engine, session_factory


def _seed_project(session_factory) -> None:
    """Persist structured lookup records."""
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no="PRJ-100",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
            )
        )
        ApplicationFormRepository(session).create(
            ApplicationForm(
                form_id="F1",
                project_id="P1",
                form_no="E-3718",
                revision="H",
                requester="Alice",
                requested_testing="Salt spray per customer spec",
                test_type="Validation",
                sample_condition="Good",
                requested_completion_date="2026-05-10",
                lab="DGLAB",
                assigned_personnel="Bob",
            )
        )
        SampleInfoRepository(session).create(
            SampleInfo(
                sample_id="S1",
                project_id="P1",
                product_name="Connector",
                part_number="PN-100",
                revision="A",
                quantity=12,
            )
        )
        LtrRecordRepository(session).create(
            LtrRecord(
                ltr_id="L1",
                project_id="P1",
                ltr_number="DL-2026-04-001",
                status=LtrStatus.REGISTERED,
            )
        )
        FileAssetRepository(session).create(
            FileAsset(
                asset_id="A1",
                project_id="P1",
                asset_type=FileAssetType.ATTACHMENT,
                path=Path("customer_spec.pdf"),
                original_name="customer_spec.pdf",
            )
        )
        session.commit()
