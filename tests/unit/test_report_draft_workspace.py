from hashlib import sha256

import pytest
import json

from backend.infrastructure.files.report_draft_workspace import ReportDraftWorkspace


def test_successful_copies_chain_and_each_download_is_immutable(tmp_path):
    original = tmp_path / "DL-001 Test Report_Draft (1).docx"
    original.write_bytes(b"manual")
    workspace = ReportDraftWorkspace(tmp_path / "working")
    def llcr(source, output):
        output.write_bytes(source.read_bytes() + b"|LLCR")
    first = workspace.update("P1", "DL-001", original, llcr, lambda: None)
    assert first.file_path.read_bytes() == b"manual|LLCR"
    def equipment(source, output):
        output.write_bytes(source.read_bytes() + b"|equipment")
    second = workspace.update("P1", "DL-001", first.file_path, equipment, lambda: None)
    assert workspace.latest("P1", "DL-001").file_path.read_bytes() == b"manual|LLCR|equipment"
    assert workspace.read_revision("P1", first.report_revision_id).file_path.read_bytes() == b"manual|LLCR"
    assert second.file_name == "DL-001 Test Report_Draft.docx"
    assert original.read_bytes() == b"manual"
    assert workspace.latest("P2", "DL-001") is None
    assert workspace.latest("P1", "DL-002") is None


def test_failed_update_retains_last_successful_draft(tmp_path):
    original = tmp_path / "DL-001 Report_Draft.docx"
    original.write_bytes(b"manual")
    workspace = ReportDraftWorkspace(tmp_path / "working")
    def write(source, output):
        output.write_bytes(source.read_bytes() + b"|updated")
    good = workspace.update("P1", "DL-001", original, write, lambda: None)
    def changed():
        raise ValueError("Source changed")
    with pytest.raises(ValueError, match="Source changed"):
        workspace.update("P1", "DL-001", good.file_path, write, changed)
    assert workspace.latest("P1", "DL-001").file_sha256 == sha256(b"manual|updated").hexdigest()
    assert len(list((tmp_path / "working").rglob("*.docx"))) == 1


def test_expired_working_copies_stop_shadowing_downloads_and_only_owned_cache_is_pruned(tmp_path):
    now = [100]
    original = tmp_path / "DL-001 Report_Draft.docx"
    original.write_bytes(b"original")
    workspace = ReportDraftWorkspace(tmp_path / "working", clock=lambda: now[0], retention_seconds=10)
    first = workspace.update("P1", "DL-001", original, lambda src, dst: dst.write_bytes(b"updated"), lambda: None)
    now[0] = 111
    assert workspace.latest("P1", "DL-001") is None
    with pytest.raises(ValueError, match="expired"):
        workspace.read_revision("P1", first.report_revision_id)
    workspace.update("P1", "DL-001", original, lambda src, dst: dst.write_bytes(b"new"), lambda: None)
    assert not first.file_path.exists()
    assert original.read_bytes() == b"original"


def test_malformed_metadata_has_an_actionable_error_and_never_selects_another_path(tmp_path):
    original = tmp_path / "DL-001 Report_Draft.docx"
    original.write_bytes(b"source")
    workspace = ReportDraftWorkspace(tmp_path / "working")
    current = workspace.update("P1", "DL-001", original, lambda src, dst: dst.write_bytes(b"copy"), lambda: None)
    (current.file_path.parent / "revision.json").write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(ValueError):
        workspace.latest("P1", "DL-001")
    assert original.read_bytes() == b"source"
