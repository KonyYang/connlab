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
    ProjectRepository,
    SampleInfoRepository,
)
from backend.shared.config import Settings


def test_ltr_registration_preview_api_is_no_write(tmp_path: Path) -> None:
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
                "project_no": "PRJ-043",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["project_id"]
        _set_project_status(session_factory, project_id)
        _seed_readiness_inputs(session_factory, project_id)

        response = client.get(
            f"/api/projects/{project_id}/ltr/preview",
            params={"year": 2026, "month": 4},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "review_required"
        assert payload["proposed_ltr_number"] is None
        assert payload["registration_type"] == "normal"
        assert payload["number_preflight_required"] is False
        assert payload["number_preview_allowed"] is False
        assert payload["final_number_reserved"] is False
        assert payload["mode"] == "local_only"
        assert payload["target_sheet"] == "2026"
        assert payload["readiness"]["blockers"] == []
        assert payload["conflicts"] == []

        list_response = client.get(f"/api/projects/{project_id}/ltr")
        assert list_response.status_code == 200
        assert list_response.json() == []
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


def _set_project_status(session_factory, project_id: str) -> None:
    with session_factory() as session:
        repository = ProjectRepository(session)
        project = repository.get(project_id)
        assert project is not None
        repository.update(project.with_status(ProjectStatus.CONFIRMED))
        session.commit()
