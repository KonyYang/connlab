# Planner Evidence - Controlled Lane V2 User Approval Binding Corrective

Status: qa_pass / pending Integrator packaging-readiness audit

Task: `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_USER_APPROVAL_BINDING_CORRECTIVE`

Lane: `connlab-controlled-lane-orchestration-v2-user-approval-binding-corrective`

Route ID: `ctl-v2-user-approval-binding-corrective-planner-discovery`

Operation ID: `ctl-v2-user-approval-binding-corrective-planner-discovery-v1`

Authorization reconciliation route:
`ctl-v2-user-approval-binding-corrective-final-authorization-reconciliation`

Authorization reconciliation operation:
`ctl-v2-user-approval-binding-corrective-final-authorization-reconciliation-v1`

QA reconciliation route:
`ctl-v2-user-approval-binding-corrective-1c087a5d-planner-qa-reconciliation`

QA reconciliation operation:
`ctl-v2-user-approval-binding-corrective-1c087a5d-planner-qa-reconciliation-v1`

## User-Confirmed Authority

- `request_user_approval` is a separate User gate and does not require a worktree.
- It binds exact Controller thread, task, lane, gate, scope, route, and operation.
- The request must be prepared before a later User callback.
- The callback uses the existing CAS journal and cannot be written post hoc.
- Pre-dispatch approval is not reusable; the pilot must be asked again after the corrective.
- Stale, wrong-thread, wrong-gate, duplicate, and late approval fail closed.
- Developer cannot be routed before callback persistence succeeds.
- Existing CTL codes are preferred.
- The existing generation `28` pilot lane must be resumed, not rebuilt.

## Read-Only Repository Findings

- `state_machine.py` groups `request_user_approval` with actions requiring role thread plus
  worktree and completion authority.
- `contracts.py` requires `worktree_path` for non-bootstrap/non-create target bindings.
- `registry.py` routes every `record-callback` to `record_completion_callback`.
- `ownership.py` materializes ordinary role binding state for approval requests.
- `callbacks.py` can parse a canonical event without independently requiring a worktree, so it
  remains locked; approval semantics belong in a new authority module.
- Existing completion authority remains correct for Planner/Developer/Reviewer/QA/Integrator and
  must remain locked.
- The accepted catalog contains 39 CTL codes and six mutation commands; discovery found no
  evidence requiring another code or command.

## Runtime Verification

Read-only registry inspection confirmed:

- generation `28`;
- pilot `plan_review_pending`;
- `implementation_authorized=false`;
- heartbeat `PAUSED`;
- no pilot Developer thread or worktree;
- registry SHA-256
  `931954069FEA68483CA3EAA8295C92846331F0241A7FC0097B598FE0C6CA9B03`.

No registry, native task, worktree, branch, controller, heartbeat, automation, or pilot mutation
was made.

## Discovery Decision

Create an independent corrective lane with seven exact future implementation/test paths. Keep
the current pilot registered and blocked. The corrected runtime later issues a new journaled
approval request from the existing generation-28 state.

## Reviewer And User Authorization

- Reviewer combined plan/readiness gate: passed.
- User exact seven-path implementation and tests: authorized.
- User one isolated corrective worktree: authorized after governance checkpoint and clean-primary
  preflight.
- Runtime registry mutation, pilot continuation, and real approval request: unauthorized.

The existing four governance paths must first form a separately authorized controlled local
checkpoint. Orchestrator may create the corrective branch/worktree only after that checkpoint
exists and primary/index are clean. No accepted bootstrap, title-corrective, pilot, or TASK_367A
worktree may be reused.

## Implementation, Reviewer, And QA Facts

- Clean reviewed checkpoint:
  `1c087a5ddc8aa7a00a9cb748c83827c4a480fd77`.
- Reviewed range:
  `fb7dc20a9775e49cde5c947346918105d91054b9..1c087a5ddc8aa7a00a9cb748c83827c4a480fd77`.
- Exact implementation candidate: seven paths, `676 additions / 15 deletions`.
- Product diff: `0`.
- Reviewer implementation re-gate: passed.
- Focused approval/recovery: `35 passed`.
- Full controlled-lane suite: `223 passed`.
- 39 CTL codes, six mutation commands, CAS, approval/callback separation, recovery/no-resend,
  budgets, compile/parser, UTF-8, trailing, and diff checks: passed.
- Registry generation/hash and pilot/heartbeat facts: unchanged.
- Runtime/pilot/bootstrap side effects: none.
- Excluded residual: `0`.

Only Planner and QA evidence files exist for this lane in the reviewed worktree. Missing
Developer/Reviewer evidence files are not invented; their verified role-gate facts are persisted
in the existing source-of-truth documents.

## Integrator Package Inventory

- Implementation layer: exact seven paths at `1c087a5d`, numstat `676/15`.
- QA governance overlay: exact five paths (task, plan, Planner evidence, QA evidence, board),
  numstat `224/27`.
- Aggregate future package: exact twelve non-overlapping paths, `900/42`.
- Excluded residual: `0`.
- QA evidence belongs to governance overlay and is not implementation May Touch.

## Exact Governance Paths In This Pass

1. `tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_USER_APPROVAL_BINDING_CORRECTIVE.md`
2. `docs/connlab_controlled_lane_orchestration_v2_user_approval_binding_corrective_plan.md`
3. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_USER_APPROVAL_BINDING_CORRECTIVE_planner.md`
4. `docs/task_board.md` exact status and lane hunks

## Future Exact May Touch

1. `scripts/connlab_controlled_lane/approval_authority.py`
2. `scripts/connlab_controlled_lane/state_machine.py`
3. `scripts/connlab_controlled_lane/contracts.py`
4. `scripts/connlab_controlled_lane/registry.py`
5. `scripts/connlab_controlled_lane/ownership.py`
6. `tests/unit/test_connlab_controlled_lane_approval_authority.py`
7. `tests/integration/test_connlab_controlled_lane_user_approval_recovery.py`

The new module owns Controller-only approval authority. Existing generic completion authority,
CLI, PowerShell entrypoint, skill, AGENTS, and old mixed tests stay locked.

## Budgets

- new authority module final `<=180`, cap `220`;
- state machine final `<=290`, cap `300`;
- contracts final/cap `<=300`;
- registry final `<=350`, cap `400`;
- ownership final `<=235`, cap `260`;
- new unit test final `<=220`, cap `260`;
- new integration test final `<=280`, cap `320`.

Counts include blank lines. Existing ceiling files require semantic extraction/replacement.

## Recovery Contract

- Only durable pre-invocation proof permits a same-ID retry.
- Once invocation may have started, exact single read-back may be adopted.
- Zero, multiple, wrong, or unreadable read-back is no-resend recovery required.
- Request ack and User decision are separate.
- Callback writes exact approval proof by fresh CAS and performs no route action.
- The next scan, not the callback scan, may select Developer.
- Duplicate canonical callback is already applied without generation drift.
- Pre-dispatch, stale, late, or non-identical callback is rejected with zero write.

## Locked Scope

No implementation/tests/scripts/skill/AGENTS changes occurred. Product and business paths, real
data, runtime registry, Controller, heartbeat, native tasks, branches/worktrees, accepted
bootstrap/title/TASK_367A topology, remote operations, migration, archive, and cleanup remain
locked.

## Planner Result

Reviewer implementation re-gate and QA passed. The exact implementation checkpoint and QA
governance overlay are frozen pending Integrator packaging-readiness audit. Runtime approval
dispatch, callback persistence, registry mutation, and pilot continuation remain unauthorized.

Next role: Integrator packaging-readiness audit only, routed separately by Orchestrator.
