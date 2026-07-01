from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import (
    get_local_path_picker_service,
    get_session,
    get_settings,
)
from backend.api.main import app
from backend.application.local_path_picker_service import LocalPathPickerService
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.shared.config import Settings


def test_external_resource_api_registers_lists_and_validates_folder(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    template = tmp_path / "folder-template"
    (template / "{DL_NUMBER}").mkdir(parents=True)
    try:
        registered = client.put(
            "/api/external-resources/project_folder_template",
            json={"path": str(template), "active": True},
        )
        listed = client.get("/api/external-resources")
        validated = client.post(
            "/api/external-resources/project_folder_template/validate"
        )

        assert registered.status_code == 200
        assert registered.json()["validation_status"] == "not_validated"
        assert listed.status_code == 200
        assert listed.json()[0]["resource_type"] == "project_folder_template"
        assert validated.status_code == 200
        assert validated.json()["validation_status"] == "valid"
        assert validated.json()["validation_failure_reason"] is None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_external_resource_api_registers_project_output_root(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    output_root = tmp_path / "project-output"
    output_root.mkdir()
    try:
        registered = client.put(
            "/api/external-resources/project_output_root",
            json={"path": str(output_root), "active": True},
        )
        validated = client.post(
            "/api/external-resources/project_output_root/validate"
        )

        assert registered.status_code == 200
        assert registered.json()["resource_type"] == "project_output_root"
        assert registered.json()["validation_status"] == "not_validated"
        assert validated.status_code == 200
        assert validated.json()["validation_status"] == "valid"
        assert validated.json()["validation_failure_reason"] is None
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_external_resource_api_records_invalid_excel_path(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        client.put(
            "/api/external-resources/standard_record_excel",
            json={"path": str(tmp_path / "missing.xlsx"), "active": True},
        )
        response = client.post(
            "/api/external-resources/standard_record_excel/validate"
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["validation_status"] == "invalid"
        assert "Expected an existing file" in payload["validation_failure_reason"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_external_resource_api_syncs_ltr_workbook_local_config(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "ConnLab" / "config" / "connlab.local.toml"
    workbook_path = tmp_path / "LTR_updated.xlsx"
    workbook_path.write_bytes(b"placeholder")
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))
    client, engine = _client(tmp_path)
    try:
        response = client.put(
            "/api/external-resources/ltr_workbook",
            json={"path": str(workbook_path), "active": True},
        )

        assert response.status_code == 200
        source = config_path.read_text(encoding="utf-8")
        assert f'path = "{workbook_path.as_posix()}"' in source
        assert "write_enabled = true" in source
        assert 'mode = "excel_com"' in source
        assert "modify_password" not in source
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_external_resource_api_returns_404_for_missing_registration(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        response = client.post("/api/external-resources/ltr_workbook/validate")

        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_external_resource_api_picks_directory_path(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    chosen = tmp_path / "templates"
    chosen.mkdir()
    app.dependency_overrides[get_local_path_picker_service] = lambda: _PickerService(chosen)
    try:
        response = client.post("/api/external-resources/project_folder_template/pick")

        assert response.status_code == 200
        assert response.json() == {"path": str(chosen)}
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(tmp_path: Path) -> tuple[TestClient, object]:
    """Create an isolated external resource API client."""
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
        """Yield a test database session."""
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


class _PickerService(LocalPathPickerService):
    def __init__(self, chosen: Path | None) -> None:
        self._chosen = chosen

    def pick_path(self, resource_type):  # type: ignore[override]
        return self._chosen
