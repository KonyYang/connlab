from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.completion_authority import (
    observe_completion_authority,
    validate_completion_contract,
)
from scripts.connlab_controlled_lane.contracts import CtlError


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "lane"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "ConnLab Test")
    _git(repo, "config", "user.email", "connlab@example.invalid")
    evidence = repo / "docs" / "evidence.md"
    evidence.parent.mkdir()
    evidence.write_text("before\n", encoding="utf-8")
    _git(repo, "add", "docs/evidence.md")
    _git(repo, "commit", "-m", "base")
    return repo, _git(repo, "rev-parse", "HEAD")


def _binding(repo: Path, base: str) -> dict[str, object]:
    return {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "route_id": "route-1",
        "operation_id": "operation-1",
        "role": "Developer",
        "thread_id": "thread-1",
        "worktree_path": str(repo),
        "payload_digest": "payload-1",
        "completion_authority_nullable": False,
        "expected_evidence_path": "docs/evidence.md",
        "base_lane_head": base,
        "allowed_changed_paths": ["docs/evidence.md"],
        "checkpoint_required": True,
    }


def _complete(repo: Path) -> tuple[str, str]:
    evidence = repo / "docs" / "evidence.md"
    evidence.write_text("after\n", encoding="utf-8")
    _git(repo, "add", "docs/evidence.md")
    _git(repo, "commit", "-m", "role completion")
    return hashlib.sha256(evidence.read_bytes()).hexdigest(), _git(repo, "rev-parse", "HEAD")


def test_dispatch_contract_freezes_path_and_base_but_not_final_authority(
    tmp_path: Path,
) -> None:
    repo, base = _repo(tmp_path)
    binding = _binding(repo, base)

    validate_completion_contract(binding)

    assert "expected_evidence_sha256" not in binding
    assert "expected_lane_head" not in binding


def test_post_role_observation_reads_actual_digest_and_completion_head(
    tmp_path: Path,
) -> None:
    repo, base = _repo(tmp_path)
    digest, head = _complete(repo)
    payload = {
        "evidence_path": "docs/evidence.md",
        "evidence_sha256": digest,
        "lane_head": head,
    }

    observed = observe_completion_authority(_binding(repo, base), payload)

    assert observed["evidence_sha256"] == digest
    assert observed["lane_head"] == head
    assert observed["base_lane_head"] == base
    assert observed["changed_paths"] == ["docs/evidence.md"]


@pytest.mark.parametrize("field", ["evidence_sha256", "lane_head"])
def test_tampered_callback_authority_fails_closed(
    tmp_path: Path, field: str
) -> None:
    repo, base = _repo(tmp_path)
    digest, head = _complete(repo)
    payload = {
        "evidence_path": "docs/evidence.md",
        "evidence_sha256": digest,
        "lane_head": head,
        field: "tampered",
    }

    with pytest.raises(CtlError) as exc_info:
        observe_completion_authority(_binding(repo, base), payload)

    assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"


def test_predispatch_head_dirty_tree_and_unallowed_change_fail_closed(
    tmp_path: Path,
) -> None:
    repo, base = _repo(tmp_path)
    digest = hashlib.sha256((repo / "docs/evidence.md").read_bytes()).hexdigest()
    with pytest.raises(CtlError) as predispatch:
        observe_completion_authority(
            _binding(repo, base),
            {
                "evidence_path": "docs/evidence.md",
                "evidence_sha256": digest,
                "lane_head": base,
            },
        )
    assert predispatch.value.code == "CTL_CALLBACK_CONFLICT"

    (repo / "outside.txt").write_text("outside\n", encoding="utf-8")
    _git(repo, "add", "outside.txt")
    _git(repo, "commit", "-m", "outside")
    head = _git(repo, "rev-parse", "HEAD")
    with pytest.raises(CtlError) as changed:
        observe_completion_authority(
            _binding(repo, base),
            {
                "evidence_path": "docs/evidence.md",
                "evidence_sha256": digest,
                "lane_head": head,
            },
        )
    assert changed.value.code == "CTL_CALLBACK_CONFLICT"

    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(CtlError) as dirty:
        observe_completion_authority(
            _binding(repo, base),
            {
                "evidence_path": "docs/evidence.md",
                "evidence_sha256": digest,
                "lane_head": head,
            },
        )
    assert dirty.value.code == "CTL_CALLBACK_CONFLICT"


def test_wrong_ancestry_fails_closed(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    _git(repo, "checkout", "--orphan", "unrelated")
    digest, head = _complete(repo)

    with pytest.raises(CtlError) as exc_info:
        observe_completion_authority(
            _binding(repo, base),
            {"evidence_path": "docs/evidence.md",
             "evidence_sha256": digest, "lane_head": head})

    assert exc_info.value.code == "CTL_CALLBACK_CONFLICT"


def test_explicit_user_null_authority_is_the_only_legal_null_stage() -> None:
    binding = {
        "role": "User",
        "completion_authority_nullable": True,
        "expected_evidence_path": None,
        "base_lane_head": None,
        "allowed_changed_paths": [],
        "checkpoint_required": False,
    }

    assert observe_completion_authority(
        binding,
        {"evidence_path": None, "evidence_sha256": None, "lane_head": None},
    ) == {
        "evidence_path": None,
        "evidence_sha256": None,
        "lane_head": None,
        "base_lane_head": None,
        "changed_paths": [],
    }
    with pytest.raises(CtlError):
        validate_completion_contract({**binding, "role": "Developer"})
