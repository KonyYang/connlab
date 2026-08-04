from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "connlab_active_context.py"
BEGIN = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
END = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
FIRST_TASK = "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def board_text(control: dict[str, object], terminal_count: int, filler_lines: int = 0) -> str:
    active = control["active"]
    assert isinstance(active, dict)
    payload = json.dumps(control, indent=2)
    terminal = "\n".join(
        f"- `TASK_OLD_{index:03d}`: complete/accepted. Evidence: `old-{index}.md`."
        for index in range(terminal_count)
    )
    filler = "\n".join(f"Historical explanatory line {index}." for index in range(filler_lines))
    return (
        "# ConnLab Task Board\n\n"
        f"> Current Active Task: `{active['task_id']}` is the sole WIP=`1` token owner "
        f"in `{control['execution_state']}/{active['role']}` on lane `{active['lane']}`.\n\n"
        f"{BEGIN}\n```json\n{payload}\n```\n{END}\n\n"
        "## Active Execution Model\n\n"
        f"- `{active['task_id']}`: gate_running/Integrator; current evidence retained.\n"
        "- `TASK_NEXT`: `planned_pending_user_approval`; proposed and not executable.\n"
        f"{terminal}\n{filler}\n"
    )


def context_digest(control: dict[str, object]) -> str:
    active = control.get("active") or {}; assert isinstance(active, dict)
    facts = {key: control.get(key) for key in ("execution_token_owner", "queue", "paused", "quick_fix", "residuals", "parallel_exception")}
    facts["active"] = {key: active.get(key) for key in ("task_id", "lane", "branch", "worktree", "base_sha", "locked_paths", "required_gates", "scope_contract_ref", "may_touch_digest", "locked_paths_digest")}
    return hashlib.sha256(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def transition_digest(entry: dict[str, object], lane: str) -> str:
    facts = {
        "event": entry["event"], "task": entry["task_id"], "lane": lane,
        "primary": entry["primary_head"], "lane_head": entry["lane_head"],
        "evidence": entry["evidence_ref"], "status": entry["evidence_status"],
        "from_state": entry["from_state"], "from_role": entry["from_role"],
        "to_state": entry["to_state"], "to_role": entry["to_role"],
    }
    return hashlib.sha256(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def make_repo(tmp_path: Path, *, terminal_count: int = 30, filler_lines: int = 430) -> dict[str, object]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "master")
    git(repo, "config", "user.email", "maintenance@example.invalid")
    git(repo, "config", "user.name", "Maintenance Test")
    (repo / "docs").mkdir()
    (repo / "scripts").mkdir()
    shutil.copy2(HELPER, repo / "scripts" / HELPER.name)
    evidence_dir = repo / "docs/lane_evidence"; evidence_dir.mkdir()
    evidence_specs = {
        "developer": ("Developer", "ready_for_review", "Reviewer"),
        "reviewer": ("Reviewer", "reviewer_pass", "QA"),
        "qa": ("QA", "qa_pass", "Integrator"),
    }
    for name, (role, status, next_role) in evidence_specs.items():
        (evidence_dir / f"TASK_A_{name}.md").write_text(
            f"TASK_ID: {FIRST_TASK}\nROLE: {role}\nSTATUS: {status}\n"
            f"EVIDENCE: docs/lane_evidence/TASK_A_{name}.md\nCOMMIT: " + "0" * 40
            + f"\nNEXT: {next_role}\nBLOCKER: none\n",
            encoding="utf-8",
        )
    git(repo, "add", "scripts/connlab_active_context.py", "docs/lane_evidence")
    git(repo, "commit", "-m", "accepted helper and gate evidence")
    gate_head = git(repo, "rev-parse", "HEAD")

    def transition(event: str, name: str, from_role: str, to_role: str, status: str) -> dict[str, object]:
        path = f"docs/lane_evidence/TASK_A_{name}.md"
        raw = subprocess.run(["git", "-C", str(repo), "show", f"{gate_head}:{path}"], check=True, capture_output=True).stdout
        evidence_blob = git(repo, "rev-parse", f"{gate_head}:{path}")
        helper_blob = git(repo, "rev-parse", f"{gate_head}:scripts/connlab_active_context.py")
        entry = {
            "transition_id": "pending", "event": event,
            "task_id": FIRST_TASK, "evidence_ref": f"{path}@{gate_head}#{hashlib.sha256(raw).hexdigest()}",
            "evidence_commit": gate_head, "evidence_blob_sha": evidence_blob,
            "evidence_sha256": hashlib.sha256(raw).hexdigest(), "evidence_status": status,
            "lane_head": gate_head, "primary_head": gate_head, "helper_blob_sha": helper_blob,
            "retained_context_digest": "pending",
            "from_state": "implementation_running" if from_role == "Developer" else "gate_running",
            "from_role": from_role, "to_state": "gate_running", "to_role": to_role,
        }
        entry["transition_id"] = transition_digest(entry, "task-governance-active-context-deterministic-transition-and-event-handoff")
        return entry
    control: dict[str, object] = {
        "schema": "connlab.execution-control", "version": 1, "wip_limit": 1,
        "execution_token_owner": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
        "execution_state": "gate_running",
        "active": {
            "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
            "lane": "task-governance-active-context-deterministic-transition-and-event-handoff",
            "role": "Integrator", "branch": "lane/task-a", "worktree": str(tmp_path / "lane"),
            "base_sha": gate_head, "head_sha": gate_head, "locked_paths": ["docs/task_board.md"],
            "required_gates": ["Reviewer", "QA", "Integrator"],
            "evidence": transition("QA_PASS", "qa", "QA", "Integrator", "qa_pass")["evidence_ref"],
        },
        "queue": [], "paused": None, "quick_fix": None,
        "residuals": [{"task_id": "OLD", "residual_owner": "owner", "disposition": "retain", "evidence": "old.md"}],
        "parallel_exception": None, "last_governance_commit": "fixture",
        "transition_history": [
            transition("DEVELOPER_READY", "developer", "Developer", "Reviewer", "ready_for_review"),
            transition("REVIEWER_PASS", "reviewer", "Reviewer", "QA", "reviewer_pass"),
            transition("QA_PASS", "qa", "QA", "Integrator", "qa_pass"),
        ],
    }
    for entry in control["transition_history"]: entry["retained_context_digest"] = context_digest(control)  # type: ignore[index]
    control["evidence"] = control["active"]["evidence"]  # type: ignore[index]
    board = repo / "docs" / "task_board.md"
    board.write_text(board_text(control, terminal_count, filler_lines), encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "integrator closeout")
    return {"repo": repo, "board": board, "head": git(repo, "rev-parse", "HEAD")}


def invoke(fx: dict[str, object], command: str, **extra: str) -> tuple[int, dict[str, object]]:
    args = ["py", str(HELPER), command, "--repo-root", str(fx["repo"])]
    if command in {"plan-maintenance", "apply-maintenance"}:
        values = {
            "expected-head": str(fx["head"]),
            "expected-board-sha256": hashlib.sha256(Path(fx["board"]).read_bytes()).hexdigest(),
        }
        values.update(extra)
        for key, value in values.items():
            args.extend((f"--{key}", value))
        if command == "apply-maintenance" and "expected-plan-digest" not in values:
            plan = invoke(fx, "plan-maintenance")[1]
            args.extend(("--expected-plan-digest", str(plan["plan_digest"])))
    args.append("--json")
    done = subprocess.run(args, check=False, capture_output=True, text=True)
    return done.returncode, json.loads(done.stdout)


def test_first_plan_is_zero_write_and_first_apply_archives_exact_board(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    board = Path(fx["board"])
    before = board.read_bytes()
    before_tree = sorted(path.relative_to(fx["repo"]).as_posix() for path in Path(fx["repo"]).rglob("*") if path.is_file())

    code, plan = invoke(fx, "plan-maintenance")
    assert code == 0 and plan["decision"] == "MAINTENANCE_REQUIRED"
    assert plan["generation"] == 1 and plan["zero_write"] is True
    assert board.read_bytes() == before
    assert sorted(path.relative_to(fx["repo"]).as_posix() for path in Path(fx["repo"]).rglob("*") if path.is_file()) == before_tree

    code, applied = invoke(fx, "apply-maintenance")
    assert code == 0 and applied["decision"] == "APPLIED_MAINTENANCE"
    assert applied["changed_paths"] == [
        "docs/archive/task_board_history/generation-000001-" + str(fx["head"]) + ".md",
        "docs/archive/task_board_history/index.v1.jsonl",
        "docs/task_board.md",
    ]
    archive = Path(fx["repo"]) / applied["archive_path"]
    assert archive.read_bytes() == before
    assert len(board.read_text(encoding="utf-8").splitlines()) <= 400
    assert len(board.read_bytes()) <= 65_536
    assert "TASK_NEXT" in board.read_text(encoding="utf-8")
    assert BEGIN in board.read_text(encoding="utf-8")


def test_below_all_thresholds_is_zero_write(tmp_path: Path) -> None:
    fx = make_repo(tmp_path, terminal_count=2, filler_lines=0)
    before = Path(fx["board"]).read_bytes()

    code, plan = invoke(fx, "plan-maintenance")

    assert code == 0 and plan["decision"] == "NO_MAINTENANCE_REQUIRED"
    assert plan["changed_paths"] == []
    assert Path(fx["board"]).read_bytes() == before


def test_each_line_byte_and_terminal_threshold_triggers_independently(tmp_path: Path) -> None:
    line_fx = make_repo(tmp_path / "lines", terminal_count=2, filler_lines=430)
    terminal_fx = make_repo(tmp_path / "terminal", terminal_count=25, filler_lines=0)
    byte_fx = make_repo(tmp_path / "bytes", terminal_count=2, filler_lines=0)
    board = Path(byte_fx["board"])
    board.write_text(board.read_text(encoding="utf-8") + ("X" * 66_000) + "\n", encoding="utf-8")
    git(Path(byte_fx["repo"]), "add", "docs/task_board.md")
    git(Path(byte_fx["repo"]), "commit", "-m", "byte threshold")
    byte_fx["head"] = git(Path(byte_fx["repo"]), "rev-parse", "HEAD")

    for fx in (line_fx, terminal_fx, byte_fx):
        code, plan = invoke(fx, "plan-maintenance")
        assert code == 0 and plan["decision"] == "MAINTENANCE_REQUIRED"


def test_first_generation_proves_byte_exact_rollback(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    original = Path(fx["board"]).read_bytes()
    invoke(fx, "apply-maintenance")
    temp_root = tmp_path / "rollback-temp"; temp_root.mkdir()
    output = temp_root / "rollback.md"
    done = subprocess.run(
        ["py", str(HELPER), "prove-rollback", "--repo-root", str(fx["repo"]), "--generation", "1", "--temp-root", str(temp_root), "--output", str(output), "--json"],
        check=False, capture_output=True, text=True,
    )
    result = json.loads(done.stdout)
    assert done.returncode == 0 and result["decision"] == "ROLLBACK_PROVEN"
    assert output.read_bytes() == original


def test_first_generation_proves_mixed_newline_source_rollback(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    repo = Path(fx["repo"])
    board = Path(fx["board"])
    lines = board.read_text(encoding="utf-8").splitlines()
    mixed_board = "\r\n".join(lines[:5]) + "\n" + "\r\n".join(lines[5:])
    board.write_bytes((mixed_board + "\r\nMixed newline regression anchor\n").encode())
    original = board.read_bytes()
    assert original.count(b"\n") > original.count(b"\r\n")
    git(repo, "config", "core.autocrlf", "true")
    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "mixed newline source board")
    fx["head"] = git(repo, "rev-parse", "HEAD")

    assert invoke(fx, "apply-maintenance")[0] == 0
    temp_root = tmp_path / "rollback-temp"; temp_root.mkdir()
    output = temp_root / "rollback.md"
    done = subprocess.run(
        ["py", str(HELPER), "prove-rollback", "--repo-root", str(repo), "--generation", "1",
         "--temp-root", str(temp_root), "--output", str(output), "--json"],
        check=False, capture_output=True, text=True,
    )
    result = json.loads(done.stdout)

    assert done.returncode == 0 and result["decision"] == "ROLLBACK_PROVEN"
    assert output.read_bytes() == original


def test_rollback_rejects_repository_existing_and_escaped_targets_without_mutation(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    assert invoke(fx, "apply-maintenance")[0] == 0
    repo = Path(fx["repo"]); board = Path(fx["board"])
    temp_root = tmp_path / "rollback-temp"; temp_root.mkdir()
    existing = temp_root / "existing.md"; existing.write_bytes(b"preserve-existing")
    targets = (board, existing, tmp_path / "escaped.md")
    before_board = board.read_bytes(); before_existing = existing.read_bytes()
    before_status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    for target in targets:
        done = subprocess.run(
            ["py", str(HELPER), "prove-rollback", "--repo-root", str(repo), "--generation", "1",
             "--temp-root", str(temp_root), "--output", str(target), "--json"],
            check=False, capture_output=True, text=True,
        )
        result = json.loads(done.stdout)
        assert done.returncode != 0 and any(code.startswith("BLOCKED_ROLLBACK_OUTPUT") for code in result["reason_codes"])
        assert board.read_bytes() == before_board and existing.read_bytes() == before_existing
        assert git(repo, "status", "--porcelain=v1", "--untracked-files=all") == before_status


def test_rollback_rejects_linked_temp_root_and_output_target(tmp_path: Path) -> None:
    fx = make_repo(tmp_path); assert invoke(fx, "apply-maintenance")[0] == 0
    safe = tmp_path / "safe"; safe.mkdir(); linked = tmp_path / "linked"
    try: os.symlink(safe, linked, target_is_directory=True)
    except OSError:
        junction = subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(safe)], check=False, capture_output=True)
        if junction.returncode: pytest.skip("directory links and junctions are unavailable on this Windows host")
    output = linked / "rollback.md"; board = Path(fx["board"]); before = board.read_bytes()
    done = subprocess.run(
        ["py", str(HELPER), "prove-rollback", "--repo-root", str(fx["repo"]), "--generation", "1",
         "--temp-root", str(linked), "--output", str(output), "--json"],
        check=False, capture_output=True, text=True,
    )
    result = json.loads(done.stdout)
    assert done.returncode != 0 and "BLOCKED_ROLLBACK_OUTPUT_ROOT" in result["reason_codes"]
    assert board.read_bytes() == before and not output.exists()


def test_same_generation_apply_is_idempotent(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    original_hash = hashlib.sha256(Path(fx["board"]).read_bytes()).hexdigest()
    plan = invoke(fx, "plan-maintenance")[1]
    assert invoke(fx, "apply-maintenance")[0] == 0

    code, repeated = invoke(
        fx,
        "apply-maintenance",
        **{
            "expected-board-sha256": original_hash,
            "expected-plan-digest": str(plan["plan_digest"]),
        },
    )

    assert code == 0 and repeated["decision"] == "ALREADY_APPLIED"
    assert repeated["changed_paths"] == []


def test_apply_requires_integrator_and_complete_gate_history(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    board = Path(fx["board"])
    raw = board.read_text(encoding="utf-8")
    raw = raw.replace('"role": "Integrator"', '"role": "Reviewer"').replace("gate_running/Integrator", "gate_running/Reviewer")
    board.write_text(raw, encoding="utf-8")
    git(Path(fx["repo"]), "add", "docs/task_board.md")
    git(Path(fx["repo"]), "commit", "-m", "reviewer authority")
    fx["head"] = git(Path(fx["repo"]), "rev-parse", "HEAD")

    code, result = invoke(fx, "apply-maintenance")

    assert code != 0
    assert "BLOCKED_MAINTENANCE_AUTHORITY" in result["reason_codes"]


def test_event_name_only_gate_history_is_rejected_without_write(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    repo = Path(fx["repo"]); board = Path(fx["board"])
    control = json.loads(board.read_text(encoding="utf-8").split(BEGIN, 1)[1].split(END, 1)[0].split("```json", 1)[1].rsplit("```", 1)[0])
    control["transition_history"] = [{"event": "DEVELOPER_READY"}, {"event": "REVIEWER_PASS"}, {"event": "QA_PASS"}]
    board.write_text(board_text(control, 30, 430), encoding="utf-8")
    git(repo, "add", "docs/task_board.md"); git(repo, "commit", "-m", "event names only")
    fx["head"] = git(repo, "rev-parse", "HEAD")
    before = board.read_bytes()
    code, result = invoke(fx, "apply-maintenance")
    assert code != 0 and "BLOCKED_MAINTENANCE_GATES" in result["reason_codes"]
    assert board.read_bytes() == before


@pytest.mark.parametrize(
    ("field", "value"),
    [("task_id", "TASK_OTHER"), ("evidence_status", "reviewer_blocked"),
     ("evidence_sha256", "0" * 64), ("evidence_blob_sha", "0" * 40),
     ("helper_blob_sha", "0" * 40), ("primary_head", "0" * 40)],
)
def test_gate_evidence_mismatch_matrix_is_zero_write(tmp_path: Path, field: str, value: str) -> None:
    fx = make_repo(tmp_path); repo = Path(fx["repo"]); board = Path(fx["board"])
    control = json.loads(board.read_text(encoding="utf-8").split(BEGIN, 1)[1].split(END, 1)[0].split("```json", 1)[1].rsplit("```", 1)[0])
    control["transition_history"][1][field] = value
    board.write_text(board_text(control, 30, 430), encoding="utf-8")
    git(repo, "add", "docs/task_board.md"); git(repo, "commit", "-m", "gate evidence drift"); fx["head"] = git(repo, "rev-parse", "HEAD")
    before = board.read_bytes(); code, result = invoke(fx, "apply-maintenance")
    assert code != 0 and set(result["reason_codes"]) & {"BLOCKED_MAINTENANCE_GATES", "BLOCKED_HELPER_ANCESTRY"}
    assert board.read_bytes() == before


def test_gate_tuple_and_transition_id_must_be_exact_and_zero_write(tmp_path: Path) -> None:
    for name, mutate in (
        ("tuple", lambda entry: entry.update({"from_role": "Quick Fixer", "to_role": "Developer"})),
        ("transition-id", lambda entry: entry.update({"transition_id": "f" * 64})),
    ):
        fx = make_repo(tmp_path / name); repo = Path(fx["repo"]); board = Path(fx["board"])
        control = json.loads(board.read_text(encoding="utf-8").split(BEGIN, 1)[1].split(END, 1)[0].split("```json", 1)[1].rsplit("```", 1)[0])
        entry = control["transition_history"][1]; mutate(entry)
        if name == "tuple":
            entry["transition_id"] = transition_digest(entry, control["active"]["lane"])
        board.write_text(board_text(control, 30, 430), encoding="utf-8")
        git(repo, "add", "docs/task_board.md"); git(repo, "commit", "-m", f"forged {name}"); fx["head"] = git(repo, "rev-parse", "HEAD")
        before = board.read_bytes(); code, result = invoke(fx, "apply-maintenance")
        assert code != 0 and "BLOCKED_MAINTENANCE_GATES" in result["reason_codes"]
        assert board.read_bytes() == before


def test_post_qa_unreviewed_helper_drift_is_zero_write(tmp_path: Path) -> None:
    fx = make_repo(tmp_path); repo = Path(fx["repo"]); board = Path(fx["board"])
    helper = repo / "scripts/connlab_active_context.py"
    helper.write_text(helper.read_text(encoding="utf-8") + "\n# unreviewed helper drift\n", encoding="utf-8")
    git(repo, "add", "scripts/connlab_active_context.py"); git(repo, "commit", "-m", "post-QA helper drift")
    fx["head"] = git(repo, "rev-parse", "HEAD")
    before = board.read_bytes(); code, result = invoke(fx, "apply-maintenance")
    assert code != 0 and "BLOCKED_HELPER_ANCESTRY" in result["reason_codes"]
    assert board.read_bytes() == before


def test_idempotent_apply_revalidates_compact_board_and_index(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    original_hash = hashlib.sha256(Path(fx["board"]).read_bytes()).hexdigest()
    plan = invoke(fx, "plan-maintenance")[1]
    assert invoke(fx, "apply-maintenance")[0] == 0
    board = Path(fx["board"]); board.write_bytes(board.read_bytes() + b"corrupt\n")
    tampered = board.read_bytes()
    code, result = invoke(fx, "apply-maintenance", **{
        "expected-board-sha256": original_hash, "expected-plan-digest": str(plan["plan_digest"]),
    })
    assert code != 0 and "BLOCKED_ALREADY_APPLIED_DRIFT" in result["reason_codes"]
    assert board.read_bytes() == tampered
