from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "connlab_execution_transition.py"
ACTIVE_HELPER = ROOT / "scripts" / "connlab_active_context.py"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def control_from(board: Path) -> dict[str, object]:
    text = board.read_text(encoding="utf-8")
    payload = text.split(BEGIN, 1)[1].split(END, 1)[0]
    return json.loads(payload.split("```json", 1)[1].rsplit("```", 1)[0])


def write_board(repo: Path, control: dict[str, object]) -> None:
    active = control["active"]
    assert isinstance(active, dict)
    summary = (
        f"> Current Active Task: `{active['task_id']}` is the sole WIP=`1` token owner "
        f"in `{control['execution_state']}/{active['role']}` on lane `{active['lane']}`."
    )
    payload = json.dumps(control, indent=2)
    (repo / "docs" / "task_board.md").write_text(
        f"# Board\n\n{summary}\n\n{BEGIN}\n```json\n{payload}\n```\n{END}\n",
        encoding="utf-8",
    )


def fixture(tmp_path: Path, *, required_gates: list[str] | None = None) -> dict[str, object]:
    repo = tmp_path / "primary"
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "transition@example.invalid")
    git(repo, "config", "user.name", "Transition Test")
    (repo / "docs").mkdir()
    (repo / "tasks").mkdir()
    (repo / "scripts").mkdir()
    shutil.copy2(HELPER, repo / "scripts" / HELPER.name)
    shutil.copy2(ACTIVE_HELPER, repo / "scripts" / ACTIVE_HELPER.name)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    gates = required_gates or ["Reviewer", "QA", "Integrator"]
    qa_omission = "\nQA is not required.\n" if "QA" not in gates else ""
    locks = ["implementation.txt", "docs/lane_evidence/TASK_X_*", "scripts/connlab_execution_transition.py", "scripts/connlab_active_context.py"]
    (repo / "tasks" / "TASK_X.md").write_text(
        "# TASK_X\n\nStatus: `approved`\n\nRequired gates: " + ", ".join(gates) + ".\n" + qa_omission
        + "\n## Exact May Touch\n\n" + "\n".join(f"{index}. `{path}`" for index, path in enumerate(locks, 1))
        + "\n\n## Must Not Touch\n\n- every other path\n",
        encoding="utf-8",
    )
    (repo / "docs" / "task_x_plan.md").write_text(
        "# TASK_X implementation plan\n\nStatus: `approved`\n\nTask: `TASK_X`\n",
        encoding="utf-8",
    )
    placeholder = "0" * 40
    active = {
        "task_id": "TASK_X",
        "lane": "task-x",
        "role": "Developer",
        "branch": "lane/task-x",
        "worktree": str(tmp_path / "lane"),
        "base_sha": placeholder,
        "head_sha": placeholder,
        "locked_paths": locks,
        "required_gates": gates,
        "evidence": "docs/lane_evidence/TASK_X_planner.md",
        "scope_contract_ref": "pending",
        "may_touch_digest": "0" * 64,
        "locked_paths_digest": hashlib.sha256(json.dumps(locks, separators=(",", ":")).encode()).hexdigest(),
        "last_transition_id": None,
    }
    control: dict[str, object] = {
        "schema": "connlab.execution-control",
        "version": 1,
        "wip_limit": 1,
        "execution_token_owner": "TASK_X",
        "execution_state": "implementation_running",
        "active": active,
        "queue": [],
        "paused": None,
        "quick_fix": None,
        "residuals": [{"task_id": "OLD", "residual_owner": "owner", "disposition": "retain", "evidence": "old.md"}],
        "parallel_exception": None,
        "last_governance_commit": "fixture",
        "evidence": "docs/lane_evidence/TASK_X_planner.md",
    }
    write_board(repo, control)
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    task_blob = subprocess.run(
        ["git", "-C", str(repo), "show", f"{base}:tasks/TASK_X.md"], check=True, capture_output=True
    ).stdout
    task_ref = f"tasks/TASK_X.md@{base}#{hashlib.sha256(task_blob).hexdigest()}"
    control["active"]["scope_contract_ref"] = task_ref  # type: ignore[index]
    control["active"]["may_touch_digest"] = hashlib.sha256(json.dumps(locks, separators=(",", ":")).encode()).hexdigest()  # type: ignore[index]
    lane = tmp_path / "lane"
    git(repo, "worktree", "add", "-b", "lane/task-x", str(lane), base)
    (lane / "implementation.txt").write_text("implemented\n", encoding="utf-8")
    evidence_dir = lane / "docs" / "lane_evidence"
    evidence_dir.mkdir(parents=True)
    evidence = evidence_dir / "TASK_X_developer.md"
    evidence.write_text(
        "TASK_ID: TASK_X\nROLE: Developer\nSTATUS: ready_for_review\n"
        "EVIDENCE: docs/lane_evidence/TASK_X_developer.md\nCOMMIT: " + "0" * 40
        + "\nNEXT: Reviewer\nBLOCKER: none\n",
        encoding="utf-8",
    )
    git(lane, "add", "implementation.txt", "docs/lane_evidence/TASK_X_developer.md")
    git(lane, "commit", "-m", "developer checkpoint")
    lane_head = git(lane, "rev-parse", "HEAD")
    control["active"]["base_sha"] = base  # type: ignore[index]
    control["active"]["head_sha"] = lane_head  # type: ignore[index]
    write_board(repo, control)
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "dispatch authority")
    evidence_blob = subprocess.run(
        ["git", "-C", str(lane), "show", f"{lane_head}:docs/lane_evidence/TASK_X_developer.md"],
        check=True,
        capture_output=True,
    ).stdout
    evidence_hash = hashlib.sha256(evidence_blob).hexdigest()
    return {
        "repo": repo,
        "lane": lane,
        "lane_head": lane_head,
        "primary_head": git(repo, "rev-parse", "HEAD"),
        "ref": f"docs/lane_evidence/TASK_X_developer.md@{lane_head}#{evidence_hash}",
    }


def run(fx: dict[str, object], command: str, **overrides: str) -> tuple[int, dict[str, object]]:
    args = ["py", str(HELPER), command, "--repo-root", str(fx["repo"])]
    if command != "inspect":
        values = {
            "event": "DEVELOPER_READY",
            "task-id": "TASK_X",
            "lane": "task-x",
            "expected-primary-head": str(fx["primary_head"]),
            "expected-lane-head": str(fx["lane_head"]),
            "evidence-ref": str(fx["ref"]),
            "evidence-status": "ready_for_review",
        }
        values.update(overrides)
        for key, value in values.items():
            args.extend((f"--{key}", value))
        if command == "apply" and "expected-snapshot-digest" not in values:
            planned = run(fx, "plan", **overrides)[1]
            args.extend(("--expected-snapshot-digest", str(planned["before_digest"])))
    args.append("--json")
    completed = subprocess.run(args, check=False, capture_output=True, text=True)
    return completed.returncode, json.loads(completed.stdout)


def commit_applied_transition(fx: dict[str, object]) -> str:
    repo = Path(fx["repo"])
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "commit deterministic transition")
    return git(repo, "rev-parse", "HEAD")


def test_developer_ready_plan_is_zero_write_and_apply_changes_only_board(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    board = Path(fx["repo"]) / "docs" / "task_board.md"
    before = board.read_bytes()
    preserved = control_from(board)

    code, plan = run(fx, "plan")
    assert code == 0 and plan["decision"] == "ALLOW_TRANSITION"
    assert plan["next_role"] == "Reviewer"
    assert board.read_bytes() == before

    code, applied = run(fx, "apply")
    assert code == 0 and applied["decision"] == "APPLIED"
    assert applied["changed_paths"] == ["docs/task_board.md"]
    after = control_from(board)
    assert after["execution_state"] == "gate_running"
    assert after["active"]["role"] == "Reviewer"
    for key in ("execution_token_owner", "queue", "paused", "quick_fix", "residuals", "parallel_exception"):
        assert after[key] == preserved[key]
    assert after["active"]["base_sha"] == preserved["active"]["base_sha"]
    assert after["active"]["locked_paths"] == preserved["active"]["locked_paths"]
    assert applied["before_digest"] != applied["after_digest"]

    commit_applied_transition(fx)
    code, repeated = run(fx, "apply")
    assert code == 0 and repeated["decision"] == "ALREADY_APPLIED", json.dumps(repeated)
    assert repeated["changed_paths"] == []


def test_status_or_legal_state_mismatch_fails_closed_without_write(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    board = Path(fx["repo"]) / "docs" / "task_board.md"
    before = board.read_bytes()

    code, result = run(fx, "plan", **{"evidence-status": "qa_pass"})

    assert code != 0
    assert "BLOCKED_EVENT_STATUS_MISMATCH" in result["reason_codes"]
    assert board.read_bytes() == before


def test_general_inspect_accepts_consistent_terminal_authority(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    repo = Path(fx["repo"])
    board = repo / "docs" / "task_board.md"
    control = control_from(board)
    control["execution_state"] = "complete"
    control["execution_token_owner"] = None
    control["active"] = None
    payload = json.dumps(control, indent=2)
    board.write_text(
        f"# Board\n\n> Current Active Task: None; terminal execution state is `complete`.\n\n{BEGIN}\n```json\n{payload}\n```\n{END}\n",
        encoding="utf-8",
    )
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "terminal authority")

    code, result = run({**fx, "repo": repo}, "inspect")

    assert code == 0 and result["decision"] == "ALLOW_INSPECT"
    assert result["next_role"] is None


def test_reviewer_pass_routes_by_immutable_required_gates(tmp_path: Path) -> None:
    for gates, expected in ((["Reviewer", "QA", "Integrator"], "QA"), (["Reviewer", "Integrator"], "Integrator")):
        fx = fixture(tmp_path / expected, required_gates=gates)
        board = Path(fx["repo"]) / "docs" / "task_board.md"
        control = control_from(board)
        control["execution_state"] = "gate_running"
        control["active"]["role"] = "Reviewer"
        evidence = Path(fx["lane"]) / "docs" / "lane_evidence" / "TASK_X_reviewer.md"
        evidence.write_text(
            "TASK_ID: TASK_X\nROLE: Reviewer\nSTATUS: reviewer_pass\n"
            "EVIDENCE: docs/lane_evidence/TASK_X_reviewer.md\nCOMMIT: " + "0" * 40
            + f"\nNEXT: {expected}\nBLOCKER: none\n",
            encoding="utf-8",
        )
        git(Path(fx["lane"]), "add", "docs/lane_evidence/TASK_X_reviewer.md")
        git(Path(fx["lane"]), "commit", "-m", "reviewer evidence")
        fx["lane_head"] = git(Path(fx["lane"]), "rev-parse", "HEAD")
        control["active"]["head_sha"] = fx["lane_head"]
        write_board(Path(fx["repo"]), control)
        git(Path(fx["repo"]), "add", "docs/task_board.md")
        git(Path(fx["repo"]), "commit", "-m", "review gate")
        fx["primary_head"] = git(Path(fx["repo"]), "rev-parse", "HEAD")
        evidence_blob = subprocess.run(
            ["git", "-C", str(fx["lane"]), "show", f"{fx['lane_head']}:docs/lane_evidence/TASK_X_reviewer.md"],
            check=True,
            capture_output=True,
        ).stdout
        digest = hashlib.sha256(evidence_blob).hexdigest()
        fx["ref"] = f"docs/lane_evidence/TASK_X_reviewer.md@{fx['lane_head']}#{digest}"

        code, result = run(fx, "plan", event="REVIEWER_PASS", **{"evidence-status": "reviewer_pass"})

        assert code == 0
        assert result["next_role"] == expected


def test_reviewer_blocked_and_qa_pass_complete_the_four_event_matrix(tmp_path: Path) -> None:
    cases = (
        ("REVIEWER_BLOCKED", "Reviewer", "reviewer_blocked", "Developer"),
        ("QA_PASS", "QA", "qa_pass", "Integrator"),
    )
    for event, role, status, expected in cases:
        fx = fixture(tmp_path / event)
        board = Path(fx["repo"]) / "docs" / "task_board.md"
        control = control_from(board)
        control["execution_state"] = "gate_running"
        control["active"]["role"] = role
        evidence_name = f"TASK_X_{role.lower()}.md"
        evidence = Path(fx["lane"]) / "docs" / "lane_evidence" / evidence_name
        evidence.write_text(
            f"TASK_ID: TASK_X\nROLE: {role}\nSTATUS: {status}\n"
            f"EVIDENCE: docs/lane_evidence/{evidence_name}\nCOMMIT: " + "0" * 40
            + f"\nNEXT: {expected}\nBLOCKER: none\n",
            encoding="utf-8",
        )
        git(Path(fx["lane"]), "add", f"docs/lane_evidence/{evidence_name}")
        git(Path(fx["lane"]), "commit", "-m", f"{role} evidence")
        fx["lane_head"] = git(Path(fx["lane"]), "rev-parse", "HEAD")
        control["active"]["head_sha"] = fx["lane_head"]
        write_board(Path(fx["repo"]), control)
        git(Path(fx["repo"]), "add", "docs/task_board.md")
        git(Path(fx["repo"]), "commit", "-m", f"{role} authority")
        fx["primary_head"] = git(Path(fx["repo"]), "rev-parse", "HEAD")
        blob = subprocess.run(
            ["git", "-C", str(fx["lane"]), "show", f"{fx['lane_head']}:docs/lane_evidence/{evidence_name}"],
            check=True,
            capture_output=True,
        ).stdout
        fx["ref"] = f"docs/lane_evidence/{evidence_name}@{fx['lane_head']}#{hashlib.sha256(blob).hexdigest()}"

        code, result = run(fx, "plan", event=event, **{"evidence-status": status})

        assert code == 0 and result["next_role"] == expected


def test_lane_scope_drift_is_blocked(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    lane = Path(fx["lane"])
    (lane / "outside.txt").write_text("scope drift\n", encoding="utf-8")
    git(lane, "add", "outside.txt")
    git(lane, "commit", "-m", "scope drift")
    fx["lane_head"] = git(lane, "rev-parse", "HEAD")
    board = Path(fx["repo"]) / "docs" / "task_board.md"
    control = control_from(board)
    control["active"]["head_sha"] = fx["lane_head"]
    write_board(Path(fx["repo"]), control)
    git(Path(fx["repo"]), "add", "docs/task_board.md")
    git(Path(fx["repo"]), "commit", "-m", "advance lane authority")
    fx["primary_head"] = git(Path(fx["repo"]), "rev-parse", "HEAD")

    code, result = run(fx, "plan")

    assert code != 0
    assert "BLOCKED_SCOPE_DRIFT" in result["reason_codes"]


def test_missing_or_drifted_scope_metadata_fails_closed(tmp_path: Path) -> None:
    mutations = (
        lambda active: active.pop("scope_contract_ref"),
        lambda active: active.__setitem__("may_touch_digest", "f" * 64),
        lambda active: active.__setitem__("locked_paths_digest", "e" * 64),
        lambda active: active.pop("last_transition_id"),
    )
    for index, mutate in enumerate(mutations):
        fx = fixture(tmp_path / str(index))
        repo = Path(fx["repo"]); board = repo / "docs" / "task_board.md"
        control = control_from(board); mutate(control["active"])
        write_board(repo, control); git(repo, "add", "docs/task_board.md"); git(repo, "commit", "-m", "metadata drift")
        fx["primary_head"] = git(repo, "rev-parse", "HEAD")
        before = board.read_bytes()
        code, result = run(fx, "plan")
        assert code != 0 and "BLOCKED_TRANSITION_METADATA" in result["reason_codes"]
        assert board.read_bytes() == before


def test_historical_status_substring_cannot_override_blocked_machine_record(tmp_path: Path) -> None:
    fx = fixture(tmp_path)
    lane = Path(fx["lane"]); repo = Path(fx["repo"]); board = repo / "docs" / "task_board.md"
    evidence = lane / "docs/lane_evidence/TASK_X_reviewer.md"
    evidence.write_text(
        "TASK_ID: TASK_X\nROLE: Reviewer\nSTATUS: reviewer_blocked\n"
        "EVIDENCE: docs/lane_evidence/TASK_X_reviewer.md\nCOMMIT: " + "0" * 40
        + "\nNEXT: Developer\nBLOCKER: B1\n\nHistorical note: STATUS: reviewer_pass\n",
        encoding="utf-8",
    )
    git(lane, "add", "docs/lane_evidence/TASK_X_reviewer.md"); git(lane, "commit", "-m", "blocked review")
    fx["lane_head"] = git(lane, "rev-parse", "HEAD")
    control = control_from(board); control["execution_state"] = "gate_running"; control["active"]["role"] = "Reviewer"; control["active"]["head_sha"] = fx["lane_head"]
    write_board(repo, control); git(repo, "add", "docs/task_board.md"); git(repo, "commit", "-m", "review authority")
    fx["primary_head"] = git(repo, "rev-parse", "HEAD")
    blob = subprocess.run(["git", "-C", str(lane), "show", f"{fx['lane_head']}:docs/lane_evidence/TASK_X_reviewer.md"], check=True, capture_output=True).stdout
    fx["ref"] = f"docs/lane_evidence/TASK_X_reviewer.md@{fx['lane_head']}#{hashlib.sha256(blob).hexdigest()}"
    before = board.read_bytes()
    code, result = run(fx, "plan", event="REVIEWER_PASS", **{"evidence-status": "reviewer_pass"})
    assert code != 0 and "BLOCKED_EVIDENCE_CONTENT" in result["reason_codes"]
    assert board.read_bytes() == before


def test_exact_duplicate_is_idempotent_but_every_divergent_duplicate_is_blocked(tmp_path: Path) -> None:
    cases = (
        {"task-id": "TASK_OTHER"}, {"lane": "other-lane"},
        {"expected-primary-head": "f" * 40}, {"evidence-status": "reviewer_pass"},
    )
    for index, overrides in enumerate(cases):
        fx = fixture(tmp_path / str(index)); assert run(fx, "apply")[0] == 0
        board = Path(fx["repo"]) / "docs/task_board.md"; before = board.read_bytes()
        code, result = run(fx, "apply", **overrides)
        assert code != 0 and "BLOCKED_DUPLICATE_CONFLICT" in result["reason_codes"]
        assert board.read_bytes() == before

    fx = fixture(tmp_path / "context"); assert run(fx, "apply")[0] == 0
    repo = Path(fx["repo"]); board = repo / "docs/task_board.md"; control = control_from(board)
    control["residuals"].append({"task_id": "NEW", "residual_owner": "owner", "disposition": "retain", "evidence": "new.md"})
    write_board(repo, control); before = board.read_bytes()
    code, result = run(fx, "apply")
    assert code != 0 and "BLOCKED_DUPLICATE_CONFLICT" in result["reason_codes"]
    assert board.read_bytes() == before
