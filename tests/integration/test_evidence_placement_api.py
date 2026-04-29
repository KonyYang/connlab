from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import FileAsset, FileAssetType, ProjectFolderRecord, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    FileAssetRepository,
    ProjectFolderRecordRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_evidence_api_preview_and_place(tmp_path: Path) -> None:
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
    client = TestClient(app)

    try:
        project_id = client.post(
            "/api/projects",
            json={
                "project_no": "PRJ-047",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        ).json()["project_id"]
        project_folder = _create_real_style_project_folder(tmp_path)
        source = _touch(tmp_path / "source" / "mail.msg")
        with session_factory() as session:
            project_repository = ProjectRepository(session)
            project = project_repository.get(project_id)
            assert project is not None
            project_repository.update(project.with_status(ProjectStatus.FOLDER_CREATED))
            ProjectFolderRecordRepository(session).create(
                ProjectFolderRecord(
                    folder_id="folder-1",
                    project_id=project_id,
                    folder_path=project_folder,
                )
            )
            FileAssetRepository(session).create(
                FileAsset(
                    asset_id="asset-1",
                    project_id=project_id,
                    asset_type=FileAssetType.ATTACHMENT,
                    path=source,
                    original_name="mail.msg",
                )
            )
            session.commit()

        preview_response = client.post(
            f"/api/projects/{project_id}/evidence/placement-preview"
        )
        place_response = client.post(f"/api/projects/{project_id}/evidence/place")
        overwrite_response = client.post(f"/api/projects/{project_id}/evidence/place")

        assert preview_response.status_code == 200
        assert preview_response.json()["conflict"] is False
        assert preview_response.json()["items"][0]["category"] == "email"
        assert place_response.status_code == 201
        copied = Path(place_response.json()["copied_paths"][0])
        assert copied.is_file()
        assert copied.parent.name == "E-mail"
        assert overwrite_response.status_code == 409
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _create_real_style_project_folder(tmp_path: Path) -> Path:
    """Create a real-sample-like generated project folder."""
    project_folder = tmp_path / "DL-2025-09-054"
    title = project_folder / "DL-2025-09-054 EK550A Qualification Testing"
    for child in (
        title / "E-mail",
        title / "Photos",
        title / "Submitted Material",
        project_folder / "Source Book",
    ):
        child.mkdir(parents=True)
    return project_folder


def _touch(path: Path) -> Path:
    """Create a small test source file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("evidence", encoding="utf-8")
    return path
