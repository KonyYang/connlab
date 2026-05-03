from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session
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


def _client(
    tmp_path: Path,
    *,
    include_session_factory: bool = False,
):
    """Create an isolated lookup option API client."""
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
    if include_session_factory:
        return client, engine, session_factory
    return client, engine
