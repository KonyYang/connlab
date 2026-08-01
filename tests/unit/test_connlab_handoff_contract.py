from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "connlab_handoff_contract.py"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def make_repo(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    repo = tmp_path / "repo"; repo.mkdir(parents=True)
    git(repo, "init", "-b", "master"); git(repo, "config", "user.email", "handoff@example.invalid"); git(repo, "config", "user.name", "Handoff Test")
    files = {
        "docs/task_board.md": "# Board\nactive authority\n",
        "tasks/TASK_X.md": "# Task\nMay Touch: implementation.txt\n",
        "docs/task_x_plan.md": "# Plan\nTDD\n",
        "docs/lane_evidence/TASK_X_planner.md": "TASK_ID: TASK_X\nROLE: Planner\nSTATUS: developer_dispatch_ready\n",
        "docs/direct.md": "# Direct dependency\n",
    }
    for name, content in files.items():
        path = repo / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")
    git(repo, "add", "."); git(repo, "commit", "-m", "authority")
    head = git(repo, "rev-parse", "HEAD")

    def ref(path: str) -> str:
        blob = subprocess.run(["git", "-C", str(repo), "show", f"{head}:{path}"], check=True, capture_output=True).stdout
        return f"{path}@{head}#{hashlib.sha256(blob).hexdigest()}"

    capsule: dict[str, object] = {
        "schema": "connlab.handoff.v1", "task_id": "TASK_X", "role": "Orchestrator",
        "status": "developer_dispatch_ready", "next": "Developer", "blocker": "none",
        "board_ref": ref("docs/task_board.md"), "task_ref": ref("tasks/TASK_X.md"),
        "plan_ref": ref("docs/task_x_plan.md"), "evidence_ref": ref("docs/lane_evidence/TASK_X_planner.md"),
        "direct_dependencies": [ref("docs/direct.md")], "omissions": [],
        "transition_count": 1, "dispatch_count": 1,
        "dispatch_template": "Read exact refs, validate authority, perform the named role, callback once.",
    }
    return repo, capsule


def invoke(command: str, value: str, repo: Path | None = None) -> tuple[int, dict[str, object]]:
    option = "--events" if command == "validate-cadence" else "--input"
    args = ["py", str(HELPER), command, option, value]
    if repo is not None: args.extend(("--repo-root", str(repo)))
    args.append("--json")
    done = subprocess.run(args, check=False, capture_output=True, text=True)
    return done.returncode, json.loads(done.stdout)


def test_dispatch_and_minimal_read_set_use_verified_refs_within_budgets(tmp_path: Path) -> None:
    repo, capsule = make_repo(tmp_path)
    source = tmp_path / "capsule.json"; source.write_text(json.dumps(capsule), encoding="utf-8")

    code, validated = invoke("validate-dispatch", str(source), repo)
    assert code == 0 and validated["decision"] == "ALLOW_DISPATCH_CAPSULE"
    assert validated["capsule_bytes"] <= 4096
    assert validated["dispatch_template_bytes"] <= 2048
    assert validated["transition_count"] == 1 and validated["dispatch_count"] == 1

    code, resolved = invoke("resolve-read-set", str(source), repo)
    assert code == 0 and resolved["decision"] == "ALLOW_MINIMAL_READ_SET"
    assert resolved["read_set_bytes"] <= 4096
    assert len(resolved["references"]) == 5


def test_invalid_ref_or_unprovable_omission_requires_full_read(tmp_path: Path) -> None:
    repo, capsule = make_repo(tmp_path)
    capsule["task_ref"] = str(capsule["task_ref"]).replace("#", "#0", 1)
    source = tmp_path / "bad.json"; source.write_text(json.dumps(capsule), encoding="utf-8")
    code, result = invoke("resolve-read-set", str(source), repo)
    assert code == 0 and result["decision"] == "FULL_READ_REQUIRED"

    _, capsule = make_repo(tmp_path / "unsafe")
    capsule["omissions"] = [{"path": "backend/authority.py", "reason": "unrelated"}]
    source = tmp_path / "unsafe.json"; source.write_text(json.dumps(capsule), encoding="utf-8")
    code, result = invoke("validate-dispatch", str(source), tmp_path / "unsafe" / "repo")
    assert code == 0 and result["decision"] == "FULL_READ_REQUIRED"


def test_unrelated_archive_change_does_not_force_full_read(tmp_path: Path) -> None:
    repo, capsule = make_repo(tmp_path)
    capsule["changed_paths"] = ["docs/archive/task_board_history/generation-000001-" + "a" * 40 + ".md"]
    capsule["omissions"] = [{"path": "docs/archive/task_board_history", "reason": "immutable_history"}]
    source = tmp_path / "archive-only.json"; source.write_text(json.dumps(capsule), encoding="utf-8")
    code, result = invoke("validate-dispatch", str(source), repo)
    assert code == 0 and result["decision"] == "ALLOW_DISPATCH_CAPSULE"

    capsule["changed_paths"] = ["backend/authority.py"]
    source.write_text(json.dumps(capsule), encoding="utf-8")
    code, result = invoke("validate-dispatch", str(source), repo)
    assert code == 0 and result["decision"] == "FULL_READ_REQUIRED"


def test_callback_is_exactly_seven_ordered_nonempty_fields_and_bounded(tmp_path: Path) -> None:
    callback = (
        "TASK_ID: TASK_X\nROLE: Developer\nSTATUS: ready_for_review\n"
        "EVIDENCE: docs/evidence.md\nCOMMIT: " + "a" * 40 + "\nNEXT: Reviewer\nBLOCKER: none\n"
    )
    source = tmp_path / "callback.txt"; source.write_text(callback, encoding="utf-8")
    code, result = invoke("validate-callback", str(source))
    assert code == 0 and result["decision"] == "ALLOW_CALLBACK"
    assert result["callback_bytes"] <= 1024

    code, literal = invoke("validate-callback", callback)
    assert code == 0 and literal["decision"] == "ALLOW_CALLBACK"

    source.write_text(callback + "EXTRA: no\n", encoding="utf-8")
    code, result = invoke("validate-callback", str(source))
    assert code != 0 and "BLOCKED_CALLBACK_SHAPE" in result["reason_codes"]

    source.write_text(callback.replace("BLOCKER: none", "BLOCKER: " + "x" * 1100), encoding="utf-8")
    code, result = invoke("validate-callback", str(source))
    assert code != 0 and "BLOCKED_CALLBACK_BUDGET" in result["reason_codes"]


def test_cadence_enforces_one_transition_one_dispatch_and_90_second_pilot(tmp_path: Path) -> None:
    events = [
        {"kind": "role_end", "timestamp": "2026-08-01T00:00:00Z", "task_id": "TASK_X", "status": "ready_for_review"},
        {"kind": "transition", "timestamp": "2026-08-01T00:00:10Z", "task_id": "TASK_X"},
        {"kind": "dispatch", "timestamp": "2026-08-01T00:00:45Z", "task_id": "TASK_X", "role": "Reviewer"},
    ]
    source = tmp_path / "events.jsonl"; source.write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
    code, result = invoke("validate-cadence", str(source))
    assert code == 0 and result["decision"] == "ALLOW_CADENCE"
    assert result["callback_to_dispatch_seconds"] == 45

    events.append({"kind": "dispatch", "timestamp": "2026-08-01T00:00:46Z", "task_id": "TASK_X", "role": "Reviewer"})
    source.write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
    code, result = invoke("validate-cadence", str(source))
    assert code != 0 and "BLOCKED_TURN_BUDGET" in result["reason_codes"]


def test_cadence_requires_60_second_changed_heartbeats_and_suppresses_waits(tmp_path: Path) -> None:
    events = [
        {"kind": "heartbeat", "timestamp": "2026-08-01T00:00:00Z", "state": "running"},
        {"kind": "heartbeat", "timestamp": "2026-08-01T00:01:00Z", "state": "validated"},
        {"kind": "direction", "timestamp": "2026-08-01T00:01:01Z", "state": "dispatch"},
    ]
    source = tmp_path / "heartbeat.jsonl"
    source.write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
    code, result = invoke("validate-cadence", str(source))
    assert code == 0 and result["decision"] == "ALLOW_CADENCE"

    events[1]["state"] = "running"
    source.write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
    code, result = invoke("validate-cadence", str(source))
    assert code != 0 and "BLOCKED_UNCHANGED_WAIT" in result["reason_codes"]


def test_capsule_and_template_budgets_fail_closed(tmp_path: Path) -> None:
    repo, capsule = make_repo(tmp_path)
    capsule["dispatch_template"] = "x" * 2049
    source = tmp_path / "large-template.json"; source.write_text(json.dumps(capsule), encoding="utf-8")
    code, result = invoke("validate-dispatch", str(source), repo)
    assert code != 0 and "BLOCKED_TEMPLATE_BUDGET" in result["reason_codes"]


def test_routine_event_cannot_launch_planner(tmp_path: Path) -> None:
    repo, capsule = make_repo(tmp_path)
    capsule["next"] = "Planner"
    source = tmp_path / "planner.json"; source.write_text(json.dumps(capsule), encoding="utf-8")
    code, result = invoke("validate-dispatch", str(source), repo)
    assert code != 0 and "BLOCKED_ROUTINE_PLANNER" in result["reason_codes"]
