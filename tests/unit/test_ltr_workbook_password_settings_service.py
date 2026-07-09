from pathlib import Path

import pytest

from backend.application.ltr_workbook_password_settings_service import (
    LtrWorkbookPasswordSettingsError,
    LtrWorkbookPasswordSettingsService,
)
from backend.shared.config import Settings


def test_ltr_workbook_password_update_requires_operator_confirmation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "connlab.local.toml"
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))
    service = LtrWorkbookPasswordSettingsService(base_dir=tmp_path)

    with pytest.raises(LtrWorkbookPasswordSettingsError, match="Confirm password update"):
        service.update_password("secret", operator_confirmed=False)

    assert config_path.exists() is False


def test_ltr_workbook_password_update_writes_local_config(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "connlab.local.toml"
    config_path.write_text(
        """[paths]
templates_dir = "templates"

[ltr_workbook]
path = "local/LTR_updated.xlsx"
modify_password = "old-secret"
write_enabled = true
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))
    service = LtrWorkbookPasswordSettingsService(base_dir=tmp_path)

    status = service.update_password("new-secret", operator_confirmed=True)

    assert status.configured is True
    assert status.overridden_by_environment is False
    assert status.password == "new-secret"
    assert Settings.load(base_dir=tmp_path).ltr_workbook.modify_password == "new-secret"
    source = config_path.read_text(encoding="utf-8")
    assert 'modify_password = "new-secret"' in source
    assert 'templates_dir = "templates"' in source
    assert 'path = "local/LTR_updated.xlsx"' in source


def test_ltr_workbook_password_status_reports_environment_override(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CONNLAB_LTR_WORKBOOK_PASSWORD", "env-secret")
    service = LtrWorkbookPasswordSettingsService(base_dir=tmp_path)

    status = service.status()

    assert status.configured is True
    assert status.overridden_by_environment is True
    assert status.password == "env-secret"
