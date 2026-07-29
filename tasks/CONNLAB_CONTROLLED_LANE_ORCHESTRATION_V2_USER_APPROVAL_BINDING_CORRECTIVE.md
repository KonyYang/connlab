# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_USER_APPROVAL_BINDING_CORRECTIVE

Status: implementation/tests authorized / pending controlled governance checkpoint and isolated corrective worktree creation

Lane: `connlab-controlled-lane-orchestration-v2-user-approval-binding-corrective`

Blocked lane:
`CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`

## Current Phase And Why Allowed

Current phase is final authorization source-of-truth reconciliation. Reviewer combined
plan/readiness passed, and the User explicitly authorized the exact seven-path implementation,
tests, and creation of one isolated corrective worktree.

This docs-only reconciliation is allowed now because the accepted runtime correctly failed closed
before requesting User approval or creating any pilot implementation resource. Implementation may
not start until the current four-path governance candidate is committed as a controlled local
checkpoint and primary/index are clean. Pilot continuation remains unauthorized.

## Authoritative Entry Facts

- Registry generation: `28`.
- Pilot lane state: `plan_review_pending`.
- Pilot `implementation_authorized`: `false`.
- Heartbeat: `PAUSED`.
- Pilot branch, worktree, and Developer task: absent.
- Primary worktree and index: clean at entry.
- The registry SHA-256 observed by Planner is
  `931954069FEA68483CA3EAA8295C92846331F0241A7FC0097B598FE0C6CA9B03`.
- This discovery did not mutate the registry or runtime topology.

## Authorization And Checkpoint Sequence

The current authority is:

- Reviewer combined plan/readiness: passed.
- User exact seven-path implementation and tests: authorized.
- User isolated corrective worktree creation: authorized only after the governance checkpoint.
- Runtime pilot continuation, registry mutation, and any real approval request: unauthorized.

The required order is:

1. validate and commit only the exact four-path governance candidate;
2. restore primary and index to clean;
3. have Orchestrator create one isolated corrective branch/worktree from that checkpoint;
4. route the same corrective contract to Developer implementation;
5. keep the generation-28 pilot and registry read-only throughout corrective implementation.

This pass does not authorize staging or committing the governance checkpoint. A separate exact
User / Orchestrator checkpoint authorization is required.

## Problem Statement

The current implementation treats `request_user_approval` like a role-completion dispatch:

- `state_machine.py` requires both `thread_id` and `worktree_path` for targeted actions;
- it also attaches a role completion authority to `request_user_approval`;
- `contracts.py` requires `worktree_path` in ordinary native target bindings;
- `registry.py` sends every `record-callback` through completion authority;
- `ownership.py` materializes an ordinary role binding for the User action.

A User approval gate is not worktree completion. It belongs to the exact Controller task and must
be prepared before the approval request is shown. A later User callback must be bound to that
prepared request and persisted by CAS before any Developer route becomes legal.

## Frozen Approval Request Contract

`request_user_approval` is an independent external action. It requires no `worktree_path`,
branch, lane HEAD, evidence digest, or completion authority.

The prepared approval target must contain:

- exact Controller `thread_id`;
- exact `task_id`;
- exact `lane_id`;
- exact gate: `planning_first` or `tests_only_implementation`;
- exact canonical scope digest and current lane `scope_fingerprint`;
- exact `route_id`;
- exact `operation_id`;
- exact `action_kind=request_user_approval`;
- canonical request payload digest;
- a deterministic approval-contract digest;
- the expected pre-approval lane state.

Unknown, empty, inferred, or ambient thread identity is invalid. A role worktree, primary path,
Developer path, or retained worktree must never be substituted for Controller identity.

## Journal And State Sequence

The accepted six mutation commands remain unchanged:

1. `prepare-dispatch` persists the complete approval request binding by
   `expected_registry_generation` CAS.
2. `mark-invocation-started` durably proves the single external approval request may begin.
3. Exactly one request is shown in the exact Controller task.
4. `record-action-result` stores the opaque receipt/result digest.
5. Exact Controller-thread read-back proves the request envelope carries the frozen
   `route_id`, `operation_id`, task, lane, gate, and scope.
6. `ack-dispatch` and `advance-state` move:
   - `plan_review_pending -> user_planning_approval_pending`, or
   - `implementation_readiness_pending -> user_implementation_approval_pending`.

The request acknowledgement and User decision callback are separate events. Request dispatch
acknowledgement proves only that the correct gate was presented in the exact Controller task.

## Frozen User Callback Contract

The later `CONNLAB_CALLBACK_V2` User callback must:

- use role `User` and canonical status `user_approved`;
- identify the exact prepared approval `route_id` and `operation_id`;
- repeat exact task, lane, gate, scope digest, and Controller `thread_id`;
- identify the prepared dispatch as its `dispatch_operation_id`;
- have a canonical callback event ID and a distinct callback idempotency key;
- arrive while the lane remains in the matching `user_*_approval_pending` state;
- be written by existing `record-callback` with a fresh expected generation.

The callback mutation atomically records the approval event and the exact approval proof. It does
not dispatch Developer in the same scan. Only the next authoritative scan may select the next
route.

Pre-dispatch chat text, a historical User message, or approval received before the corrected
request was prepared and acknowledged is not authority. After this corrective is accepted, the
pilot must receive a new approval request.

## Failure-Closed Matrix

- Stale expected generation: `CTL_CAS_CONFLICT`, zero write.
- Changed canonical payload or idempotency key: `CTL_IDEMPOTENCY_CONFLICT`, zero write.
- Request operation at the wrong journal stage: `CTL_DISPATCH_STAGE_MISMATCH`, zero write.
- Wrong Controller thread: `CTL_THREAD_BINDING_MISMATCH`, zero write.
- Wrong task, lane, gate, scope, route, operation, status, or callback event:
  `CTL_CALLBACK_CONFLICT` or existing role-state mismatch, zero write.
- Callback before request acknowledgement or after the gate was consumed:
  `CTL_ROLE_CALLBACK_STATE_MISMATCH`, zero write.
- Canonical callback replay: `CTL_ALREADY_APPLIED`, no generation drift and no second route.
- Non-identical duplicate: `CTL_IDEMPOTENCY_CONFLICT`, zero write.
- Possible-start request with missing receipt:
  exact single read-back may be adopted; zero, multiple, wrong, or unreadable read-back is
  `CTL_RECOVERY_REQUIRED`, no resend.
- Durable pre-invocation proof is the only condition permitting same-ID request retry.

No new CTL code or mutation command is authorized. The accepted 39-code catalog and six-command
CAS journal remain exact.

## Pilot Recovery Point

The corrective must not delete, re-register, or rebuild the pilot lane. After acceptance and a
separate runtime authorization:

1. read generation `28` as the recovery baseline;
2. verify the same pilot lane remains `plan_review_pending`, heartbeat remains `PAUSED`, and no
   pilot task/worktree exists;
3. run a fresh authoritative scan using the corrected approval binding;
4. prepare and send a new User planning-first approval request;
5. accept only the subsequent bound User callback;
6. leave Developer routing for the following scan.

Any drift from the frozen baseline returns to Planner/User. No cleanup or repair write is implied.

## Future Exact May Touch

Implementation and tests are authorized after the controlled governance checkpoint and isolated
worktree preconditions are satisfied. They may touch only:

1. `scripts/connlab_controlled_lane/approval_authority.py` (new)
2. `scripts/connlab_controlled_lane/state_machine.py`
3. `scripts/connlab_controlled_lane/contracts.py`
4. `scripts/connlab_controlled_lane/registry.py`
5. `scripts/connlab_controlled_lane/ownership.py`
6. `tests/unit/test_connlab_controlled_lane_approval_authority.py` (new)
7. `tests/integration/test_connlab_controlled_lane_user_approval_recovery.py` (new)

Governance may additionally use this task, its plan, role evidence, reconciliation evidence, and
the exact board hunk.

## Future Line Budgets

Blank-inclusive UTF-8 physical lines are authoritative:

| Path | Current | Cap | Required final |
|---|---:|---:|---:|
| `approval_authority.py` | absent | 220 | `<=180` |
| `state_machine.py` | 278 | 300 | `<=290` |
| `contracts.py` | 300 | 300 | `<=300` |
| `registry.py` | 350 | 400 | `<=350` |
| `ownership.py` | 226 | 260 | `<=235` |
| unit approval test | absent | 260 | `<=220` |
| integration recovery test | absent | 320 | `<=280` |

Existing modules at their final ceiling require semantic replacement/extraction into
`approval_authority.py`. Blank deletion, statement compaction, or unrelated refactoring may not
be used to satisfy a budget.

## Must Not Touch

- `scripts/connlab_controlled_lane/callbacks.py`
- `scripts/connlab_controlled_lane/completion_authority.py`
- `scripts/connlab_controlled_lane/cli.py`
- `scripts/connlab_controlled_lane.ps1`
- `.agents/skills/connlab-controlled-lane/**`
- `AGENTS.md`
- existing oversized/mixed registry, callback, state-machine, or pilot test files
- `tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`
- product, backend, frontend, API, schema, database, Matrix, Fee, Office, LTR, and business tests
- real business data, public shares, attachments, workbooks, and generated artifacts
- runtime registry, controller, heartbeat, automation, native tasks, branches, and worktrees
- TASK_367A and accepted bootstrap/corrective worktrees or branches
- fetch, push, migration, archive, cleanup, reset, restore, or destructive Git operations

## Frozen TDD

Clean accepted HEAD must first demonstrate:

- an approval request cannot be prepared without a worktree;
- a pre-dispatch `user_approved` callback can be accepted by the generic completion path or cannot
  be represented with exact Controller-only authority;
- successful approval routing is therefore unavailable without the corrective.

GREEN must cover:

- Controller-only approval target validation with no worktree;
- exact task/lane/gate/scope/route/operation/thread binding;
- planning-first and tests-only implementation gates;
- request prepare/start/result/read-back/ack/advance;
- request dispatch acknowledgement without User completion;
- callback persisted after acknowledgement and Developer selected only on a later scan;
- stale, wrong-thread, wrong-gate, wrong-scope, wrong-route, wrong-operation, duplicate,
  non-identical replay, pre-dispatch, and late callback;
- durable pre-invocation retry and every possible-start no-resend recovery branch;
- generation stability for every rejected/replayed case;
- unchanged role completion callbacks and unchanged 39-code/six-command parity.

Focused commands must use explicit PowerShell-safe file arrays. Full controlled-lane tests,
`py_compile`, PowerShell parser, UTF-8/trailing, line budgets, exact-path scope, diff-check,
staging-empty, no-registry-write, and no-real-side-effect checks remain mandatory.

## Rollback And Package Isolation

The package is atomic across the seven Future May Touch paths plus task-owned governance. A
rollback removes the new approval authority and restores the five exact existing modules; it does
not mutate generation `28`, the pilot lane, or any native resource.

Implementation packaging must start from a clean isolated corrective worktree. Reviewer and QA
must inspect a clean checkpoint/archive. Mixed or whole-repository staging is forbidden.

## Stop Condition

The corrective contract is implementation-authorized but not yet executable. The next legal role
is User / Orchestrator exact governance checkpoint authorization. Developer may be routed only
after that checkpoint is committed, primary/index are clean, and the isolated corrective worktree
exists. QA, Integrator, runtime approval request, and pilot continuation remain unauthorized.
