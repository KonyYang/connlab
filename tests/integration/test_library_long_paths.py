"""Exercise legacy Windows path limits without changing the machine configuration."""
import os
from pathlib import Path

import pytest

from backend.api.routes_project_library import get_configured_library
from tests.integration.test_material_archive import archive


pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows MAX_PATH")


@pytest.fixture
def legacy_limit(monkeypatch):
    # This workstation may allow long paths. Model the Win32 limit at the OS calls.
    def limit(call):
        def wrapped(path, *args, **kwargs):
            if not isinstance(path, int):
                name = os.fsdecode(path)
                if not name.startswith("\\\\?\\") and len(name.encode("utf-16-le")) >= 520:
                    raise FileNotFoundError(2, "Legacy Windows path limit", name)
            return call(path, *args, **kwargs)
        return wrapped
    for operation in ("stat", "lstat", "scandir"):
        monkeypatch.setattr(os, operation, limit(getattr(os, operation)))


def deep_file(root):
    folder = root
    while len(str(folder)) < 265:
        folder /= "连接器测试资料0123456789"
    path = folder / "Qualification Report.pdf"
    native = Path("\\\\?\\" + str(path))
    native.parent.mkdir(parents=True)
    native.write_bytes(b"isolated report")
    return path


def test_configured_refresh_browse_and_open_long_file(archive, legacy_limit, monkeypatch):
    _, store, files, materials = archive
    files.settings.projects_dir.mkdir(exist_ok=True)
    outer = materials / "DL-2024-05-029B"
    path = deep_file(outer)
    view = get_configured_library(store.session, files.settings)
    assert view.refresh()["warnings"] == []
    row, = view.search(path.name)["files"]
    assert row["relative_path"] == path.relative_to(outer).as_posix()
    listing = view.browse(row["key"], row["directory"])
    assert listing["warnings"] == []
    assert [item["name"] for item in listing["items"]] == [path.name]
    opened = []
    monkeypatch.setattr(os, "startfile", opened.append)
    assert view.open(row["key"], row["relative_path"])["message"] == "File opened."
    assert view.open(row["key"], row["relative_path"], containing=True)["message"] == "Folder opened."
    opened_file, opened_folder = map(Path, opened)
    assert opened_file.read_bytes() == b"isolated report"
    assert opened_folder.samefile(opened_file.parent)


@pytest.mark.parametrize("long_folder", ["file", "project", "library"])
def test_archive_receives_and_indexes_long_file(archive, tmp_path, legacy_limit, long_folder):
    service, store, _, materials = archive
    name = "DL-2024-05-029B"
    if long_folder == "project":
        name += " " + "样" * max(0, 265 - len(str(tmp_path / name)))
    elif long_folder == "library":
        while len(str(materials)) < 265:
            materials /= "历史资料0123456789"
        Path("\\\\?\\" + str(materials)).mkdir(parents=True)
        store.receipts.configure(str(materials))
    source = tmp_path / name
    path = deep_file(source)
    plan = service.preview(str(source))
    result = service.confirm(plan["plan_id"], plan["fingerprint"])
    assert result["status"] == "completed", result["message"]
    assert result["target_path"] == str(materials / name)
    assert service.preview(str(source))["status"] == "conflict"
    assert service.retry(result["batch_id"])["status"] == "completed"
    relative = path.relative_to(source)
    assert Path("\\\\?\\" + str(materials / source.name / relative)).read_bytes() == b"isolated report"
    assert [r["relative_path"] for r in store.indexed_files(result["target_key"])] == [relative.as_posix()]


def test_unc_material_paths_keep_the_same_share_and_public_spelling():
    from backend.infrastructure.project_library.material_paths import material_io_path, display_path

    path = Path(r"\\server\share\资料") / ("a" * 160) / ("b" * 130)
    native = material_io_path(path)
    assert str(native) == "\\\\?\\UNC\\" + str(path)[2:]
    assert material_io_path(native) == native
    assert display_path(native) == path


def test_open_keeps_verbatim_only_names_distinct_from_ordinary_names(archive):
    _, store, files, materials = archive
    outer = materials / "DL-2024-05-029B"
    outer.mkdir()
    (outer / "sample.txt").write_bytes(b"ordinary")
    Path("\\\\?\\" + str(outer / "sample.txt.")).write_bytes(b"verbatim")
    view = get_configured_library(store.session, files.settings)
    view.refresh()
    row, = view.search("sample.txt.")["files"]
    opened = []
    view.opener = opened.append
    with pytest.raises(ValueError, match="parent folder"):
        view.open(row["key"], row["relative_path"])
    assert not opened
    view.open(row["key"], row["relative_path"], containing=True)
    assert opened == [outer]
