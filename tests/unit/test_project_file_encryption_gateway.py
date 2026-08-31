from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.project_file_encryption_service import ProjectFileEncryptionPlanItem
from backend.infrastructure.files.project_file_encryption_gateway import (
    LocalProjectFileEncryptionGateway,
)


class _FakeProtector:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def encrypt_and_verify(
        self,
        *,
        source_path: Path,
        output_path: Path,
        password: str,
        office_kind: str,
    ) -> None:
        if self.fail:
            raise RuntimeError("Office save failed")
        output_path.write_text(
            f"encrypted:{office_kind}:{password}:{source_path.read_text(encoding='utf-8')}",
            encoding="utf-8",
        )


def _item(source: Path, target: Path, *, location: str, kind: str) -> ProjectFileEncryptionPlanItem:
    return ProjectFileEncryptionPlanItem(
        source_path=source,
        target_path=target,
        file_name=source.name,
        location=location,
        office_kind=kind,
        mode="replace_in_place" if location == "official_root" else "secured_copy",
        conflict=target.exists() and target != source,
        source_fingerprint="fingerprint",
        target_fingerprint=None,
    )


def test_root_file_is_verified_then_replaced_in_place(tmp_path: Path) -> None:
    source = tmp_path / "report.docx"
    source.write_text("plain", encoding="utf-8")
    gateway = LocalProjectFileEncryptionGateway(_FakeProtector())

    result = gateway.encrypt(
        item=_item(source, source, location="official_root", kind="word"),
        password="DGLAB",
        history_root=tmp_path / "History" / "Encryption" / "stamp" / "Test results",
        overwrite=False,
    )

    assert result == source
    assert source.read_text(encoding="utf-8") == "encrypted:word:DGLAB:plain"
    assert list(tmp_path.glob(".connlab-encryption-*")) == []


def test_test_result_archives_plain_source_and_existing_secured_copy(tmp_path: Path) -> None:
    results = tmp_path / "Test results"
    results.mkdir()
    source = results / "record.docx"
    target = results / "record_Secured.docx"
    source.write_text("new plain", encoding="utf-8")
    target.write_text("old secured", encoding="utf-8")
    history = tmp_path / "History" / "Encryption" / "stamp" / "Test results"
    gateway = LocalProjectFileEncryptionGateway(_FakeProtector())

    gateway.encrypt(
        item=_item(source, target, location="test_results", kind="word"),
        password="DGLAB",
        history_root=history,
        overwrite=True,
    )

    assert not source.exists()
    assert target.read_text(encoding="utf-8") == "encrypted:word:DGLAB:new plain"
    assert (history / "record.docx").read_text(encoding="utf-8") == "new plain"
    assert (history / "record_Secured.docx").read_text(encoding="utf-8") == "old secured"


def test_office_failure_keeps_source_and_conflict_untouched(tmp_path: Path) -> None:
    results = tmp_path / "Test results"
    results.mkdir()
    source = results / "record.docx"
    target = results / "record_Secured.docx"
    source.write_text("plain", encoding="utf-8")
    target.write_text("old", encoding="utf-8")
    gateway = LocalProjectFileEncryptionGateway(_FakeProtector(fail=True))

    with pytest.raises(RuntimeError, match="Office save failed"):
        gateway.encrypt(
            item=_item(source, target, location="test_results", kind="word"),
            password="DGLAB",
            history_root=tmp_path / "History" / "Encryption" / "stamp" / "Test results",
            overwrite=True,
        )

    assert source.read_text(encoding="utf-8") == "plain"
    assert target.read_text(encoding="utf-8") == "old"

