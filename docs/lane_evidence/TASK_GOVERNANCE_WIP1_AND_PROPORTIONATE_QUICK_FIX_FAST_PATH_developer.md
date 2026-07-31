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
- Final helper is 492 physical lines, below the 500-line hard limit.

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

Total: `39 passed` across the five required modules.

Additional validation:

- PowerShell AST parse passed for `connlab_execution_gate.ps1`, `run_task.ps1`, and
  `connlab_lane_worktree.ps1`.
- Real lane board `Inspect` returned `ALLOW_INSPECT`, `zero_write: true`.
- `run_task.ps1 -Preview` returned/passed `ALLOW_RESUME` JSON into the Orchestrator prompt and did
  not invoke Codex.
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
- Paths: production root derives from the script location; alternate roots require explicit
  test-only opt-in. The exact lane path in board/evidence is approved dispatch metadata.
- Quality: no TODO, no unfinished production branch, no unrequested dependency, and all changed
  scripts/tests remain below 500 physical lines.
- Input/output: input is board JSON plus requested intent/task/lane and read-only Git facts; output
  is stable JSON such as `ALLOW_START`, `QUEUE_REQUIRED`, `ALLOW_DISPATCH`,
  `ALLOW_PREEMPT_CHECKPOINTED`, `ALLOW_RECONCILE`, `ALLOW_RESUME`, or `BLOCKED_*`.

## Stop Point

Developer implementation is complete at the immutable checkpoint above. The lane remains local;
no push or merge is authorized. Reviewer must review base
`a1968c4999a33c6bee18c9185882ea3b927c2004` through the final lane evidence commit, with product
paths and protected retained/frozen/cancelled worktrees excluded.
