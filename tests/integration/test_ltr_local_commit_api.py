from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import ApplicationForm, FileAsset, FileAssetType, ProjectStatus, SampleInfo
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    FileAssetRepository,
    ProjectRepository,
    SampleInfoRepository,
)
from backend.shared.config import Settings


def test_ltr_local_commit_api_creates_local_record_only(tmp_path: Path) -> None:
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
        project_response = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-044",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["project_id"]
        _set_project_status(session_factory, project_id, ProjectStatus.CONFIRMED)
        _seed_readiness_inputs(session_factory, project_id)

        response = client.post(
            f"/api/projects/{project_id}/ltr/commit",
            json={
                "year": 2026,
                "month": 4,
                "operator_confirmed": True,
                "registration_type": "associated",
                "proposed_ltr_number": "DL-2026-04-001A",
                "requested_by": "Alice",
                "operator_note": "Approved local registration",
            },
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["ltr"]["ltr_number"] == "DL-2026-04-001A"
        assert payload["ltr"]["status"] == "registered"
        assert payload["preview"]["status"] == "review_required"
        assert '"commit_mode": "local_only"' in payload["ltr"]["notes"]

        list_response = client.get(f"/api/projects/{project_id}/ltr")
        assert list_response.status_code == 200
        assert [row["ltr_number"] for row in list_response.json()] == [
            "DL-2026-04-001A"
        ]

        duplicate_response = client.post(
            f"/api/projects/{project_id}/ltr/commit",
            json={"year": 2026, "month": 4, "operator_confirmed": True},
        )
        assert duplicate_response.status_code == 400

        with session_factory() as session:
            project = ProjectRepository(session).get(project_id)
            assert project is not None
            assert project.status is ProjectStatus.LTR_REGISTERED
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_ltr_local_commit_api_rejects_unconfirmed_operator(tmp_path: Path) -> None:
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
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    try:
        project_response = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-044B",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["project_id"]

        response = client.post(
            f"/api/projects/{project_id}/ltr/commit",
            json={"year": 2026, "month": 4, "operator_confirmed": False},
        )

        assert response.status_code == 400
        assert "Operator confirmation is required" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _seed_readiness_inputs(
    session_factory,
    project_id: str,
) -> None:
    with session_factory() as session:
        ApplicationFormRepository(session).create(
            ApplicationForm(
                form_id="F1",
                project_id=project_id,
                form_no="E-3718",
                revision="H",
                requester="Alice",
                phone="555-0101",
                email="alice@example.test",
                manufacturing_site="DGLAB",
                requested_testing="Durability test per specification",
                subcontract_allowed=False,
                test_type="Validation",
                project_type="Qualification",
                post_testing_disposition="Return samples",
                additional_information="PO pending",
                lab="DGLAB",
                assigned_personnel="Bob",
            )
        )
        SampleInfoRepository(session).create(
            SampleInfo(
                sample_id="S1",
                project_id=project_id,
                product_name="Connector",
                part_number="PN-100",
            )
        )
        FileAssetRepository(session).create(
            FileAsset(
                asset_id="A1",
                project_id=project_id,
                asset_type=FileAssetType.ATTACHMENT,
                path=Path("spec.pdf"),
                original_name="Connector spec.pdf",
            )
        )
        session.commit()


def _set_project_status(
    session_factory,
    project_id: str,
    status: ProjectStatus,
) -> None:
    with session_factory() as session:
        repository = ProjectRepository(session)
        project = repository.get(project_id)
        assert project is not None
        repository.update(project.with_status(status))
        session.commit()
