# ConnLab Controlled Lane V2 User Approval Binding Corrective Plan

Status: local implementation integrated and accepted at e2240445 / pending Reviewer docs-only closeout gate

Task: `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_USER_APPROVAL_BINDING_CORRECTIVE`

Lane: `connlab-controlled-lane-orchestration-v2-user-approval-binding-corrective`

## 1. Discovery Decision

Create an independent corrective lane. Do not weaken production preflight, infer User authority
from chat history, or absorb the change into the pilot test lane.

Reviewer combined plan/readiness passed. The User explicitly authorized the exact seven-path
implementation/tests and one isolated corrective worktree. This authority is conditional on first
committing the current exact four-path governance candidate and restoring primary/index to clean.

The accepted Controller stopped correctly at registry generation `28` because the pilot was
registered but had no valid User approval binding. The pilot remains `plan_review_pending`,
heartbeat is `PAUSED`, implementation authority is false, and no implementation resource exists.

Repository evidence shows the defect is structural:

- `request_user_approval` shares generic role-target validation;
- generic target validation requires a worktree;
- dispatch preparation freezes completion authority for User approval;
- `record-callback` always invokes role completion authority;
- ordinary role binding materialization treats approval as a worktree role.

## 1.1 Implementation And QA Result

Reviewer implementation re-gate and isolated QA passed against checkpoint
`1c087a5ddc8aa7a00a9cb748c83827c4a480fd77`.

- Reviewed range:
  `fb7dc20a9775e49cde5c947346918105d91054b9..1c087a5ddc8aa7a00a9cb748c83827c4a480fd77`.
- Exact implementation candidate: seven paths, `676/15`.
- Product diff: `0`.
- Focused approval/recovery: `35 passed`.
- Full controlled-lane suite: `223 passed`.
- CTL codes: `39`; mutation commands: `6`.
- Registry generation/hash, pilot state, implementation authority, and heartbeat: unchanged.
- Runtime/bootstrap/pilot side effects: none.

No separate Developer or Reviewer evidence file exists in the reviewed checkpoint. Their
verified completion/re-gate facts are recorded here and in task/Planner governance; no role-owned
evidence is fabricated.

## 1.2 Local Integration Result

Integrator accepted a local ff-only integration:

- base `fb7dc20a9775e49cde5c947346918105d91054b9`;
- implementation checkpoint `1c087a5ddc8aa7a00a9cb748c83827c4a480fd77`;
- governance/final commit `e22404456d0ee99d2d557e78d511c94d2e363002`;
- exact five-path governance commit `224/27`, parent `1c087a5d`;
- exact twelve-path base-to-master package `900/42`;
- `git show --check` passed;
- excluded residual `0`;
- no merge commit, fetch, push, runtime mutation, or pilot continuation.

Local `origin/master` is an unfetched tracking ref at `3614a6d1`; the local comparison is
behind `0`, ahead `16`. It is not evidence of the current remote SHA.

## 2. Authority Separation

Three authorities are distinct:

| Authority | Proves | Does not prove |
|---|---|---|
| approval request dispatch ack | exact gate was shown in exact Controller task | User approved |
| User approval callback | User approved exact prepared task/lane/gate/scope | Developer completed work |
| role completion callback | role completed against frozen worktree/evidence/HEAD | User approval |

`request_user_approval` therefore has no `worktree_path`, completion HEAD, or evidence SHA. The
existing completion-authority module remains read-only.

## 3. Canonical Approval Binding

`approval_authority.py` will own a pure canonical structure:

```text
task_id
lane_id
approval_gate
scope_fingerprint
approval_scope_digest
route_id
operation_id
controller_thread_id
action_kind=request_user_approval
request_payload_digest
approval_contract_digest
expected_from_state
expected_pending_state
```

Preparation accepts only an exact Controller thread already bound by bootstrap authority. It does
not accept a role worktree, future Developer identity, or ambient current task.

Approved gate pairs are:

| From state | Gate | Pending state |
|---|---|---|
| `plan_review_pending` | `planning_first` | `user_planning_approval_pending` |
| `implementation_readiness_pending` | `tests_only_implementation` | `user_implementation_approval_pending` |

Any other state/gate pair is an existing transition/state mismatch.

## 4. Single-Action Journal

The six accepted commands remain unchanged:

```text
prepare-dispatch
mark-invocation-started
one external request action
record-action-result
ack-dispatch
advance-state
```

The request result is opaque. Exact read-back must find one request envelope in the exact
Controller thread with matching route, operation, task, lane, gate, and scope. Read-back itself
is an observation in a later scan when the native surface requires a separate action. No scan or
callback performs more than one external action.

After `advance-state`, the lane waits for a separate User callback. The callback uses
`record-callback` under fresh expected-generation CAS, stores its canonical event and approval
proof, and performs no external action. Developer routing occurs only on the next scan.

## 5. Callback Rules

Required callback fields:

- canonical event ID and status `user_approved`;
- role `User`;
- exact Controller `thread_id`;
- exact task, lane, approval gate, scope digest, route, operation;
- `dispatch_operation_id` equal to the prepared approval operation;
- canonical callback idempotency key.

Acceptance requires the dispatch to be acknowledged/advanced and the lane to remain at the exact
matching pending state. It must not invoke `completion_authority.py`.

Canonical replay returns `CTL_ALREADY_APPLIED` without incrementing generation. Changed payload
or key, stale generation, wrong thread/gate/state/scope/route/operation, pre-dispatch callback,
and late callback all fail closed with existing CTL codes and zero write.

## 6. Crash Recovery

| Crash point | Recovery |
|---|---|
| after prepare, before durable invocation marker | same IDs may retry only with durable proof invocation never started |
| after invocation marker, before result | exact Controller read-back may adopt one matching request; otherwise `CTL_RECOVERY_REQUIRED`, no resend |
| after result, before ack | exact read-back, local ack, no resend |
| after ack, before advance | CAS advance only |
| after advance, before User callback | wait; never synthesize approval |
| callback received before corrected request | reject; request approval again after corrective acceptance |
| callback persisted, before next scan | replay is already applied; next scan may route exactly once |
| wrong/multiple/unreadable read-back | fail closed and preserve dispatch for manual recovery |

## 7. Future File Plan

Exact implementation May Touch:

1. `scripts/connlab_controlled_lane/approval_authority.py`
2. `scripts/connlab_controlled_lane/state_machine.py`
3. `scripts/connlab_controlled_lane/contracts.py`
4. `scripts/connlab_controlled_lane/registry.py`
5. `scripts/connlab_controlled_lane/ownership.py`
6. `tests/unit/test_connlab_controlled_lane_approval_authority.py`
7. `tests/integration/test_connlab_controlled_lane_user_approval_recovery.py`

File responsibilities:

- `approval_authority.py`: canonical approval target, request read-back, callback validation,
  atomic approval proof mutation, and approval replay comparison.
- `state_machine.py`: select Controller-only approval action and gate/state pair; never add
  worktree/completion authority.
- `contracts.py`: delegate approval target/ack validation while preserving generic and bootstrap
  behavior.
- `registry.py`: route acknowledged approval callbacks to approval authority under the existing
  `record-callback` mutation.
- `ownership.py`: keep Controller approval binding distinct from worktree role ownership.
- new tests: direct unit matrix and end-to-end CAS/recovery matrix.

All other implementation and test paths are locked.

## 8. Line And Split Budget

Blank-inclusive counts at discovery:

- `state_machine.py`: 278
- `contracts.py`: 300
- `registry.py`: 350
- `ownership.py`: 226

Required final limits:

- `approval_authority.py <=180` (cap 220)
- `state_machine.py <=290` (cap 300)
- `contracts.py <=300` (cap 300)
- `registry.py <=350` (cap 400)
- `ownership.py <=235` (cap 260)
- unit test `<=220` (cap 260)
- integration test `<=280` (cap 320)

New approval logic must replace or extract superseded generic User-approval handling. No
blank-line suppression, one-line statement compression, or unrelated refactor is allowed.

## 9. TDD Matrix

RED:

- exact Controller-only request rejected because worktree is missing;
- callback cannot be safely distinguished from role completion or pre-dispatch history.

Direct unit GREEN:

- binding field/type/canonical digest validation;
- exact gate/state pairs;
- worktree forbidden for approval authority;
- wrong/stale/late/duplicate callback matrix;
- canonical replay and generation stability;
- pending/started/result/ack/advance invariants.

Integration GREEN:

- planning approval full journal then callback then next-scan Developer route;
- implementation approval equivalent flow;
- callback before ack rejected;
- request crash at every boundary;
- exact read-back adoption and zero/multiple/wrong/unreadable no-resend;
- pilot generation-28-shaped fixture resumes the same lane without re-registration;
- role completion regression, 39 CTL codes, and six mutation commands unchanged.

Verification uses explicit file arrays, no shell globs. It includes the two new tests, all
controlled-lane unit/integration tests, `py_compile`, PowerShell parser, line budgets, UTF-8,
trailing, `git diff --check`, exact whitelist, staging empty, disposable registry/Git roots, and
proof that no real native or business side effect occurred.

## 10. Worktree And Package

After the exact governance checkpoint is separately authorized and committed, and primary/index
are clean, Orchestrator creates a new isolated corrective branch/worktree from that checkpoint. It
must not reuse the accepted bootstrap, title-corrective, pilot, or TASK_367A worktrees.

The implementation package contains only the seven implementation/test paths and task-owned
governance. Reviewer and QA validate a clean checkpoint or exact archive. Integrator must report
excluded residuals explicitly.

For Integrator, freeze two non-overlapping layers:

- implementation: exact seven paths at `1c087a5d`, `676/15`;
- QA governance overlay: task, plan, Planner evidence, QA evidence, and exact board hunks, five
  paths, `224/27`;
- aggregate package: exact twelve paths, `900/42`;
- excluded residual: `0`.

## 11. Runtime Lock

This task does not authorize:

- modification of registry generation `28`;
- approval request dispatch or callback recording;
- pilot branch/worktree/Developer task creation;
- bootstrap, controller, heartbeat, automation, migration, archive, cleanup, fetch, or push.

After corrective acceptance, runtime resumes from the existing pilot lane and requests approval
again. The earlier pre-dispatch User approval is not reusable.

## 12. Next Gate

Reviewer, QA, and Integrator accepted the local package. The next gate is Reviewer docs-only
closeout over exact six paths and `185/27`. This Planner
pass does not stage, commit, fetch, or push. Runtime pilot continuation remains unauthorized
pending a separate User gate.
