from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os

import pytest

from backend.infrastructure.files.report_publication_gateway import (
    ReportPublicationConflictError,
    ReportPublicationGateway,
)


def test_discovers_only_internal_reports_for_the_project(tmp_path: Path) -> None:
    official = tmp_path / "official"
    official.mkdir()
    internal = official / "DL-001 Product Qualification Testing Report_Rev_A.docx"
    internal.write_bytes(b"internal")
    (official / "DL-001-CR Product Qualification Testing Report_Customer_Rev_A.docx").write_bytes(
        b"customer"
    )
    (official / "DL-001 Test Record.docx").write_bytes(b"record")
    (official / "DL-002 Product Qualification Testing Report_Rev_A.docx").write_bytes(
        b"other"
    )
    (official / "DL-0012 Product Qualification Testing Report_Rev_A.docx").write_bytes(
        b"prefix-collision"
    )

    candidates = ReportPublicationGateway().discover_internal_reports(
        official_folder=official,
        dl_number="DL-001",
    )

    assert candidates == (internal,)


def test_changed_report_is_archived_and_atomically_replaced(tmp_path: Path) -> None:
    current = tmp_path / "official" / "DL-001 Report.docx"
    current.parent.mkdir()
    current.write_bytes(b"operator-maintained|old-llcr")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway(
        clock=lambda: datetime(2026, 8, 30, 14, 35, 22)
    )
    expected = gateway.fingerprint(current)

    result = gateway.publish_update(
        current_path=current,
        expected_current_sha256=expected,
        history_root=history,
        update_document=lambda source, output: _write_update(
            source,
            output,
            b"operator-maintained|new-llcr",
        ),
    )

    assert result.changed is True
    assert current.read_bytes() == b"operator-maintained|new-llcr"
    assert result.archive_path == (
        history / "20260830-143522" / "DL-001 Report.docx"
    )
    assert result.archive_path.read_bytes() == b"operator-maintained|old-llcr"
    assert result.current_sha256 == gateway.fingerprint(current)
    assert not list(current.parent.glob(".*.stage.docx"))


def test_unchanged_report_does_not_create_history(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Report.docx"
    current.write_bytes(b"same")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()

    result = gateway.publish_update(
        current_path=current,
        expected_current_sha256=gateway.fingerprint(current),
        history_root=history,
        update_document=lambda source, output: _write_update(
            source,
            output,
            source.read_bytes(),
        ),
    )

    assert result.changed is False
    assert result.archive_path is None
    assert current.read_bytes() == b"same"
    assert not history.exists()


def test_writer_failure_keeps_current_report_and_leaves_no_history(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Report.docx"
    current.write_bytes(b"reviewed")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()

    with pytest.raises(RuntimeError, match="Word update failed"):
        gateway.publish_update(
            current_path=current,
            expected_current_sha256=gateway.fingerprint(current),
            history_root=history,
            update_document=_failing_update,
        )

    assert current.read_bytes() == b"reviewed"
    assert not history.exists()
    assert not list(tmp_path.glob(".*.stage.docx"))


def test_stale_current_report_is_rejected_before_update(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Report.docx"
    current.write_bytes(b"previewed")
    gateway = ReportPublicationGateway()
    expected = gateway.fingerprint(current)
    current.write_bytes(b"edited-in-word")

    with pytest.raises(
        ReportPublicationConflictError,
        match="changed after preview",
    ):
        gateway.publish_update(
            current_path=current,
            expected_current_sha256=expected,
            history_root=tmp_path / "History" / "Report",
            update_document=lambda source, output: _write_update(
                source,
                output,
                b"new",
            ),
        )

    assert current.read_bytes() == b"edited-in-word"


def test_manual_edit_during_staging_wins_and_creates_no_history(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Report.docx"
    current.write_bytes(b"previewed")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()

    def stage_while_operator_edits(source: Path, output: Path) -> Path:
        output.write_bytes(b"automated-update")
        source.write_bytes(b"operator-edit")
        return output

    with pytest.raises(ReportPublicationConflictError, match="changed after preview"):
        gateway.publish_update(
            current_path=current,
            expected_current_sha256=gateway.fingerprint(current),
            history_root=history,
            update_document=stage_while_operator_edits,
        )

    assert current.read_bytes() == b"operator-edit"
    assert not history.exists()


def test_locked_publish_never_removes_the_current_report_and_leaves_no_history(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = tmp_path / "DL-001 Report.docx"
    current.write_bytes(b"reviewed")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()
    real_replace = os.replace
    current_existed_during_publish: list[bool] = []

    def fail_staged_replace(source, target):
        if ".stage.docx" in str(source):
            current_existed_during_publish.append(current.exists())
            raise PermissionError("opened in Word")
        return real_replace(source, target)

    monkeypatch.setattr(
        "backend.infrastructure.files.report_publication_gateway.os.replace",
        fail_staged_replace,
    )

    with pytest.raises(ReportPublicationConflictError, match="Close the current report"):
        gateway.publish_update(
            current_path=current,
            expected_current_sha256=gateway.fingerprint(current),
            history_root=history,
            update_document=lambda source, output: _write_update(
                source,
                output,
                b"updated",
            ),
        )

    assert current_existed_during_publish == [True]
    assert current.read_bytes() == b"reviewed"
    assert not history.exists()


def _write_update(source: Path, output: Path, content: bytes) -> Path:
    assert source != output
    output.write_bytes(content)
    return output


def _failing_update(source: Path, output: Path) -> Path:
    output.write_bytes(b"partial")
    raise RuntimeError("Word update failed")
