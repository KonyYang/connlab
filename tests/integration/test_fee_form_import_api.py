from pathlib import Path
import runpy

from backend.api.main import app


def test_inspect_upload_reads_workbook_without_changing_project(tmp_path):
    fixture = runpy.run_path(str(Path(__file__).with_name("test_matrix_editor_session_api.py")))
    sample = runpy.run_path(str(Path(__file__).parents[1] / "unit" / "test_fee_form_import_gateway.py"))
    client, engine, _ = fixture["_client"](tmp_path)
    try:
        fixture["_seed_project"]("P1", tmp_path)
        before = client.get("/api/projects/P1").json()
        response = client.post("/api/projects/P1/fee-evaluation/import/inspect",
                               files={"file": ("fee.xlsx", sample["workbook_bytes"]())})
        assert response.status_code == 200, response.text
        assert response.json()["rows"][1]["values"]["discount"] == "10"
        assert client.get("/api/projects/P1").json() == before
        rejected = client.post("/api/projects/P1/fee-evaluation/import/inspect", files={"file": ("bad.xlsm", b"bad")})
        assert rejected.status_code == 422
        missing = client.post("/api/projects/MISSING/fee-evaluation/import/inspect", files={"file": ("fee.xlsx", b"bad")})
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
