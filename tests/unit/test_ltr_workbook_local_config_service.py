from __future__ import annotations

from pathlib import Path

from backend.application.ltr_workbook_local_config_service import (
    LtrWorkbookLocalConfigService,
)


def test_sync_ltr_workbook_path_creates_write_enabled_local_config(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "ConnLab" / "config" / "connlab.local.toml"
    workbook_path = tmp_path / "LTR" / "LTR_updated.xlsx"
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))

    LtrWorkbookLocalConfigService(base_dir=tmp_path).sync_workbook_path(workbook_path)

    source = config_path.read_text(encoding="utf-8")
    assert "[ltr_workbook]" in source
    assert f'path = "{workbook_path.as_posix()}"' in source
    assert 'mode = "excel_com"' in source
    assert "write_enabled = true" in source
    assert f'lock_dir = "{(tmp_path / "ConnLab" / "locks").as_posix()}"' in source
    assert f'backup_dir = "{(tmp_path / "ConnLab" / "backups").as_posix()}"' in source
    assert "modify_password" not in source


def test_sync_ltr_workbook_path_preserves_existing_user_settings(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "connlab.local.toml"
    config_path.write_text(
        "[ltr_workbook]\n"
        'path = "D:/Old/LTR.xlsx"\n'
        'mode = "excel_com"\n'
        "write_enabled = false\n"
        'lock_dir = "D:/UserLocks"\n'
        'backup_dir = "D:/UserBackups"\n'
        'modify_password = "operator-secret"\n',
        encoding="utf-8",
    )
    workbook_path = tmp_path / "new" / "LTR_updated.xlsx"
    monkeypatch.setenv("CONNLAB_LOCAL_CONFIG_PATH", str(config_path))

    LtrWorkbookLocalConfigService(base_dir=tmp_path).sync_workbook_path(workbook_path)

    source = config_path.read_text(encoding="utf-8")
    assert f'path = "{workbook_path.as_posix()}"' in source
    assert "write_enabled = false" in source
    assert 'lock_dir = "D:/UserLocks"' in source
    assert 'backup_dir = "D:/UserBackups"' in source
    assert 'modify_password = "operator-secret"' in source
