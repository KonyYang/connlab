from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import ApplicationForm, ProjectStatus, SampleInfo
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    ProjectRepository,
    SampleInfoRepository,
)
from backend.shared.config import LtrWorkbookSettings, Settings


def test_ltr_workbook_write_preview_api_returns_no_write_mapping(
    tmp_path: Path,
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
        ltr_workbook=LtrWorkbookSettings(path=tmp_path / "LTR_number.xls"),
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
    client = TestClient(app)

    try:
        project_response = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-132",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["project_id"]
        _set_project_status(session_factory, project_id)
        _seed_inputs(session_factory, project_id)

        response = client.post(
            f"/api/projects/{project_id}/ltr-workbook/write-preview",
            json={
                "ltr_number": "DL-2026-05-007",
                "plan_date": "2026-05-07",
                "test_item": "Qualification bend testing",
                "sample_description": "CoolPower connector samples",
                "location": "AIPG Guangzhou",
                "test_type_in_sheet": "Qualification",
                "project_leader": "Alice",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["workbook_path"].endswith("LTR_number.xls")
        assert payload["target_sheet"] == "2026"
        assert payload["target_row"] is None
        values = {column["column"]: column["value"] for column in payload["columns"]}
        assert values["D"] == "DL-2026-05-007"
        assert values["E"] == "NPD"
        assert values["F"] == "CoolPower connector samples"
        assert values["G"] == "Qualification bend testing"
        assert values["H"] == "Qualification"
        assert values["J"] == "Nantong"
        assert values["K"] == "Alice"
        assert "target row is unknown" in payload["warnings"][0]
        assert client.get(f"/api/projects/{project_id}/ltr").json() == []
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _seed_inputs(session_factory, project_id: str) -> None:
    """Seed confirmed form and sample data for preview mapping."""
    with session_factory() as session:
        ApplicationFormRepository(session).create(
            ApplicationForm(
                form_id="F132",
                project_id=project_id,
                form_no="E-3718",
                revision="H",
                requester="Alice",
                project_type="New Product Development",
                manufacturing_site="Nantong",
                post_testing_disposition="Keep in the Lab",
                subcontract_allowed=False,
                additional_information="PO pending",
            )
        )
        SampleInfoRepository(session).create(
            SampleInfo(
                sample_id="S132",
                project_id=project_id,
                product_name="Connector",
                part_number="PN-001",
            )
        )
        session.commit()


def _set_project_status(session_factory, project_id: str) -> None:
    """Move the seeded project into confirmed state."""
    with session_factory() as session:
        repository = ProjectRepository(session)
        project = repository.get(project_id)
        assert project is not None
        repository.update(project.with_status(ProjectStatus.CONFIRMED))
        session.commit()
