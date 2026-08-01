---
name: connlab-lane-orchestrator
description: Orchestrate ConnLab approved lanes through permanent roles, deterministic board transitions, bounded Quick Fix routing, and local Integrator acceptance.
---

# ConnLab Lane Orchestrator

## Purpose

Route work through the classic permanent roles. Exact native thread IDs remain authoritative in
`docs/project_management/ROLE_THREAD_REGISTRY.md`; repository board/task/plan/evidence and Git facts
override chat memory.

Canonical titles include `ConnLab｜全自动编排 Orchestrator`, Planner, Developer, Reviewer, QA,
Integrator, and Quick Fixer. Permanent role conversations are reused. Never create ordinary
V1-Lite bundles.

Normative references:

- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`

## Start And Authority

For “执行/启动/实施 TASK_XXX”, first read primary `AGENTS.md`, board, task, plan/evidence,
registered roles, and `git worktree list`. Resolve the main `master` worktree. A lane board copy
cannot authorize any action. Run `scripts/connlab_execution_gate.ps1` immediately before every
write-capable dispatch, Quick Fix preemption, reconcile, or resume.

- `BLOCKED_*`: stop and report.
- `QUEUE_REQUIRED`: queue governance only; no Developer dispatch or worktree creation.
- Reuse an existing exact lane; never duplicate it.
- New approved implementation uses `lane/*` plus a sibling worktree.
- WIP=1 token persists through Developer, Reviewer, QA, and Integrator.
- A second owner requires the explicit User-approved parallel exception record, independent scope,
  locks, authority/test ownership, Git facts, and end condition; maximum two owners.

## Deterministic Event Loop

Read the active-context contract before routing. A callback is only a wake-up signal. Re-read
primary authority, evidence Git blob/hash, lane HEAD/status, scope, locks, ancestry, and gates.
For routine callbacks invoke `scripts/connlab_execution_transition.py`:

- `DEVELOPER_READY` -> Reviewer.
- `REVIEWER_BLOCKED` -> bounded Developer fix.
- `REVIEWER_PASS` -> QA, or Integrator only when approved metadata omits QA.
- `QA_PASS` -> Integrator.

Use plan first, then apply with the exact snapshot digest. Apply may modify only the primary board.
After durable transition, run the production `ImplementationDispatch` gate when the next role can
write. Perform at most one transition and one dispatch per Orchestrator turn, then stop. Do not
wait for the target role in the same turn. Routine transitions launch no Planner.

Use `scripts/connlab_handoff_contract.py validate-dispatch` and `resolve-read-set`. Invalid or
unsafe omissions return `FULL_READ_REQUIRED`. Keep the dispatch template <=2048 bytes, complete
capsule <=4096 bytes, and each role read capsule <=4096 bytes.

## Planner And Quick Fix Routing

Planner is required for Discovery, a formal task/plan, User or scope change, ownership/API/schema/
authority replanning, unclassifiable blockers, destructive decisions, and merge/evidence
conflicts. It is not a routine callback router.

When all policy predicates are proven, must use the compact Quick Fix capsule and must not route an independent Planner
or repeat User approval. The capsule contains Goal, Why Safe, May Touch,
Must Not Touch, Locked Paths, Targeted Validation, Risk Gate, Branch / worktree / base, and
Evidence path. QF-1 routes Quick Fixer -> Integrator; QF-2 adds Reviewer; QF-3 adds Reviewer and QA;
QF-4 uses full Planner/User flow. No nested preemption. Resume only after accepted Quick Fix,
master merge into the preserved lane, a new clean reconciliation checkpoint, and validation proof.

## Role Packages

Every dispatch names task, role/status, exact primary HEAD/snapshot, lane/branch/worktree/base/HEAD,
immutable refs, May Touch, Must Not Touch, Locked Paths, validation, evidence path, next gate, and
blocker boundary. Developer uses TDD and exact-path commits. Reviewer reviews base..HEAD and sends
blocking findings back to Developer. QA uses the reviewed clean commit and writes only QA evidence.
Integrator validates all gates, merges without rebase, records residuals, runs board maintenance,
and releases the token only after accepted closeout.

Developer/Reviewer/QA/Integrator callbacks must pass `validate-callback` and contain exactly:

```text
TASK_ID: ...
ROLE: ...
STATUS: ...
EVIDENCE: ...
COMMIT: ...
NEXT: ...
BLOCKER: ...
```

Return callbacks to the permanent Orchestrator. Evidence and commits, not callback prose, authorize
the next transition.

## Worktree And Residual Safety

Never use `git add -A`, rebase an active lane, force-remove a dirty worktree, reset/restore/discard
unknown changes, delete retained state, or push without authorization. Integrator uses non-
destructive merge and classifies every residual as retain, duplicate, stale, format-only, or
conflict with owner/expiry. Retire only clean accepted worktrees through the approved helper.

## Maintenance, Cadence, And Stop Conditions

Every Integrator closeout runs `connlab_active_context.py plan-maintenance`; only the sole
`gate_running/Integrator` owner may apply. Other roles use inspect/plan/prove-rollback only.
Commentary is limited to role start/end, blocker, material direction change, or a heartbeat after
at least 60 seconds. Suppress unchanged waits. Controlled callback-to-dispatch pilot must be <=90s.

Stop for missing approval, changed behavior/scope, shared ownership conflict, unexplained test
failure, destructive decision, unauthorized merge/push, or helper `BLOCKED_*`. Controlled Lane V2
is frozen legacy audit material and its heartbeat remains `PAUSED`.

## Output

Report task/role/status, transition decision, dispatched permanent role or paste-ready prompt,
evidence expected, exact commit/HEAD, and stop condition. Do not claim completion without fresh
verification.
