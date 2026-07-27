from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from scripts.connlab_controlled_lane.bootstrap import (
    HEARTBEAT_NAME, HEARTBEAT_RRULE, V2_CONTROLLER_TITLE)
from scripts.connlab_controlled_lane.contracts import ADMIN_COMMANDS, canonical_digest
from scripts.connlab_controlled_lane.registry import RegistryStore


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _request(
    command: str,
    *,
    generation: int,
    key: str,
    lane_id: str = "bootstrap-v2",
    payload: dict[str, object],
) -> dict[str, object]:
    request = {
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
    if command == "bootstrap-registry":
        controller = payload["controller"]
        request.update(repo_root=payload["primary_repo_root"],
                       repository_fingerprint=controller["repository_fingerprint"])
    return request


def _bootstrap_payload(repo: Path, fingerprint: str) -> dict[str, object]:
    source_digest = hashlib.sha256((repo / "roles.md").read_bytes()).hexdigest()
    legacy_inventory = {
        "source": "roles.md", "source_digest": source_digest,
        "roles": {"Developer": "developer-thread"},
    }
    authority = {"task.md": hashlib.sha256((repo / "task.md").read_bytes()).hexdigest()}
    return {
        "state": "bootstrap_controller_pending",
        "primary_repo_root": str(repo.resolve()),
        "authority_files": authority,
        "authority_digest": canonical_digest(authority),
        "requested_scope": {"paths": ["tests/integration/pilot.py"]},
        "owner_claims": [],
        "legacy_inventory": legacy_inventory,
        "legacy_inventory_digest": canonical_digest(legacy_inventory),
        "migration": {
            "status": "not_required",
            "source_digest": source_digest,
        },
        "controller": {
            "title": V2_CONTROLLER_TITLE, "native_mode": "create_thread_local",
            "saved_project_id": "project", "project_path": str(repo.resolve()),
            "repository_fingerprint": fingerprint, "prompt_digest": "prompt",
        },
        "heartbeat": {
            "name": HEARTBEAT_NAME,
            "rrule": HEARTBEAT_RRULE,
            "status": "PAUSED",
        },
    }


@pytest.fixture
def genesis(tmp_path: Path) -> tuple[RegistryStore, dict[str, object]]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "master")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "roles.md").write_text("roles\n", encoding="utf-8")
    (repo / "task.md").write_text("task\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    fingerprint = canonical_digest({"git_common_dir": str((repo / ".git").resolve())})
    return (
        RegistryStore(tmp_path / "registry", repository_fingerprint=fingerprint),
        _bootstrap_payload(repo, fingerprint),
    )


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
    genesis: tuple[RegistryStore, dict[str, object]],
) -> None:
    store, payload = genesis
    request = _request(
        "bootstrap-registry",
        generation=0,
        key="bootstrap",
        payload=payload,
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
    genesis: tuple[RegistryStore, dict[str, object]],
    mutation: str, expected: str,
) -> None:
    store, payload = genesis
    original = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=payload
    )
    assert store.execute("bootstrap-registry", original)["code"] == "CTL_OK"
    changed = dict(original)
    if mutation == "changed-payload":
        changed_payload = {**payload, "requested_scope": {"paths": ["changed"]}}
        changed.update(payload=changed_payload,
                       payload_digest=canonical_digest(changed_payload))
    else:
        changed.update(idempotency_key="other", expected_registry_generation=0)

    result = store.execute("bootstrap-registry", changed)

    assert result["code"] == expected
    assert result["zero_write"] is True
    assert store.load()["generation"] == 1


def test_bootstrap_rejects_recovery_marker_before_any_write(
    genesis: tuple[RegistryStore, dict[str, object]],
) -> None:
    store, payload = genesis
    root = store.root
    root.mkdir()
    (root / "registry-v2.recovery.json").write_text("{}\n", encoding="utf-8")
    request = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=payload
    )

    result = store.execute("bootstrap-registry", request)

    assert result["code"] == "CTL_RECOVERY_REQUIRED"
    assert not store.path.exists()


def test_register_lane_is_planned_only_and_idempotent(
    genesis: tuple[RegistryStore, dict[str, object]],
) -> None:
    store, payload = genesis
    bootstrap = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=payload
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


def test_admin_dry_run_validates_without_creating_registry(
    genesis: tuple[RegistryStore, dict[str, object]],
) -> None:
    store, payload = genesis
    request = _request(
        "bootstrap-registry", generation=0, key="dry", payload=payload
    )
    request["dry_run"] = True

    result = store.execute("bootstrap-registry", request)

    assert result["code"] == "CTL_DRY_RUN"
    assert result["facts"]["external_action_count"] == 0
    assert not store.root.exists()


def test_register_lane_rejects_existing_cross_lane_owner(
    genesis: tuple[RegistryStore, dict[str, object]],
) -> None:
    store, payload = genesis
    bootstrap = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=payload
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
    genesis: tuple[RegistryStore, dict[str, object]],
    field: str, value: str, code: str,
) -> None:
    store, bootstrap_payload = genesis
    bootstrap = _request(
        "bootstrap-registry", generation=0, key="bootstrap", payload=bootstrap_payload
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
