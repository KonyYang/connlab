"""Local picker -> separate encrypted siblings, without upload or source replacement."""
import os
from pathlib import Path

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
    originals = {"report.docx": b"Word", "DL-2026-10-030.xlsx": b"Excel",
        "no-number.xlsx": b"Excel", "broken.doc": b"broken", "~$lock.docx": b"lock",
        "readme.txt": b"note", "report_Secured.docx": b"older secured copy"}
    for name, content in originals.items():
        (root / name).write_bytes(content)
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 200, result.text
    value = result.json()
    assert value["summary"] == {"succeeded": 2, "failed": 1, "skipped": 4}
    assert (root / "report_Secured (1).docx").read_bytes() == b"secured:Word"
    assert (root / "DL-2026-10-030_Secured.xlsx").read_bytes() == b"secured:Excel"
    assert all((root / name).read_bytes() == content for name, content in originals.items())
    assert not any(path.name.startswith(".connlab") for path in root.rglob("*"))
    assert not list(root.rglob("*.zip"))
    assert "DL-YYYY-MM-NNN" in next(item["reason"] for item in value["entries"] if item["file"] == "no-number.xlsx")


@pytest.mark.parametrize("suffix", [".xls", ".xlsx"])
def test_folder_skips_ineligible_excel_without_attempting_a_copy(local_lab, monkeypatch, suffix):
    from backend.infrastructure.files.tools_local_folder_gateway import ToolsLocalFolderGateway
    root, client, _ = local_lab
    names = [f"measurements{suffix}", f"notes DL-2026-10-030{suffix}",
             f"DL-2026-10-0300{suffix}", f"DL-2026-13-030{suffix}"]
    for name in names:
        (root / name).write_bytes(b"original")
    attempted = []
    def unexpected_copy(*args, **kwargs):
        attempted.append(args)
        raise RuntimeError("Ineligible Excel files must not be staged or encrypted")
    monkeypatch.setattr(ToolsLocalFolderGateway, "create_copy", unexpected_copy)
    response = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert response.status_code == 200, response.text
    assert attempted == []
    assert response.json()["summary"] == {"succeeded": 0, "failed": 0, "skipped": len(names)}
    assert all(entry["status"] == "Skipped" for entry in response.json()["entries"])
    assert all((root / name).read_bytes() == b"original" for name in names)
    assert not list(root.glob("*_Secured*"))


@pytest.mark.parametrize("name", ["DL-2026-10-030.xls", "DL-2026-10-030A results.xlsx", "broken.docx", "broken.pptx"])
def test_folder_counts_failed_operations_for_eligible_office_files(local_lab, name):
    root, client, _ = local_lab
    source = root / name
    source.write_bytes(b"broken")
    response = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert response.status_code == 200, response.text
    assert response.json()["summary"] == {"succeeded": 0, "failed": 1, "skipped": 0}
    assert response.json()["entries"][0]["status"] == "Failed"
    assert source.read_bytes() == b"broken"
    assert not list(root.glob("*_Secured*"))


@pytest.mark.parametrize("has_direct_file", [False, True])
def test_folder_never_inspects_or_processes_subfolders(local_lab, monkeypatch, has_direct_file):
    root, client, _ = local_lab
    nested = root / "子目录"
    for number in range(501):
        (nested / f"report{number}.docx").write_bytes(b"child original")
    if has_direct_file:
        (root / "direct.pptx").write_bytes(b"direct original")
    scan = os.scandir
    def guarded_scan(path):
        if isinstance(path, (str, bytes, os.PathLike)):
            directory = Path(os.fsdecode(path)).resolve()
            assert not directory.is_relative_to(nested.resolve()), "Subfolders must not even be inspected"
        return scan(path)
    monkeypatch.setattr(os, "scandir", guarded_scan)
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    monkeypatch.setattr(os, "scandir", scan)
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == {"succeeded": int(has_direct_file), "failed": 0, "skipped": 0}
    assert [entry["file"] for entry in result.json()["entries"]] == (["direct.pptx"] if has_direct_file else [])
    assert not list(nested.glob("*_Secured*"))
    assert all(path.read_bytes() == b"child original" for path in nested.glob("*.docx"))


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


def test_office_can_modify_its_working_input_without_touching_originals(local_lab):
    root, client, app = local_lab
    original = root / "DL-2026-10-030.xls"
    original.write_bytes(b"original workbook")

    class SavingProtector(Protector):
        def encrypt_and_verify(self, **kwargs):
            super().encrypt_and_verify(**kwargs)
            kwargs["source_path"].write_bytes(b"Office changed working metadata")

    app.dependency_overrides[deps.get_tools_service] = lambda: ToolsService(
        customer_report_writer=None, office_protector=SavingProtector())
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.json()["summary"]["succeeded"] == 1
    assert original.read_bytes() == b"original workbook"
    assert (root / "DL-2026-10-030_Secured.xls").read_bytes() == b"secured:original workbook"


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


def test_ineligible_excel_files_do_not_consume_the_source_file_limit(local_lab):
    root, client, _ = local_lab
    (root / "report.docx").write_bytes(b"Word")
    for number in range(501):
        (root / f"measurements{number}.xlsx").write_bytes(b"Excel")
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == {"succeeded": 1, "failed": 0, "skipped": 501}


@pytest.mark.skipif(os.name != "nt", reason="Windows directory junction boundary")
def test_linked_folders_are_ignored_and_outside_sources_stay_untouched(local_lab, tmp_path):
    import _winapi
    root, client, _ = local_lab
    outside = tmp_path / "Outside"
    outside.mkdir()
    (outside / "outside.docx").write_bytes(b"outside")
    _winapi.CreateJunction(str(outside), str(root / "linked"))
    (root / "report.docx").write_bytes(b"Word")
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == {"succeeded": 1, "failed": 0, "skipped": 0}
    assert list(outside.iterdir()) == [outside / "outside.docx"]


def test_too_many_new_sources_stop_before_any_file_is_written(local_lab):
    root, client, _ = local_lab
    for number in range(501):
        (root / f"report{number}.docx").write_bytes(b"original")
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 422
    assert not list(root.rglob("*_Secured*"))


@pytest.mark.skipif(os.name != "nt", reason="Windows native picker boundary")
@pytest.mark.parametrize("cancelled", [False, True])
def test_native_encryption_picker_returns_unicode_paths_and_releases_com(monkeypatch, tmp_path, cancelled):
    import pythoncom
    from win32com.shell import shell
    from backend.infrastructure.files.windows_path_picker import WindowsPathPicker, filedialog
    selected = tmp_path / "项目"
    released = []
    monkeypatch.setattr(pythoncom, "CoInitialize", lambda: None)
    monkeypatch.setattr(pythoncom, "CoUninitialize", lambda: released.append(True))
    monkeypatch.setattr(shell, "SHBrowseForFolder", lambda *args: (None if cancelled else b"selected", "name", 0))
    monkeypatch.setattr(shell, "SHGetPathFromIDListW", lambda value: str(selected))
    monkeypatch.setattr(filedialog, "askdirectory", lambda **kwargs: (_ for _ in ()).throw(RuntimeError("Tk owner not expected")))
    assert WindowsPathPicker().pick_encryption_directory() == (None if cancelled else selected)
    assert released == [True]


def test_folder_supports_powerpoint_without_ltr_and_skips_secured_presentations(local_lab):
    root, client, _ = local_lab
    originals = {"slides.pptx": b"slides", "legacy.PPT": b"legacy", "slides_Secured.pptx": b"prior"}
    for name, content in originals.items():
        (root / name).write_bytes(content)
    result = client.post("/api/tools/encrypt-local-folder", headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == {"succeeded": 2, "failed": 0, "skipped": 1}
    assert (root / "slides_Secured (1).pptx").read_bytes() == b"secured:slides"
    assert (root / "legacy_Secured.PPT").read_bytes() == b"secured:legacy"
    assert all((root / name).read_bytes() == content for name, content in originals.items())


@pytest.mark.parametrize("suffix", [".ppt", ".pptx"])
def test_single_file_powerpoint_download_preserves_extension(local_lab, suffix):
    _, client, _ = local_lab
    result = client.post("/api/tools/encrypt-copy", files={"file": (f"slides{suffix}", b"original slides")})
    assert result.status_code == 200, result.text
    assert f"slides_Secured{suffix}" in result.headers["content-disposition"]
    assert result.content == b"secured:original slides"


@pytest.mark.parametrize("name", ["report.doc", "report.docx", "DL-2026-10-030.xls", "DL-2026-10-030.xlsx", "slides.ppt", "slides.pptx"])
def test_native_single_file_saves_beside_only_the_selected_original(local_lab, name):
    root, client, app = local_lab
    source = root / name
    source.write_bytes(b"selected original")
    (root / "unselected.docx").write_bytes(b"must not be processed")
    target = source.with_name(f"{source.stem}_Secured{source.suffix}")
    target.write_bytes(b"prior copy")
    app.dependency_overrides[route.get_local_file_encryption_picker] = lambda: lambda: source
    result = client.post("/api/tools/encrypt-local-file", headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.json()["summary"] == {"succeeded": 1, "failed": 0, "skipped": 0}
    assert source.read_bytes() == b"selected original" and target.read_bytes() == b"prior copy"
    assert source.with_name(f"{source.stem}_Secured (1){source.suffix}").read_bytes() == b"secured:selected original"
    assert not (root / "unselected_Secured.docx").exists()
    assert not any(path.name.startswith(".connlab") for path in root.rglob("*"))


def test_single_native_cancel_and_untrusted_requests_write_nothing(local_lab):
    root, client, app = local_lab
    calls = []
    app.dependency_overrides[route.get_local_file_encryption_picker] = lambda: lambda: calls.append(True)
    assert client.post("/api/tools/encrypt-local-file").status_code == 403
    assert not calls
    assert client.post("/api/tools/encrypt-local-file", headers=HEADERS).json() == {"cancelled": True}
    assert calls == [True] and not list(root.rglob("*_Secured*"))


@pytest.mark.parametrize(("name", "reason"), [("unnumbered.xlsx", "DL-YYYY-MM-NNN"), ("file.pdf", "original Word"), ("file_Secured.ppt", "_Secured")])
def test_single_native_file_validation_has_clear_feedback_and_preserves_source(local_lab, name, reason):
    root, client, app = local_lab
    source = root / name
    source.write_bytes(b"untouched original")
    app.dependency_overrides[route.get_local_file_encryption_picker] = lambda: lambda: source
    result = client.post("/api/tools/encrypt-local-file", headers=HEADERS)
    assert result.status_code == 422 and reason in result.json()["detail"]
    assert source.read_bytes() == b"untouched original"
    assert len(list(root.glob("*.*"))) == 1


@pytest.mark.skipif(os.name != "nt", reason="Windows native file picker boundary")
@pytest.mark.parametrize("cancelled", [False, True])
def test_single_native_picker_supports_unicode_formats_and_cancellation(monkeypatch, tmp_path, cancelled):
    import pythoncom
    import win32gui
    from backend.infrastructure.files.windows_path_picker import WindowsPathPicker
    selected = tmp_path / "演示.ppt"
    released = []
    monkeypatch.setattr(pythoncom, "CoInitialize", lambda: None)
    monkeypatch.setattr(pythoncom, "CoUninitialize", lambda: released.append(True))
    def choose(**kwargs):
        assert "*.ppt;*.pptx" in kwargs["Filter"]
        if cancelled:
            raise win32gui.error(0, "GetOpenFileNameW", "Cancelled")
        return str(selected), "", 0
    monkeypatch.setattr(win32gui, "GetOpenFileNameW", choose)
    assert WindowsPathPicker().pick_encryption_file() == (None if cancelled else selected)
    assert released == [True]
