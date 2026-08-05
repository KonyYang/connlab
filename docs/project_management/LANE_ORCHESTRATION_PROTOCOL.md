# ConnLab Lane Orchestration Protocol — Frozen Legacy

> Status: frozen legacy audit reference since 2026-08-06. It cannot authorize dispatch, lane/worktree creation, reconciliation, or state changes. Daily execution uses `scripts/connlab_personal_task.py` and `connlab.personal-serial-control`.

Status: active classic permanent-role protocol. Normative WIP/Quick Fix rules are in
`EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`; deterministic transitions, active context, maintenance,
handoff, budgets, and cadence are in
`ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`.

## 1. Roles And Authority

The permanent Orchestrator is the only daily router. It reuses each permanent role: Planner, Developer,
Reviewer, QA, Integrator, and Quick Fixer in `ROLE_THREAD_REGISTRY.md`. Permanent role
conversations are not archived as task lifecycle steps. Permanent role conversations are not archived.
The primary `docs/task_board.md`
execution-control JSON is sole machine authority. Task, approved plan, role evidence, and Git facts
outrank callback text and conversation memory.

The main `master` worktree is planning/integration authority. Product and tests-only implementation
uses one `lane/*` branch in one sibling worktree. WIP=1 is serial by default; explicit User-approved
parallel exception is the only second-owner route and is capped at two owners.

## 2. Start

On an execute-task command, read primary AGENTS, board, task, plan/evidence, registry, and worktree
list. Run `connlab_execution_gate.ps1 -Intent StartTask`. Queue decisions never create a worktree or
dispatch implementation. Reuse an exact existing lane. For a newly approved lane, record branch,
worktree, base, HEAD, locks, gates, and evidence before `CreateWorktree` and
`ImplementationDispatch` gates.

Missing approval or Definition of Ready returns to Planner/User. Quick Fix uses the compact capsule
only when every 19.1 predicate is proven; QF-4 and any authority/API/schema/persistence change use
the full flow.

## 3. Durable State And Routine Events

The token remains owned through implementation and all gates. Exactly four mechanical events are
supported:

```text
DEVELOPER_READY  implementation_running/Developer + ready_for_review
                 -> gate_running/Reviewer
REVIEWER_BLOCKED gate_running/Reviewer + reviewer_blocked
                 -> implementation_running/Developer
REVIEWER_PASS    gate_running/Reviewer + reviewer_pass
                 -> gate_running/QA, or Integrator only when required_gates omits QA
QA_PASS          gate_running/QA + qa_pass
                 -> gate_running/Integrator
```

The Orchestrator runs transition inspect/plan/apply against primary authority. The helper validates
state/role/token/task/lane, expected primary and lane HEAD, evidence `path@commit#sha256`, ancestry,
clean worktrees/index, changed paths, locks, queue/pause/Quick Fix/parallel facts, gate metadata,
markers, and summary agreement. Apply changes only the board. Same transition is idempotent;
divergent duplicate blocks.

Each Orchestrator turn performs at most one transition plus one dispatch and then stops. There is
no same-turn waiting. A callback wakes routing but never authorizes it. Routine events do not launch
Planner.

## 4. Role Gates

- Developer implements only May Touch, TDD-first, verifies proportionately, creates exact-path
  implementation/evidence commits, and leaves lane/index clean.
- Reviewer reads base..HEAD, checks scope and behavior, and records pass or blocking findings. A
  blocking result durably transitions back to Developer before a fix dispatch.
- QA validates the reviewed clean commit in an isolated environment, writes only QA evidence, and
  never fixes product code.
- Integrator verifies Reviewer/QA ancestry, exact package, tests, board facts, residual ledger, and
  non-destructive merge. Never rebase an active lane.

Evidence is committed and role-owned. A callback contains exactly seven ordered non-empty fields:
TASK_ID, ROLE, STATUS, EVIDENCE, COMMIT, NEXT, BLOCKER. `validate-callback` enforces <=1024 bytes.

## 5. Reference-Only Dispatch

`connlab_handoff_contract.py` verifies dispatch capsules and resolves minimal read sets. Required
refs are board, current task, approved plan, current-role evidence, and declared direct
dependencies. Invalid refs or unsafe omissions yield `FULL_READ_REQUIRED`; unrelated immutable
archive changes alone do not. Budgets: template <=2048 bytes, full capsule <=4096, per-role read
capsule <=4096.

Standard package fields are task/role/status, primary HEAD/snapshot, branch/worktree/base/lane HEAD,
refs, May Touch/Must Not Touch/Locked Paths, validation, evidence, next gate, and blocker boundary.
The target role independently revalidates them.

## 6. Board Maintenance

Every Integrator closeout runs `connlab_active_context.py plan-maintenance` before token release.
Maintenance triggers above 400 lines, 65536 bytes, or 24 terminal details. First generation archives
exact board bytes; later generations archive the oldest eligible terminal detail needed for all
budgets. Index and archives are immutable/hash chained and rollback-proven.

Only a clean sole `gate_running/Integrator` owner with all required gates, exact HEAD/hash, accepted
helper ancestry, empty queue, and null pause/Quick Fix/parallel state may apply. Planner, Developer,
Reviewer, terminal auditors, and token-null state are inspect/plan/prove-only. Archive conflict,
corrupt index, partial failure, or path escape blocks and preserves prior bytes.

## 7. Worktrees, Reconciliation, And Residuals

Use `connlab_lane_worktree.ps1` for authorized Create/Inspect/Retire. Never Create/Retire a real
existing lane during tests. Quick Fix preemption requires a clean preserved checkpoint and disjoint
locks. Reconciliation merges current master into the preserved original lane without rebase,
commits a new checkpoint, validates it, then resumes through the gate.

Integrator classifies residuals as retain, duplicate, stale, format-only, or conflict and records
owner/expiry. No force removal, destructive cleanup, reset/restore/discard, unknown deletion, or
unauthorized push is allowed.

## 8. Cadence And Failure

Commentary occurs only at role start/end, blocker, material direction change, or heartbeat after at
least 60 seconds. Suppress unchanged waits. The measured controlled callback-to-dispatch pilot is
<=90 seconds. `validate-cadence` enforces at most one transition and one dispatch.

Stop and return to Planner/User for scope/product-contract changes, missing approval, shared
ownership conflict, unexplained failures, destructive decisions, merge/evidence conflict, or any
fail-closed helper result. Ordinary retryable Reviewer/QA findings return to Developer.

## 9. Frozen Compatibility

V1-Lite bundles and Controlled Lane V2 are historical audit modes. Controlled Lane V2 heartbeat
heartbeat remains `PAUSED`; no bootstrap, scan, CAS, pilot, migration, or corrective may resume without a new
approved task. Historical `dispatch_ack` and `mark-invocation-started` vocabulary remains reference
only and never authorizes classic execution.
