# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF Planner Evidence

Status: `approved_worktree_preparation`

Date: 2026-08-01

Role: permanent Planner

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

## Authority Audit

- Primary was clean at `master@cdb96b4ed80143ba40d571615282f0ee95708a0f` before planning.
- Production `Inspect=ALLOW_INSPECT`; execution state is `complete`; Current Active Task is None;
  token, active, queue, paused, Quick Fix, and parallel records are empty.
- This revision made no execution/lane/worktree/token/queue/role/product/remote/runtime change.
- The original umbrella is `superseded_by_split_plans`; A is the first approval-eligible package.

## User Approval Record

- On 2026-08-01 the User explicitly approved Task A only and authorized automatic isolated
  Developer -> Reviewer -> mandatory QA -> local Integrator acceptance.
- Approved planning HEAD: `d791e74a9811033058c38ee329bb3be8ee1f6504`.
- Task B was not approved and remains serially blocked. The umbrella remains non-executable.
- Approval/worktree base is the committed approved package
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Primary authority acquires Task A as the sole token owner in
  `implementation_running/Developer` only to authorize exact worktree creation. The worktree and
  branch do not yet exist and Developer is not dispatched.
- No queue, parallel exception, live migration, product, retained-lane, remote, or runtime action
  occurs in this governance transition.

## Sources Read

- User rejection attachment in full and the original umbrella task/plan/Planner evidence.
- `AGENTS.md` sections 13-20 and current board execution JSON/active summary.
- Planner and Orchestrator skills; Planner Discovery, WIP/Quick Fix, parallel model/operations,
  lane orchestration, task execution, and review protocols.
- `scripts/run_task.ps1`, read-only execution gate, completed-Markdown archive helper, and directly
  affected execution gate/recovery, WIP/Quick Fix, archive, and permanent-role tests.
- TASK_368E Developer/Reviewer/QA/Integrator evidence and its exact bounded-fix history.

## Discovery Classification

### Confirmed by User

- A must own active board/history, recurring closeout maintenance, deterministic transitions,
  event handoffs, compact references/reads/callbacks/cadence, and quantitative budgets.
- Routine transitions cannot require Planner.
- Production compaction is sole-token `gate_running/Integrator` only; token-null audits cannot
  write.
- WIP/token/role/worktree/no-push/non-destructive/V2 safety remains unchanged.

### Confirmed by Repository

- Board is `2466` lines / `781091` bytes at revision base.
- Orchestrator skill is `305` lines / `17304` bytes; Planner skill `98` / `3972`; orchestration
  protocol `303` / `14120`; `run_task.ps1` `123` / `4854`.
- `run_task.ps1` copies long routing prose and a full worktree snapshot.
- The execution gate is read-only and already validates much of the state/Git foundation; it has
  no mutation interface and is locked from modification.
- Existing board has one execution JSON block but no generated active-summary marker contract,
  transition digest, recurring board-history index, or partial-write recovery tests.
- TASK_368E required repeated Planner governance transitions totaling about 32 minutes per User
  audit and used a long-lived Orchestrator turn with repeated context/waits.

### Planner inference

- Three single-purpose helpers prevent the 307-line execution gate from becoming a writer/god
  script.
- Future active records need immutable gate/scope digests so the transition helper can validate
  QA routing and changed paths without prose heuristics.
- Board is replaced last in a staged transaction; immutable generation files plus a chained index
  provide audit and rollback proof.
- Context budgets are hard acceptance gates, not documentation aspirations.

### Not yet confirmed

- Physical worktree creation/verification, implementation commits, final archive/index hashes,
  after-size metrics, and measured pilot duration.

These are future execution outputs and do not alter scope. No blocking planning question remains.

## Definition Of Ready

- Goal, authority, exact transition events/guards, production writer boundary, helper CLIs,
  migration/rollback, recurring thresholds, budgets, file ownership, validation, performance,
  lane identity, and role gates are explicit.
- No active or parallel owner conflicts with the planned paths.
- The planned branch/worktree identity is exact; creation base is intentionally the future
  approval-governance HEAD and must be recorded before Create.
- User approval and exact approval base are recorded; Task A is the sole token owner for worktree
  creation. Implementation is not yet dispatched.

## Risk And Mitigation

- Unsafe automatic transition: exact plan digest, evidence blob, Git/state/scope guards, zero-write
  failures, and legacy manual fallback.
- Split authority: JSON remains sole authority; summary is generated and verified.
- History loss: byte-exact archives, chained hashes/counts, board-last transaction, and rollback
  proof through third closeout.
- Context omission: verified refs and `FULL_READ_REQUIRED` on any unsafe omission.
- Hidden long turn: one transition/dispatch maximum, no same-turn wait, callback-driven next turn.

## Stop Point

Return `approved_worktree_preparation` to Orchestrator. Do not create the worktree, dispatch
Developer, or run live maintenance in this Planner turn.
