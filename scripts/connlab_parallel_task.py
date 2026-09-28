"""Two isolated task slots; persistence and locking stay in the existing board writer."""
from __future__ import annotations

import json
from pathlib import Path

import connlab_sol_task as w


def deny(code: str, reason: str) -> None:
    raise w.Blocked(code, reason)


def git(root: Path, *args: str) -> str:
    outcome = w.run_git(root, *args)
    if outcome.returncode:
        deny("BLOCKED_GIT_INVALID", outcome.stderr.strip() or "Git operation failed.")
    return outcome.stdout.strip()


def validate_control(value: dict) -> None:
    fields = {"schema", "version", "mode", "wip_limit", "tasks", "last_closed", "retained_history"}
    if (set(value) != fields or value["schema"] != w.CONTROL_SCHEMA or value["version"] != 2
            or value["mode"] != "sol_native" or value["wip_limit"] != 2
            or not isinstance(value["tasks"], dict) or len(value["tasks"]) > 2
            or not isinstance(value["retained_history"], list)):
        deny("BLOCKED_BOARD_INVALID", "Invalid two-slot board.")
    slots, roots, branches = set(), set(), set()
    for identity, entry in value["tasks"].items():
        if (not isinstance(entry, dict) or set(entry) != {"slot", "state", "worktree", "branch", "resources", "task", "integrated_head"}
                or entry["slot"] not in {"main", "micro"} or entry["slot"] in slots
                or not isinstance(entry["worktree"], str) or not Path(entry["worktree"]).is_absolute()
                or entry["worktree"].casefold() in roots or not isinstance(entry["branch"], str)
                or not entry["branch"] or entry["branch"] in branches
                or (entry["integrated_head"] is not None and
                    (not isinstance(entry["integrated_head"], str) or len(entry["integrated_head"]) != 40))
                or not isinstance(entry["resources"], list)
                or any(not isinstance(item, str) or not item for item in entry["resources"])):
            deny("BLOCKED_BOARD_INVALID", "Invalid or duplicate task host/slot.")
        legacy = dict(schema=w.CONTROL_SCHEMA, version=1, mode="sol_native", wip_limit=1,
                      state=entry["state"], active=entry["task"], last_closed=None, retained_history=[])
        w.validate_control(legacy)
        if (not isinstance(entry["task"], dict) or entry["task"]["task_id"] != identity
                or (entry["slot"] == "micro" and entry["task"]["tier"] != "micro")):
            deny("BLOCKED_BOARD_INVALID", "Task identity or micro tier is invalid.")
        slots.add(entry["slot"])
        roots.add(entry["worktree"].casefold())
        branches.add(entry["branch"])


def result(code, command, root, control, before, after, *, task_id=None, changed=False, reason=""):
    snapshots = {}
    for identity, entry in control["tasks"].items():
        view = {"active": entry["task"], "state": entry["state"]}
        snapshots[identity] = dict(w.active_snapshot(view), slot=entry["slot"], state=entry["state"],
                                   worktree=entry["worktree"], next_action=w.next_action(view))
    selected = snapshots.get(task_id)
    return dict(schema="connlab.sol-task-result", version=2, code=code,
                allowed=not code.startswith("BLOCKED_"), changed=changed, command=command,
                task_id=task_id, primary_root=str(root), board_sha256_before=before,
                board_sha256_after=after, state="running" if snapshots else "idle",
                active_task_id=task_id if selected else None, active_snapshot=selected,
                active_tasks=snapshots, reason=reason,
                next_action=selected["next_action"] if selected else {"command": "select_task" if snapshots else "submit", "requires_user": False})


def normalized_paths(paths: list[str]) -> list[str]:
    normalized = [w.repository_path(path, code="BLOCKED_REQUEST_INVALID").casefold().rstrip("/") for path in paths]
    if not normalized or any(path in {"", "."} or ":" in path or any(c in path for c in "*?[") for path in normalized):
        deny("BLOCKED_REQUEST_INVALID", "Parallel tasks require concrete relative file/directory scopes.")
    return normalized


def overlaps(first: list[str], second: list[str]) -> bool:
    return any(a == b or a.startswith(b + "/") or b.startswith(a + "/") for a in first for b in second)


def host(root: Path, entry: dict) -> Path:
    tree = Path(entry["worktree"]).resolve()
    if (tree == root or Path(git(tree, "rev-parse", "--show-toplevel")).resolve() != tree
            or w.primary_root(tree) != root
            or git(tree, "branch", "--show-current") != entry["branch"]):
        deny("BLOCKED_HOST_IDENTITY", "Task must keep its registered independent worktree and branch.")
    return tree


def activate(args, root: Path, control: dict, task_id: str) -> None:
    payload = w.request_payload(args.request_json, task_id)
    slot = args.slot or ("main" if not control["tasks"] else "micro")
    if task_id in control["tasks"] or len(control["tasks"]) >= 2 or any(e["slot"] == slot for e in control["tasks"].values()):
        deny("BLOCKED_WIP_LIMIT", "Only one main and one micro task may be active.")
    if slot == "micro" and payload["tier"] != "micro":
        deny("BLOCKED_TIER_UNSAFE", "The secondary slot accepts only micro tasks.")
    paths = normalized_paths(payload["scope_paths"])
    if overlaps(paths, [w.BOARD_REL.as_posix()]):
        deny("BLOCKED_SCOPE_OVERLAP", "Task branches must not edit the shared board.")
    try:
        resources = json.loads(args.resources_json)
    except (ValueError, TypeError):
        deny("BLOCKED_REQUEST_INVALID", "Resources must be a JSON array.")
    if not isinstance(resources, list) or any(not isinstance(r, str) or not r.strip() for r in resources):
        deny("BLOCKED_REQUEST_INVALID", "Resources must be named shared write targets.")
    resources = sorted(set(r.strip().casefold() for r in resources))
    for peer in control["tasks"].values():
        if overlaps(paths, normalized_paths(peer["task"]["scope_paths"])):
            deny("BLOCKED_SCOPE_OVERLAP", "Scope overlaps the other active task.")
        if set(resources) & set(peer["resources"]):
            deny("BLOCKED_RESOURCE_OVERLAP", "Shared write resources must be exclusive.")
    if not args.worktree_root:
        deny("BLOCKED_HOST_REQUIRED", "Parallel-capable tasks require an independent worktree.")
    tree = Path(args.worktree_root).resolve()
    branch = git(tree, "branch", "--show-current")
    entry = dict(slot=slot, state="running", worktree=str(tree), branch=branch, resources=resources, integrated_head=None)
    host(root, entry)
    if not branch or branch == "master" or any(e["worktree"].casefold() == str(tree).casefold() or e["branch"] == branch for e in control["tasks"].values()):
        deny("BLOCKED_HOST_IDENTITY", "Each task needs a distinct named non-master branch/worktree.")
    w.require_clean(tree, "Task worktree must be clean at activation.")
    if w.current_head(tree) != w.current_head(root):
        deny("BLOCKED_BASE_STALE", "Start the task from current primary HEAD.")
    entry["task"] = w.activated_task(payload, w.current_head(tree), w.utc_now())
    control["tasks"][task_id] = entry


def finish(args, root: Path, entry: dict) -> None:
    if entry["state"] != "running":
        deny("BLOCKED_STATE", "Only a running task can finish.")
    payload = w.report_payload(args.result_json, args.task_id, pending_integration=True)
    task = entry["task"]
    tree = host(root, entry)
    w.require_clean(tree, "Validate and commit the exact task worktree before finishing.")
    w.require_clean(root, "Primary must be clean before serial integration.")
    subject = w.current_head(tree)
    if payload["subject"] != subject:
        deny("BLOCKED_SUBJECT_MISMATCH", "Validation report does not describe the current task HEAD.")
    if any(not isinstance(payload["roles"].get(role), dict) or payload["roles"][role].get("status") != "passed"
           for role in w.REQUIRED_ROLES[task["tier"]]):
        deny("BLOCKED_REPORT_INCOMPLETE", "Report lacks the task tier's review/validation results.")
    if w.run_git(root, "merge-base", "--is-ancestor", task["activation_head"], subject).returncode:
        deny("BLOCKED_HOST_IDENTITY", "Task history no longer contains its activation commit.")
    head = w.current_head(root)
    message = f"integrate({args.task_id}): {subject}"
    parents = git(root, "show", "-s", "--format=%P", head).split()
    # A crash after merge but before board replacement must record that same merge, not repeat it.
    recovered = (len(parents) == 2 and parents[1] == subject
                 and git(root, "show", "-s", "--format=%s", head) == message
                 and not w.changed_paths(root, subject, head))
    primary_before = parents[0] if recovered else head
    base = git(root, "merge-base", primary_before, subject)
    if w.changed_paths(root, base, primary_before):
        deny("BLOCKED_REVALIDATION_REQUIRED", "Primary code changed: merge master into task, review and rerun affected validation.")
    changed = w.changed_paths(root, base, subject)
    if sorted(payload["changed_paths"]) != changed:
        deny("BLOCKED_SCOPE_DRIFT", "Report paths must match this task's exact diff, excluding peer work.")
    scopes = normalized_paths(task["scope_paths"])
    if any(not any(p.casefold() == s or p.casefold().startswith(s + "/") for s in scopes) for p in changed):
        deny("BLOCKED_SCOPE_DRIFT", "Task exceeds reserved paths; amend scope after checking peer overlap.")
    if git(root, "diff", "--name-only", base, subject, "--", w.BOARD_REL.as_posix()):
        deny("BLOCKED_SCOPE_DRIFT", "Task worktree must not edit the central board.")
    if not recovered:
        outcome = w.run_git(root, "merge", "--no-ff", "--no-edit", "-m", message, subject)
        if outcome.returncode:
            deny("BLOCKED_INTEGRATION", "Integration stopped; preserve and inspect Git state. " + outcome.stderr.strip())
    w.require_clean(root, "Integration left unexpected changes; inspect without retrying.")
    integrated = w.current_head(root)
    if w.run_git(root, "merge-base", "--is-ancestor", subject, integrated).returncode or w.changed_paths(root, subject, integrated):
        deny("BLOCKED_INTEGRATION", "Integrated code differs from validated task code.")
    payload["integration"] = dict(status="passed", mode="serial_local_merge", subject=subject,
                                   primary_before=primary_before, integrated_head=integrated, recovered=recovered)
    task["report"] = payload
    task["updated_at"] = w.utc_now()
    entry["integrated_head"] = integrated
    entry["state"] = "ready_for_close"


def close(args, root: Path, control: dict, entry: dict) -> None:
    decision = w.required_decision_ref(args.decision_ref, "Explicit User close or cancel decision is required.")
    if args.disposition != "cancelled" and entry["state"] != "ready_for_close":
        deny("BLOCKED_STATE", "Complete integration before closing normally.")
    w.require_clean(root, "Commit pending board checkpoints before closing.")
    if entry["integrated_head"] and w.run_git(root, "merge-base", "--is-ancestor", entry["integrated_head"], w.current_head(root)).returncode:
        deny("BLOCKED_INTEGRATION", "Recorded integration is not in master history.")
    if control["last_closed"]:
        control["retained_history"].append(control["last_closed"])
    control["last_closed"] = w.closed_task(entry["task"], disposition=args.disposition,
        decision_ref=decision, fallback_subject=w.current_head(root), timestamp=w.utc_now())
    del control["tasks"][args.task_id]


def transition(args, root: Path):
    def mutate(control):
        if git(root, "branch", "--show-current") != "master":
            deny("BLOCKED_BRANCH", "Shared board authority must be on primary master.")
        if control["version"] == 1:
            if args.command != "submit" or control["state"] != "idle":
                deny("BLOCKED_ACTIVE_TASK_RUNNING", "Close the legacy task before enabling parallel slots.")
            control.update(version=2, wip_limit=2, tasks={})
            del control["state"], control["active"]
        if args.command == "submit":
            w.require_clean(root, "Commit the primary board checkpoint before activation.")
            activate(args, root, control, args.task_id)
            return
        entry = control["tasks"].get(args.task_id)
        if not entry:
            deny("BLOCKED_TASK_MISMATCH", "Requested task is not active.")
        if args.command == "checkpoint":
            if entry["state"] != "running":
                deny("BLOCKED_STATE", "Only running tasks accept checkpoints.")
            entry["task"]["checkpoint"] = w.checkpoint_payload(args.checkpoint_json, args.task_id)
            entry["task"]["updated_at"] = w.utc_now()
            return
        if args.command == "finish":
            finish(args, root, entry)
        elif args.command == "revise":
            feedback = w.required_decision_ref(args.decision_ref, "User feedback is required.")
            if entry["state"] != "ready_for_close":
                deny("BLOCKED_STATE", "Only delivered tasks can be revised.")
            entry["state"] = "running"
            entry["task"]["report"] = None
            entry["task"]["updated_at"] = w.utc_now()
            entry["task"]["checkpoint"] = dict(schema=w.CHECKPOINT_SCHEMA, version=1, task_id=args.task_id,
                stage="revision", status="running", summary=feedback, requires_user=False)
        elif args.command in {"close", "close-and-submit"}:
            close(args, root, control, entry)
            if args.command == "close-and-submit":
                activate(args, root, control, args.next_task_id)
        elif args.command == "amend-scope":
            amend_scope(args, root, control, entry)
        else:
            deny("BLOCKED_COMMAND_UNSUPPORTED", "Unsupported parallel task transition.")
    # The board and master belong to the coordinator, never to either working branch.
    # Commit while holding the same lock so two callers cannot mix their checkpoints.
    with w.board_lock(root):
        w.require_clean(root, "Primary has uncommitted work/checkpoint; resolve it before the next transition.")
        outcome = w.update_board(root, args.expected_board_sha256, mutate)
        from connlab_task_close import commit_board
        commit_board(root, f"task({args.task_id}): {args.command}")
        return outcome


def amend_scope(args, root: Path, control: dict, entry: dict) -> None:
    if entry["state"] != "running":
        deny("BLOCKED_STATE", "Only running task scopes may be adjusted.")
    payload = w.scope_amendment_payload(args.request_json, args.task_id)
    paths = normalized_paths(payload["scope_paths"])
    if overlaps(paths, [w.BOARD_REL.as_posix()]):
        deny("BLOCKED_SCOPE_OVERLAP", "The central board is not a task scope.")
    for identity, peer in control["tasks"].items():
        if identity != args.task_id and overlaps(paths, normalized_paths(peer["task"]["scope_paths"])):
            deny("BLOCKED_SCOPE_OVERLAP", "Scope adjustment overlaps the other task.")
    if entry["task"]["tier"] == "high_risk":
        w.required_decision_ref(args.decision_ref, "High-risk scope changes require explicit User approval.")
        tree = host(root, entry)
        w.require_clean(tree, "High-risk scope correction requires a clean task worktree.")
        base = git(root, "merge-base", w.current_head(root), w.current_head(tree))
        if payload["scope_paths"] != w.changed_paths(root, base, w.current_head(tree)):
            deny("BLOCKED_SCOPE_DRIFT", "High-risk scope correction must match exact committed changes.")
    entry["task"]["scope_paths"] = payload["scope_paths"]
    entry["task"]["updated_at"] = w.utc_now()
