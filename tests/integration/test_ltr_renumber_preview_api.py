from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
from backend.api.main import app
from backend.domain import (
    FileAsset,
    FileAssetType,
    LtrRecord,
    LtrStatus,
    ProjectFolderRecord,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    FileAssetRepository,
    LtrRecordRepository,
    ProjectFolderRecordRepository,
)
from backend.shared.config import Settings


def test_ltr_renumber_preview_api_returns_non_destructive_plan(tmp_path: Path) -> None:
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
                "project_no": "PRJ-046",
                "product_name": "Connector",
                "requestor": "Alice",
            },
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["project_id"]
        _seed_records(session_factory, tmp_path, project_id)

        response = client.post(
            f"/api/projects/{project_id}/ltr/renumber-preview",
            json={
                "old_ltr_number": "DL-2026-04-001",
                "new_ltr_number": "DL-2026-04-002",
                "reason": "Corrected LTR assignment",
                "operator_confirmed": True,
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["old_ltr_number"] == "DL-2026-04-001"
        assert payload["new_ltr_number"] == "DL-2026-04-002"
        assert payload["operator_confirmation_required"] is True
        assert payload["operator_confirmed"] is True
        assert payload["conflicts"] == []
        assert [impact["record_type"] for impact in payload["impacts"]] == [
            "project_folder",
            "file_asset:application_form",
        ]

        list_response = client.get(f"/api/projects/{project_id}/ltr")
        assert list_response.status_code == 200
        assert list_response.json()[0]["ltr_number"] == "DL-2026-04-001"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _seed_records(
    session_factory,
    tmp_path: Path,
    project_id: str,
) -> None:
    old_number = "DL-2026-04-001"
    project_folder = tmp_path / f"{old_number}_PRJ-046"
    asset_path = project_folder / f"{old_number}_application.docx"
    with session_factory() as session:
        LtrRecordRepository(session).create(
            LtrRecord(
                ltr_id="LTR1",
                project_id=project_id,
                ltr_number=old_number,
                status=LtrStatus.REGISTERED,
            )
        )
        ProjectFolderRecordRepository(session).create(
            ProjectFolderRecord(
                folder_id="FOLDER1",
                project_id=project_id,
                folder_path=project_folder,
            )
        )
        FileAssetRepository(session).create(
            FileAsset(
                asset_id="ASSET1",
                project_id=project_id,
                asset_type=FileAssetType.APPLICATION_FORM,
                path=asset_path,
            )
        )
        session.commit()
