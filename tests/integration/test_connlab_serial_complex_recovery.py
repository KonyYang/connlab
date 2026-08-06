from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.connlab_serial_board import migrate_v1_to_v2, parse_board, render_board


ROOT = Path(__file__).resolve().parents[2]


def test_cutover_migration_preserves_fifo_history_and_closes_active_atomically() -> None:
    prefix, current, suffix = parse_board((ROOT / "docs/task_board.md").read_bytes())
    source = copy.deepcopy(current)
    source["state"] = "implemented_pending_human_review"
    source["active"]["phase"] = "human_review"
    source["active"]["blocker"] = None
    source["active"]["validation"] = {
        "schema": "connlab.personal-task-validation",
        "version": 1,
        "status": "passed",
        "checks": [{"command": "bounded", "exit_code": 0, "summary": "passed"}],
        "observed_paths": source["active"]["scope_contract"]["may_touch"],
        "manual_checks": [],
        "recorded_at": "2026-08-06T00:00:00Z",
    }
    retained = copy.deepcopy(source["retained_history"])
    queue = copy.deepcopy(source["queue"])
    migrated = migrate_v1_to_v2(
        source,
        decision_ref="User approved exact cutover manifest",
        closed_at="2026-08-06T00:00:01Z",
    )

    assert migrated["version"] == 2
    assert migrated["state"] == "idle"
    assert migrated["active"] is None
    assert migrated["queue"] == queue
    assert migrated["retained_history"] == retained
    assert migrated["last_closed"]["task_id"] == source["active"]["task_id"]

    encoded = render_board(prefix, migrated, suffix)
    _, recovered, _ = parse_board(encoded)
    assert json.loads(json.dumps(recovered)) == migrated


def test_v2_complex_active_survives_byte_round_trip_without_conversation_memory() -> None:
    prefix, current, suffix = parse_board((ROOT / "docs/task_board.md").read_bytes())
    migrated = migrate_v1_to_v2(
        {**copy.deepcopy(current), "state": "implemented_pending_human_review", "active": {
            **copy.deepcopy(current["active"]),
            "phase": "human_review",
            "blocker": None,
            "validation": {
                "schema": "connlab.personal-task-validation", "version": 1, "status": "passed",
                "checks": [{"command": "bounded", "exit_code": 0, "summary": "passed"}],
                "observed_paths": current["active"]["scope_contract"]["may_touch"],
                "manual_checks": [], "recorded_at": "2026-08-06T00:00:00Z",
            },
        }},
        decision_ref="cutover",
        closed_at="2026-08-06T00:00:01Z",
    )
    migrated["state"] = "running"
    migrated["active"] = {
        "task_id": "TASK_RECOVERY",
        "summary": "recover entirely from durable refs",
        "kind": "planned",
        "classification": "complex",
        "phase": "review",
        "scope_contract": {"may_touch": ["backend/example.py"]},
        "plan_ref": "tasks/plan.md@" + "1" * 40 + "#" + "2" * 64,
        "approval_ref": "User approval",
        "activation_parent_sha": "3" * 40,
        "activated_at": "2026-08-06T00:00:00Z",
        "updated_at": "2026-08-06T00:00:02Z",
        "blocker": None,
        "validation": None,
        "complex_context": {
            "workflow_version": 1,
            "task_branch": "codex/task-recovery",
            "task_worktree": "D:/tmp/task-recovery",
            "base_sha": "3" * 40,
            "head_sha": "4" * 40,
            "integration_target": "master",
            "worktree_lifecycle": "ready",
            "current_role": "Reviewer",
            "current_attempt": 1,
            "role_invocations": [],
            "host_thread_id": "thread-1",
            "host_id": "host-1",
            "approved_code_paths": ["backend/example.py"],
            "required_gates": ["Reviewer", "QA", "Integrator"],
            "developer_subject_commit": "4" * 40,
            "reviewer_subject_commit": None,
            "qa_subject_commit": None,
            "integrated_commit": None,
            "evidence_refs": [],
            "pending_callback": None,
            "archive_target_ids": ["thread-1"],
            "archived_ids": [],
            "archive_attempts": [],
            "close_decision_ref": None,
            "probe_approved_closeout_order": "retire_then_archive",
        },
    }

    _, recovered, _ = parse_board(render_board(prefix, migrated, suffix))
    assert recovered == migrated
    assert "conversation" not in json.dumps(recovered).lower()
