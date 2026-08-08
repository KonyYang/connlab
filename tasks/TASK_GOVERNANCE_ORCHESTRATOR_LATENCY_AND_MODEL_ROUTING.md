# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING

Status: `planned_pending_user_approval`

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Activation commit: `6227acb7cfccaab276194d2a7cbda96bc1f09a89`

## Goal

Reduce avoidable retries, orchestration latency, and model cost in Personal Serial Workflow V2 without
adding a governance framework, changing product behavior, or changing the board/runtime schema.

The permanent Orchestrator and direct simple tasks remain on `gpt-5.6-sol` with
`reasoning_effort=medium`. The automatic complex chain uses explicit role-level routing, with
`gpt-5.6-terra` as the default and narrowly defined risk-based escalation to `gpt-5.6-sol`.

## Approved-Plan Boundary

Implementation is forbidden until the User approves the exact committed Plan and its
`connlab.personal-task-approved-request` contract.

Implementation may touch exactly:

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
2. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
3. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
4. `docs/task_board.md`

Planning changed only:

1. `docs/task_board.md` through `scripts/run_task.ps1` Submit and the activation commit;
2. `tasks/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING.md`;
3. `docs/task_governance_orchestrator_latency_and_model_routing_plan.md`.

## Must Not Touch

- `scripts/run_task.ps1`, `scripts/connlab_personal_task.py`, `scripts/connlab_serial_board.py`, or the
  board JSON schema;
- product/backend/frontend code, API/database/schema/migration/persistence/authority/public-drive or
  business semantics;
- browser plugin, retained/frozen/cancelled lane resources, legacy V1/V2 audit resources, lifecycle
  cleanup, remotes, or push.

## Acceptance

- Submit, Approve, and Close guidance uses only `scripts/run_task.ps1`; no direct Python request-JSON
  construction or legacy schema probing is prescribed.
- Simple work keeps the direct two-interaction path: submit requirement, then inspect and close.
- Recovery reconstructs the active task/host from board, Git, and evidence without duplicate activation.
- Every complex role dispatch records the exact model and reasoning effort; Luna is not used.
- UI smoke is required only for user-visible UI changes and uses documented load state or deterministic
  selectors; unsupported `networkidle` probing is forbidden.
- Reviewer, mandatory QA, and Integrator remain required after approval.

`STATUS: PLANNED_PENDING_USER_APPROVAL`
