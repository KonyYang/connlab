from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.shared.config import Settings


def test_standard_sheet_api_distinguishes_omission_reset_and_nonstandard(tmp_path: Path) -> None:
    client, engine = _client(tmp_path)
    try:
        custom = client.put(
            "/api/external-resources/standard_record_excel",
            json={"path": "standard.xlsx", "active": True, "worksheet_name": " Methods "},
        )
        omitted = client.put(
            "/api/external-resources/standard_record_excel",
            json={"path": "changed.xlsx", "active": True},
        )
        reset = client.put(
            "/api/external-resources/standard_record_excel",
            json={"path": "changed.xlsx", "active": True, "worksheet_name": None},
        )
        rejected = client.put(
            "/api/external-resources/equipment_calibration_excel",
            json={"path": "equipment.xlsx", "active": True, "worksheet_name": None},
        )

        assert custom.status_code == 200
        assert custom.json()["worksheet_name"] == "Methods"
        assert omitted.json()["worksheet_name"] == "Methods"
        assert reset.json()["worksheet_name"] == "认可标准"
        assert rejected.status_code == 400
        listed = client.get("/api/external-resources").json()
        assert all(item["resource_type"] != "equipment_calibration_excel" for item in listed)
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
    factory = create_session_factory(engine)

    def override_session() -> Generator[Session, None, None]:
        with factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), engine
