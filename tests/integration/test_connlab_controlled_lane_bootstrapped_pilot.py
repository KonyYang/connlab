from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

from scripts.connlab_controlled_lane.contracts import canonical_digest


def _request(
    command: str,
    *,
    generation: int,
    key: str,
    lane_id: str,
    payload: dict[str, object],
    repo: Path,
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "command": command,
        "request_id": f"request-{key}",
        "repo_root": str(repo),
        "repository_fingerprint": "pilot-repo",
        "task_id": "CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY",
        "lane_id": lane_id,
        "expected_registry_generation": generation,
        "idempotency_key": key,
        "operation_id": f"operation-{key}",
        "route_id": f"route-{key}",
        "scope_fingerprint": "pilot-scope",
        "payload": payload,
        "payload_digest": canonical_digest(payload),
    }


def _run(
    tmp_path: Path, request: dict[str, object], *, dry_run: bool = False
) -> dict[str, object]:
    request_path = tmp_path / f"{request['command']}-{request['request_id']}.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    command = [
        sys.executable,
        "-m",
        "scripts.connlab_controlled_lane.cli",
        str(request["command"]),
        "--request-json",
        str(request_path),
        "--registry-root",
        str(tmp_path / "registry"),
        "--allow-test-registry-root",
    ]
    if dry_run:
        command.append("--dry-run")
    completed = subprocess.run(
        command, check=False, capture_output=True, text=True
    )
    output = json.loads(completed.stdout)
    assert completed.stderr == ""
    assert completed.returncode == 0, output.get("message")
    return output


def _git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-b", "master"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "pilot@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Pilot"],
        check=True,
    )
    (repo / "README.md").write_text("pilot\n", encoding="utf-8")
    (repo / "task.md").write_text("planned pilot\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md", "task.md"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "pilot fixture"], check=True
    )
    return repo


def test_bootstrap_then_register_tests_only_pilot_without_native_side_effects(
    tmp_path: Path,
) -> None:
    repo = _git_repo(tmp_path)
    bootstrap_payload = {
        "state": "bootstrap_controller_pending",
        "primary_repo_root": str(repo),
        "authority_files": {},
        "authority_digest": canonical_digest({}),
        "requested_scope": {},
        "owner_claims": [],
        "legacy_inventory": {"source_digest": "legacy", "roles": {}},
        "legacy_inventory_digest": canonical_digest(
            {"source_digest": "legacy", "roles": {}}
        ),
        "migration": {"status": "not_required", "source_digest": "legacy"},
        "controller": {"title": "ConnLab｜研发任务编排与集成主控 v2"},
        "heartbeat": {
            "name": "ConnLab v2 controlled-lane scan",
            "rrule": "FREQ=MINUTELY;INTERVAL=5",
            "status": "PAUSED",
        },
    }
    bootstrap = _request(
        "bootstrap-registry",
        generation=0,
        key="bootstrap",
        lane_id="bootstrap-v2",
        payload=bootstrap_payload,
        repo=repo,
    )
    dry_run = _run(tmp_path, bootstrap, dry_run=True)
    assert dry_run["code"] == "CTL_DRY_RUN"
    assert not (tmp_path / "registry").exists()
    assert _run(tmp_path, bootstrap)["new_generation"] == 1

    scope = {
        "paths": [
            "tests/integration/"
            "test_connlab_controlled_lane_bootstrapped_pilot.py"
        ]
    }
    owners = [{
        "key": f"path:{scope['paths'][0]}",
        "paths": scope["paths"],
        "directories": [],
        "authorities": [],
    }]
    authority = {
        "task.md": hashlib.sha256((repo / "task.md").read_bytes()).hexdigest()
    }
    register_payload = {
        "state": "planned",
        "base_commit": subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "primary_repo_root": str(repo),
        "requested_scope": scope,
        "scope_digest": canonical_digest(scope),
        "owner_claims": owners,
        "owner_claims_digest": canonical_digest(owners),
        "authority_files": authority,
        "authority_digest": canonical_digest(authority),
        "proof": {
            "reviewer_thread_id": "fake-reviewer",
            "reviewer_worktree_path": str(repo),
            "completion_authority": {
                "role": "Reviewer",
                "evidence_path": "docs/fake-reviewer.md",
                "base_lane_head": "base",
                "allowed_changed_paths": ["docs/fake-reviewer.md"],
                "checkpoint_required": False,
                "nullable": False,
            },
        },
    }
    register = _request(
        "register-lane",
        generation=1,
        key="register",
        lane_id="connlab-controlled-lane-automation-pilot-test-only",
        payload=register_payload,
        repo=repo,
    )
    assert _run(tmp_path, register)["new_generation"] == 2

    scan = _request(
        "scan",
        generation=2,
        key="scan",
        lane_id="connlab-controlled-lane-automation-pilot-test-only",
        payload={"scan": True},
        repo=repo,
    )
    result = _run(tmp_path, scan)

    assert result["state"] == "planned"
    assert result["next_action"] == {
        "kind": "dispatch_role",
        "target_role": "Reviewer",
        "thread_id": "fake-reviewer",
        "worktree_path": str(repo),
    }
    assert not any(path.name.startswith("connlab-controlled-lane")
                   for path in repo.iterdir())
