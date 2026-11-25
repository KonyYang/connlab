"""Exercise the directory view with isolated Settings, SQLite, folders and opener."""
from pathlib import Path
from threading import Event
import pytest

from backend.api.routes_project_library import get_configured_library
from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.storage.repositories import ExternalResourceRepository
from tests.integration.test_material_archive import archive


def test_directory_view_follows_current_roots_and_folder_names(archive, tmp_path):
    _, store, files, materials = archive
    projects = tmp_path / "projects"
    number = "DL-2026-08-008"
    outer = materials / number
    child = outer / (number + " 中文连接器")
    child.mkdir(parents=True)
    (outer / "Source Book").mkdir()
    (child / "测试记录.txt").write_text("isolated", encoding="utf8")
    other = projects / (number + " Another sample")
    other.mkdir(parents=True)
    def view():
        return get_configured_library(store.session, files.settings)
    service = view()
    service.refresh()
    matches = service.search(number)["projects"]
    assert {(r["number"], r["title"], Path(r["folder_path"])) for r in matches} == {
        (number, "中文连接器", outer), (number, "Another sample", other)}
    entry, = service.search("测试记录")["projects"]
    assert {r["name"] for r in service.browse(entry["key"])["items"]} == {child.name, "Source Book"}
    opened = []
    service.opener = opened.append
    service.open(entry["key"], child.name + "/测试记录.txt")
    service.open(entry["key"], child.name + "/测试记录.txt", containing=True)
    assert opened == [child / "测试记录.txt", child]
    (outer / (number + " Second description")).mkdir()
    (materials / "无编号").mkdir()
    service.refresh()
    assert service.search(project=entry["key"])["projects"][0]["title"] == ""
    assert service.search("无编号")["projects"][0]["number"] is None
    new = tmp_path / "changed"
    (new / "new folder").mkdir(parents=True)
    store.receipts.configure(str(new))
    assert not view().search("测试记录")["projects"]
    with pytest.raises(LookupError):
        view().open(entry["key"])
    view().refresh()
    assert len(view().search("new folder")["projects"]) == 1
    new.rename(tmp_path / "offline")
    result = view().refresh()
    assert any(str(new) in message for message in result["warnings"]) and result["available"] is False
    assert [r["title"] for r in view().search()["projects"]] == ["Another sample"]
    other.rename(projects / "renamed")
    view().refresh()
    assert [r["title"] for r in view().search()["projects"]] == ["renamed"]
    replacement = tmp_path / "project replacement"
    (replacement / "Different").mkdir(parents=True)
    ExternalResourceRepository(store.session).upsert(ExternalResource(
        "new-project-default", ExternalResourceType.PROJECT_OUTPUT_ROOT, replacement))
    view().refresh()
    assert [r["title"] for r in view().search()["projects"]] == ["Different"]

def test_cancel_internal_files_and_unrelated_registrations(archive, tmp_path):
    _, store, files, materials = archive
    folder = materials / "DL-2026-04-003"
    (folder / "Source Book").mkdir(parents=True)
    (folder / "DL-2026-04-004 Wrong").mkdir()
    (folder / ".connlab").mkdir()
    (folder / ".connlab" / "secret.txt").write_text("isolated")
    outside = tmp_path / "old root" / "unrelated"
    outside.mkdir(parents=True)
    store.register(outside.parent, outside, None, outside.name)
    view = get_configured_library(store.session, files.settings)
    view.refresh()
    row, = view.search()["projects"]
    assert (row["number"], row["title"]) == ("DL-2026-04-003", "")
    assert view.search("secret")["files"] == []
    assert not view.search("unrelated")["projects"]
    with pytest.raises(ValueError):
        view.open(row["key"], ".connlab/secret.txt")
    with pytest.raises(ValueError):
        view.open(row["key"], "../other.txt")
    from backend.infrastructure.project_library.material_archive_files import ArchiveCancelled
    view.scanner.cancellation = Event()
    view.scanner.cancellation.set()
    with pytest.raises(ArchiveCancelled):
        view.refresh()
    assert view.search()["projects"] == [row]
