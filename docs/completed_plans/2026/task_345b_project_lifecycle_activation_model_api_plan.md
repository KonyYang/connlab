# TASK_345B Project Lifecycle Activation Model API Plan

Status: implementation authorized - pending Developer implementation
Task: `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`
Lane: `project-lifecycle-activation-model-api`
Role: Planner / Developer planning-first
Date: 2026-06-28

## 1. Current Phase And Permission

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active implementation lane: `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API` is authorized for Developer implementation after Planner reconciliation.

Why Planner is allowed:

- TASK_345A contract passed Reviewer plan gate per the current Orchestrator/User delegation.
- The user explicitly replied `批准` for downstream lane creation.
- Developer planning-first completed and this plan now contains the implementation strategy.
- Reviewer implementation-readiness passed via conversational callback, but no separate Reviewer evidence/checkpoint file exists in the repository.
- The user explicitly approved the Developer implementation pass after readiness.
- Planner reconciliation created source-of-truth evidence for that authorization gap. Product code edits are still forbidden during Planner reconciliation, but Developer implementation may proceed after Orchestrator routing.

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

## 6. Developer Planning-First API Strategy

Developer planning inspection resolved the earlier API shape questions into the following concrete implementation strategy. This is still planning only; no backend/API/schema/test product code is changed by this pass.

### 6.1 Unified Close Endpoint And Compatibility

Implement the new product contract through:

- `POST /api/projects/{project_id}/lifecycle/close`
- request fields:
  - `reason_category`: one of `completed`, `failed`, `cancelled`, `cannot_test`, `duplicate`, `other`;
  - `note`: required non-empty operator note for every reason category;
  - `operator`: optional operator identity.
- response: the normal lifecycle response with business close reason fields and no user-facing `administrative` value.

Preserve the existing split routes only as compatibility wrappers:

- `POST /api/projects/{project_id}/lifecycle/close-completed` maps to the unified close service with `reason_category="completed"` and `note=close_note`. Existing confirmation/ack fields may be preserved in event metadata when supplied, but the unified endpoint does not require a special completed-only acknowledgement.
- `POST /api/projects/{project_id}/lifecycle/close-administrative` maps to the unified close service with `reason_category="other"` and `note=reason`, plus compatibility metadata such as `legacy_route="close_administrative"`.
- Compatibility wrapper responses must not expose `administrative` as the API-facing business close reason. `administrative` remains storage/legacy compatibility only.

### 6.2 Close Reason Compatibility Model And Migration

Add a new business close reason concept, for example `ProjectCloseReasonCategory`, with values:

- `completed`
- `failed`
- `cancelled`
- `cannot_test`
- `duplicate`
- `other`

Add a persisted project-level close reason category field, for example `close_reason_category VARCHAR(32)`, rather than overloading `closed_reason`, because `closed_reason` currently stores the operator note.

Compatibility rules:

- Existing `closure_type="completed"` rows backfill `close_reason_category="completed"`.
- Existing `closure_type="administrative"` rows backfill `close_reason_category="other"`.
- Existing rows with `lifecycle_state="closed"` and no closure type backfill `close_reason_category="other"`.
- `ProjectClosureType` remains available internally for migration/read compatibility, but product/API semantics use the new close reason category.
- For compatibility only, completed reason may keep `closure_type="completed"` and all non-completed reasons may keep `closure_type="administrative"` until a later cleanup lane removes the legacy field.

The lifecycle API response should add business fields such as:

- `close_reason_category`
- `close_reason_label`
- `closed_note` or keep `closed_reason` as the note field with clear docs

It may keep the legacy `closure_type` field temporarily to avoid breaking older clients, but it must not return `administrative` as business meaning. If retained, the response should either return `completed` for completed rows and `null` for non-completed rows, or mark `closure_type` as compatibility-only while the new business fields drive all user-facing logic.

### 6.3 Activate Endpoint Semantics

Implement:

- `POST /api/projects/{project_id}/lifecycle/activate`
- request fields:
  - `reason`: required non-empty activation reason/note;
  - `operator`: optional operator identity.

Activation is allowed from:

- `stopped`
- `closed`, including rows whose close reason category is `completed`

Activation is rejected from:

- `active`, with a structured `409 project_lifecycle_conflict`.
- closed legacy rows where no recoverable previous project status exists in audit metadata or new persisted compatibility metadata. The implementation must not guess a project progress status such as `draft` or `ltr_registered`.

Activation result:

- sets `lifecycle_state="active"`;
- clears close overlay fields that should no longer describe the current state, while preserving close history in `project_lifecycle_events`;
- restores `Project.status` from a recorded previous project status;
- records `resumed_*` fields for compatibility or introduces explicit `activated_*` API aliases, but the public action vocabulary is `activate`.

### 6.4 Activation Reason Requiredness

Activation reason/note is required in v1.

Reason:

- TASK_345A requires close/activate audit history to preserve reasons, operator, time, and previous close information.
- A required note avoids ambiguous activation from closed Completed or other business-close reasons.
- Frontend lanes can later provide concise inline validation around this backend rule.

### 6.5 Audit / Event Ledger Metadata

Add new event type(s):

- `close`
- `activate`

Keep existing `stop`, `resume`, `close_completed`, and `close_administrative` readable for legacy history.

New close events must record:

- previous lifecycle state;
- new lifecycle state;
- previous project status;
- close reason category;
- close note;
- operator;
- timestamp;
- legacy closure type mapping when applicable;
- any compatibility route metadata.

New activate events must record:

- previous lifecycle state;
- previous project status;
- restored project status;
- previous close reason category;
- previous close note;
- previous closure type when present;
- activation reason;
- operator;
- timestamp.

`project_lifecycle_events.metadata_json` is sufficient for these metadata fields in v1. A new event table is not planned.

### 6.6 Error Contract

Lifecycle action errors should keep the structured 409 shape:

- `code`
- `project_id`
- `lifecycle_state`
- `message`
- `allowed_actions`

Add business close/activation fields where useful:

- `close_reason_category`
- `close_reason_label`
- `can_activate`

Do not expose `administrative` in error `message` or business fields. If legacy `closure_type` remains in error details for compatibility, it must not be used as user-facing guidance.

### 6.7 Tests And Migration Checks

Future implementation tests should cover:

- unified close endpoint closes active formal/registered projects with each reason category;
- unified close endpoint can close temporary projects only when the accepted business contract allows it, without public-drive LTR authority side effects;
- completed close no longer requires a special completed-only API path;
- compatibility `close-completed` wrapper maps to `reason_category="completed"`;
- compatibility `close-administrative` wrapper maps to `reason_category="other"` and does not return `administrative` as business reason;
- stopped activation restores previous project status from stop event metadata;
- closed activation restores previous project status from close event metadata;
- closed completed activation is allowed when previous status is recoverable;
- legacy closed without recoverable previous status returns a structured conflict instead of guessing;
- activation requires a non-empty reason;
- event ledger stores close and activate metadata, including previous close type/reason;
- migration backfills `close_reason_category` for completed/admin/unknown legacy closed rows;
- old lifecycle baseline tests are updated from `resume`/split close expectations to `activate`/unified close expectations;
- write guards are not changed in TASK_345B except where lifecycle response allowed action metadata is required for the new API. Full write guard rule changes remain TASK_345C.

## 7. Future Implementation File List

These files are not editable in this Developer planning-first pass. They are the exact future implementation candidate list after Reviewer implementation-readiness gate and explicit implementation routing:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
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
- `tests/unit/test_project_lifecycle_write_guard.py` only for baseline assertions that must remain unchanged until TASK_345C

Implementation should not modify frontend files, `frontend/src/api/client.ts`, Projects registry files, public-drive LTR workbook authority code, or write-guard behavior beyond necessary response compatibility.

## 8. Downstream Lane Dependencies

TASK_345B is serially before:

- `TASK_345C` lifecycle write guard and readonly rule update.
- `TASK_345D` frontend Workbench primary action UI.
- `TASK_345E` Projects registry copy/routing realignment.
- `TASK_345F` Temporary Apply/Register LTR entrypoint if not folded into Workbench UI.
- `TASK_345H` lifecycle audit/migration/QA closeout.

TASK_345G public-drive LTR workbook authority writing remains separate and later; it must not be pulled into TASK_345B.

## 9. Developer Planning-First Lane Boundary

Lane: `project-lifecycle-activation-model-api`

Task: `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`

Status: `approved - implementation authorized, pending Developer implementation`

Owner Role: Developer implementation, then Reviewer/QA/Integrator gates

Depends On:

- TASK_345A accepted contract;
- user approval for downstream lane creation;
- Reviewer plan gate pass from the current Orchestrator/User delegation;
- Developer planning-first completion;
- Reviewer implementation-readiness callback pass;
- user approval for Developer implementation;
- current repository lifecycle state/API evidence.

May Touch For Developer Implementation:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
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
- `tests/unit/test_project_lifecycle_write_guard.py` only for baseline assertions that must remain unchanged until TASK_345C
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`

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

- All frontend, API-client, Projects registry, public-drive LTR authority, Office, Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive, StepInstance, Report, AI, permissions, LAN/server, and multi-user paths are locked.
- Backend/API/schema/test paths outside the implementation May Touch list are locked.
- Existing dirty product/governance residuals remain excluded unless a future approved lane names them.

Evidence Files:

- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md`

Validation Gate:

- Focused backend lifecycle state service tests pass.
- Focused lifecycle API tests pass.
- Lifecycle migration tests pass.
- Registry summary lifecycle compatibility tests pass when affected.
- `tests/unit/test_project_lifecycle_write_guard.py` remains behaviorally scoped to baseline preservation until TASK_345C.
- `git diff --check` over TASK_345B changed files.
- Static targeted status check records no frontend/API-client/public-drive LTR authority/future-scope files changed by TASK_345B.

Merge Gate:

- Developer evidence reaches `ready_for_review`.
- Reviewer implementation gate passes with no blocking findings.
- QA gate is required if Reviewer or Integrator determines migration/API smoke needs independent validation; otherwise Integrator may package after Reviewer pass and focused backend validation.
- Integrator confirms only allowed TASK_345B backend/API/test/evidence/board files are included.

## 10. Implementation Authorization Reconciliation

Planner reconciliation on 2026-06-28 records:

- Reviewer implementation-readiness passed via conversational callback, but no separate Reviewer checkpoint file exists.
- User explicitly approved the Developer implementation pass after that callback.
- Developer implementation legality check correctly blocked because repository source-of-truth still showed `planned`.
- The reconciliation evidence file closes that source mismatch and updates the task/plan/board to implementation authorized.

The object ready for the next implementation route is:

`TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API` / lane `project-lifecycle-activation-model-api`.

## 11. Stop Point

Stop after Developer implementation evidence reaches `ready_for_review`. Do not implement TASK_345C write guards, frontend UI, Projects registry, Temporary LTR authority, or future scope in this task.
