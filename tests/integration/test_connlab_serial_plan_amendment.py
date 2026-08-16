from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.connlab_serial_board import parse_board
from tests.integration.test_connlab_nondestructive_evidence_topology import TASK_ID, fixture, git
from tests.integration.test_connlab_serial_complex_recovery import board_hash, invoke_personal


def corrected_plan(repo: Path, active: dict, *, mixed: bool = False, route: str = "gpt-5.6-sol / medium / risk:authority") -> str:
    approved = {
        "schema": "connlab.personal-task-approved-request",
        "version": 1,
        "task_id": TASK_ID,
        "summary": active["summary"],
        "kind": "planned",
        **active["scope_contract"],
    }
    path = repo / f"docs/{TASK_ID.lower()}_plan.md"
    data = (
        "# Corrected Plan\n\nDeveloper, Reviewer, QA and Integrator are all "
        f"`{route}`.\n\n```json\n"
        + json.dumps(approved, ensure_ascii=False, separators=(",", ":"))
        + "\n```\n"
    ).encode("utf-8")
    path.write_bytes(data)
    git(repo, "add", str(path.relative_to(repo)))
    if mixed:
        (repo / "unexpected.txt").write_text("scope drift\n", encoding="utf-8")
        git(repo, "add", "unexpected.txt")
    git(repo, "commit", "-m", "governance: correct exact Plan metadata")
    return f"{path.relative_to(repo).as_posix()}@{git(repo, 'rev-parse', 'HEAD')}#{hashlib.sha256(data).hexdigest()}"


def test_exact_plan_amendment_reuses_pending_callback_and_evidence(tmp_path: Path) -> None:
    repo, _, initial, callback, _ = fixture(tmp_path)
    pending_before = initial["complex_context"]["pending_callback"].copy()
    plan_ref = corrected_plan(repo, initial)

    result = invoke_personal(
        repo, "amend-plan", "--expected-board-sha256", board_hash(repo), "--task-id", TASK_ID,
        "--plan-ref", plan_ref, "--approval-ref", "user:exact-plan-repair-approved",
        "--callback-json", json.dumps(callback, separators=(",", ":")),
    )

    assert result["code"] == "ALLOW_PLAN_AMEND"
    _, board, _ = parse_board((repo / "docs/task_board.md").read_bytes())
    current = board["active"]
    assert current["plan_ref"] == plan_ref
    assert current["complex_context"]["pending_callback"] == pending_before
    assert current["complex_context"]["plan_amendments"][-1]["evidence_ref"] == callback["evidence"]
    assert git(repo, "diff", "--name-only") == "docs/task_board.md"

    git(repo, "add", "docs/task_board.md")
    git(repo, "commit", "-m", "governance: bind exact Plan amendment")
    consumed = invoke_personal(
        repo, "consume-callback", "--expected-board-sha256", board_hash(repo), "--task-id", TASK_ID,
        "--callback-json", json.dumps(callback, separators=(",", ":")),
    )
    assert consumed["code"] == "ALLOW_CONSUME_CALLBACK"


def test_plan_amendment_rejects_a_code_mixed_plan_commit_without_board_write(tmp_path: Path) -> None:
    repo, _, initial, callback, _ = fixture(tmp_path)
    plan_ref = corrected_plan(repo, initial, mixed=True)
    before = (repo / "docs/task_board.md").read_bytes()

    result = invoke_personal(
        repo, "amend-plan", "--expected-board-sha256", board_hash(repo), "--task-id", TASK_ID,
        "--plan-ref", plan_ref, "--approval-ref", "user:exact-plan-repair-approved",
        "--callback-json", json.dumps(callback, separators=(",", ":")), expected_exit=2,
    )

    assert result["code"] == "BLOCKED_PLAN_INVALID"
    assert (repo / "docs/task_board.md").read_bytes() == before


def test_plan_amendment_cannot_change_the_legacy_approved_route(tmp_path: Path) -> None:
    repo, _, initial, callback, _ = fixture(tmp_path)
    plan_ref = corrected_plan(repo, initial, route="gpt-5.6-sol / high / risk:authority")
    before = (repo / "docs/task_board.md").read_bytes()

    result = invoke_personal(
        repo, "amend-plan", "--expected-board-sha256", board_hash(repo), "--task-id", TASK_ID,
        "--plan-ref", plan_ref, "--approval-ref", "user:exact-plan-repair-approved",
        "--callback-json", json.dumps(callback, separators=(",", ":")), expected_exit=2,
    )

    assert result["code"] == "BLOCKED_PLAN_INVALID"
    assert (repo / "docs/task_board.md").read_bytes() == before
