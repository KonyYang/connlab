"""Exercise folder upload/download with real policy and a fake external Office boundary."""
from io import BytesIO
import csv
import json
from zipfile import ZipFile

from fastapi.testclient import TestClient
import pytest

from backend.api import dependencies as deps
from backend.api.main import app
from backend.application.tools_service import ToolsService
from backend.shared.config import Settings


class Protector:
    def __init__(self):
        self.calls = []

    def encrypt_and_verify(self, *, source_path, output_path, password, office_kind):
        self.calls.append((source_path.name, password, office_kind))
        output_path.write_bytes(b"secured:" + source_path.read_bytes())
        if source_path.read_bytes() == b"broken":
            raise RuntimeError("Office could not read this file")


@pytest.fixture
def folder_lab(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    settings = Settings(data_dir=data, projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates", database_path=tmp_path / "unused.sqlite")
    protector = Protector()
    service = ToolsService(customer_report_writer=None, office_protector=protector)
    app.dependency_overrides[deps.get_settings] = lambda: settings
    app.dependency_overrides[deps.get_tools_service] = lambda: service
    try:
        yield TestClient(app), data, protector
    finally:
        app.dependency_overrides.pop(deps.get_settings, None)
        app.dependency_overrides.pop(deps.get_tools_service, None)


def upload(client, paths, contents=None):
    contents = contents or [b"original"] * len(paths)
    return client.post("/api/tools/encrypt-folder", data={"relative_paths": json.dumps(paths)},
        files=[("files", (path.replace("\\", "/").split("/")[-1], content, "application/octet-stream"))
               for path, content in zip(paths, contents)])


def test_folder_download_preserves_paths_rules_and_only_contains_verified_copies(folder_lab):
    client, data, protector = folder_lab
    paths = ["项目/report.docx", "项目/子目录/DL-2026-04-038A result.xlsx",
             "项目/measurements.xlsx", "项目/broken.doc", "项目/readme.txt", "项目/~$locked.docx"]
    response = upload(client, paths, [b"Word", b"Excel", b"unnumbered", b"broken", b"text", b"lock"])
    assert response.status_code == 200, response.text
    assert "zip" in response.headers["content-disposition"]
    assert json.loads(response.headers["x-encryption-summary"]) == {"succeeded": 2, "failed": 2, "skipped": 2}
    with ZipFile(BytesIO(response.content)) as bundle:
        assert set(bundle.namelist()) == {"项目/report_Secured.docx", "项目/子目录/DL-2026-04-038A result_Secured.xlsx",
                                          "EncryptionSummary.csv"}
        assert bundle.read("项目/report_Secured.docx") == b"secured:Word"
        rows = list(csv.DictReader(bundle.read("EncryptionSummary.csv").decode("utf-8-sig").splitlines()))
        assert {row["Status"] for row in rows} == {"Encrypted", "Failed", "Skipped"}
        assert "DL-YYYY-MM-NNN" in next(row["Reason"] for row in rows if row["File"] == "项目/measurements.xlsx")
        assert all("password" not in row["Reason"].lower() for row in rows)
    assert ("DL-2026-04-038A result.xlsx", "202604038A", "excel") in protector.calls
    assert list(data.iterdir()) == []


@pytest.mark.parametrize("paths", [
    ["../report.docx"], ["/Folder/report.docx"], ["C:/Folder/report.docx"],
    ["Folder/../report.docx"], ["Folder/CON.docx"], ["Folder/part./report.docx"],
    ["Folder\\report.docx"], ["Folder/a.docx", "Other/b.docx"],
    ["Folder/a.docx", "Folder/A.docx"], ["Folder/é.docx", "Folder/e\u0301.docx"],
    ["Folder/a.docx", "Folder/a_Secured.docx/b.docx"],
])
def test_unsafe_or_colliding_folder_paths_are_rejected_before_office_and_staging(folder_lab, paths):
    client, data, protector = folder_lab
    result = upload(client, paths)
    assert result.status_code == 422, result.text
    assert not protector.calls
    assert list(data.iterdir()) == []


def test_all_failed_files_produce_an_explicit_report_without_plaintext(folder_lab):
    client, data, _ = folder_lab
    response = upload(client, ["Folder/unnumbered.xlsx"])
    assert response.status_code == 200
    assert json.loads(response.headers["x-encryption-summary"])["succeeded"] == 0
    with ZipFile(BytesIO(response.content)) as bundle:
        assert bundle.namelist() == ["EncryptionSummary.csv"]
        assert "Failed" in bundle.read("EncryptionSummary.csv").decode("utf-8-sig")
    assert list(data.iterdir()) == []


def test_folder_size_limit_rejects_before_encryption_and_cleans_staging(folder_lab, monkeypatch):
    from backend.api import routes_tools_folder_encryption as route
    monkeypatch.setattr(route, "MAX_FILE_BYTES", 4)
    client, data, protector = folder_lab
    result = upload(client, ["Folder/report.docx"], [b"12345"])
    assert result.status_code == 413
    assert not protector.calls
    assert list(data.iterdir()) == []


def test_count_and_metadata_validation_do_not_start_office(folder_lab):
    client, data, protector = folder_lab
    assert upload(client, [f"Folder/{index}.docx" for index in range(501)]).status_code == 422
    result = client.post("/api/tools/encrypt-folder", data={"relative_paths": "not JSON"},
                         files={"files": ("report.docx", b"original")})
    assert result.status_code == 422
    assert not protector.calls and list(data.iterdir()) == []


@pytest.mark.parametrize("folder", ["=Folder", "+Folder", " @Folder"])
def test_csv_names_cannot_execute_spreadsheet_formulas(folder_lab, folder):
    client, _, _ = folder_lab
    result = upload(client, [folder + "/a.docx"])
    assert result.status_code == 200
    with ZipFile(BytesIO(result.content)) as bundle:
        rows = list(csv.DictReader(bundle.read("EncryptionSummary.csv").decode("utf-8-sig").splitlines()))
        assert rows[0]["File"] == "'" + folder + "/a.docx"


def test_total_upload_limit_is_checked_before_any_office_calls(folder_lab, monkeypatch):
    from backend.api import routes_tools_folder_encryption as route
    monkeypatch.setattr(route, "MAX_TOTAL_BYTES", 6)
    client, data, protector = folder_lab
    result = upload(client, ["Folder/a.docx", "Folder/b.docx"], [b"1234", b"1234"])
    assert result.status_code == 413
    assert not protector.calls and list(data.iterdir()) == []
