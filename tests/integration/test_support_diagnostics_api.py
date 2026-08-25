import io
import zipfile

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes_diagnostics import router


def test_support_diagnostics_exports_bundle_and_accepts_frontend_errors(
    tmp_path,
    monkeypatch,
    caplog,
) -> None:
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "connlab.log").write_text("backend failure\n", encoding="utf-8")
    monkeypatch.setenv("CONNLAB_LOGS_DIR", str(logs_dir))
    monkeypatch.setenv(
        "CONNLAB_RELEASE_MANIFEST_PATH", str(tmp_path / "missing-manifest.json")
    )
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    reported = client.post(
        "/api/support/frontend-errors",
        json={
            "kind": "unhandled_rejection",
            "message": "render failed\nwith detail",
            "stack": "at SettingsPage",
            "page_path": "/settings?secret=not-sent",
        },
    )
    exported = client.get("/api/support/diagnostics")

    assert reported.status_code == 204
    assert "render failed with detail" in caplog.text
    assert "not-sent" not in caplog.text
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/zip"
    assert "ConnLab_Diagnostics_" in exported.headers["content-disposition"]
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        assert "logs/connlab.log" in archive.namelist()


def test_request_diagnostics_log_route_without_query_or_body(caplog) -> None:
    from backend.api.main import app

    caplog.set_level("INFO", logger="connlab.api.requests")
    response = TestClient(app).get("/health?token=must-not-be-logged")

    assert response.status_code == 200
    assert response.headers["x-request-id"]
    assert "path=/health status=200" in caplog.text
    assert "must-not-be-logged" not in caplog.text
