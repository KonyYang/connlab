from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from backend.infrastructure.files import IntakeStorage


def test_intake_storage_resolves_package_directories(tmp_path: Path) -> None:
    """IntakeStorage resolves the controlled package directory structure."""
    storage = IntakeStorage(tmp_path / "intake")

    assert storage.package_root("pkg-1") == tmp_path / "intake" / "pkg-1"
    assert storage.source_dir("pkg-1").name == "source"
    assert storage.attachments_dir("pkg-1").name == "attachments"
    assert storage.snapshots_dir("pkg-1").name == "snapshots"


def test_intake_storage_sanitizes_file_names(tmp_path: Path) -> None:
    """Unsafe file names are collapsed into Windows-safe names."""
    storage = IntakeStorage(tmp_path / "intake")

    assert storage.sanitize_filename("../bad/name?.msg") == "name_.msg"
    assert storage.sanitize_filename("   ") == "file"


def test_intake_storage_copies_source_without_overwrite(tmp_path: Path) -> None:
    """Repeated source copies keep both files under unique names."""
    storage = IntakeStorage(tmp_path / "intake")
    source = tmp_path / "source.msg"
    source.write_text("first", encoding="utf-8")

    first = storage.copy_source_file("pkg-1", source)
    source.write_text("second", encoding="utf-8")
    second = storage.copy_source_file("pkg-1", source)

    assert first.stored_path.name == "source.msg"
    assert second.stored_path.name == "source_2.msg"
    assert first.stored_path.read_text(encoding="utf-8") == "first"
    assert second.stored_path.read_text(encoding="utf-8") == "second"


def test_intake_storage_copies_attachment_with_asset_prefix(tmp_path: Path) -> None:
    """Attachment copies include the asset id prefix and checksum metadata."""
    storage = IntakeStorage(tmp_path / "intake")
    source = tmp_path / "request.docx"
    source.write_bytes(b"docx fixture")

    stored = storage.copy_attachment("pkg-1", "asset-1", source)

    assert stored.stored_path.name == "asset-1__request.docx"
    assert stored.stored_path.parent == storage.attachments_dir("pkg-1")
    assert stored.size_bytes == len(b"docx fixture")
    assert stored.sha256 == hashlib.sha256(b"docx fixture").hexdigest()


def test_intake_storage_snapshot_path_is_non_overwriting(tmp_path: Path) -> None:
    """Snapshot paths are created under snapshots and avoid collisions."""
    storage = IntakeStorage(tmp_path / "intake")

    first = storage.snapshot_path("pkg-1", "mail_body.txt")
    first.write_text("first", encoding="utf-8")
    second = storage.snapshot_path("pkg-1", "mail_body.txt")

    assert first.name == "mail_body.txt"
    assert second.name == "mail_body_2.txt"


def test_intake_storage_rejects_missing_source(tmp_path: Path) -> None:
    """Copy operations fail clearly when the source file is missing."""
    storage = IntakeStorage(tmp_path / "intake")

    with pytest.raises(FileNotFoundError):
        storage.copy_source_file("pkg-1", tmp_path / "missing.msg")


def test_intake_storage_rejects_empty_package_id(tmp_path: Path) -> None:
    """Package ids must resolve to a usable directory segment."""
    storage = IntakeStorage(tmp_path / "intake")

    with pytest.raises(ValueError):
        storage.package_root(" ")
