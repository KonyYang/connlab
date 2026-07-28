from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.connlab_controlled_lane.controller_title import (
    CONTROLLER_TITLE_ACTION_VERSION,
    V2_CONTROLLER_TITLE,
    adopt_controller_readback,
    build_controller_title_target,
    canonical_controller_title_ids,
    validate_controller_ack,
    validate_controller_target_binding,
)
from scripts.connlab_controlled_lane.contracts import CtlError, canonical_digest
from scripts.connlab_controlled_lane.state_machine import (
    select_next_action,
    validate_action,
    validate_transition,
)


def _registry(*, exact_title: bool = False) -> dict[str, object]:
    initial_title = V2_CONTROLLER_TITLE if exact_title else "Generated task"
    return {
        "registry_id": "registry-1",
        "lanes": {"lane-1": {
            "state": "bootstrap_controller_title_pending",
            "scope_fingerprint": "scope-1",
            "proof": {
                "controller_thread_adopted": True,
                "controller_title_exact": exact_title,
            },
        }},
        "bootstrap": {"controller": {
            "thread_id": "thread-1",
            "observed_initial_title": initial_title,
            "host_id": "local",
            "cwd": "C:/repo",
            "saved_project_id": "project-1",
            "project_path": "C:/repo",
        }},
        "role_bindings": {"lane-1:Controller": {
            "lane_id": "lane-1",
            "role": "Controller",
            "thread_id": "thread-1",
            "status": "title_pending",
        }},
    }


def _target(registry: dict[str, object], action: str) -> dict[str, object]:
    return {
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "payload_digest": "payload-1",
        "role": "Controller",
        **build_controller_title_target(registry, "lane-1", action),
    }


def _ack(target: dict[str, object], **changes: object) -> dict[str, object]:
    observed = {
        **target,
        "title": V2_CONTROLLER_TITLE,
        "project_binding_verified": True,
        **changes,
    }
    return {
        "receipt_digest": "opaque-result",
        "readback_readable": True,
        "readback_matches": 1,
        "readback_binding": observed,
        "readback_digest": canonical_digest(observed),
    }


def test_title_state_selects_mutation_or_exact_adoption_and_stable_ids() -> None:
    mutation = select_next_action(
        "bootstrap_controller_title_pending",
        {"controller_thread_adopted": True, "controller_title_exact": False},
    )
    adoption = select_next_action(
        "bootstrap_controller_title_pending",
        {"controller_thread_adopted": True, "controller_title_exact": True},
    )
    first = canonical_controller_title_ids(
        "registry-1", "lane-1", "thread-1", mutation["kind"])
    replay = canonical_controller_title_ids(
        "registry-1", "lane-1", "thread-1", mutation["kind"])
    other = canonical_controller_title_ids(
        "registry-1", "lane-1", "thread-1", adoption["kind"])

    assert mutation == {"kind": "set_controller_title", "target_role": "Controller"}
    assert adoption == {
        "kind": "adopt_exact_controller_title",
        "target_role": "Controller",
    }
    assert first == replay
    assert first != other
    assert CONTROLLER_TITLE_ACTION_VERSION in first["operation_id"]
    validate_action("bootstrap_controller_title_pending", mutation["kind"])
    validate_action("bootstrap_controller_title_pending", adoption["kind"])
    validate_transition(
        "bootstrap_controller_title_pending", "bootstrap_heartbeat_pending")


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("task_id", "wrong-task", "CTL_DISPATCH_ACK_MISMATCH"),
        ("lane_id", "wrong-lane", "CTL_DISPATCH_ACK_MISMATCH"),
        ("thread_id", "wrong-thread", "CTL_THREAD_BINDING_MISMATCH"),
        ("expected_title", "wrong-title", "CTL_DISPATCH_ACK_MISMATCH"),
        ("route_id", "wrong-route", "CTL_DISPATCH_ACK_MISMATCH"),
        ("operation_id", "wrong-operation", "CTL_DISPATCH_ACK_MISMATCH"),
        ("action_version", "wrong-version", "CTL_DISPATCH_ACK_MISMATCH"),
    ),
)
def test_title_target_rejects_changed_frozen_identity(
    field: str, value: str, code: str,
) -> None:
    target = _target(_registry(), "set_controller_title")
    changed = {**target, field: value}

    with pytest.raises(CtlError) as exc_info:
        validate_controller_target_binding(
            changed, "set_controller_title", expected=target)

    assert exc_info.value.code == code


def test_exact_title_readback_promotes_controller_binding() -> None:
    registry = _registry()
    target = _target(registry, "set_controller_title")
    dispatch = {"action_kind": "set_controller_title", "target_binding": target}
    payload = _ack(target)

    observed = validate_controller_ack(dispatch, payload)
    adopt_controller_readback(registry, "lane-1", dispatch, payload)

    assert observed["thread_id"] == "thread-1"
    assert registry["bootstrap"]["controller"]["title"] == V2_CONTROLLER_TITLE
    assert registry["lanes"]["lane-1"]["proof"]["controller_acknowledged"] is True
    assert registry["role_bindings"]["lane-1:Controller"]["status"] == "active"


@pytest.mark.parametrize(
    ("payload_change", "code"),
    (
        ({"readback_matches": 0}, "CTL_RECOVERY_REQUIRED"),
        ({"readback_matches": 2}, "CTL_NATIVE_READBACK_AMBIGUOUS"),
        ({"readback_readable": False}, "CTL_RECOVERY_REQUIRED"),
        ({"binding": {"thread_id": "wrong"}}, "CTL_THREAD_BINDING_MISMATCH"),
        ({"binding": {"title": "wrong"}}, "CTL_DISPATCH_ACK_MISMATCH"),
    ),
)
def test_title_ack_fails_closed_for_ambiguous_or_wrong_readback(
    payload_change: dict[str, object], code: str,
) -> None:
    target = _target(_registry(), "set_controller_title")
    dispatch = {"action_kind": "set_controller_title", "target_binding": target}
    binding_change = payload_change.pop("binding", {})
    payload = _ack(target, **binding_change)
    payload.update(payload_change)

    with pytest.raises(CtlError) as exc_info:
        validate_controller_ack(dispatch, payload)

    assert exc_info.value.code == code


def test_adoption_does_not_mutate_input_payload() -> None:
    registry = _registry(exact_title=True)
    target = _target(registry, "adopt_exact_controller_title")
    payload = _ack(target)
    before = deepcopy(payload)

    adopt_controller_readback(
        registry,
        "lane-1",
        {"action_kind": "adopt_exact_controller_title", "target_binding": target},
        payload,
    )

    assert payload == before
