import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.application.public_folder_binding import PublicFolderBinding
from backend.application.public_folder_path_resolver import PublicFolderPathResolver
from backend.application.public_folder_workflow_service import PublicFolderWorkflowState


def binding(tmp_path, number="DL-2026-09-002"):
    root = tmp_path / "public"
    year = root / "Open projects" / "2026"
    year.mkdir(parents=True)
    record = SimpleNamespace(project_id="P1", dl_number=number,
                             official_folder_path=tmp_path / (number + " Product"))
    state = [PublicFolderWorkflowState(project_id="P1")]
    commits = []
    def save(value):
        state[0] = value
    value = PublicFolderBinding(repository=SimpleNamespace(get_state=lambda _: state[0], save_state=save),
        workspaces=SimpleNamespace(get_by_project=lambda _: record),
        year_resolver=SimpleNamespace(resolve=lambda _: SimpleNamespace(year=2026, blockers=[])),
        path_resolver=PublicFolderPathResolver(), public_root=root, commit=lambda: commits.append(state[0].binding_json))
    return value, record, state, year, commits


def test_full_number_candidates_distinguish_suffix_and_require_explicit_review(tmp_path):
    value, record, state, year, commits = binding(tmp_path)
    (year / "DL-2026-09-002A Other").mkdir()
    candidate = year / "DL-2026-09-002 Earlier description"
    candidate.mkdir()
    (candidate / "colleague.txt").write_text("retain", encoding="utf-8")
    preview = value.preview("P1")
    assert preview["status"] == "review_required"
    assert not preview["can_create"]
    assert [item["path"] for item in preview["candidates"]] == [str(candidate)]
    assert state[0].binding_json is None
    assert value.confirm("P1", preview["expected_context"], preview["candidates"][0]["candidate_id"])["status"] == "bound"
    assert len(commits) == 1
    assert (candidate / "colleague.txt").read_text(encoding="utf-8") == "retain"
    record.official_folder_path = tmp_path / "DL-2026-09-002 New description"
    assert value.preview("P1")["current_path"] == str(candidate)
    assert not (year / record.official_folder_path.name).exists()


def test_empty_target_is_created_and_binding_committed_without_file_copy(tmp_path):
    value, record, state, year, commits = binding(tmp_path)
    preview = value.preview("P1")
    assert preview["can_create"]
    value.confirm("P1", preview["expected_context"], "create")
    target = year / record.official_folder_path.name
    assert target.is_dir() and list(target.iterdir()) == []
    assert json.loads(commits[0])["identity"]
    assert value.preview("P1")["status"] == "bound"


def test_commit_failure_retains_new_directory_for_explicit_recovery(tmp_path):
    value, record, state, year, _ = binding(tmp_path)
    def fail():
        state[0] = PublicFolderWorkflowState(project_id="P1")
        raise RuntimeError("DB disconnected")
    value.commit = fail
    preview = value.preview("P1")
    with pytest.raises(RuntimeError):
        value.confirm("P1", preview["expected_context"], "create")
    recovered = value.preview("P1")
    assert recovered["status"] == "review_required"
    assert not recovered["can_create"]
    assert len(recovered["candidates"]) == 1


def test_missing_year_blocks_without_creating_parents(tmp_path):
    value, _, _, year, _ = binding(tmp_path)
    year.rmdir()
    preview = value.preview("P1")
    assert preview["status"] == "blocked"
    assert str(year) in preview["blockers"][0]
    assert not year.exists()


def test_multiple_and_replaced_candidate_stale_confirmation(tmp_path):
    value, _, state, year, _ = binding(tmp_path)
    first = year / "DL-2026-09-002 One"
    first.mkdir()
    (year / "DL-2026-09-002 Two").mkdir()
    preview = value.preview("P1")
    assert len(preview["candidates"]) == 2
    first.rename(year / "retained")
    first.mkdir()
    with pytest.raises(ValueError, match="changed"):
        value.confirm("P1", preview["expected_context"], preview["candidates"][0]["candidate_id"])
    assert state[0].binding_json is None


def test_incomplete_enumeration_is_blocked_not_empty(tmp_path, monkeypatch):
    value, _, _, year, _ = binding(tmp_path)
    original = Path.iterdir
    def denied(path):
        if path == year:
            raise PermissionError("share inaccessible")
        return original(path)
    monkeypatch.setattr(Path, "iterdir", denied)
    preview = value.preview("P1")
    assert preview["status"] == "blocked" and not preview["can_create"]


def test_changed_config_requires_review_no_automatic_new_folder(tmp_path):
    value, record, state, year, _ = binding(tmp_path)
    p = value.preview("P1")
    value.confirm("P1", p["expected_context"], "create")
    original = json.loads(state[0].binding_json)["path"]
    other = tmp_path / "other"
    (other / "Open projects" / "2026").mkdir(parents=True)
    value.root = other
    preview = value.preview("P1")
    assert preview["status"] == "review_required" and preview["current_path"] == original
    assert not (other / "Open projects" / "2026" / record.official_folder_path.name).exists()
