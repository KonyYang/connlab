import shutil
import uuid
from pathlib import Path

from backend.shared.config import DEFAULT_LOG_LEVEL, Settings


def test_settings_load_defaults_and_create_directories() -> None:
    workspace_tmp = _make_workspace_temp_dir()
    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.data_dir == workspace_tmp / "data"
        assert settings.projects_dir == workspace_tmp / "projects"
        assert settings.templates_dir == workspace_tmp / "templates"
        assert settings.log_level == DEFAULT_LOG_LEVEL
        assert settings.data_dir.is_dir()
        assert settings.projects_dir.is_dir()
        assert settings.templates_dir.is_dir()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_settings_respect_environment_overrides(
    monkeypatch,
) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    monkeypatch.setenv("CONNLAB_DATA_DIR", "custom-data")
    monkeypatch.setenv("CONNLAB_PROJECTS_DIR", str(workspace_tmp / "project-store"))
    monkeypatch.setenv("CONNLAB_TEMPLATES_DIR", "custom-templates")
    monkeypatch.setenv("CONNLAB_LOG_LEVEL", "debug")

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.data_dir == (workspace_tmp / "custom-data").resolve()
        assert settings.projects_dir == (workspace_tmp / "project-store").resolve()
        assert settings.templates_dir == (workspace_tmp / "custom-templates").resolve()
        assert settings.log_level == "DEBUG"
        assert settings.data_dir.is_dir()
        assert settings.projects_dir.is_dir()
        assert settings.templates_dir.is_dir()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def _make_workspace_temp_dir() -> Path:
    root = Path.cwd() / "tmp"
    root.mkdir(exist_ok=True)
    path = root / f"task002-{uuid.uuid4().hex}"
    path.mkdir()
    return path
