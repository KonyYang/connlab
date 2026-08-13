from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import FileAsset, FileAssetType, Project, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.infrastructure.storage.repositories import (
    FileAssetRepository,
    ProjectOfficialWorkspaceRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_source_candidates_api_lists_project_docx_and_preview_by_candidate(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        spec = tmp_path / "product_matrix_spec.docx"
        _write_product_spec_docx(spec)
        note = tmp_path / "notes.docx"
        note.write_bytes(b"x")
        _create_file_asset("P1", "A1", spec, "Product Matrix Spec.docx", tmp_path)
        _create_file_asset("P1", "A2", note, "notes.docx", tmp_path)

        listed = client.get("/api/projects/P1/test-plan/source-candidates")
        assert listed.status_code == 200
        payload = listed.json()
        assert payload["project_id"] == "P1"
        assert payload["candidates"][0]["source_asset_id"] == "A1"
        assert payload["candidates"][0]["candidate_kind"] == "likely_spec_or_matrix"

        preview = client.post("/api/projects/P1/test-plan/source-candidates/A1/matrix-preview")
        assert preview.status_code == 200
        preview_body = preview.json()
        assert preview_body["project_id"] == "P1"
        assert preview_body["source_document_name"] == "product_matrix_spec.docx"
        assert preview_body["source_format"] == ".docx"
        assert preview_body["groups"][0]["group_label"] == "Group 1"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_source_candidate_preview_rejects_cross_project_asset(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        _create_project("P2", tmp_path)
        spec = tmp_path / "spec.docx"
        _write_product_spec_docx(spec)
        _create_file_asset("P1", "A1", spec, "spec.docx", tmp_path)

        response = client.post("/api/projects/P2/test-plan/source-candidates/A1/matrix-preview")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_source_candidates_api_projects_submitted_material_directory(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        _create_project("P1", tmp_path)
        official = tmp_path / "official"
        submitted = official / "Submitted Material"
        submitted.mkdir(parents=True)
        _create_workspace("P1", official, tmp_path)

        response = client.get("/api/projects/P1/test-plan/source-candidates")

        assert response.status_code == 200
        assert response.json()["preferred_import_directory"] == str(submitted)
        assert response.json()["preferred_import_directory_source"] == "submitted_material"
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


def _create_project(project_id: str, tmp_path: Path) -> None:
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
                created_on=date(2026, 5, 14),
            )
        )
        session.commit()
    engine.dispose()


def _create_file_asset(
    project_id: str,
    asset_id: str,
    path: Path,
    original_name: str,
    tmp_path: Path,
) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        FileAssetRepository(session).create(
            FileAsset(
                asset_id=asset_id,
                project_id=project_id,
                asset_type=FileAssetType.ATTACHMENT,
                path=path,
                original_name=original_name,
                registered_on=date(2026, 5, 14),
            )
        )
        session.commit()
    engine.dispose()


def _create_workspace(project_id: str, official: Path, tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        ProjectOfficialWorkspaceRepository(session).save(
            OfficialWorkspaceRecord(
                workspace_id="W1",
                project_id=project_id,
                dl_number="DL-2026-05-P1",
                local_workspace_path=tmp_path / "local",
                source_book_path=tmp_path / "source.xlsx",
                official_folder_path=official,
                manifest_path=tmp_path / "manifest.json",
                template_source_path=tmp_path / "template",
                created_at="2026-05-14T00:00:00Z",
            )
        )
        session.commit()
    engine.dispose()


def _write_product_spec_docx(path: Path) -> None:
    document = Document()
    table = document.add_table(rows=4, cols=4)
    rows = [
        ["test Items", "Section", "Group 1", "Group 2"],
        ["Examination of Product", "5.4", "1,10", "1,13"],
        ["Contact Resistance (Low Level)", "6.1", "2,5,8", "2,5,10"],
        ["Durability", "7.1", "", "3"],
    ]
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            table.cell(row_index, column_index).text = value
    document.save(path)
