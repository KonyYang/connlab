# Controlled Lane Automation Tests-Only Pilot Plan

Status: administrative_planning_first_complete / pending User / Orchestrator exact governance checkpoint authorization

Task: `CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`

Lane: `connlab-controlled-lane-automation-pilot-test-only`

## 1. Administrative Decision

Create a planned-only authority candidate; do not register or dispatch the lane in this pass.

Controller authority reports generation `21`, state `bootstrap_ready`, and no pilot lane.
Dispatching an absent lane returned `CTL_NO_ACTION`, proving the required fail-closed precondition.
Repository inspection confirms that the sole candidate already exists at 229 UTF-8 physical lines
and can remain bounded below the frozen 250-line maximum.

## 2. Scope

Implementation changes exactly one file:

`tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`

The implementation test uses public CLI/contracts with temporary Git and registry roots plus a
fake/in-memory native adapter. It must not modify or import product behavior.

Governance changes use only the nine exact paths listed in the task. Runtime authority, after all
future gates, is limited to this lane's registry/owner/dispatch/callback/recovery records, one
native-created Developer task/worktree, short-lived role bindings, and one local tests-only
integration.

## 3. Test Contract

The bounded integration test must prove:

- planned registration never implies User approval or implementation authority;
- the exact Planner -> Reviewer -> User -> Developer-planning -> Planner -> Reviewer-readiness ->
  User-implementation sequence;
- Option A one-call Developer task/worktree creation and atomic exact-identity adoption;
- same Developer/worktree reuse for Reviewer and attributed bounded QA fixes;
- immutable clean checkpoint/archive validation;
- CAS conflict and changed-payload fail-close;
- canonical replay without generation drift;
- crash recovery at prepared, invocation-started, result-recorded, and acknowledged stages;
- possible-start uncertainty produces no resend;
- Integrator accepts only exact package scope with excluded residual `0`;
- closeout drains owner/callback/recovery records before non-force retirement;
- one task is archived per scan only after authorization;
- callback-first heartbeat remains active only while work exists and ends `PAUSED`.

The test must remain deterministic and must not depend on network, real native tasks, or ambient
repository state.

## 4. Gate And State Sequence

Repository gate chain:

1. Planner planning-first complete.
2. User authorizes exact four-path governance checkpoint.
3. Local docs-only checkpoint restores clean primary/index.
4. A later authoritative scan runs one `register-lane` action, creating state `planned`.
5. `planned -> plan_review_pending`.
6. Reviewer blocked -> same Planner; Reviewer passed -> `user_planning_approval_pending`.
7. User planning approval -> `developer_planning_active`.
8. Developer planning complete -> `planner_reconciliation_pending`.
9. Planner complete -> `implementation_readiness_pending`.
10. Reviewer blocked -> same Developer planning task; Reviewer passed ->
    `user_implementation_approval_pending`.
11. User tests-only approval -> Planner final reconciliation -> `authorized`.
12. Option A creation -> `developer_environment_pending`; exact adoption -> `developer_active`.
13. Developer complete -> `review_pending`.
14. Reviewer pass -> `qa_pending`; Reviewer blocker -> `developer_fix_active`.
15. QA pass -> `integration_pending`; attributed bounded QA blocker ->
    `developer_fix_active -> review_pending -> qa_pending`.
16. Integrator accepted -> `closeout_pending`.
17. Clean closeout -> `retired`; separately authorized one-task archive -> `archived`.

Each scan/callback emits at most one external action.

## 5. Journal And Recovery

Use the existing six-command CAS journal unchanged:

1. `prepare-dispatch`
2. `mark-invocation-started`
3. one external action
4. `record-action-result`
5. exact read-back plus `ack-dispatch`
6. `advance-state`

Stable route/operation/idempotency keys bind task, lane, role, gate, worktree/archive, authority
HEAD, and scope digest. Same canonical replay is no-op/idempotent. Stale generation, wrong
authority, changed payload, owner conflict, ambiguous read-back, or possible-start uncertainty
fails closed. Completion callbacks cannot acknowledge dispatch.

## 6. Worktree, QA, And Integration

- Developer implementation uses one native-created project-bound worktree from the approved clean
  base and one exact branch.
- Reviewer fixes and attributed bounded QA fixes reuse that same Developer task/worktree.
- Reviewer reviews immutable base-to-lane HEAD.
- QA uses the reviewed clean lane HEAD or an exact isolated archive, never ambient primary files.
- Integrator stages only the accepted test/governance whitelist, verifies residual `0`, and
  performs local integration only.
- Remote push is not authorized.

## 7. Locks And Stop Conditions

Locked scope includes all product/backend/frontend/API/schema/database/Matrix/Fee/Office/LTR code,
all business tests, real DB/files/workbooks/artifacts, bootstrap helper, skill, `AGENTS.md`, v1,
TASK_367A, push/fetch, migration, unrelated archive, and destructive cleanup.

Stop at Planner/User for:

- helper behavior that cannot satisfy the frozen test;
- dirty or non-HEAD authority during production preflight;
- shared-owner or scope conflict;
- stale CAS, partial registry, wrong or ambiguous native identity;
- product diff, extra implementation path, line count over 250;
- nonzero residual, unclean retirement, external/unattributed blocker;
- any need to alter helper/skill/AGENTS or perform push/migration/destructive cleanup.

## 8. Validation

Run the sole focused test, the complete bounded controlled-lane unit/integration set, py_compile,
PowerShell parser checks, 39-code/six-command parity, line count, strict UTF-8, trailing,
diff-check, whitelist/forbidden path, index, clean checkpoint/archive, product-diff-zero, and
residual-ledger checks.

## 9. Rollback And Heartbeat

Planning rollback is omission of the exact uncommitted four-path candidate. Runtime failure keeps
the journal and recovery point; it never guesses, resends, force-cleans, or deletes evidence.
Retirement is non-force and requires clean integration plus drained ownership.

Heartbeat activation is a separate action and only while the pilot is pending/active. Callbacks
run first. Final idle state must be a separately applied `PAUSED` heartbeat.

## 10. Current Gate

No production action is permitted from this document state. The current deliverable is an exact
four-path, `415/69` docs-only checkpoint candidate with index empty.

Suggested commit message:

`docs(orchestration): plan controlled lane tests-only pilot`

Next role: User / Orchestrator exact governance checkpoint authorization only.
