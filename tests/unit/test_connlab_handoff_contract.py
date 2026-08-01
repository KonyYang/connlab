from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "connlab_handoff_contract.py"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def make_repo(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    repo = tmp_path / "repo"; repo.mkdir(parents=True)
    git(repo, "init", "-b", "master"); git(repo, "config", "user.email", "handoff@example.invalid"); git(repo, "config", "user.name", "Handoff Test")
    locks = ["implementation.txt", "docs/lane_evidence/TASK_X_*"]
    gates = ["Reviewer", "QA", "Integrator"]
    files = {
        "tasks/TASK_X.md": "# TASK_X\n\nStatus: `approved`\n\n## Exact May Touch\n\n1. `implementation.txt`\n2. `docs/lane_evidence/TASK_X_*`\n\n## Must Not Touch\n\n- every other path\n",
        "docs/task_x_plan.md": "# Plan\n\nStatus: `approved`\n\nTask: `TASK_X`\n",
        "docs/lane_evidence/TASK_X_planner.md": (
            "TASK_ID: TASK_X\nROLE: Planner\nSTATUS: developer_dispatch_ready\n"
            "EVIDENCE: docs/lane_evidence/TASK_X_planner.md\nCOMMIT: " + "0" * 40
            + "\nNEXT: Developer\nBLOCKER: none\n"
        ),
        "docs/direct.md": "# Direct dependency\n",
    }
    for name, content in files.items():
        path = repo / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")
    git(repo, "add", "."); git(repo, "commit", "-m", "approved authority")
    approved_head = git(repo, "rev-parse", "HEAD")
    lane = tmp_path / "lane"
    git(repo, "worktree", "add", "-b", "lane/task-x", str(lane), approved_head)

    def ref(path: str) -> str:
        blob = subprocess.run(["git", "-C", str(repo), "show", f"{approved_head}:{path}"], check=True, capture_output=True).stdout
        return f"{path}@{approved_head}#{hashlib.sha256(blob).hexdigest()}"

    task_ref = ref("tasks/TASK_X.md")
    evidence_ref = ref("docs/lane_evidence/TASK_X_planner.md")
    control = {
        "schema": "connlab.execution-control", "version": 1, "wip_limit": 1,
        "execution_token_owner": "TASK_X", "execution_state": "implementation_running",
        "active": {
            "task_id": "TASK_X", "lane": "task-x", "role": "Developer",
            "branch": "lane/task-x", "worktree": str(lane), "base_sha": approved_head,
            "head_sha": approved_head, "locked_paths": locks, "required_gates": gates,
            "evidence": evidence_ref, "scope_contract_ref": task_ref,
            "may_touch_digest": canonical_digest(locks), "locked_paths_digest": canonical_digest(locks),
            "last_transition_id": None,
        },
        "queue": [], "paused": None, "quick_fix": None, "residuals": [],
        "parallel_exception": None, "evidence": evidence_ref,
    }
    payload = json.dumps(control, indent=2)
    board = repo / "docs/task_board.md"
    board.write_text(
        "# Board\n\n> Current Active Task: `TASK_X` is the sole WIP=`1` token owner in "
        "`implementation_running/Developer` on lane `task-x`.\n\n"
        f"{BEGIN}\n```json\n{payload}\n```\n{END}\n",
        encoding="utf-8",
    )
    git(repo, "add", "docs/task_board.md"); git(repo, "commit", "-m", "dispatch authority")
    board_head = git(repo, "rev-parse", "HEAD")

    def board_ref() -> str:
        blob = subprocess.run(["git", "-C", str(repo), "show", f"{board_head}:docs/task_board.md"], check=True, capture_output=True).stdout
        return f"docs/task_board.md@{board_head}#{hashlib.sha256(blob).hexdigest()}"

    capsule: dict[str, object] = {
        "schema": "connlab.handoff.v1", "task_id": "TASK_X", "role": "Orchestrator",
        "status": "developer_dispatch_ready", "next": "Developer", "blocker": "none",
        "execution_token_owner": "TASK_X", "execution_state": "implementation_running",
        "lane": "task-x", "branch": "lane/task-x", "worktree": str(lane),
        "base_sha": approved_head, "head_sha": approved_head,
        "board_ref": board_ref(), "task_ref": task_ref,
        "plan_ref": ref("docs/task_x_plan.md"), "evidence_ref": evidence_ref,
        "direct_dependencies": [ref("docs/direct.md")], "omissions": [],
        "scope_contract_ref": task_ref, "may_touch_digest": canonical_digest(locks),
        "locked_paths_digest": canonical_digest(locks), "required_gates": gates,
        "gate_snapshot_digest": canonical_digest(gates), "evidence_status": "developer_dispatch_ready",
        "next_action": "implement_approved_scope",
        "stop_conditions": ["scope_expansion", "authority_drift", "unexplained_test_failure", "destructive_action_required"],
        "changed_paths": [],
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
        {"kind": "role_start", "timestamp": "2026-08-01T00:00:00Z", "state": "started"},
        {"kind": "heartbeat", "timestamp": "2026-08-01T00:01:00Z", "state": "validated"},
        {"kind": "direction", "timestamp": "2026-08-01T00:01:01Z", "state": "dispatch"},
        {"kind": "heartbeat", "timestamp": "2026-08-01T00:02:01Z", "state": "dispatched"},
    ]
    source = tmp_path / "heartbeat.jsonl"
    source.write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
    code, result = invoke("validate-cadence", str(source))
    assert code == 0 and result["decision"] == "ALLOW_CADENCE"

    events[-1]["state"] = "dispatch"
    source.write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
    code, result = invoke("validate-cadence", str(source))
    assert code != 0 and "BLOCKED_UNCHANGED_WAIT" in result["reason_codes"]


def test_first_heartbeat_requires_prior_material_event_and_sixty_seconds(tmp_path: Path) -> None:
    cases = (
        [{"kind": "heartbeat", "timestamp": "2026-08-01T00:01:00Z", "state": "running"}],
        [
            {"kind": "role_start", "timestamp": "2026-08-01T00:00:00Z", "state": "started"},
            {"kind": "heartbeat", "timestamp": "2026-08-01T00:00:01Z", "state": "running"},
        ],
        [
            {"kind": "role_start", "timestamp": "2026-08-01T00:01:00Z", "state": "started"},
            {"kind": "heartbeat", "timestamp": "2026-08-01T00:00:00Z", "state": "running"},
        ],
    )
    for index, events in enumerate(cases):
        source = tmp_path / f"bad-{index}.jsonl"
        source.write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
        code, result = invoke("validate-cadence", str(source))
        assert code != 0
        assert set(result["reason_codes"]) & {"BLOCKED_CADENCE_HEARTBEAT", "BLOCKED_CADENCE_ORDER"}


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


def test_capsule_cross_task_stale_and_drifted_authority_never_dispatches(tmp_path: Path) -> None:
    mutations = (
        lambda capsule: capsule.__setitem__("task_id", "TASK_OTHER"),
        lambda capsule: capsule.__setitem__("status", "reviewer_pass"),
        lambda capsule: capsule.__setitem__("next", "QA"),
        lambda capsule: capsule.__setitem__("head_sha", "f" * 40),
        lambda capsule: capsule.__setitem__("gate_snapshot_digest", "e" * 64),
        lambda capsule: capsule.pop("stop_conditions"),
    )
    for index, mutate in enumerate(mutations):
        repo, capsule = make_repo(tmp_path / str(index)); mutate(capsule)
        source = tmp_path / f"drift-{index}.json"; source.write_text(json.dumps(capsule), encoding="utf-8")
        before = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
        code, result = invoke("validate-dispatch", str(source), repo)
        assert result["decision"] in {"FULL_READ_REQUIRED", "BLOCKED"}
        assert code in {0, 2}
        assert git(repo, "status", "--porcelain=v1", "--untracked-files=all") == before
