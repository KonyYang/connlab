#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path
from typing import Any

from scripts.connlab_serial_board import (
    BOARD_REL, Blocked, approved_payload, blocker_payload, committed_board, git_dirty, now,
    parse_board, request_payload, resolve_primary, run_git, sha, validation_payload, v2_activate_next,
    v2_submit, write_board, writer_lock,
)
from scripts.connlab_serial_complex import SerialContractError, classification_result, complex_transition

COMPLEX_COMMANDS = ("begin-role", "record-invocation", "consume-callback", "begin-host", "record-host", "record-integration", "request-close", "record-closeout", "finalize-close")
COMMANDS = ("inspect", "check", "classify", "submit", "activate-next", "approve", "mark-review", "block", "resume", "cancel", "close", *COMPLEX_COMMANDS, "plan-cutover", "apply-cutover", "verify-cutover-commit")
RESULT_FIELDS = ("schema", "version", "code", "allowed", "changed", "command", "task_id", "state", "active_task_id", "queue_position", "board_sha256_before", "board_sha256_after", "primary_root", "reason")

def result(code: str, command: str, root: Path | None, before: str | None, after: str | None, control: dict[str, Any] | None, *, task_id: str | None = None, changed: bool = False, reason: str = "") -> dict[str, Any]:
    active = control.get("active") if control else None
    queue_position = None
    if control and task_id:
        for position, item in enumerate(control.get("queue", []), 1):
            if item.get("task_id") == task_id:
                queue_position = position
                break
    return dict(zip(RESULT_FIELDS, (
        "connlab.personal-task-result", 1, code, not code.startswith("BLOCKED_"), changed,
        command, task_id, control.get("state") if control else None,
        active.get("task_id") if isinstance(active, dict) else None, queue_position, before, after,
        str(root) if root else None, reason,
    )))
def require_active(control: dict[str, Any], task_id: str) -> dict[str, Any]:
    active = control.get("active")
    if not isinstance(active, dict) or active.get("task_id") != task_id:
        raise Blocked("BLOCKED_TASK_MISMATCH", "The requested task is not active.")
    return active
def active_from_request(request: dict[str, Any], scope: dict[str, Any] | None, head: str) -> dict[str, Any]:
    timestamp = now()
    return {
        "task_id": request["task_id"], "summary": request["summary"], "kind": request["kind"],
        "phase": "implementation" if request["kind"] == "simple" else "planning",
        "scope_contract": scope, "plan_ref": None, "approval_ref": None,
        "activation_parent_sha": head, "activated_at": timestamp, "updated_at": timestamp,
        "blocker": None, "validation": None,
    }
def transition(args: argparse.Namespace, root: Path, control: dict[str, Any]) -> tuple[str, bool, str]:
    command, task_id = args.command, args.task_id
    active = control.get("active")
    if control.get("version") == 2 and command in {"submit", "activate-next"}:
        request = json.loads(args.request_json or "")
        action = v2_submit if command == "submit" else v2_activate_next
        code, reason = action(control, request, run_git(root, "rev-parse", "HEAD").stdout.strip())
        return code, not code.startswith(("NOOP_", "QUEUED_EXISTING")), reason
    if command in COMPLEX_COMMANDS:
        if control.get("version") != 2: raise Blocked("BLOCKED_LEGACY_MODE_FROZEN", "Complex commands remain dormant before cutover.")
        active = require_active(control, task_id)
        raw = {"role": args.role, "native_action": json.loads(args.native_action_json or "null"), "invocation": json.loads(args.invocation_json or "null"), "callback": json.loads(args.callback_json or "null"), "worktree": json.loads(args.worktree_json or "null"), "integration": json.loads(args.integration_json or "null"), "closeout": json.loads(args.closeout_json or "null"), "decision_ref": args.decision_ref}
        complex_transition(active, command, raw)
        if active.pop("_release_active", False): control["last_closed"] = {"task_id": task_id, "disposition": "complex closeout complete", "decision_ref": args.decision_ref, "closed_at": now()}; control["active"] = None; control["state"] = "idle"
        elif active["phase"] == "human_review": control["state"] = "implemented_pending_human_review"
        else: control["state"] = "running"
        return "ALLOW_" + command.replace("-", "_").upper(), True, "Durable complex transition recorded."
    if command in {"plan-cutover", "apply-cutover", "verify-cutover-commit"}: raise Blocked("BLOCKED_CUTOVER_NOT_AUTHORIZED", "Cutover requires the exact second User approval.")
    if command == "submit":
        request, scope = request_payload(args.request_json, task_id)
        if isinstance(active, dict) and active.get("task_id") == task_id:
            return "NOOP_ALREADY_ACTIVE", False, "Task is already active."
        for item in control["queue"]:
            if item["task_id"] == task_id:
                return "QUEUED_EXISTING", False, "Task is already queued."
        if control["state"] == "idle" and not control["queue"]:
            if git_dirty(root):
                raise Blocked("BLOCKED_WORKTREE_DIRTY", "A clean primary worktree is required for activation.")
            head = run_git(root, "rev-parse", "HEAD").stdout.strip()
            control["active"] = active_from_request(request, scope, head)
            control["state"] = "running"
            return "ALLOW_ACTIVATE", True, "Task activated."
        sequence = control["next_enqueue_sequence"]
        control["queue"].append({
            "task_id": task_id, "summary": request["summary"], "kind": request["kind"],
            "enqueue_sequence": sequence, "queued_at": now(), "scope_contract": scope,
        })
        control["next_enqueue_sequence"] = sequence + 1
        return "QUEUED_NEW", True, "Task appended to FIFO queue."
    if command == "activate-next":
        if control["state"] != "idle":
            raise Blocked("BLOCKED_STATE", "Board must be idle before activating the queue head.")
        if not control["queue"]:
            return "NOOP_QUEUE_EMPTY", False, "FIFO queue is empty."
        if control["queue"][0]["task_id"] != task_id:
            raise Blocked("BLOCKED_FIFO_ORDER", "Only the exact FIFO head may activate.")
        if git_dirty(root):
            raise Blocked("BLOCKED_WORKTREE_DIRTY", "A clean primary worktree is required for activation.")
        item = control["queue"].pop(0)
        request = {"task_id": item["task_id"], "summary": item["summary"], "kind": item["kind"]}
        control["active"] = active_from_request(request, item["scope_contract"], run_git(root, "rev-parse", "HEAD").stdout.strip())
        control["state"] = "running"
        return "ALLOW_ACTIVATE_NEXT", True, "FIFO head activated."
    active = require_active(control, task_id)
    if command == "approve":
        if active["kind"] != "planned":
            raise Blocked("BLOCKED_STATE", "Only a planned task can be approved.")
        if active["phase"] == "implementation" and active["approval_ref"]:
            return "NOOP_ALREADY_APPROVED", False, "Task is already approved."
        blocked_reapproval = active["phase"] == "blocked" and isinstance(active.get("blocker"), dict) and isinstance(active.get("scope_contract"), dict)
        if active["phase"] != "planning" and not blocked_reapproval:
            raise Blocked("BLOCKED_STATE", "Planned task is not in planning phase.")
        if not committed_board(root):
            raise Blocked("BLOCKED_TRANSITION_UNCOMMITTED", "The preceding board transition must be committed first.")
        approved, scope = approved_payload(args.approved_request_json, task_id)
        if not args.plan_ref:
            raise Blocked("BLOCKED_PLAN_REQUIRED", "A committed plan reference is required.")
        if not re.fullmatch(r".+@[0-9a-f]{40}#[0-9a-f]{64}", args.plan_ref):
            raise Blocked("BLOCKED_PLAN_REQUIRED", "Plan reference format is invalid.")
        if not args.approval_ref:
            raise Blocked("BLOCKED_APPROVAL_REQUIRED", "Explicit User approval is required.")
        if blocked_reapproval:
            previous = active["scope_contract"]; old_paths, new_paths = set(previous["may_touch"]), set(scope["may_touch"])
            if scope == previous:
                active.update(summary=approved["summary"], plan_ref=args.plan_ref, approval_ref=args.approval_ref, updated_at=now())
                return "ALLOW_APPROVAL_EVIDENCE_CORRECTION", True, "Approval evidence corrected; blocker remains until explicit resume."
            if active["blocker"].get("code") != "SCOPE_EXPANDED": raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "Only a scope-expansion blocker permits path changes.")
            if not old_paths < new_paths: raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment must be a strict path superset.")
            if scope["forbidden_categories"] != previous["forbidden_categories"]: raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment cannot change risk-category facts.")
            active.update(summary=approved["summary"], scope_contract=scope, plan_ref=args.plan_ref, approval_ref=args.approval_ref, updated_at=now())
            return "ALLOW_SCOPE_AMEND", True, "User-approved scope expansion recorded; blocker remains until explicit resume."
        active.update(summary=approved["summary"], scope_contract=scope, plan_ref=args.plan_ref, approval_ref=args.approval_ref, phase="implementation", updated_at=now())
        return "ALLOW_APPROVE", True, "Approved scope bound to active task."
    if command == "mark-review":
        if control["state"] == "implemented_pending_human_review":
            return "NOOP_ALREADY_PENDING_REVIEW", False, "Task already awaits human review."
        if active["phase"] != "implementation" or active["blocker"] is not None or active["scope_contract"] is None:
            raise Blocked("BLOCKED_STATE", "Task is not eligible for human review.")
        value = validation_payload(args.validation_json, require_pass=True)
        allowed = set(active["scope_contract"]["may_touch"])
        unexpected = set(value["observed_paths"]) - allowed
        if unexpected:
            raise Blocked("BLOCKED_UNEXPECTED_PATHS", "Validation reports paths outside approved scope.")
        active.update(phase="human_review", validation=value, updated_at=now())
        control["state"] = "implemented_pending_human_review"
        return "ALLOW_MARK_REVIEW", True, "Implementation awaits human review."
    if command == "block":
        value = blocker_payload(args.blocker_json)
        if active["blocker"] == value and active["phase"] == "blocked":
            return "NOOP_ALREADY_BLOCKED", False, "Identical blocker is already recorded."
        active.update(blocker=value, phase="blocked", updated_at=now())
        control["state"] = "running"
        return "ALLOW_BLOCK", True, "Blocker recorded; active slot retained."
    if command == "resume":
        if active["phase"] != "blocked" or active["blocker"] is None:
            raise Blocked("BLOCKED_STATE", "Task is not blocked.")
        if not args.decision_ref:
            raise Blocked("BLOCKED_STATE", "Explicit User decision reference is required.")
        active.update(blocker=None, phase="implementation" if active["scope_contract"] else "planning", updated_at=now())
        return "ALLOW_RESUME", True, "Blocker cleared by explicit User direction."
    if command in {"cancel", "close"}:
        if git_dirty(root):
            raise Blocked("BLOCKED_WORKTREE_DIRTY", "A clean primary worktree is required.")
        if not args.decision_ref:
            raise Blocked("BLOCKED_STATE", "Explicit User decision reference is required.")
        if command == "close":
            if control["state"] != "implemented_pending_human_review" or active["phase"] != "human_review" or not active["validation"] or active["validation"].get("status") != "passed":
                raise Blocked("BLOCKED_STATE", "Only a validated task awaiting human review can close.")
            code, disposition = "ALLOW_CLOSE", "closed after human review"
        else:
            if not args.disposition:
                raise Blocked("BLOCKED_STATE", "Cancellation disposition is required.")
            code, disposition = "ALLOW_CANCEL", args.disposition
        control["last_closed"] = {"task_id": task_id, "disposition": disposition, "decision_ref": args.decision_ref, "closed_at": now()}
        control["active"] = None
        control["state"] = "idle"
        return code, True, disposition
    raise Blocked("BLOCKED_STATE", "Unsupported transition.")
def check(args: argparse.Namespace, root: Path, control: dict[str, Any]) -> tuple[str, str]:
    if args.intent == "Inspect":
        return "ALLOW_INSPECT", "Personal serial board is readable."
    active = require_active(control, args.task_id)
    if args.intent == "Implementation":
        if active["phase"] == "planning":
            raise Blocked("BLOCKED_APPROVAL_REQUIRED", "Planned task requires approved scope.")
        if active["phase"] != "implementation" or active["blocker"] is not None or control["state"] != "running":
            raise Blocked("BLOCKED_STATE", "Task is not eligible for implementation.")
        return "ALLOW_IMPLEMENTATION", "Active task may be implemented."
    if control["state"] != "implemented_pending_human_review" or active["phase"] != "human_review":
        raise Blocked("BLOCKED_STATE", "Task is not eligible to close.")
    if git_dirty(root):
        raise Blocked("BLOCKED_WORKTREE_DIRTY", "Primary worktree must be clean to close.")
    return "ALLOW_CLOSE", "Task is eligible to close after explicit User direction."
def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("command", choices=COMMANDS)
    value.add_argument("--repo-root", required=True)
    value.add_argument("--json", action="store_true")
    for name in ("expected-board-sha256", "task-id", "request-json", "approved-request-json", "plan-ref", "approval-ref", "validation-json", "blocker-json", "decision-ref", "disposition", "role", "native-action-json", "native-action-id", "invocation-json", "callback-json", "worktree-json", "integration-json", "closeout-json", "cutover-manifest-ref", "expected-primary-head", "closeout-order", "cutover-commit", "permission-preflight-json"): value.add_argument(f"--{name}")
    value.add_argument("--intent", choices=("Inspect", "Implementation", "Close", "Cutover"))
    return value
def validate_argument_combination(args: argparse.Namespace) -> None:
    names = {"expected_board_sha256", "task_id", "request_json", "approved_request_json", "plan_ref", "approval_ref", "validation_json", "blocker_json", "decision_ref", "disposition", "intent", "role", "native_action_json", "native_action_id", "invocation_json", "callback_json", "worktree_json", "integration_json", "closeout_json", "cutover_manifest_ref", "expected_primary_head", "closeout_order", "cutover_commit", "permission_preflight_json"}
    allowed = {"inspect": set(), "check": {"task_id", "intent"}, "classify": {"request_json"}, "submit": {"expected_board_sha256", "task_id", "request_json"}, "activate-next": {"expected_board_sha256", "task_id", "request_json"}, "approve": {"expected_board_sha256", "task_id", "approved_request_json", "plan_ref", "approval_ref"}, "mark-review": {"expected_board_sha256", "task_id", "validation_json"}, "block": {"expected_board_sha256", "task_id", "blocker_json"}, "resume": {"expected_board_sha256", "task_id", "decision_ref"}, "cancel": {"expected_board_sha256", "task_id", "decision_ref", "disposition"}, "close": {"expected_board_sha256", "task_id", "decision_ref"}, "begin-role": {"expected_board_sha256", "task_id", "role", "native_action_json"}, "record-invocation": {"expected_board_sha256", "task_id", "role", "native_action_id", "invocation_json"}, "consume-callback": {"expected_board_sha256", "task_id", "callback_json"}, "begin-host": {"expected_board_sha256", "task_id", "native_action_json"}, "record-host": {"expected_board_sha256", "task_id", "native_action_id", "worktree_json"}, "record-integration": {"expected_board_sha256", "task_id", "integration_json"}, "request-close": {"expected_board_sha256", "task_id", "decision_ref"}, "record-closeout": {"expected_board_sha256", "task_id", "closeout_json"}, "finalize-close": {"expected_board_sha256", "task_id", "decision_ref"}, "plan-cutover": {"task_id", "expected_primary_head", "closeout_order"}, "apply-cutover": {"expected_board_sha256", "task_id", "cutover_manifest_ref", "expected_primary_head", "approval_ref"}, "verify-cutover-commit": {"task_id", "cutover_manifest_ref", "cutover_commit", "approval_ref"}}[args.command]
    if {name for name in names if getattr(args, name) is not None} - allowed: raise Blocked("BLOCKED_ARGUMENT_COMBINATION", "Arguments are incompatible with the selected command.")
def main() -> int:
    args = parser().parse_args()
    root: Path | None = None
    control: dict[str, Any] | None = None
    before: str | None = None
    try:
        validate_argument_combination(args)
        root = resolve_primary(args.repo_root)
        board = root / BOARD_REL
        data = board.read_bytes()
        before = sha(data)
        prefix, control, suffix = parse_board(data)
        if args.command == "classify":
            output = classification_result(json.loads(args.request_json or ""), command=args.command, primary_root=str(root), primary_head=run_git(root, "rev-parse", "HEAD").stdout.strip(), board_sha256=before)
        elif args.command == "inspect":
            output = result("ALLOW_INSPECT", args.command, root, before, before, control, reason=f"Git dirty paths: {len(git_dirty(root))}.")
        elif args.command == "check":
            if not args.intent or (args.intent != "Inspect" and not args.task_id):
                raise Blocked("BLOCKED_STATE", "Check intent/task arguments are incomplete.")
            code, reason = check(args, root, control)
            output = result(code, args.command, root, before, before, control, task_id=args.task_id, reason=reason)
        else:
            if not args.task_id or not re.fullmatch(r"[A-Z][A-Z0-9_\-]+", args.task_id):
                raise Blocked("BLOCKED_TASK_MISMATCH", "A valid task ID is required.")
            if not args.expected_board_sha256 or not re.fullmatch(r"[0-9a-f]{64}", args.expected_board_sha256):
                raise Blocked("BLOCKED_BOARD_HASH_MISMATCH", "Expected board SHA-256 is required.")
            with writer_lock(root):
                data = board.read_bytes()
                before = sha(data)
                prefix, control, suffix = parse_board(data)
                if before != args.expected_board_sha256:
                    raise Blocked("BLOCKED_BOARD_HASH_MISMATCH", "Board changed since caller inspection.")
                code, changed, reason = transition(args, root, control)
                after = write_board(root, board, prefix, control, suffix) if changed else before
            output = result(code, args.command, root, before, after, control, task_id=args.task_id, changed=changed, reason=reason)
    except (Blocked, SerialContractError, OSError, json.JSONDecodeError) as exc:
        blocked = exc if isinstance(exc, Blocked) else Blocked(getattr(exc, "code", "BLOCKED_CLASSIFICATION_INVALID"), str(exc))
        output = result(blocked.code, args.command, root, before, before, control, task_id=getattr(args, "task_id", None), reason=blocked.reason)
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")) if args.json else "\n".join(f"{key}: {value}" for key, value in output.items()))
    return 2 if output["code"].startswith("BLOCKED_") else 0
if __name__ == "__main__": sys.exit(main())
