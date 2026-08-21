from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import ExternalResource, ExternalResourceType, Project, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ExternalResourceRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_customer_feedback_generation_api_returns_output_metadata(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _seed_project_and_template(tmp_path)

        response = client.post("/api/projects/P1/customer-feedback/generate")

        assert response.status_code == 200
        payload = response.json()
        assert payload["project_id"] == "P1"
        assert payload["template_path"].endswith("E-4243_D Customer Feedback Form.xlsx")
        assert payload["output_file_name"] == "DL-2026-05-003_customer_feedback_E-4243.xlsx"
        assert Path(payload["output_path"]).is_file()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_customer_feedback_generation_api_missing_project_returns_404(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _seed_template_only(tmp_path)

        response = client.post("/api/projects/MISSING/customer-feedback/generate")

        assert response.status_code == 404
        assert "Project was not found" in response.text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_customer_feedback_generation_api_rejects_output_dir_request_field(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _seed_project_and_template(tmp_path)

        response = client.post(
            "/api/projects/P1/customer-feedback/generate",
            json={"output_dir": str(tmp_path / "public-drive")},
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_customer_feedback_generation_api_missing_template_returns_409(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _seed_project_and_template(tmp_path, include_template=False)

        response = client.post("/api/projects/P1/customer-feedback/generate")

        assert response.status_code == 409
        assert "E-4243" in response.text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_customer_feedback_generation_api_multiple_templates_returns_409(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _seed_project_and_template(tmp_path, extra_template=True)

        response = client.post("/api/projects/P1/customer-feedback/generate")

        assert response.status_code == 409
        assert "Multiple" in response.text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object]:
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
    return TestClient(app), engine


def _seed_project_and_template(
    tmp_path: Path,
    *,
    include_template: bool = True,
    extra_template: bool = False,
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    template_dir = tmp_path / "template-root"
    template_dir.mkdir()
    if include_template:
        _write_feedback_template(template_dir / "E-4243_D Customer Feedback Form.xlsx")
    if extra_template:
        _write_feedback_template(template_dir / "copy E-4243 customer feedback.xlsx")
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id="P1",
                project_no="DL-2026-05-003",
                product_name="Coolpower",
                requestor="MP Cao",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 6, 1),
            )
        )
        ExternalResourceRepository(session).upsert(
            ExternalResource(
                resource_id="R1",
                resource_type=ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
                path=template_dir,
            )
        )
        session.commit()
    engine.dispose()


def _seed_template_only(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    template_dir = tmp_path / "template-root"
    template_dir.mkdir()
    _write_feedback_template(template_dir / "E-4243_D Customer Feedback Form.xlsx")
    with session_factory() as session:
        ExternalResourceRepository(session).upsert(
            ExternalResource(
                resource_id="R1",
                resource_type=ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
                path=template_dir,
            )
        )
        session.commit()
    engine.dispose()


def _write_feedback_template(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "Work Request No."
    sheet["A2"] = "Project Details"
    workbook.save(path)
    workbook.close()
