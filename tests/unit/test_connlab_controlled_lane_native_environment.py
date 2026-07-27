from __future__ import annotations

import pytest

from scripts.connlab_controlled_lane.contracts import CtlError, canonical_digest
from scripts.connlab_controlled_lane.callbacks import native_task_decision
from scripts.connlab_controlled_lane.native_environment import (
    adopt_native_environment,
    native_create_decision,
    observe_pending_environment,
    validate_native_create_binding,
)
from scripts.connlab_controlled_lane.state_machine import select_next_action


def _provisional() -> dict[str, object]:
    binding = {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "route_id": "route-1",
        "operation_id": "operation-1",
        "payload_digest": "payload-1",
        "action_kind": "create_developer_environment",
        "role": "Developer",
        "native_mode": "create_new",
        "saved_project_id": "project-1",
        "project_path": "C:/repo",
        "repository_fingerprint": "repo-1",
        "environment": "worktree",
        "starting_ref": "master",
        "expected_base_commit": "base-1",
        "expected_primary_head": "base-1",
        "scope_fingerprint": "scope-1",
        "owner_claims_digest": canonical_digest(
            [{"key": "path:a.py", "paths": ["a.py"]}]
        ),
        "prompt_digest": "prompt-1",
        "client_request_digest": "request-1",
    }
    return binding


def _complete_binding() -> dict[str, object]:
    return {
        **_provisional(),
        "thread_id": "thread-1",
        "pending_worktree_id": "pending-1",
        "worktree_path": "C:/native/lane-1",
        "branch": "codex/lane-1",
        "base_commit": "base-1",
        "head": "base-1",
        "git_common_dir": "C:/repo/.git",
        "project_binding_verified": True,
        "prompt_markers_verified": True,
        "worktree_clean": True,
        "index_clean": True,
        "path_unique": True,
        "branch_unique": True,
    }


def test_option_a_prepare_forbids_invented_native_identity() -> None:
    binding = _provisional()

    validate_native_create_binding(binding)

    for field, value in (
        ("thread_id", "invented"),
        ("pending_worktree_id", "invented"),
        ("worktree_path", "C:/invented"),
        ("branch", "lane/invented"),
    ):
        with pytest.raises(CtlError) as exc_info:
            validate_native_create_binding({**binding, field: value})
        assert exc_info.value.code == "CTL_DISPATCH_ACK_MISMATCH"


def test_option_a_states_have_one_create_then_observe_only() -> None:
    assert select_next_action("authorized", {}) == {
        "kind": "create_developer_environment", "target_role": "Developer"}
    assert select_next_action("developer_environment_pending", {}) == {
        "kind": "observe_developer_environment", "target_role": "Developer"}


def test_native_dry_run_is_zero_action() -> None:
    assert native_task_decision(action="dry-run", stage="prepared") == {
        "code": "CTL_DRY_RUN", "execute": False, "external_action_count": 0}


def test_fake_native_create_is_one_action_only_after_invocation_marker() -> None:
    binding = _provisional()
    capability = {
        "tool": "create_thread",
        "project_worktree_supported": True,
        "saved_project_id": "project-1",
    }

    decision = native_create_decision(
        stage="invocation_started",
        binding=binding,
        capability=capability,
    )

    assert decision == {
        "code": "CTL_OK",
        "execute": True,
        "external_action_count": 1,
        "request": {
            "projectId": "project-1",
            "environment": {
                "type": "worktree",
                "startingState": {"type": "branch", "branchName": "master"},
            },
        },
    }
    with pytest.raises(CtlError) as stage_error:
        native_create_decision(
            stage="prepared", binding=binding, capability=capability
        )
    assert stage_error.value.code == "CTL_DISPATCH_STAGE_MISMATCH"


def test_pending_receipt_is_typed_no_action_and_never_resends() -> None:
    decision = observe_pending_environment(
        _provisional(),
        receipt={"pendingWorktreeId": "pending-1"},
        readback={"status": "pending", "pendingWorktreeId": "pending-1"},
    )

    assert decision == {
        "code": "CTL_NO_ACTION",
        "external_action_count": 0,
        "native_worktree_status": "pending",
        "pending_worktree_id": "pending-1",
        "route_id": "route-1",
        "operation_id": "operation-1",
        "retry_allowed": False,
        "adopted": False,
    }


def test_complete_readback_atomically_materializes_exact_identity() -> None:
    complete = _complete_binding()

    adopted = adopt_native_environment(
        _provisional(),
        receipt={"threadId": "thread-1"},
        matches=[complete],
        readable=True,
    )

    assert adopted == complete
    assert adopted["thread_id"] == "thread-1"
    assert adopted["worktree_path"] == "C:/native/lane-1"


@pytest.mark.parametrize(
    "receipt",
    [
        {},
        {"threadId": "thread-1", "pendingWorktreeId": "pending-1"},
        {"threadId": "thread-changed"},
    ],
)
def test_immediate_receipt_requires_one_exact_thread_identity(
    receipt: dict[str, str],
) -> None:
    with pytest.raises(CtlError) as exc_info:
        adopt_native_environment(
            _provisional(), receipt=receipt,
            matches=[_complete_binding()], readable=True)

    assert exc_info.value.code == "CTL_DISPATCH_ACK_MISMATCH"


@pytest.mark.parametrize(
    ("matches", "readable", "code"),
    [
        ([], True, "CTL_RECOVERY_REQUIRED"),
        ([_complete_binding(), _complete_binding()], True, "CTL_NATIVE_READBACK_AMBIGUOUS"),
        ([_complete_binding()], False, "CTL_RECOVERY_REQUIRED"),
    ],
)
def test_possible_start_ambiguous_or_unreadable_never_resends(
    matches: list[dict[str, object]], readable: bool, code: str
) -> None:
    with pytest.raises(CtlError) as exc_info:
        adopt_native_environment(
            _provisional(),
            receipt={"pendingWorktreeId": "pending-1"},
            matches=matches,
            readable=readable,
        )

    assert exc_info.value.code == code


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("thread_id", ""),
        ("pending_worktree_id", "wrong"),
        ("worktree_path", ""),
        ("branch", "master"),
        ("saved_project_id", "wrong"),
        ("base_commit", "wrong"),
        ("head", "wrong"),
        ("scope_fingerprint", "wrong"),
        ("worktree_clean", False),
    ],
)
def test_partial_or_wrong_adoption_binding_fails_closed(
    field: str, value: object
) -> None:
    with pytest.raises(CtlError) as exc_info:
        adopt_native_environment(
            _provisional(),
            receipt={"pendingWorktreeId": "pending-1"},
            matches=[{**_complete_binding(), field: value}],
            readable=True,
        )

    assert exc_info.value.code in {
        "CTL_DISPATCH_ACK_MISMATCH",
        "CTL_WORKTREE_MISMATCH",
    }
