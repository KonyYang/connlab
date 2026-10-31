"""Local picker -> separate encrypted siblings, without upload or source replacement."""
import os

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from backend.api import dependencies as deps
from backend.api import routes_tools_folder_encryption as route
from backend.api.routes_tools import router
from backend.application.tools_service import ToolsService

HEADERS = {"Origin": "http://127.0.0.1", "X-ConnLab-Local-Encryption": "1"}


class Protector:
    def encrypt_and_verify(self, *, source_path, output_path, password, office_kind):
        output_path.write_bytes(b"secured:" + source_path.read_bytes())
        if source_path.read_bytes() == b"broken":
            raise RuntimeError("Office failed")


@pytest.fixture
def local_lab(tmp_path):
    root = tmp_path / "Folder"
    (root / "子目录").mkdir(parents=True)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[deps.get_tools_service] = lambda: ToolsService(
        customer_report_writer=None, office_protector=Protector())
    app.dependency_overrides[route.get_local_encryption_picker] = lambda: lambda: root
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 12345)) as client:
        yield root, client, app


def test_local_folder_creates_siblings_without_overwriting_existing_files(local_lab):
    root, client, _ = local_lab
    originals = {"report.docx": b"Word", "子目录/DL-2026-10-030.xlsx": b"Excel",
        "no-number.xlsx": b"Excel", "broken.doc": b"broken", "~$lock.docx": b"lock",
        "readme.txt": b"note", "report_Secured.docx": b"older secured copy"}
    for name, content in originals.items():
        (root / name).write_bytes(content)
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 200, result.text
    value = result.json()
    assert value["summary"] == {"succeeded": 2, "failed": 2, "skipped": 3}
    assert (root / "report_Secured (1).docx").read_bytes() == b"secured:Word"
    assert (root / "子目录/DL-2026-10-030_Secured.xlsx").read_bytes() == b"secured:Excel"
    assert all((root / name).read_bytes() == content for name, content in originals.items())
    assert not any(path.name.startswith(".connlab") for path in root.rglob("*"))
    assert not list(root.rglob("*.zip"))
    assert "DL-YYYY-MM-NNN" in next(item["reason"] for item in value["entries"] if item["file"] == "no-number.xlsx")


def test_repeated_runs_skip_generated_copies_and_keep_both_prior_outputs(local_lab):
    root, client, _ = local_lab
    (root / "report.docx").write_bytes(b"Word")
    assert client.post("/api/tools/encrypt-local-folder", headers=HEADERS).json()["summary"]["succeeded"] == 1
    second = client.post("/api/tools/encrypt-local-folder", headers=HEADERS).json()
    assert second["summary"] == {"succeeded": 1, "failed": 0, "skipped": 1}
    assert sorted(path.name for path in root.glob("*.docx")) == ["report.docx", "report_Secured (1).docx", "report_Secured.docx"]


def test_cancel_and_untrusted_requests_never_touch_the_folder(local_lab):
    root, client, app = local_lab
    calls = []
    app.dependency_overrides[route.get_local_encryption_picker] = lambda: lambda: calls.append(True)
    for headers in ({}, {**HEADERS, "Origin": "https://other.test"}, {**HEADERS, "X-ConnLab-Local-Encryption": "0"}):
        assert client.post("/api/tools/encrypt-local-folder", headers=headers).status_code == 403
    assert not calls
    assert client.post("/api/tools/encrypt-local-folder", headers=HEADERS).json() == {"cancelled": True}
    assert len(calls) == 1 and list(root.glob("*.docx")) == []


def test_source_changes_during_encryption_are_not_published(local_lab):
    root, client, app = local_lab
    source = root / "report.docx"
    source.write_bytes(b"Word")

    class ChangingProtector(Protector):
        def encrypt_and_verify(self, **kwargs):
            super().encrypt_and_verify(**kwargs)
            source.write_bytes(b"changed by another application")

    app.dependency_overrides[deps.get_tools_service] = lambda: ToolsService(
        customer_report_writer=None, office_protector=ChangingProtector())
    assert client.post("/api/tools/encrypt-local-folder", headers=HEADERS).json()["summary"]["failed"] == 1
    assert not (root / "report_Secured.docx").exists()


def test_concurrent_existing_output_is_preserved(local_lab):
    root, client, app = local_lab
    (root / "report.docx").write_bytes(b"Word")

    class CompetingProtector(Protector):
        def encrypt_and_verify(self, **kwargs):
            super().encrypt_and_verify(**kwargs)
            (root / "report_Secured.docx").write_bytes(b"another operation")

    app.dependency_overrides[deps.get_tools_service] = lambda: ToolsService(
        customer_report_writer=None, office_protector=CompetingProtector())
    assert client.post("/api/tools/encrypt-local-folder", headers=HEADERS).json()["summary"]["succeeded"] == 1
    assert (root / "report_Secured.docx").read_bytes() == b"another operation"
    assert (root / "report_Secured (1).docx").read_bytes() == b"secured:Word"


def test_empty_folder_returns_zero_and_missing_directory_returns_clear_error(local_lab):
    root, client, app = local_lab
    value = client.post("/api/tools/encrypt-local-folder", headers=HEADERS).json()
    assert value["summary"] == {"succeeded": 0, "failed": 0, "skipped": 0}
    app.dependency_overrides[route.get_local_encryption_picker] = lambda: lambda: root / "missing"
    assert client.post("/api/tools/encrypt-local-folder", headers=HEADERS).status_code == 422


def test_existing_secured_copies_do_not_consume_the_source_file_limit(local_lab):
    root, client, _ = local_lab
    (root / "report.docx").write_bytes(b"Word")
    for number in range(501):
        (root / f"older{number}_Secured.docx").write_bytes(b"previous output")
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == {"succeeded": 1, "failed": 0, "skipped": 501}


@pytest.mark.skipif(os.name != "nt", reason="Windows directory junction boundary")
def test_linked_folders_are_skipped_and_outside_sources_stay_untouched(local_lab, tmp_path):
    import _winapi
    root, client, _ = local_lab
    outside = tmp_path / "Outside"
    outside.mkdir()
    (outside / "outside.docx").write_bytes(b"outside")
    _winapi.CreateJunction(str(outside), str(root / "linked"))
    (root / "report.docx").write_bytes(b"Word")
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == {"succeeded": 1, "failed": 0, "skipped": 1}
    assert list(outside.iterdir()) == [outside / "outside.docx"]


def test_too_many_new_sources_stop_before_any_file_is_written(local_lab):
    root, client, _ = local_lab
    for number in range(501):
        (root / f"report{number}.docx").write_bytes(b"original")
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 422
    assert not list(root.rglob("*_Secured*"))
