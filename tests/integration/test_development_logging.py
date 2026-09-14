"""Development bootstrap writes the same logs the support endpoint exports."""
import io
import logging
import os
from pathlib import Path
import zipfile

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("relative", [False, True])
def test_development_logs_capture_success_failure_and_export(tmp_path, monkeypatch, relative):
    from backend.api.development import create_app
    from backend.shared.operation_diagnostics import operation, stage

    monkeypatch.chdir(tmp_path)
    log_dir = tmp_path / "isolated-logs"
    monkeypatch.setenv("CONNLAB_LOGS_DIR", "isolated-logs" if relative else str(log_dir))
    monkeypatch.setenv("CONNLAB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CONNLAB_LOG_LEVEL", "INFO")
    root = logging.getLogger()
    original_handlers, original_level = list(root.handlers), root.level
    try:
        app = create_app()
        assert create_app() is app
        with operation("development_log_check", operation_id="dev-log-success"):
            with stage("isolated_success"):
                pass
        with pytest.raises(ValueError):
            with operation("development_log_check", operation_id="dev-log-failure"):
                with stage("isolated_failure"):
                    raise ValueError("isolated failure token=DO_NOT_EXPORT")
        assert Path(os.environ["CONNLAB_LOGS_DIR"]) == log_dir
        text = (log_dir / "connlab.log").read_text(encoding="utf-8")
        assert text.count('"event": "operation_succeeded"') == 1
        assert '"event": "stage_failed"' in text
        assert "dev-log-failure" in text
        assert "DO_NOT_EXPORT" not in text
        response = TestClient(app).get("/api/support/diagnostics")
        assert response.status_code == 200
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            exported = archive.read("logs/connlab.log").decode("utf-8")
        assert "dev-log-success" in exported and "dev-log-failure" in exported
        assert "DO_NOT_EXPORT" not in exported
    finally:
        for handler in list(root.handlers):
            if handler not in original_handlers:
                root.removeHandler(handler)
                handler.close()
        root.setLevel(original_level)
