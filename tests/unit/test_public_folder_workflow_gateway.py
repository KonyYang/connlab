from __future__ import annotations

from pathlib import Path

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
    (source / "file.txt").write_text("content", encoding="utf-8")

    gateway.move_directory_no_overwrite(source, target)

    assert not source.exists()
    assert (target / "file.txt").read_text(encoding="utf-8") == "content"


def test_gateway_pull_uses_unique_history_target(tmp_path: Path) -> None:
    gateway = PublicFolderWorkflowGateway()
    current = tmp_path / "DL-1"
    current.mkdir()
    existing = tmp_path / "DL-1 - Pull 20260630T0100000000"
    existing.mkdir()

    target = gateway.unique_history_target(current, "2026-06-30T01:00:00+00:00")

    assert target.name == "DL-1 - Pull 20260630T0100000000 (2)"
