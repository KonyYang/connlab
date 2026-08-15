import shutil
import uuid
from pathlib import Path

import pytest

from backend.shared.config import DEFAULT_LOG_LEVEL, Settings


def test_settings_load_defaults_and_create_directories() -> None:
    workspace_tmp = _make_workspace_temp_dir()
    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.data_dir == workspace_tmp / "data"
        assert settings.projects_dir == workspace_tmp / "projects"
        assert settings.templates_dir == workspace_tmp / "templates"
        assert settings.log_level == DEFAULT_LOG_LEVEL
        assert settings.contact_measurement_plan_authority_enabled is True
        assert settings.ltr_workbook.mode == "local_only"
        assert settings.ltr_workbook.write_enabled is False
        assert settings.ltr_workbook.path is None
        assert settings.ltr_workbook.modify_password is None
        assert settings.ltr_workbook.backup_retention_count == 30
        assert settings.ltr_workbook.backup_retention_days == 30
        assert settings.ltr_workbook.backup_retention_max_mb == 500
        assert settings.test_record.template_path is None
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
backup_retention_count = 12
backup_retention_days = 7
backup_retention_max_mb = 250
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
        assert settings.ltr_workbook.backup_retention_count == 12
        assert settings.ltr_workbook.backup_retention_days == 7
        assert settings.ltr_workbook.backup_retention_max_mb == 250
        assert settings.ltr_workbook.modify_password is None
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_settings_load_templates_dir_from_local_paths_config(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    config_path = workspace_tmp / "connlab.local.toml"
    config_path.write_text(
        """[paths]
templates_dir = "operator-templates"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.templates_dir == (
            workspace_tmp / "operator-templates"
        ).resolve()
        assert settings.templates_dir.is_dir()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_ltr_workbook_safe_summary_redacts_password(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    local_config_path = workspace_tmp / "connlab.local.toml"
    local_config_path.write_text(
        """[ltr_workbook]
path = "local/LTR_number.xls"
mode = "excel_com"
write_enabled = true
lock_dir = "locks"
lock_timeout_seconds = 90
backup_dir = "backups"
modify_password = "legacy-local-sentinel"
template_sheet_name = "Template"
sheet_bootstrap_clear_start_row = 3
backup_retention_count = 10
backup_retention_days = 14
backup_retention_max_mb = 300
""",
        encoding="utf-8",
    )
    admin_config_path = workspace_tmp / "connlab.admin.toml"
    admin_config_path.write_text(
        '[ltr_workbook]\nmodify_password = "admin-sentinel"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(local_config_path))

    try:
        summary = Settings.load(base_dir=workspace_tmp).ltr_workbook.safe_summary()

        assert summary["modify_password_configured"] is True
        assert summary["template_sheet_name_configured"] is True
        assert "admin-sentinel" not in str(summary)
        assert "Template" not in str(summary)
        assert summary["lock_timeout_seconds"] == 90
        assert summary["sheet_bootstrap_clear_start_row"] == 3
        assert summary["backup_retention_count"] == 10
        assert summary["backup_retention_days"] == 14
        assert summary["backup_retention_max_mb"] == 300
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_ltr_workbook_password_loads_from_default_admin_config(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    (workspace_tmp / "connlab.admin.toml").write_text(
        '[ltr_workbook]\nmodify_password = "admin-sentinel"\n',
        encoding="utf-8",
    )

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.ltr_workbook.modify_password == "admin-sentinel"
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_ltr_workbook_password_uses_explicit_admin_config_path(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    admin_config_path = workspace_tmp / "deployment" / "runtime.toml"
    admin_config_path.parent.mkdir()
    admin_config_path.write_text(
        '[ltr_workbook]\nmodify_password = "explicit-admin-sentinel"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_ADMIN_CONFIG_PATH", "deployment/runtime.toml")

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.ltr_workbook.modify_password == "explicit-admin-sentinel"
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_blank_password_environment_suppresses_admin_config(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    (workspace_tmp / "connlab.admin.toml").write_text(
        '[ltr_workbook]\nmodify_password = "admin-sentinel"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LTR_WORKBOOK_PASSWORD", "")

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.ltr_workbook.modify_password is None
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_ltr_workbook_settings_reject_invalid_lock_timeout(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    config_path = workspace_tmp / "connlab.local.toml"
    config_path.write_text(
        """[ltr_workbook]
lock_timeout_seconds = 0
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))

    try:
        with pytest.raises(ValueError, match="lock_timeout_seconds"):
            Settings.load(base_dir=workspace_tmp)
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_ltr_workbook_settings_reject_invalid_backup_retention(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    config_path = workspace_tmp / "connlab.local.toml"
    config_path.write_text(
        """[ltr_workbook]
backup_retention_count = 0
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))

    try:
        with pytest.raises(ValueError, match="backup_retention_count"):
            Settings.load(base_dir=workspace_tmp)
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_contact_measurement_plan_authority_flag_is_strict_and_env_only(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    try:
        monkeypatch.setenv("CONNLAB_CONTACT_MEASUREMENT_PLAN_AUTHORITY_ENABLED", "off")
        assert Settings.load(base_dir=workspace_tmp).contact_measurement_plan_authority_enabled is False
        monkeypatch.setenv("CONNLAB_CONTACT_MEASUREMENT_PLAN_AUTHORITY_ENABLED", "not-a-bool")
        with pytest.raises(ValueError, match="CONTACT_MEASUREMENT_PLAN_AUTHORITY_ENABLED"):
            Settings.load(base_dir=workspace_tmp)
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_ltr_workbook_password_env_override_is_redacted(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    (workspace_tmp / "connlab.admin.toml").write_text(
        '[ltr_workbook]\nmodify_password = "admin-sentinel"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LTR_WORKBOOK_PASSWORD", "env-secret")

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.ltr_workbook.modify_password == "env-secret"
        assert "env-secret" not in str(settings.ltr_workbook.safe_summary())
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
    monkeypatch.setenv("CONNLAB_TEST_RECORD_TEMPLATE_PATH", "templates/record.docx")
    monkeypatch.setenv("CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_COUNT", "9")
    monkeypatch.setenv("CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_DAYS", "11")
    monkeypatch.setenv("CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_MAX_MB", "123")

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.data_dir == (workspace_tmp / "custom-data").resolve()
        assert settings.projects_dir == (workspace_tmp / "project-store").resolve()
        assert settings.templates_dir == (workspace_tmp / "custom-templates").resolve()
        assert settings.log_level == "DEBUG"
        assert settings.test_record.template_path == (workspace_tmp / "templates" / "record.docx").resolve()
        assert settings.ltr_workbook.backup_retention_count == 9
        assert settings.ltr_workbook.backup_retention_days == 11
        assert settings.ltr_workbook.backup_retention_max_mb == 123
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
