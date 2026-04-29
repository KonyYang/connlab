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
        assert settings.ltr_workbook.mode == "local_only"
        assert settings.ltr_workbook.write_enabled is False
        assert settings.ltr_workbook.path is None
        assert settings.ltr_workbook.modify_password is None
        assert settings.data_dir.is_dir()
        assert settings.projects_dir.is_dir()
        assert settings.templates_dir.is_dir()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_settings_load_ltr_workbook_from_local_config(
    monkeypatch,
) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    config_path = workspace_tmp / "connlab.local.toml"
    config_path.write_text(
        """[ltr_workbook]
path = "local/LTR_number.xls"
mode = "excel_com"
write_enabled = true
lock_dir = "locks"
backup_dir = "backups"
modify_password = "placeholder-secret"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.ltr_workbook.path == (workspace_tmp / "local" / "LTR_number.xls").resolve()
        assert settings.ltr_workbook.mode == "excel_com"
        assert settings.ltr_workbook.write_enabled is True
        assert settings.ltr_workbook.lock_dir == (workspace_tmp / "locks").resolve()
        assert settings.ltr_workbook.backup_dir == (workspace_tmp / "backups").resolve()
        assert settings.ltr_workbook.modify_password == "placeholder-secret"
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
