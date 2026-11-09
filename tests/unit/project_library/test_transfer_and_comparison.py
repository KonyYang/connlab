import errno
from pathlib import Path
import pytest
import json
from types import SimpleNamespace
from backend.domain.project_library import ProjectLibraryConflict
from backend.infrastructure.project_library.files import move_verified
from backend.infrastructure.project_library.comparison import snapshot_differences


def test_restore_preserves_template_free_origin_and_requires_public_binding_review(tmp_path):
    from backend.infrastructure.project_library.assets import decode_rows
    rows = {"projects": [{"project_id": "P1"}],
        "project_official_workspace_records": [{"creation_kind": "basic", "template_source_path": None}],
        "project_public_folder_workflow_states": [{"binding_json": json.dumps({
            "version": 1, "path": "Z:/Open projects/2026/DL-2026-09-002 Product", "identity": [1, 2]})}]}
    settings = SimpleNamespace(data_dir=tmp_path / "data", templates_dir=tmp_path / "templates")
    decoded = decode_rows(rows, settings, tmp_path / "project")
    assert decoded["project_official_workspace_records"][0]["template_source_path"] is None
    saved = json.loads(decoded["project_public_folder_workflow_states"][0]["binding_json"])
    assert saved["requires_review"] is True
    assert saved["path"] == "Z:/Open projects/2026/DL-2026-09-002 Product"


@pytest.mark.parametrize("folder", [True, False])
@pytest.mark.parametrize("interruption", ["copy", "promoted", "none"])
def test_cross_volume_transfer_can_retry_without_overwriting_or_losing_original(tmp_path, monkeypatch, folder, interruption):
    import backend.infrastructure.project_library.files as files
    source, target = tmp_path / "left" / "source", tmp_path / "right" / "target"
    source.parent.mkdir(); target.parent.mkdir()
    if folder:
        source.mkdir(); (source / "evidence.txt").write_text("original evidence", encoding="utf-8")
    else:
        source.write_text("original evidence", encoding="utf-8")
    rename = files.os.rename
    crashed = []
    def cross_volume(origin, destination):
        if Path(origin).is_relative_to(source.parent) and Path(destination).is_relative_to(target.parent):
            raise OSError(errno.EXDEV, "different volumes")
        if not crashed and Path(origin).name.startswith(".connlab-transfer-"):
            if interruption == "copy":
                crashed.append(True); raise RuntimeError("process stopped before promotion")
            result = rename(origin, destination)
            if interruption == "promoted":
                crashed.append(True); raise RuntimeError("process stopped after promotion")
            return result
        return rename(origin, destination)
    monkeypatch.setattr(files.os, "rename", cross_volume)
    if interruption != "none":
        with pytest.raises(RuntimeError, match="process stopped"):
            move_verified(source, target)
        assert source.exists()
    move_verified(source, target)
    assert not source.exists()
    evidence = target / "evidence.txt" if folder else target
    assert evidence.read_text(encoding="utf-8") == "original evidence"
    assert not list(target.parent.glob(".connlab-transfer-*"))


def test_transfer_never_overwrites_an_unowned_same_name_destination(tmp_path):
    source, target = tmp_path / "source", tmp_path / "target"
    source.write_text("wanted", encoding="utf-8"); target.write_text("other", encoding="utf-8")
    with pytest.raises(ProjectLibraryConflict, match="occupied"):
        move_verified(source, target)
    assert source.read_text(encoding="utf-8") == "wanted"
    assert target.read_text(encoding="utf-8") == "other"


def test_snapshot_differences_name_material_and_recognizable_business_changes():
    def snapshot(title, content, sample, revision):
        return {"title": title, "files": [{"relative_path": "Results/force.csv", "directory": False, "size": 3, "sha256": content}],
            "rows": {"projects": [{"project_id": "same", "product_name": sample}],
                "confirmed_matrix_versions": [{"confirmed_revision": revision}]}}
    notes = snapshot_differences(snapshot("Current", "a", "Old sample", 1), snapshot("Incoming", "b", "New sample", 2))
    assert any("Results/force.csv" in note and "Changed" in note for note in notes)
    assert any("Old sample" in note and "New sample" in note for note in notes)
    assert any("Matrix" in note and "1" in note and "2" in note for note in notes)


def test_snapshot_comparison_does_not_treat_record_order_as_a_data_change():
    first = {"title": "Same", "files": [], "rows": {"projects": [{"product_name": "A"}, {"product_name": "B"}]}}
    second = {**first, "rows": {"projects": list(reversed(first["rows"]["projects"]))}}
    assert "Saved project and test data matches." in snapshot_differences(first, second)
