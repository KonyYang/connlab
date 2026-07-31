# TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH — Developer Evidence

Status: `ready_for_review`
Role: permanent Developer
Date: 2026-07-31
Lane: `task-governance-wip1-and-proportionate-quick-fix-fast-path`
Branch: `lane/task-governance-wip1-and-proportionate-quick-fix-fast-path`
Worktree: `D:\PythonProject\connlab-worktrees\task-governance-wip1-and-proportionate-quick-fix-fast-path`
Base: `a1968c4999a33c6bee18c9185882ea3b927c2004`
Primary dispatch HEAD: `f465b5f576229544f773095bb1086961152e6be8`
Implementation checkpoint: `41a604d15f7472e4d8efc4673dbd8c9272c1e45d`
Reviewer fix checkpoint: `7cb4d6db7f978875de73c1f6b0fec5e557f4e565`
Second Reviewer fix checkpoint: `911713b85b28d172b8919fac1f127a2e3b843246`
Next: permanent Reviewer

## Scope And Authority

The exact approved task/plan and primary dispatch metadata authorize this governance-only lane as
the sole WIP=1 execution-token owner. The lane base predates the primary-only dispatch commit, so
the lane board contains the candidate structured representation of the authoritative primary
dispatch facts. Permanent Integrator owns then-live primary reconciliation.

No product/backend/frontend/API/domain/database/schema/Office/LTR/Matrix/Fee/runtime path changed.
`ROLE_THREAD_REGISTRY.md`, `ACTIVE_TASK_THREAD_BUNDLE.md`, Controlled Lane V2, and
`scripts/task_complete_commit.ps1` remained read-only.

## Implementation Result

- Added one normative WIP/token/queue/Quick Fix/preemption/reconciliation/exception/recovery
  policy and one unique marker-delimited board JSON authority block.
- Added a read-only PowerShell gate with stable JSON decisions and `BLOCKED_*` reason codes. It
  validates schema, owner/state, queue, pause, Quick Fix, parallel exception, and relevant Git/
  worktree facts without writing or routing.
- Gated `run_task.ps1`, worktree `Create`, and Orchestrator write-capable dispatch. The explicit
  Controlled Lane V2 branch remains frozen and unchanged.
- Replaced default-parallel/V1-Lite active guidance with WIP=1, permanent roles, compact Quick Fix
  capsule rules, serialized merge-not-rebase recovery, and explicit max-two parallel exceptions.
- Added disposable-repository behavior tests and bounded static governance compatibility tests.

## Exact Implementation Paths

The implementation checkpoint contains exactly 17 paths:

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
2. `.agents/skills/connlab-planner/SKILL.md`
3. `AGENTS.md`
4. `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
5. `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
6. `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
7. `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
8. `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
9. `docs/task_board.md`
10. `scripts/connlab_execution_gate.ps1`
11. `scripts/connlab_lane_worktree.ps1`
12. `scripts/run_task.ps1`
13. `tests/integration/test_connlab_execution_gate_recovery.py`
14. `tests/unit/test_connlab_execution_gate_script.py`
15. `tests/unit/test_connlab_lane_worktree_script.py`
16. `tests/unit/test_execution_wip_and_quick_fix_governance.py`
17. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`

This evidence file is committed separately as required by the dispatch.

## TDD Evidence

- Existing governance baseline before implementation: `4 failed, 4 passed`; failures were the
  known stale V1-Lite/bundle assertions.
- New RED matrix before production implementation: `27 failed, 8 passed`; failures named the
  missing helper, policy, board block, gate wiring, and permanent-role governance.
- First helper GREEN attempt exposed a PowerShell backtick-regex defect; the legal fenced JSON
  fixtures failed with `BLOCKED_JSON_INVALID`. Changing only the parser regex to a single-quoted
  literal produced `21 passed` for helper/recovery tests.
- Secondary parallel dispatch was added through its own RED test (`1 failed`) and minimal GREEN
  change (`1 passed`) with exact secondary branch/worktree/HEAD checks.
- Original handoff helper was 492 physical lines. The Reviewer fix pass consolidated the final
  helper to 268 physical lines while adding stricter behavior, below the 500-line hard limit.

## Validation Matrix

The plan's 27 scenarios are covered as follows:

- 1-7, 11-12, 17-18: execution-gate unit tests cover idle start, second-task queue, token retention
  through Developer/Reviewer/QA/Integrator, dirty/clean preemption, lock overlap, nested rejection,
  explicit parallel exception, malformed/duplicate JSON, duplicate queue positions, and owner
  contradictions.
- 8-10, 13-14, 23-27: recovery integration tests cover accepted-on-master reconciliation,
  deterministic restart digest, clean resume, checkpoint drift/fail-closed behavior, exact
  real-worktree preservation, standalone completion/cancellation/running ownership, preempting
  ownership transfer, cancelled/failure owner-null pause, and reconciliation-failure owner-null
  invariants.
- 15-16, 19: governance tests cover mandatory QF-1 capsule/no Planner/full-plan/default-QA,
  semantic-copy negatives, QF-4 authority/schema/API rejection, and `run_task` gate-before-route /
  queue-only behavior.
- 20-22: worktree/permanent-role compatibility tests cover TaskId/gate-required Create,
  no-force/no-reset safety, permanent role callbacks, and frozen V2 behavior.

Exact planned pytest commands, rerun after final implementation edits:

```text
py -m pytest tests\unit\test_connlab_execution_gate_script.py -q
13 passed in 7.25s

py -m pytest tests\integration\test_connlab_execution_gate_recovery.py -q
11 passed in 12.43s

py -m pytest tests\unit\test_execution_wip_and_quick_fix_governance.py -q
6 passed in 0.07s

py -m pytest tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
9 passed in 0.44s
```

Original handoff total: `39 passed` across the five required modules. The bounded Reviewer fix
pass supersedes this with the fresh validation recorded below.

Additional validation:

- PowerShell AST parse passed for `connlab_execution_gate.ps1`, `run_task.ps1`, and
  `connlab_lane_worktree.ps1`.
- Original pre-review lane-local previews returned allow decisions; Reviewer correctly identified
  those as stale-board authority. The fix-pass production previews now resolve
  `D:\PythonProject\connlab` and fail closed with `BLOCKED_MARKERS_MISSING` until Integrator
  installs the candidate execution block on primary. Disposable divergent-board tests prove the
  primary board controls run-task, Create, and dispatch decisions.
- `git diff --check` and staged `git diff --cached --check` passed.
- Exact implementation allowlist: `17/17`; forbidden-scope scan passed.
- Before/after primary and protected retained/frozen/cancelled worktree HEAD/status equality
  passed. Primary `ROLE_THREAD_REGISTRY.md`, `ACTIVE_TASK_THREAD_BUNDLE.md`,
  `task_complete_commit.ps1`, and `connlab_controlled_lane.ps1` SHA-256 values were unchanged.
- No real worktree Create/Retire, remote push, merge, service restart, real-data access, stash,
  reset, restore, discard, or cleanup was performed.

## Task Review Checklist And Self-Check

- Architecture: governance-only; no product layering, UI, application, domain, Office, or API
  boundary changed.
- Scope: only the current approved task and exact May Touch implementation/evidence paths were
  changed; no Matrix/Report/future product behavior was added.
- Design: board is the sole authority; helper is read-only; stable state/owner invariants and
  exact failure codes avoid a second mutable control plane.
- Errors: missing/malformed/stale/contradictory facts fail closed. No swallowed exception or
  broad silent fallback exists.
- Paths: production root resolves the main `master` worktree through Git common-worktree metadata;
  a lane-local board copy cannot authorize execution. Alternate roots require explicit test-only
  opt-in. The exact lane path in board/evidence remains approved dispatch metadata.
- Quality: no TODO, no unfinished production branch, no unrequested dependency, and all changed
  scripts/tests remain below 500 physical lines.
- Input/output: input is board JSON plus requested intent/task/lane and read-only Git facts; output
  is stable JSON such as `ALLOW_START`, `QUEUE_REQUIRED`, `ALLOW_DISPATCH`,
  `ALLOW_PREEMPT_CHECKPOINTED`, `ALLOW_RECONCILE`, `ALLOW_RESUME`, or `BLOCKED_*`.

## First Bounded Reviewer Fix Pass

Reviewer evidence at `ee2c179659c9636093cc2c3dc37c38a79f07bb7a` reported four blocking
findings. The fix checkpoint `7cb4d6db7f978875de73c1f6b0fec5e557f4e565` changes exactly these nine
approved paths:

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
2. `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
3. `scripts/connlab_execution_gate.ps1`
4. `scripts/connlab_lane_worktree.ps1`
5. `scripts/run_task.ps1`
6. `tests/integration/test_connlab_execution_gate_recovery.py`
7. `tests/unit/test_connlab_execution_gate_script.py`
8. `tests/unit/test_connlab_lane_worktree_script.py`
9. `tests/unit/test_execution_wip_and_quick_fix_governance.py`

### Reviewer Finding Closure Map

- Blocking 1 closed: `ImplementationDispatch` now permits only durable
  `implementation_running`/Developer or `quick_fix_running`/Quick Fixer states. Reviewer, QA, and
  Integrator `gate_running` dispatches return `BLOCKED_DISPATCH_STATE`. A positive disposable Git
  test proves a Developer fix is allowed only after the board records the transition back to
  `implementation_running` with matching task/lane/role/worktree/branch/HEAD. `Resume` now requires
  accepted Quick Fix/master ancestry, current master merged into the original lane, a distinct
  clean reconciliation checkpoint, and passing validation evidence.
- Blocking 2 closed: general validation rejects active/owner mismatch, duplicate queued task IDs,
  non-contiguous/duplicate positions, ownerless primary plus secondary exception, incomplete
  parallel approval/scope/independence/end-condition/owner facts, reconciling without accepted
  Quick Fix proof, terminal residual omission, and failed-preemption residual omission.
- Blocking 3 closed: production helper and both entry scripts resolve and verify the main
  `master` worktree through Git common-worktree metadata. Dynamic two-worktree tests use divergent
  primary/lane boards and prove the stale lane cannot authorize run-task routing, worktree Create,
  or implementation dispatch. Unverifiable/missing primary authority fails closed.
- Blocking 4 closed: the permissive pre-merge Resume test was replaced by an actual disposable
  master Quick Fix commit, `--no-ff` merge into the preserved original lane, new reconciliation
  checkpoint, clean-state check, and ancestry proof. Dynamic tests cover merge conflict with both
  histories preserved and `paused_preempted(null)`, gate-running dispatch negatives, terminal and
  preempting residual negatives, invalid parallel/duplicate queue facts, executable QF-1 button
  label dispatch, QF-4 API/schema/authority rejection, run-task queue/no-Codex, and Create
  queue/no-worktree behavior.

### Fix-Pass TDD And Validation

- Initial Reviewer reproductions: `9 failed, 23 passed`, with failures on duplicate task identity,
  active/owner mismatch, invalid parallel owner, gate-running dispatch, untouched Resume, and
  terminal residual omission.
- Entry/Quick Fix dynamic RED: eight gate failures, three Quick Fix/run-task failures, and one
  worktree Create queue failure, each with the expected pre-fix decision mismatch.
- Fresh required five-module suite after all edits:

```text
py -m pytest tests\unit\test_connlab_execution_gate_script.py tests\integration\test_connlab_execution_gate_recovery.py tests\unit\test_execution_wip_and_quick_fix_governance.py tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
57 passed in 38.79s
```

- `--collect-only` reported 57 executable cases, covering the approved 27-scenario matrix plus
  the Reviewer negatives and positive fix-handoff/terminal-closeout paths.
- Windows PowerShell AST parsing passed for all three scripts. Helper length is 268 physical lines;
  both expanded Python test modules are at or below the 500-line hard limit.
- Read-only production gate/run-task previews resolved the primary root and returned
  `BLOCKED_MARKERS_MISSING`, `zero_write: true`, because the pre-integration primary board does not
  yet contain the lane candidate markers. Worktree `List -Json` returned `CTL_OK`,
  `ZeroWrite: true`.
- `git diff --check`, exact nine-path fix allowlist, forbidden product/V2/bundle/registry scans,
  and protected primary/frozen/cancelled/retained HEAD/status equality passed. The four protected
  primary file SHA-256 values are unchanged.
- No real Create/Retire, merge, push, restart, cleanup, stash, reset, restore, discard, or remote/
  runtime/real-data action was performed.

## Second Narrowly Bounded Reviewer Fix Pass

The Reviewer re-gate at lane HEAD `090fdc254edadaeb91a003890d3a920adcd9c739`
left one blocking schema-validation finding. Fix checkpoint
`911713b85b28d172b8919fac1f127a2e3b843246` changes exactly two approved paths:

1. `scripts/connlab_execution_gate.ps1`
2. `tests/unit/test_connlab_execution_gate_script.py`

### Remaining Finding Closure Map

- General `Inspect` now requires every queue record to carry the frozen canonical fields
  `task_id`, `lane`, `enqueue_sequence`, `enqueued_at`, `dependencies`, `locked_paths`,
  `requested_priority`, `queue_position`, and `evidence`. It validates non-empty scalar values,
  positive integer sequence/position values, parseable timestamps, string-array dependency/lock
  shapes, non-empty locks, unique task IDs/positions/sequences, contiguous stored FIFO order, and
  chronological/same-priority FIFO consistency.
- General `Inspect` now requires `secondary_role`, `secondary_branch`, `secondary_worktree`, and
  `secondary_head_sha` in every non-null `parallel_exception`, in addition to the existing User
  approval, independence, end-condition, ownership, and proof fields. It validates canonical
  scalar/array shapes, Developer role, lane-derived branch, absolute worktree, 40-hex Git HEAD,
  primary/secondary branch-worktree separation, secondary-owner consistency, and locked-path
  independence.
- Bounded regressions reproduce both former `ALLOW_INSPECT` gaps. Positive complete-record
  fixtures prove valid queue and parallel paths remain allowed. Existing duplicate-position,
  duplicate-task, ordering, dispatch, and Create coverage now uses the complete frozen records.
- The lane candidate board has an empty queue and null `parallel_exception`; it was inspected and
  intentionally left unchanged. No policy or skill contract needed modification.

### Second-Pass TDD And Validation

- Exact RED before the helper change: `8 failed, 10 passed, 13 deselected`. The incomplete queue,
  out-of-order queue, five malformed queue-field cases, and missing four secondary proof fields
  all incorrectly returned `ALLOW_INSPECT`.
- Focused GREEN after the helper change: `18 passed, 13 deselected`.
- Full gate unit module: `31 passed`.
- Fresh required five-module suite:

```text
py -m pytest tests\unit\test_connlab_execution_gate_script.py tests\integration\test_connlab_execution_gate_recovery.py tests\unit\test_execution_wip_and_quick_fix_governance.py tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
66 passed in 41.90s
```

- Windows PowerShell AST parsing passed for all three entry/helper scripts. The helper is 307
  physical lines and the expanded gate unit module is 496 lines; all approved size limits hold.
- `git diff --check`, the exact two-path implementation allowlist, forbidden product/V2/bundle/
  registry scans, and before/after protected primary/frozen/cancelled/retained HEAD/status equality
  passed. The four protected primary file SHA-256 values are unchanged.
- No real Create/Retire, merge, push, restart, cleanup, stash, reset, restore, discard, or remote/
  runtime/real-data action was performed.

## Stop Point

Developer implementation is complete at the immutable checkpoint above. The lane remains local;
no push or merge is authorized. Reviewer must review base
`a1968c4999a33c6bee18c9185882ea3b927c2004` through the final lane evidence commit, with product
paths and protected retained/frozen/cancelled worktrees excluded.
