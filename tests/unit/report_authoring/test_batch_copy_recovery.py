"""Completed isolated copies can be recovered before their authoring revision is recorded."""
from hashlib import sha256
import shutil

import pytest

from backend.infrastructure.files.report_draft_workspace import ReportDraftWorkspace


def test_replaying_the_same_completed_copy_reuses_its_revision_and_bytes(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"isolated source")
    workspace = ReportDraftWorkspace(tmp_path / "copies")
    operation = "a" * 32
    first = workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None,
                             make_current=False, operation_id=operation, operation_sha256="b" * 64)
    def must_not_generate(*args):
        pytest.fail("Completed batch was generated a second time")
    second = ReportDraftWorkspace(tmp_path / "copies").update(
        "P1", "DL-2026-05-001", source, must_not_generate, lambda: None,
        make_current=False, operation_id=operation, operation_sha256="b" * 64)
    assert first.report_revision_id == second.report_revision_id == operation
    assert first.file_path.read_bytes() == b"isolated source"
    assert workspace.latest("P1", "DL-2026-05-001") is None


def test_completed_copy_does_not_recover_against_changed_inputs(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"initial")
    workspace = ReportDraftWorkspace(tmp_path / "copies")
    first = workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None,
                             make_current=False, operation_id="a" * 32, operation_sha256="b" * 64)
    source.write_bytes(b"changed")
    with pytest.raises(ValueError, match="input|source"):
        workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None,
                         make_current=False, operation_id="a" * 32, operation_sha256="b" * 64)
    assert first.file_path.read_bytes() == b"initial"


def test_incomplete_copy_is_preserved_not_overwritten_or_claimed_complete(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"isolated")
    root = tmp_path / "copies"
    folder = root / sha256(b"P1").hexdigest() / ("a" * 32)
    folder.mkdir(parents=True)
    partial = folder / "partial.docx"
    partial.write_bytes(b"interrupted")
    with pytest.raises(ValueError, match="incomplete|interrupted"):
        ReportDraftWorkspace(root).update("P1", "DL-2026-05-001", source,
            shutil.copy2, lambda: None, make_current=False, operation_id="a" * 32, operation_sha256="b" * 64)
    assert partial.read_bytes() == b"interrupted"


def test_completed_batch_recovers_after_download_expiry_without_generating_again(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"completed before database registration")
    now = [0]
    workspace = ReportDraftWorkspace(tmp_path / "copies", clock=lambda: now[0])
    operation = "a" * 32
    first = workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None,
        matrix_id="M1", make_current=False, operation_id=operation, operation_sha256="b" * 64)
    now[0] = 25 * 60 * 60
    with pytest.raises(ValueError, match="expired"):
        workspace.read_revision("P1", operation)

    def must_not_generate(*args):
        pytest.fail("The completed batch must survive a cross-day database registration retry")

    reopened = ReportDraftWorkspace(tmp_path / "copies", clock=lambda: now[0])
    recovered = reopened.update("P1", "DL-2026-05-001", source, must_not_generate, lambda: None,
        matrix_id="M1", make_current=False, operation_id=operation, operation_sha256="b" * 64)
    assert recovered.report_revision_id == first.report_revision_id
    assert recovered.file_path.read_bytes() == b"completed before database registration"
    assert reopened.latest("P1", "DL-2026-05-001") is None


def test_normal_cache_pruning_preserves_unregistered_batch_but_expires_ordinary_drafts(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"isolated source")
    now = [0]
    workspace = ReportDraftWorkspace(tmp_path / "copies", clock=lambda: now[0])
    batch = workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None,
        make_current=False, operation_id="a" * 32, operation_sha256="b" * 64)
    ordinary = workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None)
    now[0] = 25 * 60 * 60
    assert workspace.latest("P1", "DL-2026-05-001") is None
    with pytest.raises(ValueError, match="expired"):
        workspace.read_revision("P1", ordinary.report_revision_id)
    latest = workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None)
    assert not ordinary.folder_path.exists()
    assert batch.file_path.read_bytes() == b"isolated source"
    assert workspace.latest("P1", "DL-2026-05-001").report_revision_id == latest.report_revision_id


@pytest.mark.parametrize("changed", ["source", "output", "plan", "matrix"])
def test_cross_day_recovery_still_rejects_changed_identity_or_bytes(tmp_path, changed):
    source = tmp_path / "source.docx"
    source.write_bytes(b"isolated source")
    now = [0]
    workspace = ReportDraftWorkspace(tmp_path / "copies", clock=lambda: now[0])
    request = {"matrix_id": "M1", "make_current": False,
               "operation_id": "a" * 32, "operation_sha256": "b" * 64}
    completed = workspace.update("P1", "DL-2026-05-001", source, shutil.copy2, lambda: None, **request)
    now[0] = 25 * 60 * 60
    if changed == "source":
        source.write_bytes(b"changed source")
    elif changed == "output":
        completed.file_path.write_bytes(b"changed output")
    elif changed == "plan":
        request["operation_sha256"] = "c" * 64
    else:
        request["matrix_id"] = "M2"

    def must_not_generate(*args):
        pytest.fail("An uncertain completed batch must never be overwritten")

    with pytest.raises(ValueError, match="changed|different"):
        workspace.update("P1", "DL-2026-05-001", source, must_not_generate, lambda: None, **request)
    assert completed.file_path.read_bytes() == (b"changed output" if changed == "output" else b"isolated source")
