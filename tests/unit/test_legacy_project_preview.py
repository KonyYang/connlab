import hashlib
import json
from pathlib import Path

from backend.application.legacy_project_preview_service import LegacyProjectPreviewService
from backend.infrastructure.files.legacy_project_preview_gateway import LegacyProjectPreviewGateway


def preview(*roots):
    return LegacyProjectPreviewService(LegacyProjectPreviewGateway()).preview([str(p) for p in roots])


def write(path, text="sample"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def test_batch_groups_workspace_and_inner_folder_and_deduplicates_overlapping_roots(tmp_path):
    manual = tmp_path / "DL-2021-01-030A1 Manual force test"
    write(manual / "Submitted material" / "request.docx")
    workspace = tmp_path / "ConnLabProjects" / "DL-2026-07-013"
    inner = workspace / "DL-2026-07-013 Qualification Testing"
    write(inner / "report.docx")
    write(workspace / "Source Book" / "record.xls")
    write(workspace / ".connlab" / "manifest.json", json.dumps({
        "schema_version": 1, "project_id": "source-id", "dl_number": "DL-2026-07-013",
        "local_workspace_path": "Z:/Other computer/DL-2026-07-013",
    }))
    before = inventory(tmp_path)

    result = preview(inner, tmp_path, workspace, tmp_path)

    assert {item["folder"] for item in result["projects"]} == {str(manual), str(workspace)}
    assert len(result["projects"]) == 2
    assert result["duplicate_roots"] == 3
    moved = next(item for item in result["projects"] if item["number"] == "DL-2026-07-013")
    assert moved["status"] == "ready"
    assert moved["name"] == "Qualification Testing"
    assert any("previous location" in message for message in moved["notes"])
    assert inventory(tmp_path) == before


def test_unnumbered_folder_can_be_previewed_without_metadata_or_current_template(tmp_path):
    project = tmp_path / "Old motor qualification"
    write(project / "customer feedback.xls")

    result = preview(tmp_path)

    assert len(result["projects"]) == 1
    assert result["projects"][0]["name"] == "Old motor qualification"
    assert result["projects"][0]["number"] is None
    assert result["projects"][0]["status"] == "ready"
    assert result["read_only"] is True


def test_mixed_numbers_and_same_number_with_different_source_ids_need_review(tmp_path):
    mixed = tmp_path / "DL-2026-07-013A"
    write(mixed / "application_data.json", json.dumps({"DL": "DL-2026-07-005"}))
    write(mixed / "DL-2026-07-013 Confirm.xlsm")
    for suffix in ["male", "female"]:
        project = tmp_path / f"DL-2026-09-001 {suffix}"
        write(project / ".connlab" / "manifest.json", json.dumps({
            "dl_number": "DL-2026-09-001", "project_id": suffix,
        }))
    result = preview(tmp_path)

    assert len(result["projects"]) == 3
    assert all(item["status"] == "review" for item in result["projects"])
    conflict = next(item for item in result["projects"] if item["number"] == "DL-2026-07-013A")
    assert any("DL-2026-07-005" in note and "DL-2026-07-013A" in note for note in conflict["notes"])
    duplicates = [item for item in result["projects"] if item["number"] == "DL-2026-09-001"]
    assert all(len(item["duplicate_folders"]) == 1 for item in duplicates)


def test_selected_project_inside_wrapper_is_promoted_when_parent_is_also_selected(tmp_path):
    project = tmp_path / "Projects" / "Unnumbered workspace"
    write(project / "Source Book" / "record.xlsx")
    inner = project / "DL-2025-06-043A Test"
    write(inner / "report.docx")

    result = preview(tmp_path, inner)

    assert len(result["projects"]) == 1
    assert result["projects"][0]["folder"] == str(project)


def test_hundreds_of_projects_are_not_cut_off_and_internal_history_is_not_a_project(tmp_path):
    for index in range(320):
        write(tmp_path / f"DL-2025-01-{index:03} Sample" / "report.docx")
    write(tmp_path / "History" / "DL-2024-01-001" / "old.docx")
    write(tmp_path / "Photos" / "image.jpg")
    result = preview(tmp_path)

    assert len(result["projects"]) == 320
    assert not result["truncated"]


def test_bad_metadata_and_one_missing_root_do_not_block_other_projects(tmp_path):
    project = tmp_path / "DL-2025-01-001 Test"
    write(project / ".connlab" / "manifest.json", "not json")
    result = preview(tmp_path / "missing", project)

    assert len(result["projects"]) == 1
    assert any("manifest.json" in note for note in result["projects"][0]["notes"])
    assert result["diagnostics"]
    assert result["duplicate_roots"] == 0


def test_partial_scan_is_explicit(tmp_path):
    gateway = LegacyProjectPreviewGateway()
    gateway.MAX_ENTRIES = 2
    for index in range(3):
        write(tmp_path / f"DL-2025-01-00{index}" / "report.docx")
    result = LegacyProjectPreviewService(gateway).preview([str(tmp_path)])
    assert result["truncated"]


def test_redirected_ancestor_is_rejected_without_traversal(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import stat
    actual = Path.lstat
    redirected = tmp_path / "junction"
    write(redirected / "DL-2025-01-001" / "report.docx")

    def lstat(path, *args, **kwargs):
        if path == redirected:
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        return actual(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", lstat)
    result = preview(redirected / "DL-2025-01-001")
    assert result["projects"] == []
    assert result["diagnostics"]


def test_many_duplicate_copies_have_bounded_explanations_and_no_internal_ids(tmp_path):
    for index in range(12):
        write(tmp_path / f"DL-2025-01-001 copy {index}" / ".connlab" / "manifest.json",
              json.dumps({"project_id": "old-identity"}))
    result = preview(tmp_path)
    assert len(result["projects"]) == 12
    for item in result["projects"]:
        assert item["status"] == "review"
        assert len(item["duplicate_folders"]) == 5
        assert item["duplicate_count"] == 11
        assert "source_id" not in item


def test_metadata_size_limit_does_not_prevent_folder_preview(tmp_path):
    project = tmp_path / "DL-2025-01-001"
    write(project / "application_data.json", "x" * 70000)
    result = preview(project)
    assert result["projects"][0]["status"] == "ready"
    assert result["projects"][0]["notes"]


def test_redirected_metadata_cannot_supply_identity_but_folder_remains_available(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import stat
    project = tmp_path / "Old qualification"
    write(project / "report.docx")
    write(project / ".connlab" / "manifest.json", json.dumps({"dl_number": "DL-2025-01-001"}))
    actual = Path.lstat

    def lstat(path, *args, **kwargs):
        if path == project / ".connlab":
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        return actual(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", lstat)
    result = preview(project)
    assert result["projects"][0]["number"] is None
    assert result["projects"][0]["notes"]
