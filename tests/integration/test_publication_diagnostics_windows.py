"""Real Windows sharing violation, not a mocked permission exception."""
import os
import pytest

from backend.infrastructure.files.test_record_publication_gateway import TestRecordPublicationGateway as PublicationGateway
from backend.shared.operation_diagnostics import operation, failure_details


@pytest.mark.skipif(os.name != "nt", reason="Windows handle semantics")
def test_archive_sharing_violation_reports_original_code_and_keeps_file(tmp_path):
    import win32con
    import win32file
    target = tmp_path / "fee.xls"
    target.write_bytes(b"original")
    staged = tmp_path / "new.xls"
    staged.write_bytes(b"new")
    gateway = PublicationGateway(resource_label="Fee Form")
    handle = win32file.CreateFile(str(target), win32con.GENERIC_READ,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE, None, win32con.OPEN_EXISTING, 0, None)
    try:
        with pytest.raises(PermissionError) as caught:
            with operation("fee_form_publication", operation_id="windows-lock"):
                gateway.publish(staged_path=staged, target_path=target, conflict_action="archive",
                    history_dir=tmp_path / "history", expected_target_fingerprint=gateway.fingerprint(target))
        detail = failure_details(caught.value)
        assert detail["stage"] == "archive_old_file"
        assert detail["exceptions"][0]["winerror"] == 32
        assert target.read_bytes() == b"original"
    finally:
        win32file.CloseHandle(handle)
