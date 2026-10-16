from pathlib import Path
import pytest
from backend.infrastructure.files.existing_project_gateway import ExistingProjectGateway


def test_bounded_multi_root_scan_deduplicates_and_skips_history(tmp_path):
    folder = tmp_path / "DL-2026-01-005"; folder.mkdir()
    (folder / "data.txt").write_text("data")
    hidden = tmp_path / "History"; hidden.mkdir(); (hidden / "old.txt").write_text("old")
    gateway = ExistingProjectGateway()
    result = gateway.scan([str(tmp_path), str(folder)], depth=3)
    assert len([item for item in result["candidates"] if item["name"] == folder.name]) == 1
    assert not any(item["name"] == "History" for item in result["candidates"])
    assert gateway.files(str(folder))["entries"][0]["name"] == "data.txt"
    with pytest.raises(ValueError): gateway.files(str(folder), "../History")
    with pytest.raises(ValueError): gateway.file(str(folder), str(hidden / "old.txt"))


def test_redirected_selected_root_and_files_are_rejected(tmp_path):
    outside = tmp_path / "outside"; outside.mkdir(); (outside / "secret.txt").write_text("keep")
    project = tmp_path / "project"; project.mkdir()
    alias = project / "alias"
    try:
        alias.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Host does not grant symlink creation")
    gateway = ExistingProjectGateway()
    with pytest.raises(ValueError, match="Redirected"): gateway.inspect(str(alias))
    assert gateway.files(str(project))["entries"] == []
    with pytest.raises(ValueError): gateway.file(str(project), "alias/secret.txt")


def test_windows_reparse_attribute_on_ancestor_blocks_discovery_and_file_access(tmp_path,monkeypatch):
    from types import SimpleNamespace
    project=tmp_path/"redirected";project.mkdir();(project/"result.txt").write_text("data")
    original=Path.lstat
    def marked(path,*args,**kwargs):
        info=original(path,*args,**kwargs)
        return SimpleNamespace(st_mode=info.st_mode,st_file_attributes=0x400) if path==project else info
    monkeypatch.setattr(Path,"lstat",marked)
    gateway=ExistingProjectGateway()
    with pytest.raises(ValueError,match="Redirected"):gateway.inspect(str(project))
    with pytest.raises(ValueError,match="Redirected"):gateway.file(str(project),"result.txt")
    assert gateway.scan([str(project)])["diagnostics"]

