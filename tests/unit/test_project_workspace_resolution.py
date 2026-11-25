import json
import os
from pathlib import Path
import shutil

import pytest

from test_basic_project_workspace_service import service


def resolution(tmp_path):
    from backend.application.project_workspace_resolution import ProjectWorkspaceResolutionService
    basic, store, _ = service(tmp_path)
    basic.create("P1", basic.preview("P1")["expected_context"], "first")
    store.require_workspace_unclaimed = lambda project_id, workspace: None
    old = store.record
    backup = tmp_path / "moved"
    old.local_workspace_path.parent.rename(backup)
    target = tmp_path / "destination"
    target.mkdir()
    return basic, store, old, backup / old.local_workspace_path.name, target, ProjectWorkspaceResolutionService(basic, store, lambda: target)


@pytest.mark.parametrize("strategy", ["recreate", "relink"])
def test_resolve_preserves_project_and_history_and_replays_only_confirmed_request(tmp_path, strategy):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    manual = moved / old.official_folder_path.name / "manual.txt"
    manual.write_text("operator bytes")
    assert basic.preview("P1")["resolution_required"]
    path = moved / old.official_folder_path.name if strategy == "relink" else target
    review = resolver.preview("P1", strategy, str(path))
    assert store.record == old
    result = resolver.apply("P1", strategy, str(path), review["expected_context"], "fix")
    assert result["directory_available"] and store.record.workspace_id == old.workspace_id
    assert store.record.local_workspace_path.parent == path if strategy == "recreate" else store.record.local_workspace_path == moved
    assert (store.record.official_folder_path / "manual.txt").exists() == (strategy == "relink")
    assert manual.read_text() == "operator bytes"
    assert basic.journal.read("P1")["previous_record"]["official_folder_path"] == str(old.official_folder_path)
    assert resolver.apply("P1", strategy, str(path), review["expected_context"], "fix") == result
    assert not basic.preview("P1")["resolution_required"]


def test_recreate_refuses_changed_target_and_restored_original(tmp_path):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    preview = resolver.preview("P1", "recreate", None)
    occupied = target / old.dl_number
    occupied.mkdir()
    with pytest.raises(ValueError):
        resolver.apply("P1", "recreate", None, preview["expected_context"], "race")
    assert not list(occupied.iterdir())
    moved.parent.rename(old.local_workspace_path.parent)
    with pytest.raises(ValueError):
        resolver.preview("P1", "recreate", None)
    assert store.record == old


def test_relink_verifies_manifest_and_rejects_stale_copy_before_binding(tmp_path):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    manifest = moved / ".connlab/manifest.json"
    preview = resolver.preview("P1", "relink", str(moved))
    payload = json.loads(manifest.read_text())
    payload["project_id"] = "P2"
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        resolver.apply("P1", "relink", str(moved), preview["expected_context"], "wrong-owner")
    assert store.record == old
    assert json.loads(manifest.read_text())["project_id"] == "P2"


def test_relink_complete_backup_with_legacy_manifest_preserves_original(tmp_path):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    copied = Path(shutil.copytree(moved, target / "restored backup"))
    identity_file = copied / ".connlab/manifest.json"
    original = json.loads(identity_file.read_text(encoding="utf-8"))
    original.pop("workspace_id")
    original["schema_version"] = 1
    identity_file.write_text(json.dumps(original), encoding="utf-8")
    review = resolver.preview("P1", "relink", str(copied))
    result = resolver.apply("P1", "relink", str(copied), review["expected_context"], "backup")
    assert result["directory_available"]
    assert store.record.local_workspace_path == copied
    assert json.loads((moved / ".connlab/manifest.json").read_text())["local_workspace_path"] == str(old.local_workspace_path)


def test_existing_renamed_official_folder_stays_with_description_recovery(tmp_path):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    moved.parent.rename(old.local_workspace_path.parent)
    old.official_folder_path.rename(old.official_folder_path.with_name(f"{old.dl_number} revised description"))
    with pytest.raises(ValueError, match="renamed"):
        resolver.preview("P1", "recreate", None)
    assert store.record == old
    assert not list(target.iterdir())


def test_resume_after_binding_write_interruption(tmp_path, monkeypatch):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    review = resolver.preview("P1", "recreate", None)
    save = store.save
    def fail(record):
        raise OSError("simulated interruption")
    monkeypatch.setattr(store, "save", fail)
    with pytest.raises(OSError, match="simulated"):
        resolver.apply("P1", "recreate", None, review["expected_context"], "recover")
    assert store.record == old
    operation = basic.preview("P1")["resolution_operation_id"]
    assert operation
    monkeypatch.setattr(store, "save", save)
    result = resolver.resume("P1", operation)
    assert result["directory_available"]
    assert store.record.official_folder_path == Path(review["target_path"])


def test_restored_original_can_end_interrupted_resolution_without_removing_files(tmp_path, monkeypatch):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    preview = resolver.preview("P1", "recreate", None)
    save = store.save

    def temporarily_offline(record):
        raise OSError("registration unavailable")

    monkeypatch.setattr(store, "save", temporarily_offline)
    with pytest.raises(OSError):
        resolver.apply("P1", "recreate", None, preview["expected_context"], "interrupted")
    operation = basic.preview("P1")["resolution_operation_id"]
    moved.parent.rename(old.local_workspace_path.parent)
    assert resolver.abandon("P1", operation)["directory_available"]
    assert resolver.abandon("P1", operation)["status"] == "abandoned"
    with pytest.raises(ValueError, match="ended"):
        resolver.resume("P1", operation)
    with pytest.raises(ValueError, match="ended"):
        resolver.apply("P1", "recreate", None, preview["expected_context"], "interrupted")
    assert basic.preview("P1")["directory_available"]
    assert store.record == old and (target / old.dl_number / ".connlab/manifest.json").exists()
    old.local_workspace_path.parent.rename(moved.parent)
    monkeypatch.setattr(store, "save", save)
    review = resolver.preview("P1", "relink", str(target / old.dl_number))
    result = resolver.apply("P1", "relink", str(target / old.dl_number), review["expected_context"], "next")
    assert result["directory_available"]
    with pytest.raises(ValueError, match="registered"):
        resolver.abandon("P1", result["operation_id"])


def test_missing_official_directory_with_conflicting_manifest_needs_review(tmp_path):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    moved.parent.rename(old.local_workspace_path.parent)
    old.official_folder_path.rename(target / "outside")
    original = json.loads(old.manifest_path.read_text())
    old.manifest_path.write_text(json.dumps({**original, "project_id": "foreign"}))
    assert not basic.preview("P1")["resolution_required"]
    with pytest.raises(ValueError, match="conflicting"):
        resolver.preview("P1", "recreate", None)
    assert store.record == old


def test_ended_legacy_relink_requires_audited_manifest_for_its_new_paths(tmp_path, monkeypatch):
    basic, store, old, moved, target, resolver = resolution(tmp_path)
    manifest = moved / ".connlab/manifest.json"
    payload = json.loads(manifest.read_text())
    payload.pop("workspace_id")
    payload["schema_version"] = 1
    manifest.write_text(json.dumps(payload))
    review = resolver.preview("P1", "relink", str(moved))
    with monkeypatch.context() as interrupted:
        def reject_index(record):
            raise OSError("interrupted")
        interrupted.setattr(store, "save", reject_index)
        with pytest.raises(OSError):
            resolver.apply("P1", "relink", str(moved), review["expected_context"], "first-link")
    resolver.abandon("P1", basic.preview("P1")["resolution_operation_id"])
    published = manifest.read_bytes()
    manifest.write_bytes(published + b" ")
    with pytest.raises(ValueError, match="layout"):
        resolver.preview("P1", "relink", str(moved))
    manifest.write_bytes(published)
    retry = resolver.preview("P1", "relink", str(moved))
    assert resolver.apply("P1", "relink", str(moved), retry["expected_context"], "second-link")["directory_available"]
    with pytest.raises(ValueError, match="ended"):
        resolver.apply("P1", "relink", str(moved), review["expected_context"], "first-link")


def test_workspace_overlap_follows_existing_aliased_parent_for_new_leaf(tmp_path):
    from backend.infrastructure.official_workspace_manifest import workspace_locations_overlap
    registered = tmp_path / "registered"
    registered.mkdir()
    alias = tmp_path / "alias"
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(registered), str(alias))
    else:
        alias.symlink_to(registered, target_is_directory=True)
    assert workspace_locations_overlap(registered, alias / "uncreated")
    assert workspace_locations_overlap(alias / "offline", registered / "offline" / "child")
    assert not workspace_locations_overlap(alias / "first", registered / "second")
