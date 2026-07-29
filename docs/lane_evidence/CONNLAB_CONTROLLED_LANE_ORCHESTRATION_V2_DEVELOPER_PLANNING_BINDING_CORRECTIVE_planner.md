# Planner Evidence - Controlled Lane V2 Developer Planning Binding Corrective

Status: implementation_and_tests_authorized / pending controlled governance checkpoint and isolated corrective worktree creation

Task:
`CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE`

Lane:
`connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`

Blocked lane:
`CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`

Discovery route:
`ctl-v2-developer-planning-binding-corrective-planner-discovery`

Stabilization route:
`ctl-v2-developer-planning-binding-corrective-planner-whole-lifecycle-stabilization`

Stabilization operation:
`ctl-v2-developer-planning-binding-corrective-planner-whole-lifecycle-stabilization-v1`

Clarification route:
`ctl-v2-developer-planning-binding-corrective-planner-b3-b4-test-clarification`

Clarification operation:
`ctl-v2-developer-planning-binding-corrective-planner-b3-b4-test-clarification-v1`

Final authorization route:
`ctl-v2-developer-planning-binding-corrective-final-authorization-reconciliation`

Final authorization operation:
`ctl-v2-developer-planning-binding-corrective-final-authorization-reconciliation-v1`

## Reviewer Blockers

B1: the original null-worktree rule covered only Developer planning-first, while Planner and
Reviewer docs-only gates before Option A remained unreachable.

B2: the original test stopped after selecting Planner and did not prove the complete pilot,
recovery matrix, owner release, closeout, or retirement.

Both are closed in the revised governance contract.

B3: one continuous scenario must start from the exact generation-34-shaped current snapshot, not
from a planned fixture or by concatenating the narrow recovery test.

B4: both planning and implementation approval requests need their own complete six-command
dispatch recovery plus later independent User callback matrix.

B3/B4 are closed in this clarification.

Reviewer then passed the combined plan/readiness final re-gate. The User explicitly authorized the
exact ten-path implementation-and-tests package and one isolated corrective worktree after a
controlled four-path governance checkpoint. Runtime pilot continuation remains unauthorized.

## Runtime Verification

Read-only facts:

- registry generation `34`;
- SHA-256
  `43C4961432E3528D5239A0A65091C0DF6E0E87A5E7B085F7332372A4544A7EF3`;
- pilot `user_planning_approval_pending`;
- User planning approval true;
- implementation authority false;
- current completion authority Reviewer;
- Developer thread/worktree absent;
- heartbeat `PAUSED`;
- advanced dispatches `6`;
- persisted callbacks `2`;
- idempotency entries `34`;
- active dispatches `0`;
- recovery records `0`;
- index empty.

No runtime object changed.

## Role Authority Verification

ROLE_THREAD_REGISTRY SHA-256:

`C53F0356E5CF46816E55AB11CC131769864F0EBB4C6C646918B5A1F06EA97EC9`

Native exact-ID read-back confirmed:

- Planner `019eff12-a71a-7861-b3d2-908b204bdf73`;
- Developer `019eff12-f314-79f3-ae0b-73795dc9b2c1`;
- Reviewer `019eff13-27d3-75a2-b654-d8ac28937614`;
- exact role title, local host, and `D:\PythonProject\connlab` cwd for each.

No message or native side effect was sent. Exact `read_thread`, not title search or caller text,
is authoritative.

## B1 Stabilized Contract

The revised authority covers all pre-implementation ordinary role gates:

- Reviewer plan/re-gate;
- Planner plan fix;
- Developer planning-first/readiness planning fix;
- Planner planning/readiness-fix/final reconciliation;
- Reviewer implementation readiness/re-gate.

Every target uses exact role/thread/gate/phase authority and explicit `worktree_path:null`.
Preparation atomically switches completion authority and persists a prepared null-worktree role
binding. Advance activates it. Callback remains separate.

The final Planner callback atomically persists verified completion,
`implementation_authorized=true`, and state `authorized`; the next scan alone may select Option A.

Implementation and all post-Option-A role work remain isolated-worktree/checkpoint bound.

## B2 Stabilized Test Architecture

The authorized package preserves the narrow generation-34 recovery test and adds:

- a shared disposable lifecycle fixture;
- separate continuous planned-to-retired and exact generation-34-to-retired scenarios in one
  bounded module;
- an independent every-stage recovery/replay/no-resend matrix.

The continuous test includes plan fix, both User gates, all pre-implementation roles, Option A,
Reviewer and attributed QA fix reuse, Integrator acceptance, owner release, closeout, retirement,
and final heartbeat `PAUSED`.

The recovery test reopens a new RegistryStore at prepare/start/result/ack/advance/callback
boundaries and proves exact continuation, one action per scan, no duplicate send/create,
generation stability, canonical replay, no-resend uncertainty, and wrong/ambiguous zero-write.

The exact generation-34 snapshot preserves six advanced dispatches, two canonical callbacks,
34 idempotency entries, zero recovery/unfinished dispatch, the accepted planning approval, current
proof/authority shape, and heartbeat `PAUSED`. It does not replay planning approval or inject the
planned scenario's plan-fix history.

Both `request_user_approval` gates are independently parameterized through
prepare/start/result/read-back/ack/advance and the later User callback. They remain Controller-only
approval actions, not ordinary role dispatches or role completion callbacks.

## Authorized Exact May Touch

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

The former seven-path proposal is superseded. No eleventh implementation/test path is authorized.

## Budgets And Split Triggers

- authority final `<=260`, cap `300`;
- state machine current `289`, final `<=290`, cap `300`;
- contracts current/final/cap `300`;
- registry current `349`, final `<=350`, cap `400`;
- ownership current `226`, final `<=235`, cap `260`;
- unit authority test final `<=280`, cap `320`;
- narrow recovery final `<=280`, cap `320`;
- fixture final `<=340`, cap `380`;
- continuous lifecycle final `<=340`, cap `380`;
- recovery matrix final `<=420`, cap `460`.

Crossing a final limit stops implementation for scope review. No whitespace compression,
statement compaction, or merged independent scenarios.

## Code And Command Parity

The accepted catalog remains 39 CTL codes and the six mutation commands:

`prepare-dispatch`, `mark-invocation-started`, `record-action-result`, `record-callback`,
`ack-dispatch`, `advance-state`.

No evidence justifies a new code or command.

## Locks

Approval authority, callbacks, generic completion authority, native environment, CLI, PowerShell,
skill, AGENTS, ROLE registry, existing mixed and pilot tests, product/business paths, real data,
production registry/runtime, retained worktrees/tasks, Git staging/commit/network, migration,
archive, and cleanup are locked.

## Governance Paths

This pass remains exact four paths:

1. task;
2. plan;
3. Planner evidence;
4. `docs/task_board.md` exact status/scope hunks.

No pilot governance file or implementation path was changed.

## Validation

- four-path status inventory;
- runtime registry generation/hash/state unchanged;
- native role read-back only;
- UTF-8 and trailing whitespace;
- tracked/no-index diff-check;
- stale seven-path/narrow-state scan;
- exact May Touch/locks/budget parity;
- index empty;
- retained worktrees clean;
- no implementation/runtime/native side effect.

## Planner Result

Reviewer B1-B4 are closed. Exact ten-path implementation/tests are authorized, but execution is
conditioned on a separately authorized four-path governance checkpoint, clean primary/index, and
a new isolated corrective worktree created from that checkpoint.

Checkpoint candidate:

1. `tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE.md`
2. `docs/connlab_controlled_lane_orchestration_v2_developer_planning_binding_corrective_plan.md`
3. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE_planner.md`
4. `docs/task_board.md` exact task-owned hunks only

Frozen candidate numstat: `1039 additions / 8 deletions`.

Suggested local commit:
`docs(orchestration): authorize developer planning binding corrective`

The checkpoint must preserve registry generation `34`, pilot `user_planning_approval_pending`,
`implementation_authorized=false`, heartbeat `PAUSED`, and all retained worktrees. Only after the
checkpoint commit and clean-primary verification may Orchestrator create the dedicated branch and
worktree frozen in task/plan. This pass performed neither action.

Next role: User / Orchestrator exact governance checkpoint authorization only.
