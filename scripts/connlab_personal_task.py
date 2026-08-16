#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
from typing import Any

SCRIPT_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if not sys.path or Path(sys.path[0]).resolve() != SCRIPT_REPOSITORY_ROOT:
    sys.path.insert(0, str(SCRIPT_REPOSITORY_ROOT))

from scripts.connlab_serial_board import (
    BOARD_REL, Blocked, approved_payload, blocker_payload, committed_board, git_dirty, now,
    parse_board, request_payload, resolve_primary, run_git, sha, validation_payload, v2_submit,
    write_board, writer_lock,
)
from scripts.connlab_serial_complex import SerialContractError, classification_result, complex_transition, validate_complex_blocker, validate_integration_transition
from scripts.connlab_serial_phase2 import (
    BOUNDED_FIX_CODES, COMMAND_ARGUMENTS, active_snapshot, apply_bounded_fix_reentry,
    apply_scope_amendment, command_contract, next_action, verify_transition_repository,
)
from scripts.connlab_serial_evidence_topology import (
    validate_approved_plan,
    verify_callback_evidence_topology,
    verify_integration_evidence_topology,
)

COMPLEX_COMMANDS = ("begin-role", "record-invocation", "consume-callback", "begin-host", "record-host", "record-integration", "request-close", "record-closeout", "finalize-close", "reenter-development")
COMMANDS = ("inspect", "check", "classify", "submit", "activate-next", "approve", "mark-review", "block", "resume", "cancel", "close", *COMPLEX_COMMANDS)
RESULT_FIELDS = ("schema", "version", "code", "allowed", "changed", "command", "task_id", "state", "active_task_id", "queue_position", "board_sha256_before", "board_sha256_after", "primary_root", "reason", "active_snapshot", "next_action")
ROLE_CALLBACKS = {"Developer", "Reviewer", "QA", "Integrator"}
CALLBACK_EVIDENCE_PATTERN = re.compile(
    r"(docs/lane_evidence/[A-Za-z0-9_./-]+)@([0-9a-f]{40})#([0-9a-f]{40}|[0-9a-f]{64})"
)

def result(code: str, command: str, root: Path | None, before: str | None, after: str | None, control: dict[str, Any] | None, *, task_id: str | None = None, changed: bool = False, reason: str = "", primary_head: str | None = None) -> dict[str, Any]:
    active = control.get("active") if control else None
    queue_position = None
    if control and task_id:
        for position, item in enumerate(control.get("queue", []), 1):
            if item.get("task_id") == task_id:
                queue_position = position
                break
    action = next_action(control)
    action["command_contract"] = command_contract(action["command"])
    return dict(zip(RESULT_FIELDS, (
        "connlab.personal-task-result", 1, code, not code.startswith("BLOCKED_"), changed,
        command, task_id, control.get("state") if control else None,
        active.get("task_id") if isinstance(active, dict) else None, queue_position, before, after,
        str(root) if root else None, reason, active_snapshot(control, primary_head), action,
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
def verify_evidence_ref(root: Path, value: Any) -> None:
    match = re.fullmatch(r"(docs/lane_evidence/[A-Za-z0-9_./-]+)@([0-9a-f]{40})#([0-9a-f]{64})", str(value))
    if not match or ".." in Path(match.group(1)).parts:
        raise Blocked("BLOCKED_EVIDENCE_INVALID", "Evidence ref is invalid.")
    evidence = subprocess.run(["git", "-C", str(root), "show", f"{match.group(2)}:{match.group(1)}"], capture_output=True, check=False)
    if evidence.returncode != 0 or hashlib.sha256(evidence.stdout).hexdigest() != match.group(3):
        raise Blocked("BLOCKED_EVIDENCE_INVALID", "Evidence is not committed at the exact byte hash.")
def canonical_callback_evidence(root: Path, value: Any) -> tuple[str, bool]:
    match = CALLBACK_EVIDENCE_PATTERN.fullmatch(str(value))
    if not match or ".." in Path(match.group(1)).parts:
        raise Blocked("BLOCKED_CALLBACK_INVALID", "Callback evidence reference is invalid.")
    evidence = subprocess.run(
        ["git", "-C", str(root), "show", f"{match.group(2)}:{match.group(1)}"],
        capture_output=True,
        check=False,
    )
    if evidence.returncode != 0:
        raise Blocked("BLOCKED_CALLBACK_INVALID", "Callback evidence is not committed at the supplied commit and path.")
    digest = hashlib.sha256(evidence.stdout).hexdigest()
    supplied_digest = match.group(3)
    if len(supplied_digest) == 64 and supplied_digest != digest:
        raise Blocked("BLOCKED_CALLBACK_INVALID", "Callback evidence SHA-256 does not match the committed bytes.")
    canonical = f"{match.group(1)}@{match.group(2)}#{digest}"
    return canonical, canonical != value
def canonicalize_role_callback_evidence(root: Path, value: Any) -> tuple[Any, bool]:
    if not isinstance(value, dict) or value.get("role") not in ROLE_CALLBACKS:
        return value, False
    callback = dict(value)
    callback["evidence"], corrected = canonical_callback_evidence(root, callback.get("evidence"))
    blocker = callback.get("blocker")
    if isinstance(blocker, dict) and blocker.get("evidence_ref") is not None:
        blocker = dict(blocker)
        blocker["evidence_ref"], blocker_corrected = canonical_callback_evidence(root, blocker["evidence_ref"])
        callback["blocker"] = blocker
        corrected = corrected or blocker_corrected
    return callback, corrected
def verify_integration_repository(root: Path, active: dict[str, Any], value: dict[str, Any]) -> None:
    if not committed_board(root):
        raise Blocked("BLOCKED_TRANSITION_UNCOMMITTED", "The integration-ready board transition must be committed first.")
    context = active["complex_context"]
    if git_dirty(root):
        raise Blocked("BLOCKED_WORKTREE_FACTS", "Primary must be clean before integration is recorded.")
    head = run_git(root, "rev-parse", "HEAD")
    parents = run_git(root, "rev-list", "--parents", "-n", "1", value["merge_commit"])
    tree = run_git(root, "rev-parse", f"{value['merge_commit']}^{{tree}}")
    if (
        head.returncode != 0
        or head.stdout.strip() != value["merge_commit"]
        or parents.returncode != 0
        or parents.stdout.strip().split() != [value["merge_commit"], *value["parents"]]
        or tree.returncode != 0
        or tree.stdout.strip() != value["merge_tree"]
    ):
        raise Blocked("BLOCKED_INTEGRATION_PROOF", "Primary merge commit, parents or tree do not match Git.")
    worktree = Path(context["task_worktree"]).resolve()
    records = run_git(root, "worktree", "list", "--porcelain").stdout.strip().split("\n\n")
    record = next((item for item in records if item.splitlines() and Path(item.splitlines()[0][9:]).resolve() == worktree), None)
    lines = set(record.splitlines()) if record else set()
    if (
        not record
        or f"HEAD {value['branch_head']}" not in lines
        or f"branch refs/heads/{context['task_branch']}" not in lines
        or run_git(worktree, "rev-parse", "HEAD").stdout.strip() != value["branch_head"]
        or bool(run_git(worktree, "status", "--porcelain=v1", "--untracked-files=all").stdout)
    ):
        raise Blocked("BLOCKED_WORKTREE_FACTS", "Task worktree branch, HEAD or clean state does not match Git.")
    if run_git(root, "merge-base", "--is-ancestor", value["subject_commit"], value["merge_commit"]).returncode != 0:
        raise Blocked("BLOCKED_INTEGRATION_PROOF", "The reviewed subject is not integrated.")
    if value["evidence_refs"] != context.get("evidence_refs"):
        raise Blocked("BLOCKED_INTEGRATION_PROOF", "Integration evidence differs from accepted role evidence.")
    for evidence_ref in value["evidence_refs"]:
        verify_evidence_ref(root, evidence_ref)
def verify_retained_repository(root: Path, active: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    context = active.get("complex_context")
    if not isinstance(context, dict) or context.get("pending_callback") is not None or context.get("current_role") is not None:
        raise Blocked("BLOCKED_CALLBACK_PENDING", "A role or callback is still active.")
    expected = (active.get("task_id"), context.get("host_thread_id"), context.get("task_worktree"), context.get("task_branch"), context.get("head_sha"), context.get("integrated_commit"))
    actual = tuple(value.get(key) for key in ("task_id", "thread_id", "worktree", "branch", "head_sha", "integrated_commit"))
    if expected != actual or value.get("clean") is not True or context.get("worktree_lifecycle") not in {"integrated", "retained"}:
        raise Blocked("BLOCKED_WORKTREE_FACTS", "Retained worktree identity or clean integration facts drifted.")
    worktree = Path(value["worktree"]).resolve()
    records = run_git(root, "worktree", "list", "--porcelain").stdout.strip().split("\n\n")
    record = next((item for item in records if item.splitlines() and Path(item.splitlines()[0][9:]).resolve() == worktree), None)
    lines = set(record.splitlines()) if record else set()
    if not record or f"HEAD {value['head_sha']}" not in lines or f"branch refs/heads/{value['branch']}" not in lines:
        raise Blocked("BLOCKED_WORKTREE_FACTS", "Registered worktree branch or HEAD drifted.")
    if run_git(worktree, "status", "--porcelain=v1").stdout:
        raise Blocked("BLOCKED_WORKTREE_FACTS", "Retained worktree is not clean.")
    if run_git(root, "merge-base", "--is-ancestor", value["head_sha"], value["integrated_commit"]).returncode != 0:
        raise Blocked("BLOCKED_INTEGRATION_PROOF", "Retained worktree HEAD is not integrated.")
    verify_evidence_ref(root, value.get("evidence_ref"))
    return value
def atomic_complex_closeout(root: Path, active: dict[str, Any], decision_ref: str) -> dict[str, Any]:
    if not decision_ref:
        raise Blocked("BLOCKED_STATE", "Explicit User decision reference is required.")
    if active.get("phase") != "human_review":
        raise Blocked("BLOCKED_STATE", "Complex task is not awaiting human review.")
    if not committed_board(root):
        raise Blocked("BLOCKED_TRANSITION_UNCOMMITTED", "The human-review board transition must be committed first.")
    if git_dirty(root):
        raise Blocked("BLOCKED_WORKTREE_DIRTY", "Primary must be clean before close.")
    context = active.get("complex_context")
    evidence_refs = context.get("evidence_refs") if isinstance(context, dict) else None
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise Blocked("BLOCKED_EVIDENCE_INVALID", "Accepted Integrator evidence is missing.")
    retained = {
        "task_id": active["task_id"],
        "thread_id": context.get("host_thread_id"),
        "worktree": context.get("task_worktree"),
        "branch": context.get("task_branch"),
        "head_sha": context.get("head_sha"),
        "clean": True,
        "integrated_commit": context.get("integrated_commit"),
        "evidence_ref": evidence_refs[-1],
    }
    verify_retained_repository(root, active, retained)
    return {
        "task_id": active["task_id"],
        "disposition": "retained",
        "decision_ref": decision_ref,
        "integration_commit": retained["integrated_commit"],
        "integrator_evidence_ref": retained["evidence_ref"],
        "retained_resources": {
            "thread_id": retained["thread_id"],
            "worktree": retained["worktree"],
            "branch": retained["branch"],
            "head_sha": retained["head_sha"],
        },
        "closed_at": now(),
    }
def transition(args: argparse.Namespace, root: Path, control: dict[str, Any]) -> tuple[str, bool, str]:
    command, task_id = args.command, args.task_id
    active = control.get("active")
    if control.get("version") == 2 and command == "submit":
        if control.get("state") != "idle" or control.get("active") is not None:
            raise Blocked("BLOCKED_ACTIVE_TASK_RUNNING", "Another task is active; submit again after it is closed.")
        head = run_git(root, "rev-parse", "HEAD").stdout.strip()
        code, reason = v2_submit(control, json.loads(args.request_json or ""), head)
        return code, not code.startswith(("NOOP_", "QUEUED_EXISTING")), reason
    if control.get("version") == 2 and command == "activate-next":
        raise Blocked("BLOCKED_LEGACY_MODE_FROZEN", "Version-2 daily workflow does not queue tasks; submit again after close.")
    if command in COMPLEX_COMMANDS:
        if control.get("version") != 2: raise Blocked("BLOCKED_LEGACY_MODE_FROZEN", "Complex commands remain dormant before cutover.")
        active = require_active(control, task_id)
        callback = json.loads(args.callback_json or "null")
        callback, evidence_corrected = canonicalize_role_callback_evidence(root, callback) if command == "consume-callback" else (callback, False)
        raw = {"role": args.role, "native_action": json.loads(args.native_action_json or "null"), "invocation": json.loads(args.invocation_json or "null"), "callback": callback, "worktree": json.loads(args.worktree_json or "null"), "integration": json.loads(args.integration_json or "null"), "closeout": json.loads(args.closeout_json or "null"), "decision_ref": args.decision_ref}
        if command == "reenter-development":
            verify_transition_repository(root, active, require_host=True)
            apply_bounded_fix_reentry(active, raw["native_action"], args.decision_ref, now())
            control["state"] = "running"
            return "ALLOW_REENTER_DEVELOPMENT", True, "Approved same-scope bounded fix resumed as the next Developer attempt."
        if command == "consume-callback":
            verify_callback_evidence_topology(root, active, callback)
        if command == "record-integration":
            validate_integration_transition(active, raw["integration"])
            verify_integration_evidence_topology(root, active, raw["integration"])
            verify_integration_repository(root, active, raw["integration"])
        transition_code = complex_transition(active, command, raw)
        if command == "record-closeout": verify_retained_repository(root, active, raw["closeout"])
        if transition_code.startswith("NOOP_"): return transition_code, False, "Exact retained closeout is already recorded."
        if active.pop("_release_active", False):
            closeout = active["complex_context"]["closeout_disposition"]
            control["last_closed"] = {"task_id": task_id, "disposition": "retained", "decision_ref": args.decision_ref, "closeout_evidence_ref": closeout["evidence_ref"], "retained_resources": {key: closeout[key] for key in ("thread_id", "worktree", "branch", "head_sha")}, "closed_at": now()}; control["active"] = None; control["state"] = "idle"
        elif active["phase"] == "human_review": control["state"] = "implemented_pending_human_review"
        else: control["state"] = "running"
        reason = "Durable complex transition recorded."
        if evidence_corrected:
            reason = "Durable complex transition recorded; committed evidence SHA-256 was corrected from the supplied digest."
        return transition_code, True, reason
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
        is_v2_complex = control.get("version") == 2 and isinstance(active.get("complex_context"), dict)
        if active["kind"] != "planned":
            raise Blocked("BLOCKED_STATE", "Only a planned task can be approved.")
        if active["phase"] in {"implementation", "development"} and active["approval_ref"]:
            return "NOOP_ALREADY_APPROVED", False, "Task is already approved."
        blocked_reapproval = active["phase"] == "blocked" and isinstance(active.get("blocker"), dict) and isinstance(active.get("scope_contract"), dict)
        expected_phase = "awaiting_user_approval" if is_v2_complex else "planning"
        if active["phase"] != expected_phase and not blocked_reapproval:
            raise Blocked("BLOCKED_STATE", f"Planned task is not in {expected_phase} phase.")
        if not committed_board(root):
            raise Blocked("BLOCKED_TRANSITION_UNCOMMITTED", "The preceding board transition must be committed first.")
        approved, scope = approved_payload(args.approved_request_json, task_id)
        if not args.plan_ref:
            raise Blocked("BLOCKED_PLAN_REQUIRED", "A committed plan reference is required.")
        if not re.fullmatch(r".+@[0-9a-f]{40}#[0-9a-f]{64}", args.plan_ref):
            raise Blocked("BLOCKED_PLAN_REQUIRED", "Plan reference format is invalid.")
        if not args.approval_ref:
            raise Blocked("BLOCKED_APPROVAL_REQUIRED", "Explicit User approval is required.")
        approved_routes = None
        if is_v2_complex and not blocked_reapproval:
            approved_routes = validate_approved_plan(root, args.plan_ref, approved)
        if blocked_reapproval:
            previous = active["scope_contract"]; old_paths, new_paths = set(previous["may_touch"]), set(scope["may_touch"])
            if scope == previous:
                active.update(summary=approved["summary"], plan_ref=args.plan_ref, approval_ref=args.approval_ref, updated_at=now())
                return "ALLOW_APPROVAL_EVIDENCE_CORRECTION", True, "Approval evidence corrected; blocker remains until explicit resume."
            if active["blocker"].get("code") != "SCOPE_EXPANDED": raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "Only a scope-expansion blocker permits path changes.")
            if not old_paths < new_paths: raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment must be a strict path superset.")
            if scope["forbidden_categories"] != previous["forbidden_categories"]: raise Blocked("BLOCKED_APPROVED_SCOPE_INVALID", "A scope amendment cannot change risk-category facts.")
            if is_v2_complex:
                verify_transition_repository(root, active, require_host=bool(active["complex_context"].get("host_id")))
                apply_scope_amendment(active, approved, scope, args.plan_ref, args.approval_ref, now())
                return "ALLOW_SCOPE_AMEND", True, "User-approved scope amendment atomically resumed development."
            active.update(summary=approved["summary"], scope_contract=scope, plan_ref=args.plan_ref, approval_ref=args.approval_ref, updated_at=now())
            return "ALLOW_SCOPE_AMEND", True, "User-approved scope expansion recorded; blocker remains until explicit resume."
        target_phase = "development" if is_v2_complex else "implementation"
        active.update(summary=approved["summary"], scope_contract=scope, plan_ref=args.plan_ref, approval_ref=args.approval_ref, phase=target_phase, updated_at=now())
        if is_v2_complex:
            active["complex_context"]["approved_code_paths"] = scope["may_touch"]
            active["complex_context"]["execution_routes"] = {
                role: {"model": route[0], "reasoning_effort": route[1], "reason": route[2]}
                for role, route in approved_routes.items()
            }
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
        if control.get("version") == 2 and isinstance(active.get("complex_context"), dict):
            value = validate_complex_blocker(json.loads(args.blocker_json or ""))
            if value["stage"] != active["phase"]:
                raise Blocked("BLOCKED_BLOCKER_INVALID", "Complex blocker stage must match the active phase.")
        else:
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
        blocker = active["blocker"]
        if isinstance(active.get("complex_context"), dict) and blocker.get("schema") == "connlab.serial-task-blocker":
            if blocker.get("code") in BOUNDED_FIX_CODES:
                raise Blocked("BLOCKED_STATE", "Bounded-fix blockers require the atomic reenter-development transition.")
            resume_phase = validate_complex_blocker(blocker)["resume_phase"]
        else:
            resume_phase = "implementation" if active["scope_contract"] else "planning"
        active.update(blocker=None, phase=resume_phase, updated_at=now())
        return "ALLOW_RESUME", True, "Blocker cleared by explicit User direction."
    if command == "close" and control.get("version") == 2 and isinstance(active.get("complex_context"), dict):
        control["last_closed"] = atomic_complex_closeout(root, active, args.decision_ref)
        control["active"] = None
        control["state"] = "idle"
        return "ALLOW_CLOSE", True, "Complex task closed atomically with retained Git and Integrator evidence facts."
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
    for name in ("expected-board-sha256", "task-id", "request-json", "approved-request-json", "plan-ref", "approval-ref", "validation-json", "blocker-json", "decision-ref", "disposition", "role", "native-action-json", "native-action-id", "invocation-json", "callback-json", "worktree-json", "integration-json", "closeout-json"): value.add_argument(f"--{name}")
    value.add_argument("--intent", choices=("Inspect", "Implementation", "Close"))
    return value
def validate_argument_combination(args: argparse.Namespace) -> None:
    names = {"expected_board_sha256", "task_id", "request_json", "approved_request_json", "plan_ref", "approval_ref", "validation_json", "blocker_json", "decision_ref", "disposition", "intent", "role", "native_action_json", "native_action_id", "invocation_json", "callback_json", "worktree_json", "integration_json", "closeout_json"}
    allowed = COMMAND_ARGUMENTS[args.command]
    if {name for name in names if getattr(args, name) is not None} - allowed: raise Blocked("BLOCKED_ARGUMENT_COMBINATION", "Arguments are incompatible with the selected command.")
def pre_git_busy_submit(args: argparse.Namespace) -> tuple[Path, dict[str, Any], str] | None:
    if args.command != "submit":
        return None
    root = Path(args.repo_root).resolve()
    data = (root / BOARD_REL).read_bytes()
    _, control, _ = parse_board(data)
    if control.get("version") == 2 and (
        control.get("state") != "idle" or control.get("active") is not None
    ):
        return root, control, sha(data)
    return None
def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parser().parse_args()
    root: Path | None = None
    control: dict[str, Any] | None = None
    before: str | None = None
    primary_head: str | None = None
    try:
        validate_argument_combination(args)
        busy = pre_git_busy_submit(args)
        if busy is not None:
            root, control, before = busy
            output = result(
                "BLOCKED_ACTIVE_TASK_RUNNING", args.command, root, before, before, control,
                task_id=args.task_id, reason="Another task is active; submit again after it is closed.",
            )
            print(json.dumps(output, ensure_ascii=False, separators=(",", ":")) if args.json else "\n".join(f"{key}: {value}" for key, value in output.items()))
            return 2
        root = resolve_primary(args.repo_root)
        primary_head = run_git(root, "rev-parse", "HEAD").stdout.strip()
        board = root / BOARD_REL
        data = board.read_bytes()
        before = sha(data)
        prefix, control, suffix = parse_board(data)
        if args.command == "classify":
            output = classification_result(json.loads(args.request_json or ""), command=args.command, primary_root=str(root), primary_head=primary_head, board_sha256=before)
        elif args.command == "inspect":
            output = result("ALLOW_INSPECT", args.command, root, before, before, control, reason=f"Git dirty paths: {len(git_dirty(root))}.", primary_head=primary_head)
        elif args.command == "check":
            if not args.intent or (args.intent != "Inspect" and not args.task_id):
                raise Blocked("BLOCKED_STATE", "Check intent/task arguments are incomplete.")
            code, reason = check(args, root, control)
            output = result(code, args.command, root, before, before, control, task_id=args.task_id, reason=reason, primary_head=primary_head)
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
            output = result(code, args.command, root, before, after, control, task_id=args.task_id, changed=changed, reason=reason, primary_head=primary_head)
    except (Blocked, SerialContractError, OSError, json.JSONDecodeError) as exc:
        blocked = exc if isinstance(exc, Blocked) else Blocked(getattr(exc, "code", "BLOCKED_CLASSIFICATION_INVALID"), str(exc))
        output = result(blocked.code, args.command, root, before, before, control, task_id=getattr(args, "task_id", None), reason=blocked.reason, primary_head=primary_head)
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")) if args.json else "\n".join(f"{key}: {value}" for key, value in output.items()))
    return 2 if output["code"].startswith("BLOCKED_") else 0
if __name__ == "__main__": sys.exit(main())
