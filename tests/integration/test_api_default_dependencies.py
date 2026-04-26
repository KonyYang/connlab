from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api import dependencies
from backend.api.main import app


def test_project_api_uses_default_session_dependency(tmp_path: Path, monkeypatch) -> None:
    """The real FastAPI dependency stack can open a local SQLite session."""
    monkeypatch.setenv("CONNLAB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CONNLAB_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("CONNLAB_TEMPLATES_DIR", str(tmp_path / "templates"))
    monkeypatch.setenv("CONNLAB_DATABASE_PATH", str(tmp_path / "connlab.sqlite3"))

    _clear_dependency_caches()
    client = TestClient(app)

    try:
        response = client.get("/api/projects")

        assert response.status_code == 200
        assert response.json() == []
    finally:
        _clear_dependency_caches()


def _clear_dependency_caches() -> None:
    """Reset cached app-level database objects between dependency-stack checks."""
    engine = dependencies.get_engine.cache_info().currsize and dependencies.get_engine()
    dependencies.get_session_factory.cache_clear()
    dependencies.get_engine.cache_clear()
    if engine:
        engine.dispose()
