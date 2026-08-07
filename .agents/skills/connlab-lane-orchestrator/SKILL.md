---
name: connlab-lane-orchestrator
description: Run ConnLab's active personal-serial complex workflow from plan through automatic Developer, Reviewer, QA, and Integrator handoffs.
---

# ConnLab Personal Serial Orchestrator

Status: active version-2 runtime.

Use this skill when the User submits, approves, resumes, inspects or closes a ConnLab complex task.
Read `AGENTS.md`, `docs/task_board.md`, the active Task/Plan and relevant evidence first. The board's
version-2 control block and Git facts override conversation memory.

## User contract

A normal complex task has only three User interactions:

1. requirement submission;
2. Planner-plan approval;
3. completed-result inspection and `关闭`.

Do not request routine approvals for host creation, Developer -> Reviewer -> QA -> Integrator, an approved
bounded fix, non-conflicting local integration, or retained closeout. Return to the User only for a
scope/behavior/authority change, a destructive action, or an unresolved blocker.

## Event loop

Perform one durable state transition at a time with `scripts/connlab_personal_task.py`, using the
fresh expected board SHA-256. Exact-stage and locally commit each authority transition before the
next write-capable action. Never use chat text as a substitute for board state.

```text
idle -> submit/classify
planning -> fresh read-only Planner -> awaiting_user_approval
User approval commit -> create one task branch/worktree host
development -> Developer
review -> Reviewer
qa -> QA
integration -> Integrator -> verified primary integration
human_review -> User
User 关闭 -> retained closeout -> idle
```

Planner runs before the host and cannot write. After approval, Developer, Reviewer, QA and Integrator
run sequentially in the same isolated task host. Spawn only the role required by the current durable
phase, record its native action and returned identity, wait for its exact callback, validate the
subject/evidence, then consume it. Reviewer or QA blocking findings route back to Developer without
new approval when the fix remains inside approved scope.

## Safety

WIP is one. When a task is active, a new submission returns `BLOCKED_ACTIVE_TASK_RUNNING` immediately
after board parsing, before Git verification, lock acquisition, request parsing or classification;
the User submits it again after close. Reuse an already-recorded
host and never create a duplicate. Do not push, rebase, force-remove, restore, reset, stash, discard,
delete a branch, archive or retire resources automatically. Stop and record a typed blocker on
unprovable identity/evidence, dirty/divergent state, conflict, scope expansion, destructive work or
repeated failure.

Integrator must bind the accepted Developer subject, Reviewer and QA evidence, and the exact clean
host HEAD before the runtime performs the approved local integration. The completed task remains
`implemented_pending_human_review` until the User says `关闭`. Closeout retains clean task/thread/
worktree/branch/HEAD/evidence references; lifecycle cleanup is outside the daily gate.

The first ordinary complex task is a monitored first real run, not a pilot or governance project.
If it fails, keep it active with its blocker and report the exact stopping fact.
