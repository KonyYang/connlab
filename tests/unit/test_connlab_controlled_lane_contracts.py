from __future__ import annotations

import pytest

from scripts.connlab_controlled_lane.contracts import (
    ADMIN_COMMANDS,
    ALL_CODES,
    MUTATION_COMMANDS,
    CtlError,
    canonical_digest,
    canonical_json,
    exit_code_for,
    validate_common_request,
    validate_target_binding,
)
from scripts.connlab_controlled_lane.registry import convert_v1_to_v2
from scripts.connlab_controlled_lane.ownership import scope_fingerprint


def _request() -> dict[str, object]:
    payload = {"b": 2, "a": "value"}
    return {
        "schema_version": 2,
        "command": "prepare-dispatch",
        "request_id": "request-1",
        "task_id": "TASK_1",
        "lane_id": "lane-1",
        "expected_registry_generation": 0,
        "idempotency_key": "key-1",
        "operation_id": "operation-1",
        "route_id": "route-1",
        "scope_fingerprint": "scope-1",
        "payload": payload,
        "payload_digest": canonical_digest(payload),
    }


def test_canonical_json_and_digest_are_order_independent() -> None:
    left = {"b": [2, 1], "a": "值"}
    right = {"a": "值", "b": [2, 1]}

    assert canonical_json(left) == '{"a":"值","b":[2,1]}'
    assert canonical_digest(left) == canonical_digest(right)


def test_stable_code_catalog_has_all_39_codes_and_exit_classes() -> None:
    assert len(ALL_CODES) == 39
    assert len(MUTATION_COMMANDS) == 6
    assert ADMIN_COMMANDS == ("bootstrap-registry", "register-lane")
    assert exit_code_for("CTL_OK") == 0
    assert exit_code_for("CTL_CAS_CONFLICT") == 3
    assert exit_code_for("CTL_OWNER_CONFLICT") == 4
    assert exit_code_for("CTL_RECOVERY_REQUIRED") == 5
    assert exit_code_for("CTL_ATOMIC_WRITE_FAILED") == 6
    assert exit_code_for("CTL_REMOTE_FORBIDDEN") == 7


def test_request_validation_rejects_payload_digest_mismatch() -> None:
    request = _request()
    request["payload_digest"] = "wrong"

    with pytest.raises(CtlError) as exc_info:
        validate_common_request(request, "prepare-dispatch")

    assert exc_info.value.code == "CTL_PAYLOAD_DIGEST_MISMATCH"


def test_synthetic_v1_conversion_preserves_source_and_marks_migration() -> None:
    source = {"schema_version": 1, "generation": 7, "lanes": {"lane-1": {}}}

    converted = convert_v1_to_v2(source, source_digest="source-sha")

    assert source["schema_version"] == 1
    assert converted["schema_version"] == 2
    assert converted["generation"] == 7
    assert converted["migration"]["source_schema_version"] == 1
    assert converted["migration"]["source_digest"] == "source-sha"


def test_scope_fingerprint_is_order_independent() -> None:
    left = scope_fingerprint(
        task_id="TASK_1", lane_id="lane-1", base_commit="abc",
        may_touch=["b.py", "a.py"], locked_paths=["z", "y"],
        authorities=["matrix.method"])
    right = scope_fingerprint(
        task_id="TASK_1", lane_id="lane-1", base_commit="abc",
        may_touch=["a.py", "b.py"], locked_paths=["y", "z"],
        authorities=["matrix.method"])

    assert left == right


def test_empty_target_binding_fails_closed() -> None:
    with pytest.raises(CtlError) as exc_info:
        validate_target_binding({}, action_kind="send_existing_task")
    assert exc_info.value.code == "CTL_DISPATCH_ACK_MISMATCH"
