# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE

Status: cancelled/frozen; incomplete RED snapshot preserved on retained lane branch, not integrated

Lane:
`connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`

Blocked lane:
`CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`

Discovery route:
`ctl-v2-developer-planning-binding-corrective-planner-discovery`

Whole-lifecycle stabilization route:
`ctl-v2-developer-planning-binding-corrective-planner-whole-lifecycle-stabilization`

Whole-lifecycle stabilization operation:
`ctl-v2-developer-planning-binding-corrective-planner-whole-lifecycle-stabilization-v1`

Lifecycle-test clarification route:
`ctl-v2-developer-planning-binding-corrective-planner-b3-b4-test-clarification`

Lifecycle-test clarification operation:
`ctl-v2-developer-planning-binding-corrective-planner-b3-b4-test-clarification-v1`

Final authorization route:
`ctl-v2-developer-planning-binding-corrective-final-authorization-reconciliation`

Final authorization operation:
`ctl-v2-developer-planning-binding-corrective-final-authorization-reconciliation-v1`

## Current Phase And Why Allowed

Current phase: Planner final docs-only authorization reconciliation after Reviewer passed the
combined plan/readiness final re-gate and the User authorized the exact ten-path implementation
and tests package.

Reviewer B1 proved that the first plan was too narrow: Developer planning-first is not the only
role gate before an implementation worktree exists. Planner reconciliation, Reviewer readiness,
readiness fixes, and Planner final authorization reconciliation are also docs-only and cannot
legally use an implementation worktree.

Reviewer B2 proved that the first integration matrix stopped too early. It did not continuously
prove the pilot from planning through Option A, review/fix, QA, integration, owner release,
closeout, and retirement.

The exact ten-path implementation and tests package is authorized only after this four-path
governance candidate becomes a controlled local checkpoint and primary/index are clean. This
Planner pass does not authorize implementation edits, worktree/branch creation, runtime mutation,
native sends, heartbeat activation, pilot continuation, stage, commit, fetch, or push.

## Current Read-Only Authority

- local HEAD: `f79d6efc933893d1d920a4e85e6ad9e6fd854d7e`;
- production registry generation: `34`;
- registry SHA-256:
  `43C4961432E3528D5239A0A65091C0DF6E0E87A5E7B085F7332372A4544A7EF3`;
- pilot state: `user_planning_approval_pending`;
- Reviewer plan proof: passed;
- bound User planning approval: true;
- pilot runtime implementation authority: false;
- Developer thread/worktree and generic worktree: absent;
- completion authority role: Reviewer;
- heartbeat: `PAUSED`;
- advanced dispatch history: exact `6`;
- callback history: exact `2`;
- idempotency entries: exact `34`;
- active dispatches: `0`;
- recovery records: `0`;
- index: empty.

The first Planner candidate was exact four governance paths, `780/8`. This stabilization replaces
its narrow active contract; it does not authorize the former seven-path implementation proposal.

## Reviewer Findings Resolved By This Contract

### B1: All Pre-Implementation Docs-Only Role Gates

The null-worktree contract now covers every ordinary role dispatch before Option A adopts an
implementation worktree:

| From state / condition | Role | Gate | Expected next state |
|---|---|---|---|
| `planned` | Reviewer | `plan_review` | `plan_review_pending` |
| `plan_review_pending`, blocked | Planner | `plan_fix` | `planner_fix_pending` |
| `planner_fix_pending`, complete | Reviewer | `plan_review_regate` | `plan_review_pending` |
| `user_planning_approval_pending`, approved | Developer | `developer_planning_first` | `developer_planning_active` |
| `developer_planning_active`, complete | Planner | `planning_source_reconciliation` | `planner_reconciliation_pending` |
| `planner_reconciliation_pending`, planning complete | Reviewer | `implementation_readiness` | `implementation_readiness_pending` |
| `implementation_readiness_pending`, blocked | Developer | `developer_planning_fix` | `developer_planning_active` |
| `developer_planning_active`, fix complete | Planner | `readiness_fix_reconciliation` | `planner_reconciliation_pending` |
| `planner_reconciliation_pending`, fix complete | Reviewer | `implementation_readiness_regate` | `implementation_readiness_pending` |
| `user_implementation_approval_pending`, approved | Planner | `final_authorization_reconciliation` | `planner_reconciliation_pending` |

User approval requests remain governed by accepted `approval_authority.py` and are not ordinary
docs-only role dispatches.

### B2: Continuous Pilot And Recovery Proof

The authorized package includes:

- a narrow generation-34 Developer-planning recovery test;
- a reusable disposable lifecycle fixture;
- one continuous full-pilot happy-path test;
- one independent full-pilot crash/replay/no-resend matrix.

No single `<=280` test is expected to carry the full lifecycle proof.

### B3: Two Independent Continuous Scenarios

The continuous full-pilot module must contain two separate scenarios:

1. a fresh planned lane runs through the plan-blocked/Planner-fix/Reviewer-re-gate branch and then
   continues to `retired`;
2. an exact generation-34-shaped snapshot starts at the current
   `user_planning_approval_pending` state and continues directly to `retired`.

The generation-34-shaped scenario must preserve the current normalized authority shape:

- generation `34`;
- the same six advanced dispatch records and their prepare/start/result/ack/advance event history;
- the pilot's advanced Reviewer-plan and planning-approval dispatches;
- exactly two persisted callbacks: Reviewer plan pass and bound User planning approval;
- exactly 34 canonical idempotency entries;
- zero recovery records and zero unfinished dispatches;
- current pilot state, scope, authority hashes, Reviewer completion authority, Reviewer pass,
  bound planning approval, `implementation_authorized=false`, and heartbeat `PAUSED`;
- no Developer implementation thread/worktree.

The fixture must construct this snapshot in a temporary registry from frozen test data. It must not
read the production registry at test runtime.

The generation-34 scenario must not replay planning approval, insert a historical plan-blocked/fix
branch, or concatenate the narrow Developer recovery test with a different planned-lane test.
It is one continuous scenario from the exact current recovery point through retirement.

### B4: Both User Approval Requests Are First-Class Journal Actions

Planning approval and tests-only implementation approval each require their own complete recovery
matrix:

`prepare -> invocation-started -> result -> exact Controller-thread read-back -> ack -> advance`

The later User decision callback is a separate CAS event after the request dispatch is advanced.
For both gates, every restart boundary must prove:

- a newly opened `RegistryStore` resumes the exact operation;
- at most one approval request is sent;
- possible-start uncertainty does not resend;
- lost receipt can be adopted only from one exact read-back;
- zero/multiple/wrong/unreadable read-back fails closed;
- same-ID canonical command replay returns already-applied without generation drift;
- changed key/payload and stale generation are zero-write;
- callback before advance, duplicate non-identical callback, wrong Controller thread/gate/scope,
  and late callback fail closed;
- canonical callback replay does not increase generation or select the next role in the same
  callback.

`request_user_approval` is neither an ordinary role dispatch nor a role completion callback. Its
accepted Controller-only authority remains unchanged.

## Authoritative Role Identity

`docs/project_management/ROLE_THREAD_REGISTRY.md` is the repository authority. Its observed
SHA-256 is:

`C53F0356E5CF46816E55AB11CC131769864F0EBB4C6C646918B5A1F06EA97EC9`

Required pre-implementation roles:

| Role | Exact thread ID | Native read-back |
|---|---|---|
| Planner | `019eff12-a71a-7861-b3d2-908b204bdf73` | exact ID/title/local host/project cwd confirmed |
| Developer | `019eff12-f314-79f3-ae0b-73795dc9b2c1` | exact ID/title/local host/project cwd confirmed |
| Reviewer | `019eff13-27d3-75a2-b654-d8ac28937614` | exact ID/title/local host/project cwd confirmed |

`list_threads` is bounded discovery only. Exact adopted-ID `read_thread` is the identity and
dispatch read-back authority. Caller-supplied role/thread/title/cwd cannot establish authority.

## Unified Pre-Implementation Binding

Every row in the B1 table uses a canonical target containing:

- task, lane, role, and exact `role_gate`;
- route, operation, idempotency, payload, and scope digests;
- exact ROLE_THREAD_REGISTRY path, authority HEAD, and SHA;
- exact role thread/title/host/project-root read-back digest;
- explicit `worktree_path: null`;
- `binding_mode=preimplementation_docs_only`;
- expected from/to state;
- exact role evidence path;
- input repository HEAD;
- exact reconciliation phase when the state name is reused.

Missing worktree is not explicit null. Any non-null, primary, retained, fabricated, or future
implementation worktree is invalid before Option A.

The binding acquires no implementation path/directory/authority owner and does not populate
`developer_worktree_path`.

## Reused State Disambiguation

`developer_planning_active` and `planner_reconciliation_pending` are reused states. The corrective
must persist a typed phase marker:

- `initial_planning`;
- `readiness_fix`;
- `final_authorization`.

The marker is frozen in the dispatch, role binding, completion authority, callback, and next-state
selection. A callback or replay from another phase is wrong-gate and zero-write.

For final authorization:

1. the bound User implementation approval already exists;
2. Planner final reconciliation is dispatched and completed as docs-only;
3. its callback atomically persists the verified Planner completion observation,
   `implementation_authorized=true`, and state `authorized`;
4. it performs no native route or worktree action;
5. only the next scan may select Option A `create_developer_environment`.

This special terminal pre-implementation completion is an expected-generation CAS mutation, not
a manual proof edit or post-hoc approval.

## Journal And Authority Switching

All docs-only role dispatches use the existing six commands:

1. `prepare-dispatch`
2. `mark-invocation-started`
3. one `send_message_to_thread`
4. `record-action-result`
5. exact adopted-thread `read_thread` and `ack-dispatch`
6. `advance-state`

`prepare-dispatch` atomically:

- freezes the exact docs-only target;
- persists one prepared explicit-null role binding;
- switches completion authority to the target role/gate;
- binds role evidence path and input HEAD;
- preserves prior accepted proofs;
- performs zero external action.

`advance-state` activates the binding and enters the target role-active/pending state. Completion
callback is a later event. Dispatch ack cannot complete a role; callback cannot acknowledge a
dispatch.

Each scan/callback performs at most one external action.

## Completion Callback

A docs-only role callback must:

- originate from the exact adopted role thread;
- bind task, lane, role, gate, phase, dispatch route/operation, and explicit null worktree;
- use the role's canonical completion status;
- bind the exact role evidence path;
- be read back from the same task;
- be persisted by `record-callback` with fresh expected-generation CAS;
- recompute evidence SHA and actual repository HEAD after role completion;
- reject pre-dispatch digest/HEAD claims.

Normal planning/review callbacks update only typed proof; the next scan chooses the next action.
The final authorization callback additionally performs the atomic transition described above.

## Recovery And Replay

- durable pre-invocation proof is the only same-ID resend permission;
- once invocation may have started, blind resend is forbidden;
- lost receipt plus exactly one matching read-back may be adopted;
- zero, multiple, wrong-thread/role/gate/phase/worktree, or unreadable read-back fails closed;
- canonical dispatch/callback replay is `CTL_ALREADY_APPLIED` with no generation drift;
- changed key/payload is `CTL_IDEMPOTENCY_CONFLICT`;
- stale expected generation is `CTL_CAS_CONFLICT`;
- wrong journal stage is `CTL_DISPATCH_STAGE_MISMATCH`;
- late/cross-gate callback is the existing callback/state mismatch;
- no new CTL code or mutation command is authorized.

## Implementation Boundary Remains Strict

Only state `authorized` may select Option A. The native create action:

- creates one Developer implementation task plus native worktree;
- atomically adopts exact thread, pending worktree, final path, branch, base, HEAD, project, lane,
  and owner identities;
- requires a clean isolated implementation worktree;
- never accepts explicit null, primary, retained, or docs-only binding;
- does not reuse the pre-implementation Developer role binding as implementation authority.

After adoption, Developer implementation, Reviewer/QA validation, bounded fixes, and Integrator
operate against exact clean lane HEAD/worktree or isolated archive according to the accepted
worktree-bound contracts.

## Full Pilot Lifecycle Contract

The planned-lane continuous disposable scenario must prove:

1. planned lane -> Reviewer plan gate;
2. blocked plan -> same Planner fix -> Reviewer re-gate;
3. bound User planning approval;
4. Developer planning-first;
5. Planner source-of-truth reconciliation;
6. blocked readiness -> same Developer planning task -> Planner reconciliation -> Reviewer
   readiness re-gate;
7. bound User implementation approval;
8. Planner final authorization reconciliation -> `authorized`;
9. Option A native task/worktree creation and exact adoption;
10. Developer implementation completion;
11. Reviewer blocked -> same Developer task/worktree fix -> Reviewer pass;
12. QA blocked with attributed/in-scope/bounded proof -> same Developer task/worktree -> Reviewer
    re-gate -> QA pass;
13. Integrator acceptance;
14. exact governance closeout and shared-owner release;
15. non-force clean worktree retirement to `retired`;
16. heartbeat remains active-only and finishes `PAUSED` in the disposable model.

QA is mandatory for this pilot. No no-QA shortcut is exercised.

The second continuous scenario starts from the exact generation-34-shaped snapshot described in
B3. It skips only already persisted history (Reviewer plan and planning approval), begins with
Developer planning-first, then proves every remaining item through `retired` without resetting
generation, callbacks, dispatch history, or idempotency.

## Full Recovery Matrix

The independent recovery test reopens a new `RegistryStore` at:

- every role dispatch `prepared`;
- every `invocation_started`;
- every `sent/result_recorded`;
- every `acknowledged`;
- every `advanced`;
- before and after every role/User completion callback;
- Option A pending receipt/read-back/adoption checkpoints;
- both planning and implementation `request_user_approval` checkpoints and their later User
  callbacks;
- Reviewer/QA bounded fix reuse;
- Integrator closeout, owner release, and retirement checkpoints.

For each checkpoint it proves:

- exact continuation to the next expected state;
- at most one native action per scan;
- no duplicate task/send/worktree operation;
- stable route/operation/idempotency identity;
- canonical replay no generation drift;
- possible-start uncertainty no resend;
- stale/changed/wrong/ambiguous input zero-write;
- generation increments only for first successful CAS mutations.

## Authorized Exact May Touch

After the controlled governance checkpoint and isolated corrective worktree are created, the
authorized implementation-and-tests package may touch exactly ten paths:

1. `scripts/connlab_controlled_lane/preimplementation_authority.py` (new)
2. `scripts/connlab_controlled_lane/state_machine.py`
3. `scripts/connlab_controlled_lane/contracts.py`
4. `scripts/connlab_controlled_lane/registry.py`
5. `scripts/connlab_controlled_lane/ownership.py`
6. `tests/unit/test_connlab_controlled_lane_preimplementation_authority.py` (new)
7. `tests/integration/test_connlab_controlled_lane_developer_planning_recovery.py` (new)
8. `tests/fixtures/connlab_controlled_lane_pilot_lifecycle.py` (new)
9. `tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py` (new)
10. `tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py` (new)

No eleventh implementation/test path is authorized.

## Module Responsibilities And Budgets

Counts are UTF-8 physical lines including blanks:

| Path | Current | Cap | Required final |
|---|---:|---:|---:|
| `preimplementation_authority.py` | absent | 300 | `<=260` |
| `state_machine.py` | 289 | 300 | `<=290` |
| `contracts.py` | 300 | 300 | `<=300` |
| `registry.py` | 349 | 400 | `<=350` |
| `ownership.py` | 226 | 260 | `<=235` |
| unit authority test | absent | 320 | `<=280` |
| narrow Developer recovery test | absent | 320 | `<=280` |
| lifecycle fixture | absent | 380 | `<=340` |
| continuous lifecycle test | absent | 380 | `<=340` |
| full recovery matrix | absent | 460 | `<=420` |

Responsibilities:

- authority module: role/gate/phase mapping, exact thread authority, explicit-null target,
  authority switch, callback observation, final authorization;
- lifecycle fixture: disposable Git/registry, fake native adapter/action ledger, canonical request
  builders, exact generation-34 normalized snapshot, restartable journal/callback runner;
- continuous lifecycle test: separate planned-to-retired and generation-34-to-retired sequences;
- recovery test: parameterized role, approval-request, Option A, callback, closeout, and retirement
  crash/replay/no-resend/generation matrix;
- narrow recovery test: exact generation-34 production-shaped resume only.

If any file exceeds its required final budget, or a pressure module cannot remain under its final
limit by semantic extraction/replacement, stop for scope review. Blank-line deletion, statement
compaction, or merging independent scenarios is forbidden.

## Must Not Touch

- `scripts/connlab_controlled_lane/approval_authority.py`
- `scripts/connlab_controlled_lane/callbacks.py`
- `scripts/connlab_controlled_lane/completion_authority.py`
- `scripts/connlab_controlled_lane/native_environment.py`
- `scripts/connlab_controlled_lane/cli.py`
- `scripts/connlab_controlled_lane.ps1`
- `.agents/skills/connlab-controlled-lane/**`
- `AGENTS.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- existing oversized/mixed controlled-lane tests
- `tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`
- all product/backend/frontend/API/schema/database/Matrix/Fee/Office/LTR paths and business tests
- production registry, Controller, heartbeat, pilot, callbacks, owners, native tasks, branches,
  worktrees, automation, and retained topology
- real DBs, public shares, attachments, workbooks, and generated artifacts
- stage, commit, fetch, push, migration, archive, cleanup, reset, restore, or destructive action

## TDD

RED must prove:

- every B1 pre-implementation ordinary role gate rejects explicit null or retains wrong authority;
- reused reconciliation state cannot distinguish planning/fix/final phases;
- final Planner completion cannot make the lane authorized deterministically;
- the accepted pilot test cannot traverse the complete lifecycle.

GREEN must satisfy the authority unit matrix, narrow generation-34 recovery, continuous full
lifecycle from both required starts, both complete approval-request matrices, and the full
recovery matrix described above.

The complete bounded suite command must use a PowerShell-expanded explicit path array, not shell
globs. Static gates include py_compile, three existing PowerShell parser checks, exact 39-code and
six-command parity, UTF-8, trailing, diff-check, line caps, ten-path whitelist, product diff zero,
index empty, disposable roots, and no-real-side-effect scans.

## Rollback And Package Isolation

Current rollback is omission of the exact four governance paths. A future implementation rollback
omits the exact ten-path package and leaves generation `34`, bound User approval, heartbeat, and
retained topology unchanged.

Reviewer and QA must validate an immutable clean corrective checkpoint/archive. Integrator may
package only the accepted ten paths plus task-owned governance/evidence. Excluded residual must be
`0`. No whole-directory staging is allowed.

## Reviewer And User Authorization

- Reviewer combined plan/readiness final re-gate: passed.
- Reviewer B1-B4: closed.
- User authorization: exact ten-path implementation and tests package plus one isolated corrective
  worktree after a controlled governance checkpoint.
- This authorization does not include runtime pilot continuation, production registry mutation,
  heartbeat activation, fetch, push, migration, archive, cleanup, or destructive action.

## Controlled Governance Checkpoint

The checkpoint candidate is exactly four governance paths:

1. `tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE.md`
2. `docs/connlab_controlled_lane_orchestration_v2_developer_planning_binding_corrective_plan.md`
3. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE_planner.md`
4. `docs/task_board.md` exact task-owned hunks only

Frozen candidate numstat after this pass: `1039 additions / 8 deletions`.

Suggested local commit message:
`docs(orchestration): authorize developer planning binding corrective`

Checkpoint preconditions:

- status contains exactly the four governance paths above;
- index is empty before separately authorized assembly;
- UTF-8, trailing, `git diff --check`, exact-scope, stale-status, and forbidden-path checks pass;
- registry generation/hash, pilot state, heartbeat, and all retained worktrees remain unchanged;
- no implementation/test/runtime path is present.

Checkpoint postconditions:

- the local commit contains exactly the four governance paths and frozen numstat;
- `git show --check` passes;
- primary and index are clean;
- registry generation remains `34`, pilot remains `user_planning_approval_pending` with
  `implementation_authorized=false`, and heartbeat remains `PAUSED`;
- no remote action or runtime side effect occurred.

## Isolated Corrective Worktree

Only after the checkpoint postconditions pass may Orchestrator create:

- branch: `lane/connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`;
- worktree:
  `D:\PythonProject\connlab\tmp\worktrees\connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`;
- base: the exact controlled governance checkpoint commit.

The worktree must be newly created from that checkpoint. It must not reuse or modify TASK_367A,
the accepted bootstrap worktree, the thread-title corrective worktree, the User-approval-binding
corrective worktree, or any other retained worktree.

## Stop Conditions

Stop at Planner/User for:

- any need for an eleventh path;
- any new CTL code or mutation command;
- any need to modify accepted approval/generic completion/callback/native/CLI/skill contracts;
- any inability to validate exact existing role tasks;
- any weakening of implementation worktree ownership;
- any runtime drift from generation `34` before separately authorized recovery;
- any real side effect, product diff, nonzero residual, or destructive operation.

## Current Gate

The User selected V1-Lite task-scoped orchestration and froze Controlled Lane V2 on 2026-07-30.
The incomplete Reviewer-fix RED snapshot is preserved on the retained lane branch at commit
`5f30db85b675b7f606a7b7474ce475d984988f6c`.

Preserved scope:

- `tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py`
- `tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py`
- exact diff `24/0`;
- focused result `3 failed, 19 passed`, matching the known unresolved P1 fixture/recovery contracts.

The preservation commit is not accepted product/governance behavior and must not be merged into
`master`. The worktree/index are clean. Production registry generation `34`, heartbeat `PAUSED`,
pilot state, product code, remote refs, and business data were not changed.

Next role: none. Reactivation requires a new formal task and explicit User approval.
