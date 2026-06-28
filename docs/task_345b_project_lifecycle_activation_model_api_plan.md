# TASK_345B Project Lifecycle Activation Model API Plan

Status: planned - ready for Reviewer plan gate, not approved for implementation
Task: `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`
Lane: `project-lifecycle-activation-model-api`
Role: Planner
Date: 2026-06-28

## 1. Current Phase And Permission

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active implementation lane: none.

Why Planner is allowed:

- TASK_345A contract passed Reviewer plan gate per the current Orchestrator/User delegation.
- The user explicitly replied `批准` for downstream lane creation.
- The requested legal action is limited to creating/activating the first downstream formal planning-first lane.
- Product code edits and Developer implementation routing are explicitly forbidden.

## 2. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/application/project_lifecycle_state_service.py`
- `backend/application/project_lifecycle_management_service.py`
- `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- `backend/api/routes_project.py` lifecycle route references found through `rg`

## 3. Confirmed By User / Delegation

- TASK_345A passed Reviewer plan gate.
- User approved creating the downstream lane.
- Stopped, closed, and Completed-closed projects use the `Activate` direction.
- `Completed` is not a special close path. All close reasons use one unified close form.
- Temporary `Apply/Register LTR` is an entrypoint only in the first lifecycle model series.
- Public-drive LTR workbook authority writing is deferred to a later authority lane.
- UI must not expose internal `administrative` terminology.
- Audit history must preserve close and activate time, reason, operator, and previous close information.

## 4. Confirmed By Repository Evidence

- `ProjectLifecycleState` currently has `active`, `stopped`, and `closed`.
- `ProjectClosureType` currently has `completed` and `administrative`.
- `ProjectLifecycleEventType` currently has `stop`, `resume`, `close_completed`, and `close_administrative`; there is no activate event type.
- `ProjectLifecycleStateService.resume_project` rejects closed projects.
- `ProjectLifecycleStateService` currently splits completed/admin close commands and events.
- `routes_project.py` currently exposes separate lifecycle close routes for `close-completed` and `close-administrative`.
- `ProjectLifecycleEvent` and `project_lifecycle_events` already provide a metadata-capable audit ledger.

## 5. Planned Backend Contract

TASK_345B should plan a backend implementation that keeps Project as the lifecycle container and Matrix as the execution authority map.

The future implementation plan should define:

- public API concept for one unified close action;
- internal compatibility with existing completed/admin closure records;
- business close reason taxonomy:
  - `Completed`
  - `Failed`
  - `Cancelled`
  - `Cannot test`
  - `Duplicate`
  - `Other`
- activation action from `stopped` and `closed` back to active work;
- audit event semantics for close and activate;
- lifecycle response shape consumed by later frontend lanes;
- structured conflict/error response shape;
- migration/backfill strategy;
- focused tests and integration/API checks.

## 6. API Shape Questions For Reviewer Gate

Reviewer should confirm the plan can leave these as implementation details or should force a specific answer before Developer implementation:

- Whether the implementation should introduce new endpoint paths such as `POST /api/projects/{project_id}/lifecycle/close` and `POST /api/projects/{project_id}/lifecycle/activate`, while preserving old split routes as compatibility wrappers.
- Whether `ProjectClosureType` should be replaced, extended, or compatibility-mapped to a new close reason enum/value object.
- Whether activation reason/note is required or optional in backend v1.

These are not blockers for creating TASK_345B as a planned lane, because they are exactly what Reviewer plan gate should evaluate before any Developer implementation starts.

## 7. Future Implementation Candidate Paths

These are not editable in this Planner pass. They are candidate paths for a later Developer implementation only after Reviewer plan gate and explicit user approval:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/application/project_lifecycle_state_service.py`
- `backend/api/routes_project.py`
- `backend/api/dependencies.py`
- `backend/api/lifecycle_errors.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/project.py`
- `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- `tests/unit/test_project_lifecycle_state_service.py`
- `tests/integration/test_project_lifecycle_api.py`
- `tests/integration/test_project_lifecycle_migration.py`
- `tests/integration/test_project_registry_summary_api.py`

## 8. Downstream Lane Dependencies

TASK_345B is serially before:

- `TASK_345C` lifecycle write guard and readonly rule update.
- `TASK_345D` frontend Workbench primary action UI.
- `TASK_345E` Projects registry copy/routing realignment.
- `TASK_345F` Temporary Apply/Register LTR entrypoint if not folded into Workbench UI.
- `TASK_345H` lifecycle audit/migration/QA closeout.

TASK_345G public-drive LTR workbook authority writing remains separate and later; it must not be pulled into TASK_345B.

## 9. Proposed Lane Definition

Lane: `project-lifecycle-activation-model-api`

Task: `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`

Status: `planned`

Owner Role: Planner, then Reviewer plan gate

Depends On:

- TASK_345A accepted contract;
- user approval for downstream lane creation;
- current repository lifecycle state/API evidence.

May Touch:

- `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md`
- `docs/task_345b_project_lifecycle_activation_model_api_plan.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`
- `docs/task_board.md` planned lane row and next-step text only

Must Not Touch:

- `backend/`
- `frontend/`
- `tests/`
- `frontend/src/api/client.ts`
- public-drive / Office / LTR workbook authority paths
- Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive implementation
- completed TASK_336 to TASK_345A task/plan/evidence files except read-only reference
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

Locked Paths:

- All product implementation paths are locked for this Planner lane.
- Candidate backend/API/test files listed above are future implementation paths only.
- Existing dirty product/governance residuals remain excluded unless a future approved lane names them.

Evidence File:

- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`

Validation Gate:

- `git diff --check` over TASK_345B planning files and `docs/task_board.md`.
- Static status check records any backend/frontend/tests dirty paths as outside this Planner package.
- Keyword checks find planned status, no implementation approval, Reviewer plan gate, Activate, unified close, audit/history, downstream lanes, Must Not Touch, and Locked Paths.

Merge Gate:

- Reviewer plan gate pass.
- User approval required before any Developer implementation may be routed.
- Orchestrator must not route Developer from this `planned` lane.

## 10. Reviewer Plan Gate Focus

The first object ready for Reviewer plan gate is:

`TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API` / lane `project-lifecycle-activation-model-api`.

Reviewer should check:

- Whether TASK_345B correctly depends on TASK_345A and does not reopen business-model decisions.
- Whether backend/API/audit candidate paths are complete enough for a later Developer plan.
- Whether old `administrative`/split-close semantics are treated as compatibility only.
- Whether activation from closed/stopped is properly auditable and testable.
- Whether public-drive LTR workbook authority, frontend UI, Projects registry, write guards, and future scope stay excluded.

## 11. Stop Point

Stop after this plan, task file, Planner evidence, and planned board row are created. Do not route Developer implementation.
