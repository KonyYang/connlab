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


def test_discovers_only_customer_reports_for_the_project(tmp_path: Path) -> None:
    official = tmp_path / "official"
    official.mkdir()
    expected = official / "DL-001-CR Product Qualification Testing Report_Rev_A.docx"
    expected.write_bytes(b"customer")
    legacy = official / "DL-001-CR Product Qualification Testing Report_Customer_Rev_A.docx"
    legacy.write_bytes(b"legacy-customer")
    (official / "DL-001 Product Qualification Testing Report_Rev_A.docx").write_bytes(
        b"internal"
    )
    (official / "DL-002-CR Product Qualification Testing Report_Rev_A.docx").write_bytes(
        b"other"
    )

    candidates = ReportPublicationGateway().discover_customer_reports(
        folder=official,
        dl_number="DL-001",
    )

    assert candidates == (expected, legacy)


def test_changed_report_is_archived_and_atomically_replaced(tmp_path: Path) -> None:
    current = (
        tmp_path
        / "official"
        / "DL-2026-08-007 Coolpower HD3.5mm Qualification Testing Report_Rev_A.docx"
    )
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
        history / "DL-2026-08-007 Report_Rev_A 20260830-143522.docx"
    )
    assert tuple(history.iterdir()) == (result.archive_path,)
    assert result.archive_path.read_bytes() == b"operator-maintained|old-llcr"
    assert result.current_sha256 == gateway.fingerprint(current)
    assert not list(current.parent.glob(".*.stage.docx"))


def test_customer_report_history_uses_compact_customer_identity_name(
    tmp_path: Path,
) -> None:
    current = (
        tmp_path
        / "official"
        / "DL-2026-08-007-CR Coolpower HD3.5mm Qualification Testing Report_Rev_A.docx"
    )
    current.parent.mkdir()
    current.write_bytes(b"old-customer")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway(
        clock=lambda: datetime(2026, 9, 1, 6, 26, 57)
    )

    result = gateway.publish_update(
        current_path=current,
        expected_current_sha256=gateway.fingerprint(current),
        history_root=history,
        update_document=lambda source, output: _write_update(
            source,
            output,
            b"new-customer",
        ),
    )

    assert result.archive_path == (
        history / "DL-2026-08-007-CR Report_Rev_A 20260901-062657.docx"
    )
    assert result.archive_path.read_bytes() == b"old-customer"


def test_report_history_keeps_both_updates_when_timestamp_collides(
    tmp_path: Path,
) -> None:
    current = tmp_path / "DL-2026-08-007 Product Report_Rev_A.docx"
    current.write_bytes(b"version-1")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway(
        clock=lambda: datetime(2026, 9, 1, 6, 26, 57)
    )

    first = gateway.publish_update(
        current_path=current,
        expected_current_sha256=gateway.fingerprint(current),
        history_root=history,
        update_document=lambda source, output: _write_update(
            source,
            output,
            b"version-2",
        ),
    )
    second = gateway.publish_update(
        current_path=current,
        expected_current_sha256=gateway.fingerprint(current),
        history_root=history,
        update_document=lambda source, output: _write_update(
            source,
            output,
            b"version-3",
        ),
    )

    assert first.archive_path == (
        history / "DL-2026-08-007 Report_Rev_A 20260901-062657.docx"
    )
    assert second.archive_path == (
        history / "DL-2026-08-007 Report_Rev_A 20260901-062657 (2).docx"
    )
    assert first.archive_path.read_bytes() == b"version-1"
    assert second.archive_path.read_bytes() == b"version-2"


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


@pytest.mark.parametrize("archive_unchanged", [False, True])
def test_writer_failure_keeps_current_report_and_leaves_no_history(tmp_path: Path, archive_unchanged: bool) -> None:
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
            archive_unchanged=archive_unchanged,
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


@pytest.mark.parametrize("archive_unchanged", [False, True])
def test_locked_publish_never_removes_the_current_report_and_leaves_no_history(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    archive_unchanged: bool,
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
                b"reviewed" if archive_unchanged else b"updated",
            ),
            archive_unchanged=archive_unchanged,
        )

    assert current_existed_during_publish == [True]
    assert current.read_bytes() == b"reviewed"
    assert not history.exists()


def test_identical_regeneration_still_rechecks_source_before_publication(tmp_path: Path) -> None:
    current = tmp_path / "DL-001-CR Report.docx"
    current.write_bytes(b"reviewed")
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()

    def stale_source() -> None:
        raise ReportPublicationConflictError("Internal Report changed")

    with pytest.raises(ReportPublicationConflictError, match="Internal Report changed"):
        gateway.publish_update(current_path=current, expected_current_sha256=gateway.fingerprint(current),
            history_root=history, update_document=lambda source, output: _write_update(source, output, b"reviewed"),
            pre_publish=stale_source, archive_unchanged=True)

    assert current.read_bytes() == b"reviewed"
    assert not history.exists()
    assert not list(tmp_path.glob(".*.stage.docx"))


def test_publishes_managed_draft_as_new_official_report_without_moving_source(
    tmp_path: Path,
) -> None:
    managed = tmp_path / "managed" / "DL-001 Product Report_Rev_A_Draft (9).docx"
    managed.parent.mkdir()
    managed.write_bytes(b"operator-maintained-draft")
    official = tmp_path / "official" / "DL-001 Product Report_Rev_A.docx"
    official.parent.mkdir()
    gateway = ReportPublicationGateway(id_factory=lambda: "publish-1")

    result = gateway.publish_new_current(
        source_path=managed,
        expected_source_sha256=gateway.fingerprint(managed),
        target_path=official,
    )

    assert result.current_path == official
    assert result.current_sha256 == gateway.fingerprint(official)
    assert official.read_bytes() == b"operator-maintained-draft"
    assert managed.read_bytes() == b"operator-maintained-draft"
    assert not list(official.parent.glob(".*.stage.docx"))


def test_publish_new_current_never_overwrites_an_existing_official_report(
    tmp_path: Path,
) -> None:
    managed = tmp_path / "managed.docx"
    managed.write_bytes(b"managed")
    official = tmp_path / "official.docx"
    official.write_bytes(b"reviewed-official")
    gateway = ReportPublicationGateway()

    with pytest.raises(ReportPublicationConflictError, match="already exists"):
        gateway.publish_new_current(
            source_path=managed,
            expected_source_sha256=gateway.fingerprint(managed),
            target_path=official,
        )

    assert official.read_bytes() == b"reviewed-official"
    assert managed.read_bytes() == b"managed"


def test_generated_publication_checks_source_before_and_after_generation(
    tmp_path: Path,
) -> None:
    source = tmp_path / "internal.docx"
    source.write_bytes(b"previewed-internal")
    target = tmp_path / "customer.docx"
    gateway = ReportPublicationGateway(id_factory=lambda: "customer-1")

    result = gateway.publish_generated_current(
        source_path=source,
        expected_source_sha256=gateway.fingerprint(source),
        target_path=target,
        generate_document=lambda source_path, output_path: _write_update(
            source_path,
            output_path,
            b"generated-customer",
        ),
    )

    assert result.current_path == target
    assert target.read_bytes() == b"generated-customer"
    assert source.read_bytes() == b"previewed-internal"
    assert not list(tmp_path.glob(".*.stage.docx"))


def test_generated_publication_aborts_when_source_changes_during_generation(
    tmp_path: Path,
) -> None:
    source = tmp_path / "internal.docx"
    source.write_bytes(b"previewed-internal")
    target = tmp_path / "customer.docx"
    gateway = ReportPublicationGateway(id_factory=lambda: "customer-1")
    expected = gateway.fingerprint(source)

    def edit_source_while_generating(source_path: Path, output_path: Path) -> Path:
        output_path.write_bytes(b"generated-customer")
        source_path.write_bytes(b"operator-edit")
        return output_path

    with pytest.raises(ReportPublicationConflictError, match="Internal Report changed"):
        gateway.publish_generated_current(
            source_path=source,
            expected_source_sha256=expected,
            target_path=target,
            generate_document=edit_source_while_generating,
        )

    assert not target.exists()
    assert source.read_bytes() == b"operator-edit"
    assert not list(tmp_path.glob(".*.stage.docx"))


def _write_update(source: Path, output: Path, content: bytes) -> Path:
    assert source != output
    output.write_bytes(content)
    return output


def _failing_update(source: Path, output: Path) -> Path:
    output.write_bytes(b"partial")
    raise RuntimeError("Word update failed")
def test_regeneration_archives_same_bytes_and_rolls_back_failed_metadata(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Old Report_Rev_A.docx"
    current.write_bytes(b"manual report")
    staged = tmp_path / "staged.docx"
    staged.write_bytes(b"manual report")
    target = tmp_path / "DL-001 New Report_Rev_A.docx"
    gateway = ReportPublicationGateway()
    history = tmp_path / "History" / "Report"

    def fail_metadata(result):
        assert result.archive_path.read_bytes() == b"manual report"
        raise RuntimeError("metadata commit failed")

    with pytest.raises(RuntimeError, match="metadata commit failed"):
        gateway.publish_regenerated_current(
            source_path=staged,
            expected_source_sha256=gateway.fingerprint(staged),
            current_path=current,
            expected_current_sha256=gateway.fingerprint(current),
            target_path=target,
            history_root=history,
            persist=fail_metadata,
        )
    assert current.read_bytes() == b"manual report"
    assert not target.exists()
    assert not history.exists()
    result = gateway.publish_regenerated_current(
        source_path=staged,
        expected_source_sha256=gateway.fingerprint(staged),
        current_path=current,
        expected_current_sha256=gateway.fingerprint(current),
        target_path=target,
        history_root=history,
        persist=lambda result: None,
    )
    assert result.changed is True
    assert result.archive_path.read_bytes() == b"manual report"
    assert not current.exists()
    assert target.read_bytes() == b"manual report"


@pytest.mark.parametrize("same_name", [False, True])
def test_failed_fresh_publication_restores_retired_report(tmp_path: Path, monkeypatch, same_name: bool) -> None:
    current = tmp_path / "DL-001 Old Report_Rev_A.docx"
    current.write_bytes(b"reviewed manual report")
    source = tmp_path / "staged.docx"
    source.write_bytes(b"fresh template report")
    target = current if same_name else tmp_path / "DL-001 New Report_Rev_A.docx"
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()

    def unavailable_link(staged, published):
        assert not current.exists()
        assert not published.exists()
        assert len(list(history.glob("*.docx"))) == 1
        raise PermissionError("publication unavailable")

    monkeypatch.setattr(os, "link", unavailable_link)
    with pytest.raises(ReportPublicationConflictError, match="Close the report"):
        gateway.publish_regenerated_current(source_path=source, expected_source_sha256=gateway.fingerprint(source),
            current_path=current, expected_current_sha256=gateway.fingerprint(current), target_path=target,
            history_root=history, persist=lambda result: pytest.fail("metadata cannot persist before publication"))
    assert current.read_bytes() == b"reviewed manual report"
    assert not history.exists()
    assert list(tmp_path.glob("DL-*.docx")) == [current]


def test_regeneration_commit_observes_exactly_one_active_report(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Old Report_Rev_A.docx"
    current.write_bytes(b"manual")
    source = tmp_path / "source.docx"
    source.write_bytes(b"fresh")
    target = tmp_path / "DL-001 New Report_Rev_A.docx"
    gateway = ReportPublicationGateway()

    def persist(result):
        assert list(tmp_path.glob("DL-*.docx")) == [target]
        assert target.read_bytes() == b"fresh"
        assert result.archive_path.read_bytes() == b"manual"

    gateway.publish_regenerated_current(source_path=source, expected_source_sha256=gateway.fingerprint(source),
        current_path=current, expected_current_sha256=gateway.fingerprint(current), target_path=target,
        history_root=tmp_path / "History" / "Report", persist=persist)


def test_failed_commit_preserves_a_foreign_same_byte_replacement_and_old_archive(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Old Report_Rev_A.docx"
    current.write_bytes(b"manual")
    source = tmp_path / "source.docx"
    source.write_bytes(b"fresh")
    target = tmp_path / "DL-001 New Report_Rev_A.docx"
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()

    def racing_commit(result):
        replacement = tmp_path / "foreign.tmp"
        replacement.write_bytes(b"fresh")
        os.replace(replacement, target)
        raise RuntimeError("metadata commit failed")

    with pytest.raises(ReportPublicationConflictError, match="retained in History"):
        gateway.publish_regenerated_current(source_path=source, expected_source_sha256=gateway.fingerprint(source),
            current_path=current, expected_current_sha256=gateway.fingerprint(current), target_path=target,
            history_root=history, persist=racing_commit)
    assert target.read_bytes() == b"fresh"
    assert [archive.read_bytes() for archive in history.glob("*.docx")] == [b"manual"]


def test_failed_commit_preserves_externally_edited_recovery_archive(tmp_path: Path) -> None:
    current = tmp_path / "DL-001 Old Report_Rev_A.docx"
    current.write_bytes(b"manual")
    source = tmp_path / "source.docx"
    source.write_bytes(b"fresh")
    target = tmp_path / "DL-001 New Report_Rev_A.docx"
    history = tmp_path / "History" / "Report"
    gateway = ReportPublicationGateway()

    def racing_commit(result):
        result.archive_path.write_bytes(b"external archive edit")
        raise RuntimeError("metadata commit failed")

    with pytest.raises(ReportPublicationConflictError, match="recovery archive changed"):
        gateway.publish_regenerated_current(source_path=source, expected_source_sha256=gateway.fingerprint(source),
            current_path=current, expected_current_sha256=gateway.fingerprint(current), target_path=target,
            history_root=history, persist=racing_commit)
    assert not target.exists()
    assert not current.exists()
    assert [archive.read_bytes() for archive in history.glob("*.docx")] == [b"external archive edit"]
