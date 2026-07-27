from __future__ import annotations

from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.bootstrap import (
    HEARTBEAT_NAME,
    HEARTBEAT_RRULE,
    V2_CONTROLLER_TITLE,
    select_bootstrap_action,
)
from scripts.connlab_controlled_lane.contracts import ADMIN_COMMANDS, canonical_digest
from scripts.connlab_controlled_lane.registry import RegistryStore


def _request(
    command: str,
    *,
    generation: int,
    key: str,
    lane_id: str = "bootstrap-v2",
    payload: dict[str, object],
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "command": command,
        "request_id": f"request-{key}",
        "task_id": "CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_BOOTSTRAP",
        "lane_id": lane_id,
        "expected_registry_generation": generation,
        "idempotency_key": key,
        "operation_id": f"operation-{key}",
        "route_id": f"route-{key}",
        "scope_fingerprint": "scope-v2",
        "payload": payload,
        "payload_digest": canonical_digest(payload),
    }


def _bootstrap_payload() -> dict[str, object]:
    legacy_inventory = {
        "source": "docs/project_management/ROLE_THREAD_REGISTRY.md",
        "source_digest": "legacy-digest",
        "roles": {
            "Planner": "planner-thread",
            "Developer": "developer-thread",
            "Reviewer": "reviewer-thread",
            "QA": "qa-thread",
            "Integrator": "integrator-thread",
        },
        "retained_lanes": {
            "TASK_367A_MATRIX_EDITOR_LIVE_XLSX_EXPORT": {
                "branch": "lane/task-367a-matrix-editor-live-xlsx-export",
                "head": "53840b42",
                "clean": True,
            }
        },
    }
    authority = {"AGENTS.md": "agents-digest"}
    return {
        "state": "bootstrap_controller_pending",
        "primary_repo_root": "C:/repo",
        "authority_files": authority,
        "authority_digest": canonical_digest(authority),
        "requested_scope": {"paths": ["tests/integration/pilot.py"]},
        "owner_claims": [],
        "legacy_inventory": legacy_inventory,
        "legacy_inventory_digest": canonical_digest(legacy_inventory),
        "migration": {
            "status": "not_required",
            "source_digest": "legacy-digest",
        },
        "controller": {"title": V2_CONTROLLER_TITLE},
        "heartbeat": {
            "name": HEARTBEAT_NAME,
            "rrule": HEARTBEAT_RRULE,
            "status": "PAUSED",
        },
    }


def _register_payload() -> dict[str, object]:
    scope = {"paths": ["tests/integration/test_bootstrapped_pilot.py"]}
    owners = [{
        "key": f"path:{scope['paths'][0]}",
        "paths": scope["paths"],
        "directories": [],
        "authorities": [],
    }]
    authority: dict[str, str] = {}
    return {
        "state": "planned",
        "base_commit": "base-commit",
        "primary_repo_root": "C:/repo",
        "requested_scope": scope,
        "scope_digest": canonical_digest(scope),
        "owner_claims": owners,
        "owner_claims_digest": canonical_digest(owners),
        "authority_files": authority,
        "authority_digest": canonical_digest(authority),
        "proof": {},
    }


def test_admin_command_catalog_is_bounded_and_uses_existing_codes() -> None:
    assert ADMIN_COMMANDS == ("bootstrap-registry", "register-lane")


def test_bootstrap_registry_creates_generation_one_and_exact_replay(
    tmp_path: Path,
) -> None:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-v2")
    request = _request(
        "bootstrap-registry",
        generation=0,
        key="bootstrap",
        payload=_bootstrap_payload(),
    )

    first = store.execute("bootstrap-registry", request)
    replay = store.execute("bootstrap-registry", request)
    registry = store.load()

    assert first["code"] == "CTL_OK"
    assert first["old_generation"] == 0
    assert first["new_generation"] == 1
    assert replay["code"] == "CTL_ALREADY_APPLIED"
    assert registry["generation"] == 1
    assert registry["migration"]["status"] == "not_required"
    assert registry["legacy_inventory"]["status"] == "legacy_retained"
    assert registry["lanes"]["bootstrap-v2"]["state"] == "bootstrap_controller_pending"
    assert registry["bootstrap"]["controller"]["title"] == V2_CONTROLLER_TITLE
    assert registry["bootstrap"]["heartbeat"]["status"] == "PAUSED"


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("changed-payload", "CTL_IDEMPOTENCY_CONFLICT"),
        ("stale-generation", "CTL_CAS_CONFLICT"),
    ],
)
def test_bootstrap_registry_fails_closed_without_generation_drift(
    tmp_path: Path, mutation: str, expected: str,
) -> None:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-v2")
    original = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=_bootstrap_payload()
    )
    assert store.execute("bootstrap-registry", original)["code"] == "CTL_OK"
    changed = dict(original)
    if mutation == "changed-payload":
        payload = {**_bootstrap_payload(), "primary_repo_root": "C:/wrong"}
        changed.update(payload=payload, payload_digest=canonical_digest(payload))
    else:
        changed.update(idempotency_key="other", expected_registry_generation=0)

    result = store.execute("bootstrap-registry", changed)

    assert result["code"] == expected
    assert result["zero_write"] is True
    assert store.load()["generation"] == 1


def test_bootstrap_rejects_recovery_marker_before_any_write(tmp_path: Path) -> None:
    root = tmp_path / "registry"
    root.mkdir()
    (root / "registry-v2.recovery.json").write_text("{}\n", encoding="utf-8")
    store = RegistryStore(root, repository_fingerprint="repo-v2")
    request = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=_bootstrap_payload()
    )

    result = store.execute("bootstrap-registry", request)

    assert result["code"] == "CTL_RECOVERY_REQUIRED"
    assert not store.path.exists()


def test_register_lane_is_planned_only_and_idempotent(tmp_path: Path) -> None:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-v2")
    bootstrap = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=_bootstrap_payload()
    )
    assert store.execute("bootstrap-registry", bootstrap)["code"] == "CTL_OK"
    request = _request(
        "register-lane",
        generation=1,
        key="register-pilot",
        lane_id="connlab-controlled-lane-automation-pilot-test-only",
        payload=_register_payload(),
    )

    first = store.execute("register-lane", request)
    replay = store.execute("register-lane", request)
    lane = store.load()["lanes"][request["lane_id"]]

    assert first["code"] == "CTL_OK"
    assert first["new_generation"] == 2
    assert replay["code"] == "CTL_ALREADY_APPLIED"
    assert lane["state"] == "planned"
    assert lane["implementation_authorized"] is False
    assert lane["base_commit"] == "base-commit"


def test_admin_dry_run_validates_without_creating_registry(tmp_path: Path) -> None:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-v2")
    request = _request(
        "bootstrap-registry", generation=0, key="dry", payload=_bootstrap_payload()
    )
    request["dry_run"] = True

    result = store.execute("bootstrap-registry", request)

    assert result["code"] == "CTL_DRY_RUN"
    assert result["facts"]["external_action_count"] == 0
    assert not store.root.exists()


def test_register_lane_rejects_existing_cross_lane_owner(tmp_path: Path) -> None:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-v2")
    bootstrap = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=_bootstrap_payload()
    )
    assert store.execute("bootstrap-registry", bootstrap)["code"] == "CTL_OK"
    registry = store.load()
    registry["shared_owners"]["tests/integration"] = {
        "lane_id": "other-lane",
        "paths": ["tests/integration"],
        "directories": [],
        "authorities": [],
    }
    store._atomic_write(registry)
    request = _request(
        "register-lane", generation=1, key="owner-conflict",
        lane_id="pilot-lane", payload=_register_payload(),
    )

    result = store.execute("register-lane", request)

    assert result["code"] == "CTL_OWNER_CONFLICT"
    assert store.load()["generation"] == 1


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("state", "authorized", "CTL_AUTHORIZATION_REQUIRED"),
        ("scope_digest", "changed", "CTL_SCOPE_CONFLICT"),
        ("owner_claims_digest", "changed", "CTL_OWNER_CONFLICT"),
        ("authority_digest", "changed", "CTL_EVIDENCE_STALE"),
    ],
)
def test_register_lane_rejects_authority_or_scope_changes(
    tmp_path: Path, field: str, value: str, code: str,
) -> None:
    store = RegistryStore(tmp_path / "registry", repository_fingerprint="repo-v2")
    bootstrap = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=_bootstrap_payload()
    )
    assert store.execute("bootstrap-registry", bootstrap)["code"] == "CTL_OK"
    payload = _register_payload()
    payload[field] = value
    request = _request(
        "register-lane", generation=1, key=f"register-{field}",
        lane_id="pilot-lane", payload=payload,
    )

    result = store.execute("register-lane", request)

    assert result["code"] == code
    assert store.load()["generation"] == 1


def test_bootstrap_state_machine_selects_exactly_one_external_action() -> None:
    assert select_bootstrap_action("bootstrap_controller_pending", {}) == {
        "kind": "create_controller_task",
        "target_role": "Controller",
    }
    assert select_bootstrap_action(
        "bootstrap_heartbeat_pending", {"controller_acknowledged": True}
    ) == {
        "kind": "create_paused_heartbeat",
        "target_role": "Controller",
    }
    assert select_bootstrap_action(
        "bootstrap_dry_run_pending", {"heartbeat_acknowledged": True}
    ) == {"kind": "run_zero_write_dry_run", "target_role": "Controller"}
    assert select_bootstrap_action(
        "bootstrap_ready", {"dry_run_passed": True}
    ) == {"kind": "no_action", "target_role": None}
