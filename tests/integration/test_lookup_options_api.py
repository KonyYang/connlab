from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain.lookup_options import LookupOption
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories.lookup_options import (
    LookupOptionRepository,
)
from backend.shared.config import Settings


def test_lookup_options_api_seeds_and_returns_intake_precheck_groups(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    try:
        response = client.get("/api/lookups/intake-precheck")

        assert response.status_code == 200
        payload = response.json()
        assert set(payload) == {
            "business_unit",
            "manufacturing_site",
            "results_format",
            "test_type",
            "sample_status",
            "project_type",
            "post_testing_disposition",
        }
        assert payload["business_unit"][0] == {"value": "AAPG", "label": "AAPG"}
        assert {"value": "AAL", "label": "AAL"} in payload["manufacturing_site"]
        assert {"value": "Prototype", "label": "Prototype"} in payload["sample_status"]
        assert payload["post_testing_disposition"] == [
            {"value": "Choose an item.", "label": "Choose an item."},
            {"value": "Send Back to Requestor", "label": "Send Back to Requestor"},
            {"value": "Scrap", "label": "Scrap"},
            {"value": "Keep in the Lab", "label": "Keep in the Lab"},
        ]

        setup = client.get("/api/new-project/completion-options").json()
        assert "AIPG Guangzhou" in setup["location_options"]
        assert "Qualification" in setup["test_type_in_sheet_options"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_lookup_options_api_returns_database_values_without_reseeding(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path, include_session_factory=True)
    try:
        with session_factory() as session:
            LookupOptionRepository(session).add_many(
                (
                    LookupOption(
                        option_id="custom-bu",
                        group_key="business_unit",
                        value="Custom BU",
                        label="Custom BU",
                        sort_order=1,
                    ),
                )
            )
            session.commit()

        response = client.get("/api/lookups/intake-precheck")

        assert response.status_code == 200
        payload = response.json()
        assert payload["business_unit"] == [
            {"value": "Custom BU", "label": "Custom BU"}
        ]
        assert payload["manufacturing_site"] == []
        assert payload["post_testing_disposition"] == [
            {"value": "Choose an item.", "label": "Choose an item."},
            {"value": "Send Back to Requestor", "label": "Send Back to Requestor"},
            {"value": "Scrap", "label": "Scrap"},
            {"value": "Keep in the Lab", "label": "Keep in the Lab"},
        ]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_lookup_options_import_config_backs_up_and_updates_active_values(
    tmp_path: Path,
) -> None:
    client, engine = _client(tmp_path)
    config_path = tmp_path / "lookup-options.toml"
    config_path.write_text(
        """
[lookup_options]
project_setup_location = [
  "Nantong Lab",
  { value = "AIPG Guangzhou", active = false },
]
project_setup_test_type_in_sheet = [
  "Qualification",
  "Reliability",
]
""".strip(),
        encoding="utf-8",
    )
    try:
        response = client.post(
            "/api/lookups/import-config",
            json={"config_path": str(config_path), "backup_dir": str(tmp_path / "backups")},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["imported_count"] == 4
        assert payload["disabled_count"] == 1
        assert payload["backup_path"]
        assert Path(payload["backup_path"]).is_file()

        setup = client.get("/api/new-project/completion-options").json()
        assert setup["location_options"] == [
            option for option in setup["location_options"] if option != "AIPG Guangzhou"
        ]
        assert "Nantong Lab" in setup["location_options"]
        assert "Reliability" in setup["test_type_in_sheet_options"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _client(
    tmp_path: Path,
    *,
    include_session_factory: bool = False,
):
    """Create an isolated lookup option API client."""
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(
        settings
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
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    if include_session_factory:
        return client, engine, session_factory
    return client, engine
