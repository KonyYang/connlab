# TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION

Status: `planned`

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Planning controller: Codex task `019fc491-21b0-77b0-bf18-53f53a366a7c`

Future runtime orchestrator: Codex task `019fb3d4-12a5-73b3-be8e-e59686fa39a9`

Planning activation commit: `a5286688`

Implementation is not approved. No role dispatch, complex worktree, cutover, archive, or push is
authorized by this task file.

## Why This Planning Task Is Allowed

The prior personal-serial simplification is closed, the board was idle, primary `master` was clean,
and FIFO was empty before activation. The current personal helper legally activated this task as the
only `running/planning` task. This is an out-of-band governance migration: the controller that plans
and later implements the change is not the runtime orchestrator being changed.

## Goal

Add one deliberately small complex-task path beside the completed simple-task path:

```text
runtime orchestrator classifies simple | complex | needs_discovery

simple:
  retain the current direct-primary personal workflow

complex / needs_discovery:
  Planner -> User approval -> Developer -> Reviewer -> QA -> Integrator
  -> implemented_pending_human_review -> User close
  -> safe worktree retirement -> task-context archive -> idle
```

Only one task may own the active slot. New requests wait in FIFO and never auto-start.

## Confirmed User Requirements

- A simple task must have a clear root cause and expected result, touch one to three total repository
  paths including tests and `docs/task_board.md`, avoid every forbidden category, and have bounded
  validation.
- Any missing simple-classification fact produces `needs_discovery`; it is never guessed as simple.
- Complex work is strictly serial and always uses Planner, explicit User approval, Developer,
  independent Reviewer, independent QA, and Integrator in that order.
- Reviewer or QA blocking findings return to the same task and Developer; QA fixes must pass Reviewer
  and QA again.
- One complex task owns one branch and one implementation worktree. No per-role worktrees exist.
- User close is required before the active slot is released. Worktree retirement and task-context
  archive are closeout work, not reasons to auto-start the FIFO head.
- No parallel execution, preemption, reconciliation, automatic discard, push, or automatic close is
  part of the new design.

## Repository-Proven Baseline

- `scripts/connlab_personal_task.py` is the only current board writer. It has CAS, ignored lock-file,
  atomic replacement, strict FIFO, explicit approval, blocker retention, validation, human review,
  close, and cancel behavior.
- The current board schema is `connlab.personal-serial-control` version 1 with WIP=`1`, state
  `idle|running|implemented_pending_human_review`, one active record, FIFO, last close, and four
  retained-history records.
- The simple workflow and gate regression set passed 62 tests at preflight.
- generation-1 history and the canonical index retain their accepted byte counts and SHA-256 values.
- Task-A remains cancelled; all four retained worktrees are clean and unchanged.
- legacy transition, handoff, worktree, permanent-role, parallel, preemption, and reconciliation
  materials are explicitly frozen. They cannot authorize new execution.

## Planner Inferences

- Keep one board writer and extract pure complex-state/classifier logic into bounded modules; do not
  grow the already 499-line personal helper into another monolith.
- Prefer one task-scoped Codex worktree task as the complex execution context. It lazily creates fresh,
  bounded Planner/Developer/Reviewer/QA/Integrator agents. This gives one physical worktree while
  preventing old task chats from entering a new role context.
- Use Git/task/plan/evidence/board facts as authority. Agent callbacks are bounded inputs that must be
  validated and committed before a transition.
- Preserve the current simple lifecycle byte-for-byte in behavior, even though the board schema and
  internal modules will need a controlled versioned migration.

## Unproven Codex Capabilities

- Native tools expose create, fork, read, send, wait, title, archive, and unarchive operations.
- Current read/list results do not expose a trustworthy `archived` field, so exact archive-state
  verification is not yet proven.
- The exact lifecycle of a Codex-created worktree when its task is archived or its worktree is retired
  is not proven.
- Fresh role-agent availability and recovery inside a task-scoped worktree are visible in the current
  environment but must be exercised by a bounded capability probe before cutover.

These are fail-closed implementation gates, not assumptions.

## Required Classifier

The classifier returns exactly `simple`, `complex`, or `needs_discovery`. Simple is allowed only when
all required facts are explicitly supplied and all simple predicates pass. Any forbidden-category
flag, more than three total paths, independent review need, destructive/external action, or unclear
root cause/validation makes it non-simple. Missing facts return `needs_discovery`.

Queued classification is provisional. The FIFO head is reclassified before activation; no queued task
auto-starts.

## Required Complex Invariants

- Same Task ID, active owner, branch, worktree, and evidence chain survive every transition and retry.
- Approval is committed before Developer dispatch.
- Developer hands off a clean local commit limited to the approved allowlist.
- Reviewer and QA receive fresh minimal context and exact immutable Git refs.
- Integrator accepts only the exact Reviewer- and QA-bound code commit.
- Blockers retain WIP and never discard/stash/restore automatically.
- User close begins closeout; it does not immediately release active.
- Dirty retirement or failed archive records a durable blocker and keeps the task active.
- Recovery reads durable authority, never conversational memory.

## Non-Goals

- Product, backend, frontend, API, database, persistence, authority, or business-rule changes.
- Parallel tasks, parallel exceptions, a second implementation owner, preemption, pauses for another
  task, multi-task recovery, cross-task reconciliation, shared-path parallel locking, leases,
  heartbeats, or a new permanent role registry.
- Controlled Lane V2, Task-A, old StartTask/CreateWorktree/Reconcile/Resume paths, external
  governance-migration work, automatic push, release, deletion, or destructive cleanup.
- Runtime-orchestrator generation rollover unless a later independent task proves it necessary.

## Exact Future Implementation Allowlist

Implementation after explicit approval may modify only:

1. `AGENTS.md`
2. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
3. `tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md`
4. `docs/task_governance_serial_complex_role_chain_automation_plan.md`
5. `docs/task_board.md`
6. `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
7. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md` (new)
8. `docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_capability_probe.md` (new)
9. `scripts/connlab_personal_task.py`
10. `scripts/connlab_serial_board.py` (new)
11. `scripts/connlab_serial_complex.py` (new)
12. `scripts/connlab_serial_worktree.ps1` (new)
13. `scripts/run_task.ps1`
14. `scripts/connlab_execution_gate.ps1`
15. `tests/unit/test_connlab_personal_serial_workflow.py`
16. `tests/unit/test_connlab_serial_classifier.py` (new)
17. `tests/unit/test_connlab_serial_complex_state.py` (new)
18. `tests/unit/test_connlab_serial_complex_worktree.py` (new)
19. `tests/unit/test_connlab_serial_complex_orchestrator_contract.py` (new)
20. `tests/unit/test_connlab_execution_gate_script.py`
21. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
22. `tests/integration/test_connlab_serial_complex_recovery.py` (new)

Adding or modifying any other path requires stopping and obtaining new User approval. Test commands
may be narrowed or expanded, but test file paths may not.

## Must Not Touch

- All product/backend/frontend/API/database/persistence/authority code and unrelated tests.
- generation-1 archive, canonical index, later archives, Task-A files, retained lane/worktree/evidence,
  and external governance-migration repository.
- Frozen legacy implementation files including `scripts/connlab_execution_transition.py`,
  `scripts/connlab_handoff_contract.py`, `scripts/connlab_lane_worktree.ps1`, Controlled Lane V2,
  legacy registry/heartbeat/pilot/corrective records, and old role threads.
- Remote branches and services; no push.

## Acceptance

- The current simple path remains behaviorally compatible and its regressions pass.
- All 29 scenario groups in the approved plan pass or have a repeatable native-capability proof.
- Board migration is CAS-protected, rollback-proven, compact, and preserves retained history exactly.
- Complex execution has one worktree, strict role order, independent Reviewer/QA, durable recovery,
  close-gated retirement, and idempotent archive behavior.
- Legacy modes stay frozen; Task-A/history/index remain unchanged; primary ends clean with local commits.
- Cutover and a real pilot require separate explicit User decisions after implementation review.

## User Approval Gate

This task is planning-only until the User explicitly approves
`docs/task_governance_serial_complex_role_chain_automation_plan.md`. Approval must be written with the
current personal helper and committed before any implementation edit. Approval does not itself
authorize cutover, a runtime-orchestrator message, a pilot, push, or destructive cleanup.
