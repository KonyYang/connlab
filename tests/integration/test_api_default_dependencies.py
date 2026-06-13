from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api import dependencies
from backend.api.dependencies import _official_workspace_settings_from_registry
from backend.api.main import app
from backend.domain import ExternalResource, ExternalResourceType


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


def test_official_workspace_settings_use_default_locations_registry(
    tmp_path: Path,
) -> None:
    """TASK_316 should reuse ordinary Settings locations, not hidden path fields."""
    project_root = tmp_path / "Test Project"
    template_root = tmp_path / "Template"
    public_root = tmp_path / "Public"
    resources = _ResourceStore(
        {
            ExternalResourceType.PROJECT_OUTPUT_ROOT: project_root,
            ExternalResourceType.PROJECT_FOLDER_TEMPLATE: template_root,
            ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT: public_root,
        }
    )

    settings = _official_workspace_settings_from_registry(
        resources,
    )

    assert settings.local_workspace_root == project_root
    assert settings.template_path == template_root
    assert settings.public_drive_root == public_root


def test_official_workspace_settings_do_not_fallback_to_hidden_config(
    tmp_path: Path,
) -> None:
    """Missing visible Settings locations must stay missing instead of using hidden config."""
    settings = _official_workspace_settings_from_registry(
        _ResourceStore({}),
    )

    assert settings.local_workspace_root is None
    assert settings.template_path is None
    assert settings.public_drive_root is None


def _clear_dependency_caches() -> None:
    """Reset cached app-level database objects between dependency-stack checks."""
    engine = dependencies.get_engine.cache_info().currsize and dependencies.get_engine()
    dependencies.get_session_factory.cache_clear()
    dependencies.get_engine.cache_clear()
    if engine:
        engine.dispose()


class _ResourceStore:
    def __init__(self, paths: dict[ExternalResourceType, Path]) -> None:
        self._paths = paths

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        path = self._paths.get(resource_type)
        if path is None:
            return None
        return ExternalResource(
            resource_id=resource_type.value,
            resource_type=resource_type,
            path=path,
            active=True,
        )
