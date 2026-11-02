from __future__ import annotations

from pathlib import Path
import errno
import shutil

import pytest

from backend.infrastructure.files.public_folder_workflow_gateway import (
    PublicFolderWorkflowGateway,
    PublicFolderWorkflowTargetChangedError,
)


def test_gateway_copy_new_file_does_not_overwrite_existing_target(tmp_path: Path) -> None:
    gateway = PublicFolderWorkflowGateway()
    source = tmp_path / "local" / "a.txt"
    target = tmp_path / "public" / "a.txt"
    source.parent.mkdir()
    target.parent.mkdir()
    source.write_text("local", encoding="utf-8")
    target.write_text("human", encoding="utf-8")

    with pytest.raises(PublicFolderWorkflowTargetChangedError):
        gateway.copy_new_file(source, target)

    assert target.read_text(encoding="utf-8") == "human"


def test_failed_copy_retains_destination_for_review(tmp_path: Path, monkeypatch) -> None:
    gateway = PublicFolderWorkflowGateway()
    source = tmp_path / "source.txt"
    target = tmp_path / "public" / "target.txt"
    source.write_text("source", encoding="utf-8")
    target.parent.mkdir()
    original = shutil.copyfileobj
    def fail_destination_copy(source_handle, target_handle, *args, **kwargs):
        if isinstance(target_handle.name, int):
            target_handle.write(b"partial")
            raise OSError("simulated write error")
        return original(source_handle, target_handle, *args, **kwargs)
    monkeypatch.setattr(shutil, "copyfileobj", fail_destination_copy)
    with pytest.raises(PublicFolderWorkflowTargetChangedError, match="Review it manually"):
        gateway.copy_new_file(source, target)
    assert target.read_bytes() == b"partial"


def test_gateway_replace_managed_file_requires_expected_fingerprint(tmp_path: Path) -> None:
    gateway = PublicFolderWorkflowGateway()
    source = tmp_path / "local.txt"
    target = tmp_path / "public.txt"
    source.write_text("new", encoding="utf-8")
    target.write_text("old", encoding="utf-8")

    with pytest.raises(PublicFolderWorkflowTargetChangedError):
        gateway.replace_managed_file(
            source,
            target,
            expected_public_fingerprint="not-current",
        )

    assert target.read_text(encoding="utf-8") == "old"


def test_gateway_moves_directory_without_overwrite(tmp_path: Path) -> None:
    gateway = PublicFolderWorkflowGateway()
    source = tmp_path / "Open" / "2026" / "DL-1"
    target = tmp_path / "Closed" / "2026" / "DL-1"
    source.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    (source / "file.txt").write_text("content", encoding="utf-8")

    gateway.move_directory_no_overwrite(source, target)

    assert not source.exists()
    assert (target / "file.txt").read_text(encoding="utf-8") == "content"


def test_gateway_refuses_move_when_parent_does_not_exist(tmp_path: Path) -> None:
    gateway = PublicFolderWorkflowGateway()
    source = tmp_path / "Open" / "2026" / "DL-1"
    target = tmp_path / "Closed" / "2026" / "DL-1"
    source.mkdir(parents=True)
    with pytest.raises(OSError):
        gateway.move_directory_no_overwrite(source, target)
    assert source.is_dir()
    assert not target.parent.exists()


def test_gateway_does_not_replace_directory_created_during_move(tmp_path: Path, monkeypatch) -> None:
    import backend.infrastructure.files.public_folder_workflow_gateway as gateway_module

    source = tmp_path / "Open" / "2026" / "DL-1"
    target = tmp_path / "Closed" / "2026" / "DL-1"
    source.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    (source / "file.txt").write_text("source", encoding="utf-8")
    real_rename = gateway_module._rename_directory_no_replace

    def create_target_then_rename(source_path, target_path):
        target_path.mkdir()
        return real_rename(source_path, target_path)

    monkeypatch.setattr(gateway_module, "_rename_directory_no_replace", create_target_then_rename)
    with pytest.raises(OSError):
        PublicFolderWorkflowGateway().move_directory_no_overwrite(source, target)

    assert target.is_dir()
    assert not list(target.iterdir())
    assert (source / "file.txt").read_text(encoding="utf-8") == "source"


def test_gateway_reports_cross_device_move_without_copying(tmp_path: Path, monkeypatch) -> None:
    import backend.infrastructure.files.public_folder_workflow_gateway as gateway_module
    source = tmp_path / "Open" / "2026" / "DL-1"
    target = tmp_path / "Closed" / "2026" / "DL-1"
    source.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    def cross_device(_source, _target):
        raise OSError(errno.EXDEV, "cross-device")
    monkeypatch.setattr(gateway_module, "_rename_directory_no_replace", cross_device)
    with pytest.raises(PublicFolderWorkflowTargetChangedError, match="remains unchanged"):
        PublicFolderWorkflowGateway().move_directory_no_overwrite(source, target)
    assert source.is_dir()
    assert not target.exists()


def test_gateway_pull_uses_unique_history_target(tmp_path: Path) -> None:
    gateway = PublicFolderWorkflowGateway()
    current = tmp_path / "DL-1"
    current.mkdir()
    existing = tmp_path / "DL-1 - Pull 20260630T0100000000"
    existing.mkdir()

    target = gateway.unique_history_target(current, "2026-06-30T01:00:00+00:00")

    assert target.name == "DL-1 - Pull 20260630T0100000000 (2)"
