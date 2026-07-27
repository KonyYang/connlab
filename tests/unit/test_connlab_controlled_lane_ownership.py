from __future__ import annotations

import pytest

from scripts.connlab_controlled_lane.contracts import CtlError, canonical_digest
from scripts.connlab_controlled_lane.ownership import (
    apply_advance_effects,
    find_owner_conflicts,
    normalize_authority,
    normalize_repo_path,
    reset_gate_proof,
    validate_governance_owner,
    validate_owner_acquisition,
)
from scripts.connlab_controlled_lane.state_machine import apply_callback_proof


def test_path_normalization_is_windows_safe_and_rejects_escape_and_glob() -> None:
    assert normalize_repo_path(r"Backend\\Api\\route.py") == "backend/api/route.py"
    with pytest.raises(CtlError):
        normalize_repo_path("../outside.py")
    with pytest.raises(CtlError):
        normalize_repo_path("backend/**/*.py")


def test_path_and_authority_ancestor_conflicts_are_detected() -> None:
    requested = {
        "paths": ["backend/api/route.py"],
        "directories": ["tests/unit"],
        "authorities": ["matrix.method"],
    }
    owners = [
        {
            "lane_id": "other",
            "paths": [],
            "directories": ["backend/api"],
            "authorities": ["matrix"],
        }
    ]

    conflicts = find_owner_conflicts(requested, owners)

    assert {item["kind"] for item in conflicts} == {"path", "authority"}
    assert normalize_authority("Matrix.Method") == "matrix.method"


def test_task_board_mutation_is_reserved_for_planner_or_integrator() -> None:
    with pytest.raises(CtlError) as exc_info:
        validate_governance_owner("docs/task_board.md", role="Developer")

    assert exc_info.value.code == "CTL_OWNER_CONFLICT"
    validate_governance_owner("docs/task_board.md", role="Planner")


def test_owner_claims_must_match_canonical_requested_scope() -> None:
    claims = [{"key": "path:a.py", "paths": ["a.py"]}]
    registry = {"lanes": {"lane-1": {
        "requested_scope": {"paths": ["b.py"]}, "owner_claims": claims}},
        "shared_owners": {}}
    target = {
        "owner_claims_digest": canonical_digest(claims),
        "scope_fingerprint": "scope-1",
        "worktree_path": "C:/lane",
        "branch": "codex/lane",
        "thread_id": "thread-1",
        "operation_id": "operation-1",
    }
    dispatch = {"target_binding": target}

    with pytest.raises(CtlError) as exc_info:
        validate_owner_acquisition(registry, "lane-1", dispatch)

    assert exc_info.value.code == "CTL_SCOPE_VIOLATION"
    registry["lanes"]["lane-1"]["requested_scope"] = {"paths": ["a.py"]}
    apply_advance_effects(
        registry,
        "lane-1",
        {"action_kind": "create_developer_environment", "target_binding": target},
        "developer_active",
    )
    validate_owner_acquisition(registry, "lane-1", dispatch)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("key", "path:other.py"),
        ("paths", ["other.py"]),
        ("content_digest", "digest-2"),
        ("directories", ["tests/integration"]),
        ("authorities", ["matrix.other"]),
        ("worktree_path", "C:/other"),
        ("branch", "codex/other"),
        ("thread_id", "thread-2"),
        ("operation_id", "operation-2"),
    ],
)
def test_same_lane_owner_requires_exact_materialized_claim(
    field: str, value: object
) -> None:
    claim = {
        "key": "path:a.py", "paths": ["a.py"], "directories": ["tests/unit"],
        "authorities": ["matrix.method"], "content_digest": "digest-1"}
    target = {
        "owner_claims_digest": canonical_digest([claim]),
        "scope_fingerprint": "scope-1",
        "worktree_path": "C:/lane",
        "branch": "codex/lane",
        "thread_id": "thread-1",
        "operation_id": "operation-1",
    }
    registry = {
        "lanes": {"lane-1": {
            "requested_scope": {
                "paths": ["a.py"], "directories": ["tests/unit"],
                "authorities": ["matrix.method"]},
            "owner_claims": [claim],
        }},
        "shared_owners": {},
        "worktrees": {},
        "role_bindings": {},
        "callbacks": {},
    }
    apply_advance_effects(
        registry,
        "lane-1",
        {"action_kind": "create_developer_environment", "target_binding": target},
        "developer_active",
    )
    stored = registry["shared_owners"]["path:a.py"]
    changed = {**stored, field: value}
    registry["shared_owners"] = {str(changed["key"]): changed}

    with pytest.raises(CtlError) as exc_info:
        validate_owner_acquisition(
            registry, "lane-1", {"target_binding": target})

    assert exc_info.value.code == "CTL_OWNER_CONFLICT"


def test_cross_lane_owner_conflict_cannot_be_overwritten() -> None:
    claim = {"key": "authority:matrix.method", "authorities": ["matrix.method"]}
    target = {
        "owner_claims_digest": canonical_digest([claim]),
        "scope_fingerprint": "scope-a",
        "worktree_path": "C:/lane-a",
        "branch": "codex/lane-a",
        "thread_id": "thread-a",
        "operation_id": "operation-a",
    }
    registry = {
        "lanes": {"lane-a": {
            "requested_scope": {"authorities": ["matrix.method"]},
            "owner_claims": [claim],
        }},
        "shared_owners": {
            "authority:matrix": {
                "key": "authority:matrix",
                "authorities": ["matrix"],
                "lane_id": "lane-b",
            }
        },
    }

    with pytest.raises(CtlError) as exc_info:
        validate_owner_acquisition(
            registry, "lane-a", {"target_binding": target}
        )

    assert exc_info.value.code == "CTL_OWNER_CONFLICT"
    assert registry["shared_owners"]["authority:matrix"]["lane_id"] == "lane-b"


def test_acknowledged_closeout_updates_registry_topology() -> None:
    registry = {
        "lanes": {"lane-1": {}},
        "worktrees": {"lane-1": {"head": "lane-head"}},
        "shared_owners": {"path:x": {"lane_id": "lane-1"}},
        "role_bindings": {},
        "callbacks": {"event-1": {"lane_id": "lane-1"}},
    }
    closeout = {
        "residual_ledger_status": "resolved", "residual_ledger_digest": "ledger",
        "released_owner_keys": ["path:x"], "consumed_callback_ids": ["event-1"],
    }
    dispatch = {
        "action_kind": "governance_closeout",
        "target_binding": {"closeout": closeout},
    }

    apply_advance_effects(registry, "lane-1", dispatch, "closeout_pending")

    assert registry["lanes"]["lane-1"]["closeout"] == closeout
    assert registry["shared_owners"] == {}
    assert registry["callbacks"]["event-1"]["consumed_at"] == "closeout"


def test_completion_callback_updates_authoritative_lane_proof() -> None:
    registry = {
        "lanes": {"lane-1": {
            "state": "implementation_readiness_pending", "proof": {}}}}

    apply_callback_proof(
        registry, "lane-1",
        {"role": "Reviewer", "status": "reviewer_blocked"}, "blocked")

    assert registry["lanes"]["lane-1"]["proof"] == {"readiness_status": "blocked"}


@pytest.mark.parametrize("state,key", [
    ("user_planning_approval_pending", "user_approved"),
    ("user_implementation_approval_pending", "user_approved"),
    ("implementation_readiness_pending", "readiness_status"),
    ("review_pending", "review_status"), ("qa_pending", "qa_status"),
    ("integration_pending", "integrator_status"),
])
def test_entering_new_gate_clears_only_its_stale_proof(state: str, key: str) -> None:
    lane = {"proof": {key: "stale", "unrelated": "retained"}}
    reset_gate_proof(lane, state)
    assert lane["proof"] == {"unrelated": "retained"}
