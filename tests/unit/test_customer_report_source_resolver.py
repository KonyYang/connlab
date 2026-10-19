from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.current_report_update_service import CurrentReportArtifact
from backend.application.customer_report_source_resolver import (
    CustomerReportSourceResolver, DownloadedInternalReportUnavailable,
)


def artifact(status="ready", mode="managed_draft"):
    return CurrentReportArtifact(status, mode, "internal.docx", Path("internal.docx"), "a" * 64, None)


def resolver(current, downloaded, *, registered="DL-2026-09-002", confirmed="DL-2026-09-002"):
    calls = []
    def latest(dl):
        calls.append(dl)
        if isinstance(downloaded, Exception):
            raise downloaded
        return downloaded
    reader = CustomerReportSourceResolver(
        current_reports=SimpleNamespace(get_current_report=lambda project: current),
        basic_information=SimpleNamespace(get_latest_confirmed=lambda project:
            SimpleNamespace(values={"dl_number": confirmed}) if confirmed else None),
        workspaces=SimpleNamespace(get_by_project=lambda project:
            SimpleNamespace(dl_number=registered) if registered else None),
        downloaded_drafts=SimpleNamespace(latest=latest),
    )
    return reader, calls


@pytest.mark.parametrize("current", [artifact(mode="official"), artifact(status="ambiguous")])
def test_formal_source_and_ambiguity_are_not_bypassed(current):
    reader, calls = resolver(current, artifact())
    assert reader.get_current_report("P1") is current
    assert not calls


@pytest.mark.parametrize("status", ["missing", "ready"])
def test_download_is_preferred_over_missing_or_older_managed_source(status):
    downloaded = artifact()
    reader, calls = resolver(artifact(status=status), downloaded)
    assert reader.get_current_report("P1") is downloaded
    assert calls == ["DL-2026-09-002"]


def test_no_download_preserves_existing_managed_source():
    current = artifact()
    reader, calls = resolver(current, None, registered="")
    assert reader.get_current_report("P1") is current
    assert calls == ["DL-2026-09-002"]


@pytest.mark.parametrize("registered,confirmed", [("", ""), ("DL-2026-09-001", "DL-2026-09-002")])
def test_missing_or_conflicting_project_identity_does_not_scan(registered, confirmed):
    reader, calls = resolver(artifact(status="missing"), artifact(), registered=registered, confirmed=confirmed)
    assert reader.get_current_report("P1").status == "missing"
    assert not calls


def test_invalid_latest_draft_requires_manual_selection_not_an_older_managed_copy():
    reader, _ = resolver(artifact(), DownloadedInternalReportUnavailable("invalid latest"))
    assert reader.get_current_report("P1").status == "missing"
