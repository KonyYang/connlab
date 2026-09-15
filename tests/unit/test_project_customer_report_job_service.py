from pathlib import Path

import pytest

from backend.application.customer_report_projection_service import CustomerReportGenerationResult
from backend.application.project_customer_report_job_service import (
    ProjectCustomerReportJobService, ProjectCustomerReportJobExpired,
)


def test_project_job_recovers_progress_prevents_duplicates_and_retains_download(tmp_path):
    pending = []
    now = [0.0]
    def generate(project_id, source, customer, root, progress):
        progress("formatting_document")
        assert service.latest(project_id)["stage"] == "formatting_document"
        output = root / "customer.docx"
        output.write_bytes(b"report")
        return CustomerReportGenerationResult(project_id, "managed_download", output.name, output, "a"*64, source, True, None)
    service = ProjectCustomerReportJobService(root=tmp_path, generate=generate, dispatch=pending.append, clock=lambda: now[0], retention_seconds=60)
    job = service.start("p", "a"*64, None)
    assert service.start("p", "a"*64, None)["operation_id"] == job["operation_id"]
    assert len(pending) == 1
    pending.pop()()
    assert service.latest("p")["status"] == "completed"
    with service.download("p", job["operation_id"]) as path:
        assert path.read_bytes() == b"report"
        now[0] = 61
        service.prune()
        assert path.exists()
    service.prune()
    with pytest.raises(ProjectCustomerReportJobExpired):
        service.read("p", job["operation_id"])
    assert list(tmp_path.iterdir()) == []


def test_failed_job_preserves_recovery_code_and_allows_retry(tmp_path):
    from backend.application.customer_report_projection_service import CustomerReportMissingAfterPreviewError
    def generate(*args):
        raise CustomerReportMissingAfterPreviewError("Customer was moved")
    service = ProjectCustomerReportJobService(root=tmp_path, generate=generate, dispatch=lambda action: action())
    first = service.start("p", "a"*64, "b"*64)
    assert first["status"] == "failed"
    assert first["can_regenerate"] is True
    assert first["error_code"] == "customer_report_missing_after_preview"
    assert service.start("p", "a"*64, None)["operation_id"] != first["operation_id"]


def test_publication_failure_is_distinct_and_cleanup_failure_is_retriable(tmp_path, monkeypatch):
    def generate(project, source, customer, root, progress):
        progress("publishing")
        raise PermissionError("Report is open in Word")
    service = ProjectCustomerReportJobService(root=tmp_path, generate=generate, dispatch=lambda action: action())
    import shutil
    remove = shutil.rmtree
    monkeypatch.setattr(shutil, "rmtree", lambda path: (_ for _ in ()).throw(PermissionError("locked temp file")))
    failed = service.start("p", "a"*64, None)
    assert failed["error_code"] == "customer_report_publication_failed"
    assert failed["message"] == "Report is open in Word"
    assert service.read("p", failed["operation_id"])["status"] == "failed"
    monkeypatch.setattr(shutil, "rmtree", remove)


def test_restart_cleanup_removes_only_expired_owned_files_of_dead_process(tmp_path, monkeypatch):
    import json
    import time
    abandoned = tmp_path / ("a"*32)
    abandoned.mkdir()
    (abandoned / ".connlab-report-job.json").write_text(json.dumps({"owner": "connlab-project-customer-report", "operation_id": abandoned.name, "pid": 999999, "created": time.time()-3700}), encoding="utf-8")
    foreign = tmp_path / "other"
    foreign.mkdir()
    monkeypatch.setattr("backend.application.project_customer_report_job_service._process_alive", lambda pid: False)
    service = ProjectCustomerReportJobService(root=tmp_path, generate=None, dispatch=None)
    assert service.latest("p") is None
    assert not abandoned.exists()
    assert foreign.exists()


def test_shutdown_is_idempotent_and_rejects_new_jobs(tmp_path):
    closed = []
    service = ProjectCustomerReportJobService(root=tmp_path, generate=None, dispatch=None, shutdown=lambda: closed.append(True))
    service.close()
    service.close()
    assert closed == [True]
    with pytest.raises(ValueError, match="shutting down"):
        service.start("p", "a"*64, None)


def test_shutdown_retires_cancelled_queue_and_its_temporary_artifacts(tmp_path):
    pending = []
    service = ProjectCustomerReportJobService(root=tmp_path, generate=None, dispatch=pending.append)
    job = service.start("p", "a"*64, None)
    service.close()
    assert service.read("p", job["operation_id"])["status"] == "failed"
    assert list(tmp_path.iterdir()) == []
