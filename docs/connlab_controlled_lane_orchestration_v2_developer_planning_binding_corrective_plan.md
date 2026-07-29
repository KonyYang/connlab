# Controlled Lane V2 Developer Planning Binding Corrective Plan

Status: implementation_and_tests_authorized / pending controlled governance checkpoint and isolated corrective worktree creation

Task:
`CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE`

Lane:
`connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`

Blocked lane:
`CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`

## 1. Stabilization Decision

Replace the narrow Developer-only null-worktree proposal with one unified pre-implementation
docs-only role authority. Add separate bounded lifecycle fixture, happy-path, and recovery tests
so the complete pilot is proven before implementation authorization.

The accepted approval authority, post-Option-A worktree-bound completion contracts, 39 CTL codes,
and six mutation commands remain unchanged.

Reviewer passed the combined plan/readiness final re-gate. The User then authorized this exact
ten-path implementation-and-tests package and one isolated corrective worktree, conditioned on
first committing the exact four-path governance checkpoint and restoring primary/index clean.

## 2. Runtime Baseline

- registry generation `34`;
- registry SHA-256
  `43C4961432E3528D5239A0A65091C0DF6E0E87A5E7B085F7332372A4544A7EF3`;
- pilot `user_planning_approval_pending`;
- User planning approval persisted;
- pilot runtime implementation authority false;
- completion authority still Reviewer;
- no Developer thread/worktree binding;
- heartbeat `PAUSED`;
- active dispatches and recovery records `0`;
- primary candidate four governance paths; index empty.

Runtime remains read-only.

## 3. B1 Unified Gate Matrix

All ordinary role dispatches before Option A use explicit-null bindings:

1. Reviewer plan review.
2. Planner plan fix.
3. Reviewer plan re-gate.
4. Developer planning-first.
5. Planner planning source reconciliation.
6. Reviewer implementation readiness.
7. Developer readiness planning fix.
8. Planner readiness-fix reconciliation.
9. Reviewer readiness re-gate.
10. Planner final implementation-authority reconciliation.

Accepted User approval requests remain separate.

The role/gate/phase map is deterministic. Reused states carry `initial_planning`,
`readiness_fix`, or `final_authorization`. Cross-phase callback/replay is rejected.

## 4. Exact Role Authority

Use ROLE_THREAD_REGISTRY at the current authority HEAD and its exact SHA. Planner, Developer, and
Reviewer rows must be validated by exact-ID native `read_thread`.

The target binds exact task/lane/role/gate/phase, route/operation/idempotency/scope, role registry
hash, read-back digest, evidence path, input HEAD, and explicit `worktree_path: null`.

Missing, non-null, primary, retained, or fabricated worktree is invalid.

## 5. CAS Sequence

Each role dispatch keeps:

`prepare -> invocation-started -> one send -> result -> exact read-back -> ack -> advance`

Prepare atomically freezes the explicit-null target, persists a prepared role binding, and
switches completion authority to the exact role/gate. Advance activates the binding. Completion
callback is separate and uses fresh expected-generation CAS.

Normal callbacks persist proof only. The final Planner reconciliation callback additionally
persists `implementation_authorized=true` and state `authorized`, with zero native action. The next
scan alone may select Option A.

## 6. Implementation Boundary

Pre-implementation null bindings acquire no implementation ownership. Option A still requires:

- one native-created Developer implementation task/worktree;
- exact adopted path/branch/base/HEAD/project/thread identity;
- clean isolated worktree;
- exact owner acquisition;
- no reuse of docs-only binding as implementation authority.

Reviewer/QA/Integrator and bounded fixes after Option A remain worktree/checkpoint/archive bound.

## 7. B2 Test Architecture

### Narrow Recovery

`test_connlab_controlled_lane_developer_planning_recovery.py` starts from a generation-34-shaped
pilot and proves the exact currently blocked Developer planning dispatch/callback.

### Shared Fixture

`tests/fixtures/connlab_controlled_lane_pilot_lifecycle.py` owns:

- disposable Git and registry roots;
- fake native task/worktree adapter;
- per-scan external-action ledger;
- exact role/thread bindings;
- request/callback builders;
- restartable six-command journal runner;
- an exact normalized generation-34 snapshot builder with six advanced dispatches, two callbacks,
  34 idempotency entries, no recovery/unfinished dispatch, and the current pilot approval/proof
  shape;
- owner and generation assertions.

It contains no pytest test cases.

### Continuous Lifecycle

`test_connlab_controlled_lane_full_pilot_lifecycle.py` runs two independent readable sequences:

- planned -> plan fix/re-gate -> both User approvals -> all roles -> Option A -> fixes ->
  integration -> owner release -> closeout -> retired;
- exact generation-34-shaped `user_planning_approval_pending` snapshot -> Developer planning ->
  all remaining gates -> Option A -> fixes -> integration -> owner release -> closeout -> retired.

The second scenario preserves current dispatch/callback/idempotency history. It neither repeats
planning approval nor inserts the planned scenario's plan-blocked/fix branch.

### Recovery Matrix

`test_connlab_controlled_lane_full_pilot_recovery.py` reopens the registry at every journal and
callback boundary for each lifecycle role/action. It separately parameterizes both
`request_user_approval` actions through prepare/start/result/exact read-back/ack/advance and their
later User callbacks. It proves canonical replay, no resend, generation stability,
wrong/ambiguous input rejection, same task/worktree fix reuse, and exact closeout/retirement
recovery.

Approval requests are Controller-only actions. They are not ordinary role dispatches and their
User callbacks are not role completion callbacks.

## 8. Authorized Exact May Touch

1. `scripts/connlab_controlled_lane/preimplementation_authority.py`
2. `scripts/connlab_controlled_lane/state_machine.py`
3. `scripts/connlab_controlled_lane/contracts.py`
4. `scripts/connlab_controlled_lane/registry.py`
5. `scripts/connlab_controlled_lane/ownership.py`
6. `tests/unit/test_connlab_controlled_lane_preimplementation_authority.py`
7. `tests/integration/test_connlab_controlled_lane_developer_planning_recovery.py`
8. `tests/fixtures/connlab_controlled_lane_pilot_lifecycle.py`
9. `tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py`
10. `tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py`

No eleventh implementation/test path is allowed.

## 9. Budgets

| Path | Current | Cap | Final |
|---|---:|---:|---:|
| pre-implementation authority | absent | 300 | `<=260` |
| state machine | 289 | 300 | `<=290` |
| contracts | 300 | 300 | `<=300` |
| registry | 349 | 400 | `<=350` |
| ownership | 226 | 260 | `<=235` |
| unit authority test | absent | 320 | `<=280` |
| narrow recovery test | absent | 320 | `<=280` |
| lifecycle fixture | absent | 380 | `<=340` |
| continuous lifecycle test | absent | 380 | `<=340` |
| recovery matrix | absent | 460 | `<=420` |

Counts are blank-inclusive UTF-8 physical lines. Exceeding any final limit is a stop condition.
Semantic extraction/replacement is required in pressure files; whitespace/statement compaction
and scenario merging are forbidden.

## 10. TDD

RED:

- null-worktree dispatch fails at every pre-implementation role gate;
- wrong completion authority remains frozen;
- phase-reused states accept cross-gate proof or cannot reach final authorization;
- current pilot test cannot reach retirement.

GREEN:

- direct authority unit matrix;
- generation-34 narrow recovery;
- planned-to-retired and exact generation-34-to-retired continuous lifecycles;
- both complete approval-request plus callback recovery matrices;
- every-stage role/Option-A/closeout/retirement crash/replay/no-resend matrix;
- Option A and post-implementation worktree enforcement;
- Reviewer/QA same-worktree fixes;
- owner release, closeout, retirement, heartbeat final `PAUSED`;
- 39-code/six-command parity.

## 11. Validation Commands

Focused:

```powershell
py -m pytest `
  tests/unit/test_connlab_controlled_lane_preimplementation_authority.py `
  tests/integration/test_connlab_controlled_lane_developer_planning_recovery.py `
  tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py `
  tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py -q
```

Full bounded suite:

```powershell
$files = Get-ChildItem tests/unit,tests/integration -File |
  Where-Object { $_.Name -like 'test_connlab_controlled_lane_*.py' } |
  Sort-Object FullName
py -m pytest $files.FullName -q
```

Also run py_compile, three existing PowerShell parser checks, UTF-8/trailing/diff/line/whitelist,
product-zero, index, disposable-root, and no-real-side-effect checks.

## 12. Locks

Lock approval authority, callbacks, generic completion authority, native environment, CLI,
PowerShell wrapper, skill, AGENTS, ROLE registry, existing tests including the accepted pilot
test, all product/business paths and data, production runtime, retained topology, and every
stage/commit/network/migration/archive/cleanup operation.

## 13. Rollback And Package

Current rollback is omission of this four-path governance candidate. Future rollback omits the
exact ten-path package and leaves generation `34` unchanged.

Reviewer/QA validate an immutable clean corrective checkpoint/archive. Integrator packages only
the accepted ten paths plus task-owned governance/evidence, with excluded residual `0`.

## 14. Governance Checkpoint And Worktree Gate

The controlled docs-only checkpoint is exactly:

1. `tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE.md`
2. `docs/connlab_controlled_lane_orchestration_v2_developer_planning_binding_corrective_plan.md`
3. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE_planner.md`
4. `docs/task_board.md` exact task-owned hunks only

Frozen candidate numstat: `1039 additions / 8 deletions`.

Suggested local commit message:
`docs(orchestration): authorize developer planning binding corrective`

Before separately authorized checkpoint assembly: exact four-path status, empty index, UTF-8,
trailing, diff-check, scope/stale/forbidden scans, unchanged generation-34 registry and retained
topology, and no implementation/test path. After commit: exact four paths and frozen numstat,
`git show --check`, clean primary/index, unchanged registry/pilot/heartbeat, and no runtime or
network side effect.

Only then may Orchestrator create the new branch
`lane/connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective` and the new
worktree
`D:\PythonProject\connlab\tmp\worktrees\connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`
from the exact checkpoint. No retained worktree may be reused or modified.

## 15. Current Gate

Reviewer B1-B4 are closed, and exact ten-path implementation/tests are authorized after the
checkpoint/worktree preconditions. This Planner pass remains governance-only: no checkpoint
assembly/commit, implementation/test edit, worktree/branch creation, pilot continuation, registry
mutation, heartbeat activation, fetch, or push.

Next role: User / Orchestrator exact governance checkpoint authorization only.
