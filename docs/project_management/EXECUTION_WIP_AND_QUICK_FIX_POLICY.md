# ConnLab Execution WIP And Proportionate Quick Fix Policy

Last Updated: 2026-07-31
Status: normative execution policy
Scope: all normal ConnLab implementation routing; Controlled Lane V2 remains frozen legacy

## 1. Single Authority

`docs/task_board.md` is the sole business execution authority. Its one uniquely
marker-delimited JSON block is the machine-readable view of the same authority, not a second
state file. Human-readable board prose and lane rows must agree with that block. A role callback,
thread status, branch, worktree, or `ACTIVE_TASK_THREAD_BUNDLE.md` never overrides it.

The default contract is `wip_limit = 1`. Worktree isolation is mandatory for implementation, but
separate branches, worktrees, threads, developers, or disjoint paths do not create concurrency
permission.

## 2. Structured Execution Record

The board contains exactly one block between:

```text
<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
<!-- CONNLAB_EXECUTION_CONTROL_END -->
```

The fenced JSON object uses schema `connlab.execution-control`, version `1`, and contains:

- `wip_limit`, `execution_token_owner`, and `execution_state`
- the current `active` task/lane/role/branch/worktree/base/head, `locked_paths`, and evidence
- ordered `queue` records with unique `queue_position`
- optional `paused` record containing `paused_reason`, `preempted_by`, `checkpoint_sha`,
  `pause_master_sha`, and `resume_condition`
- optional `quick_fix` record, including risk, locks, acceptance, and `residual_owner`
- `residuals` with an exact `residual_owner` and disposition
- optional `parallel_exception` proof and secondary owner
- the last governance commit and evidence reference

Missing or duplicate markers, malformed JSON, unsupported schema/version, duplicate queue
positions, incomplete records, stale Git facts, or owner/state contradictions fail closed.

## 3. State And Token Invariants

The only states are `idle`, `queued`, `implementation_running`, `gate_running`,
`paused_preempted`, `quick_fix_running`, `reconciling`, `complete`, and `cancelled`.

- `idle`, `paused_preempted`, `complete`, and `cancelled` have a null token owner.
- `implementation_running` and `gate_running` retain the original task as owner.
- `quick_fix_running` has the Quick Fix as sole owner.
- `reconciling` has the paused original task as sole owner.
- Reviewer, QA, and Integrator are gates inside the same token lifetime; they never release the
  token or consume a second token.
- Token release occurs only after Integrator acceptance and residual closeout, explicit
  cancelled/closed closeout, or a complete `paused_preempted` governance commit.
- A callback, clean lane, idle conversation, or elapsed time cannot acquire or release a token.

## 4. FIFO Queue

Only an approved/implementation-ready task may queue. While an owner exists, a second ordinary
task receives a unique durable FIFO position and no implementation worktree or write-capable role
dispatch. Repeated starts are idempotent. A preserved paused original has reconciliation priority
over ordinary queued tasks. User reprioritization requires an explicit board governance action and
evidence.

## 5. Mandatory Compact Quick Fix Capsule

When the User goal is explicit, every `AGENTS.md` 19.1 predicate is proven from current facts, and
no escalation trigger exists, Orchestrator must use one compact Quick Fix task capsule. It must
not route an independent Planner, create a full plan, repeat User approval, or add default QA.
The capsule is the formal task record and contains exactly these business fields:

- Goal
- Why Safe
- May Touch
- Must Not Touch
- Locked Paths
- Targeted Validation
- Risk Gate
- Branch / worktree / base
- Evidence path

Every Quick Fix still uses an isolated worktree, exact targeted validation, clean checkpoint,
risk-proportionate gates, Integrator closeout, residual ownership, and separate authority for
push, publication, restart, or destructive action.

Risk routes are normative:

| Risk | Boundary | Required route |
|---|---|---|
| QF-1 | spelling, semantically neutral copy/comment, or one assertion | Quick Fixer -> Integrator |
| QF-2 | launcher, bounded error handling/wiring/style | Quick Fixer -> Reviewer -> Integrator |
| QF-3 | Windows, Office, browser, or runtime behavior | Quick Fixer -> Reviewer -> QA -> Integrator |
| QF-4 | API contract, schema, migration, authority, persistence, public-drive write, or business semantics | full Planner/User flow; Quick Fix forbidden |

Copy is QF-1 only when action, permission, authority, and lifecycle semantics are unchanged.
`Submit -> Approve`, `Delete -> Archive`, and `Confirm Matrix -> Save` are not presumed neutral.
Ambiguity, scope growth, ownership conflict, unexplained failure, a second failed same-class fix,
destructive need, or QF-4 always returns to Planner/User.

## 6. Standalone And Preempting Quick Fixes

A standalone path is `idle(null)` -> `quick_fix_running(Quick Fix)` -> Integrator-accepted
`complete(null)`. Cancellation closes as `cancelled(null)` only after exact retained/discard
residual ownership.

A preempting path is two serialized governance commits:

1. preserve the original clean checkpoint and enter `paused_preempted(null)`;
2. acquire the Quick Fix token and enter `quick_fix_running(Quick Fix)`.

The pause record preserves branch, worktree, previous owner, unfinished work, `paused_reason`,
`preempted_by`, `checkpoint_sha`, `pause_master_sha`, locks, evidence, and `resume_condition`.
Developer-dirty work must be checkpointed first; a clean lane reuses its existing HEAD; waiting
Reviewer/QA uses the immutable gate HEAD; a running read-only gate may finish before the pause;
Integrator merge state forbids preemption. Locked paths must be disjoint. Preemption cannot nest.
No stash, reset, restore, discard, branch deletion, worktree removal, or no-op commit is allowed.

If a preempting Quick Fix is cancelled or fails, its token is released, its residual receives a
named owner, and the original remains `paused_preempted(null)`. It never resumes silently.

## 7. Non-Destructive Reconciliation

After the Quick Fix is accepted and its HEAD is proven on `master`, the board transfers the token
to the original task in `reconciling`. Integrator verifies the original lane remains clean at the
recorded checkpoint, rechecks ownership and changed paths, then must merge current `master` into
the preserved lane. Integrator must never rebase or rewrite the checkpoint.

Normative reconciliation action: merge current `master` into the preserved lane; never rebase.

After the merge, run the original affected validation and conflict-sensitive checks, record a
clean reconciliation checkpoint, update evidence, and resume `implementation_running`. Any
conflict, validation failure, drift, or ownership ambiguity returns to
`paused_preempted(null)`, preserves both histories/evidence, and routes Planner/User. No reset,
restore, discard, or automatic conflict choice is permitted.

`Resume` is fail-closed until the accepted Quick Fix HEAD and `pause_master_sha` are ancestors of
current `master`, current `master` is an ancestor of the new reconciliation checkpoint, the
preserved branch is clean at that new HEAD (not the pre-merge checkpoint), and the board contains
passing validation evidence. A callback or owner field alone is never resume authority.

## 8. Explicit Parallel Exception

Serial execution is the default. One secondary owner is permitted only when a material external
wait would otherwise block useful work or the User explicitly requests parallel execution, and
the board records exact disjoint path/lock/authority/test/governance ownership proof, both owners,
the reason, end condition, and explicit User approval evidence. Shared files, oversized mixed
tests, authority paths, uncertain ownership, or a third lane are forbidden. Maximum concurrency
is two, and the exception expires at its recorded end condition.

## 9. Cross-Conversation Enforcement

Before any write-capable dispatch or resume, re-read `AGENTS.md`, the board JSON, current
task/capsule/evidence, queue/pause/locks, Git HEAD/status, and registered worktrees. Only permanent
Orchestrator initiates or resumes implementation routing.

`scripts/connlab_execution_gate.ps1` is read-only and returns stable JSON decision/reason codes.
It never edits the board, routes a role, creates/cleans a worktree, changes a branch, or releases a
token. `scripts/run_task.ps1`, worktree `Create`, and Orchestrator implementation/preemption/
reconciliation/resume dispatch all require a fresh gate. `QUEUE_REQUIRED` routes governance only;
`BLOCKED_*` stops.

Production helper and entry-script calls resolve the main `master` worktree through Git common
worktree metadata and read only that primary board. A lane-local board copy is never execution
authority; inability to verify the main primary worktree fails closed. Test-only disposable roots
remain available only through the explicit test-root switch.

`ImplementationDispatch` is state and role specific: normal implementation requires durable
`implementation_running` plus `active.role: Developer`; a compact fast path requires
`quick_fix_running` plus `Quick Fixer`. `gate_running` under Reviewer, QA, or Integrator is
read-only and cannot authorize implementation writes. A blocking callback permits a bounded fix
only after primary governance durably transitions the same task back to
`implementation_running`/Developer.

Controlled Lane V2 remains frozen, its heartbeat remains `PAUSED`, and its helper, registry,
pilot, corrective packages, and tests are not reactivated or modified by this policy.
