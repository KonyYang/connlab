import io
import json
import logging
import zipfile

import pytest

from backend.shared.operation_diagnostics import operation, stage, failure_details, diagnostic_message
from backend.application.support_diagnostic_bundle_service import SupportDiagnosticBundleService


def test_failure_correlates_stage_codes_and_safe_trace_in_export(caplog, tmp_path):
    caplog.set_level(logging.INFO, logger="connlab.operations")
    original = OSError(13, "password=secret123", r"C:\Users\Private\Project Secret\fee.xls")
    original.winerror = 5
    with pytest.raises(RuntimeError) as caught:
        with operation("fee_form_publication", operation_id="diagnostic-test"):
            with stage("archive_old_file", target=tmp_path / "private.xls"):
                try:
                    raise original
                except OSError as exc:
                    raise RuntimeError("Archive failed") from exc
    detail = failure_details(caught.value)
    assert detail["operation_id"] == "diagnostic-test"
    assert detail["stage"] == "archive_old_file"
    assert detail["exceptions"][1]["winerror"] == 5
    assert detail["exceptions"][1]["errno"] == 13
    assert "diagnostic-test" in diagnostic_message(caught.value)
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "connlab.log").write_text(caplog.text, encoding="utf-8")
    bundle = SupportDiagnosticBundleService(logs_dir=logs).build_bundle()
    with zipfile.ZipFile(io.BytesIO(bundle.content)) as archive:
        text = archive.read("logs/connlab.log").decode()
    assert "archive_old_file" in text and '"winerror": 5' in text
    assert "secret123" not in text and "Project Secret" not in text
    assert "test_operation_diagnostics.py" in text
    events = [json.loads(r.message) for r in caplog.records if r.name == "connlab.operations"]
    assert any(e["event"] == "stage_failed" and e["elapsed_ms"] >= 0 for e in events)


def test_operation_context_does_not_leak_after_failure(caplog):
    caplog.set_level(logging.INFO, logger="connlab.operations")
    with pytest.raises(ValueError):
        with operation("first", operation_id="first-id"):
            with stage("write"):
                raise ValueError("bad")
    with operation("second", operation_id="second-id"):
        with stage("read"):
            pass
    events = [json.loads(r.message) for r in caplog.records if r.name == "connlab.operations"]
    assert events[-1]["operation_id"] == "second-id"
    assert events[-1]["event"] == "operation_succeeded"


def test_database_error_does_not_record_bound_business_values():
    from sqlalchemy.exc import StatementError
    error = StatementError("insert failed", "INSERT secret_fee_table", {"fee": "private-price"}, ValueError("database unavailable"))
    with operation("register"):
        detail = failure_details(error)
    assert "private-price" not in str(detail) and "INSERT" not in str(detail)
    assert "database unavailable" in str(detail)


def test_translated_exception_retains_deepest_failure_stage():
    with pytest.raises(RuntimeError) as caught:
        with operation("folder_generation"):
            with stage("folder_workspace"):
                try:
                    with stage("move_existing_folder_to_backup"):
                        raise PermissionError("move denied")
                except PermissionError as exc:
                    raise RuntimeError("Cannot prepare workspace") from exc
    detail = failure_details(caught.value)
    assert detail["stage"] == "move_existing_folder_to_backup"
    assert [item["type"] for item in detail["exceptions"]] == ["RuntimeError", "PermissionError"]
