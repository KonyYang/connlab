# Discovery: Project Lifecycle Business Model Rework

Date: 2026-06-28
Role: Planner
Status: discovery_checkpoint
Discovery scope: Project lifecycle business model rework after TASK_344C
Approved lane created: no
Product code changed: no

## Current Phase / Task / Role

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task/lane: none. `docs/task_board.md` reports `TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT` complete and accepted, with no active implementation lane.
- Current role: Planner.
- Why allowed: the user requested a Planner Discovery Gate for a broad lifecycle business model change and explicitly forbade approved lane creation, product code edits, and Developer routing.

## User Goal Restatement

The user is changing the lifecycle business model away from the accepted TASK_336 to TASK_344 contract. The main Workbench lifecycle action should become one primary action. Active projects should show `Close project`; stopped and closed projects should support `Activate / Reopen project`, so close is a business phase transition, not irreversible archival. Temporary projects should independently support `Apply LTR number` / `Register LTR` and enter the formal project flow. Audit history must preserve close/reopen timing, reasons, operator, and the previous close type/reason. UI copy must use business-readable close reasons such as Completed, Failed, Cancelled, Cannot test, Duplicate, and Other, not internal `administrative` wording.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context through `node .agents/skills/impeccable/scripts/load-context.mjs`
- `.agents/skills/impeccable/reference/product.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`
- `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md`
- `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
- `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`
- `docs/task_338_project_lifecycle_write_guard_integration_plan.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`
- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md`
- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `tasks/TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT.md`
- `docs/task_344c_no_matrix_workbench_empty_state_alignment_plan.md`
- selected TASK_343 and TASK_344 developer/QA evidence files
- Backend lifecycle code:
  - `backend/domain/enums.py`
  - `backend/domain/models.py`
  - `backend/application/project_lifecycle_state_service.py`
  - `backend/application/project_lifecycle_service.py`
  - `backend/application/project_lifecycle_write_guard.py`
  - `backend/application/project_lifecycle_management_service.py`
  - `backend/api/routes_project.py`
  - `backend/infrastructure/storage/models.py`
  - `backend/infrastructure/storage/database.py`
  - `backend/infrastructure/storage/repositories/project.py`
  - `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- Frontend lifecycle and registry code:
  - `frontend/src/api/client.ts`
  - `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
  - `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
  - `frontend/src/pages/ProjectListPage.tsx`
- Relevant tests were inspected by file discovery and targeted text search:
  - backend lifecycle state/API/guard tests
  - frontend project lifecycle readonly, Workbench shell/layout/close, and Projects registry tests

## Confirmed By User

- The main Workbench lifecycle action should be simplified to one primary button.
- Active projects should show `Close project`.
- Closed and stopped projects should support `Activate / Reopen project`.
- `Close project` is a business phase transition, not irreversible archive sealing.
- Temporary projects should independently support `Apply LTR number` / `Register LTR`.
- Audit history must not be lost. It must record close/reopen time, reason, operator, and previous close type.
- UI must not expose internal `administrative` terminology.
- UI close reasons should be business-readable, including Completed, Failed, Cancelled, Cannot test, Duplicate, and Other.
- This turn must not create approved lanes, write product code, route Developer implementation, or implement future StepInstance/Report/AI/permissions/LAN/server/multi-user scope.

## Confirmed By Repository Evidence

- Board state: `docs/task_board.md` says TASK_344C is complete/accepted and no implementation lane is active.
- Existing contract: TASK_336 explicitly says closed projects are readonly archives and cannot resume.
- Existing backend enum model:
  - `ProjectLifecycleState = active | stopped | closed`
  - `ProjectClosureType = completed | administrative`
  - `ProjectLifecycleEventType = stop | resume | close_completed | close_administrative`
- Existing backend transition behavior:
  - active can stop and close.
  - stopped can resume and close.
  - closed cannot stop, resume, or close again.
  - close completed is restricted to formal/registered projects.
  - close administrative can close active or stopped projects.
  - closed views return `allowed_actions=()`.
- Existing backend persistence:
  - project rows store lifecycle overlay fields, stopped/resumed/closed timestamps, operators, reasons, `closure_type`, and completion summary JSON.
  - `project_lifecycle_events` stores transition events with previous/new lifecycle state, previous/new closure type, reason, operator, created_at, and metadata JSON.
  - migration backfills old `status='closed'` rows to `lifecycle_state='closed'` and `closure_type='administrative'`.
- Existing write guards:
  - stopped projects are readonly except lifecycle actions, with allowed actions `resume, close`.
  - closed completed/admin projects are readonly and expose no lifecycle write action.
  - legacy `ProjectLifecycleService` still treats `ProjectStatus.CLOSED` and `ProjectStatus.CANCELLED` as closed-style blockers for older operation guards.
- Existing frontend API client:
  - exposes `closeProjectCompletedLifecycle(...)`
  - exposes `closeProjectAdministrativeLifecycle(...)`
  - has no reopen/activate lifecycle client helper.
  - still types closure as `"completed" | "administrative"`.
- Existing Workbench frontend:
  - `deriveProjectLifecycleReadonlyView(...)` maps closed completed/admin to readonly modes with no resume or close.
  - `deriveProjectWorkbenchLifecycleActions(...)` exposes Stop for active, Resume for stopped, and Close for active/stopped.
  - `ProjectWorkbenchCloseConfirmation.tsx` renders `Close as completed` and `Close administratively`.
  - close admin UI copy includes "Administrative close" and "Administrative reason".
  - `ProjectWorkbenchShellModel` labels closed as `Read-only archive`.
  - Temporary formalization currently shows `Convert to Formal Project`, but `ProjectWorkbenchLayout` only sets a message: "Same-project LTR registration is not wired yet. This temporary project stays intact; no duplicate project was created."
- Existing Projects registry frontend:
  - closed rows show `Closed: Completed`, `Closed: Administrative`, `Open archive`, and readonly archive next-step copy.
  - stopped temporary projects remain Planning; stopped registered projects remain On-going.
  - registry is routing-only and does not expose lifecycle mutation controls.
- Existing TASK_344A QA evidence records the local smoke data gap: zero closed rows were available in the current environment at that time.
- Existing TASK_344C QA evidence shows active no-Matrix registered and temporary/no-LTR fixtures have lifecycle `allowed_actions = stop, close`.

## Inferred By Planner

- This needs a formal lane series, not a quick fix, because the new business model reverses a core accepted contract from TASK_336/TASK_337A/TASK_338/TASK_339A/TASK_343B/TASK_343C.
- The safest first lane is a contract/planning lane that replaces the old "closed readonly archive, administrative close" semantics before any backend or frontend implementation.
- Backend changes must precede frontend implementation because there is no reopen/activate API or frontend client helper yet.
- Write guard changes must be serial after the backend lifecycle contract because closed projects may remain readonly until reopened, but lifecycle reopen must become an allowed action.
- Temporary LTR registration should be split from close/reopen unless the user confirms it should share the same backend/API lane. It may touch LTR authority and public-drive workbook workflows, which are high-risk and explicitly guarded by AGENTS.md.
- UI labels should probably distinguish "Activate project" for stopped from "Reopen project" for closed, but this is not yet confirmed.
- Existing `project_lifecycle_events.metadata_json` may be enough to store previous close reason/type details, but the current enum/event model does not name a reopen event and current response DTO does not expose history. A formal backend lane must decide whether to extend the existing event ledger or add a lifecycle history endpoint.

## Not Yet Confirmed

1. Exact public action labels and state terms:
   - Should stopped use `Activate project`, `Resume project`, or `Reopen project`?
   - Should closed use `Reopen project` only?
   - Should the one primary button vary by state or always be a generic primary lifecycle button?
2. Exact close reason taxonomy and data model:
   - Is `Completed` one close reason among several, or does it keep a special completed-close confirmation with output summary acknowledgement?
   - Are `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, and `Other` a closed reason enum, a free-text reason category, or both category plus note?
3. Temporary LTR authority path:
   - Should `Apply LTR number` from a temporary Workbench reuse the existing New Project LTR application workflow and write to the public-drive LTR workbook in this phase?
   - Or should it only create a local planning-to-formal transition pending a later LTR authority lane?

These unknowns materially affect API shape, DB migration, write guard behavior, frontend labels, May Touch, validation, and serial ordering. Therefore no lane should be marked approved from this checkpoint.

## Current State Machine vs Target Business Model

| Area | Current repository behavior | Target user direction | Gap |
|---|---|---|---|
| Active lifecycle action | Active exposes Stop and Close via `allowed_actions=["stop","close"]`; Workbench can show Stop plus Close options. | Active should show one primary `Close project` action. | Need action priority and possibly hide Stop from primary UI or move it to future/secondary scope. |
| Stopped lifecycle action | Stopped is readonly, can Resume and Close. | Stopped should support Activate/Reopen, not permanent readonly. | Backend already supports resume, but naming and one-primary-button UX must change. Close from stopped may need removal or secondary policy. |
| Closed lifecycle action | Closed is readonly archive, cannot resume, `allowed_actions=()`. | Closed should support Activate/Reopen. | Requires backend transition, DTO, frontend client, write guard exception, UI model, registry copy, tests, and audit. |
| Close meaning | Close means completed or administrative archive. Closed cannot resume. | Close means business stage end, not irreversible archive. | Requires contract rewrite and migration from archive semantics. |
| Close reasons | Backend `closure_type` is completed/admin. UI exposes `Close administratively`. | UI should use business reasons Completed/Failed/Cancelled/Cannot test/Duplicate/Other. | Requires data model/API/copy rewrite and removal of admin terminology from user-facing surfaces. |
| Completed close | Special endpoint requires formal/registered identity, close note, manual confirmation, output summary acknowledgement. | Completed remains a business reason, but exact confirmation requirements are not fully confirmed. | Need user decision whether Completed keeps output summary acknowledgement as a special close variant. |
| Audit history | Event ledger exists for stop/resume/close completed/admin, with previous/new states, closure type, reason, operator, timestamp, metadata. | Audit must preserve close/reopen time, reason, operator, and previous close type. | Need reopen/activate event type and possibly explicit close reason category/history exposure. |
| Readonly/write guard | Stopped and closed block selected writes; stopped error allows resume/close, closed allows no action. | Stopped/closed may still block business writes until activated/reopened, but lifecycle activation must be allowed. | Need guard update for closed allowed action and all error messages. |
| Temporary to formal | Temporary project exists and Workbench has a "Convert to Formal Project" button, but same-project LTR registration is not wired. | Temporary project should independently support `Apply LTR number` / `Register LTR`. | Requires a separate high-risk workflow lane touching LTR authority and project identity flow. |
| Projects registry | Closed view shows readonly archive and `Open archive`; stopped rows route to Workbench. | Registry should align with reopenable closed/stopped semantics and likely route to Workbench with activation/reopen copy. | Needs copy/routing update after backend/frontend lifecycle API is stable. |
| UI internal wording | User-facing UI includes "Administrative", "administratively", "Open archive", "Read-only archive". | UI should avoid internal `administrative` wording. | Needs frontend copy sweep and test assertions. |

## Formal Lane Need

Formal lanes are required.

Reasons:

- The user direction invalidates the accepted TASK_336 lifecycle contract and many downstream completed tasks.
- Backend enum/API/schema/service behavior must change before frontend can safely implement the new model.
- Closed reopen affects write guards, readonly errors, Projects registry classification, Workbench shell, and QA smoke data.
- Temporary LTR registration may touch public-drive LTR authority, which AGENTS.md requires to preserve.
- Audit history and migration are cross-cutting and need explicit validation.

This Discovery checkpoint is not an approved lane and must not be routed to Developer.

## Recommended Task Split

### TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT

Type: Planner / contract
Status recommendation: proposed only, pending user answers

Goal:
Define the new lifecycle semantics before implementation: active close, stopped activate/reopen, closed reopen, close reason taxonomy, temporary LTR entrypoint boundary, audit/history requirements, and UI copy rules.

May Touch draft:

- `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- `docs/task_board.md` planning/proposed section only after explicit user approval

Must Not Touch draft:

- product code
- backend/API/schema files
- frontend runtime files
- tests
- public-drive/Office/LTR authority files
- completed TASK_336 to TASK_344 source files except read-only reference
- unrelated governance/orchestration residuals

Locked Paths draft:

- none for product code
- proposed planning files above if created

Validation Gate draft:

- Contract states exact lifecycle transitions, public UI copy, API intent, reason taxonomy, audit requirements, temporary LTR boundary, non-goals, and downstream lane split.
- No product code diff.

Merge Gate draft:

- User accepts contract.
- Reviewer plan gate passes if project protocol requires plan review.

### TASK_345B_PROJECT_LIFECYCLE_BACKEND_REOPEN_CLOSE_REASON_API

Type: backend/API/schema/tests
Status recommendation: proposed, blocked by TASK_345A

Goal:
Implement backend lifecycle state model/API for close reasons and reopen/activate while preserving audit history.

May Touch draft:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/application/project_lifecycle_state_service.py`
- `backend/api/routes_project.py`
- `backend/api/lifecycle_errors.py` only if error details change
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/repositories/project.py`
- `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- focused backend lifecycle tests under `tests/unit/` and `tests/integration/`
- lane task/plan/evidence files

Must Not Touch draft:

- frontend implementation
- public-drive/Office/LTR workbook write behavior
- Matrix/Fee/Folder/Basic Information business logic outside lifecycle API contract
- StepInstance, Report, AI, permissions, LAN/server, multi-user
- Projects registry UI
- Workbench UI

Locked Paths draft:

- backend lifecycle state/service/API/model/repository files listed above
- backend lifecycle tests listed by the approved plan

Validation Gate draft:

- Unit tests for active close, stopped activate/reopen, closed reopen, reason taxonomy, audit event creation, idempotency/conflict rules.
- API tests for GET lifecycle, close, activate/reopen.
- Migration tests for old `administrative` closure compatibility.
- Audit/history assertions include previous close type/reason, timestamp, operator.

Merge Gate draft:

- Reviewer backend gate pass.
- Integrator reruns focused backend lifecycle/API/write-guard baseline tests.

### TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_AND_READONLY_RULES

Type: backend write guard/tests
Status recommendation: proposed, blocked by TASK_345B

Goal:
Update write guards and readonly errors so stopped/closed still block business writes until activated/reopened, while lifecycle activation/reopen remains allowed and errors point to the correct business action.

May Touch draft:

- `backend/application/project_lifecycle_write_guard.py`
- `backend/application/project_lifecycle_service.py`
- backend API route handlers that translate lifecycle readonly errors
- focused write guard tests
- integration tests for guarded Matrix/Fee/Folder/LTR/Basic Information writes
- lane task/plan/evidence files

Must Not Touch draft:

- frontend implementation
- LTR workbook authority writeback behavior
- Matrix/Fee/Folder business rules except guard calls and messages
- schema changes unless TASK_345B explicitly leaves a necessary guard field gap
- future scope

Locked Paths draft:

- lifecycle write guard files and tests approved in this lane

Validation Gate draft:

- Stopped and closed reject covered business writes.
- Stopped allows lifecycle activate.
- Closed allows lifecycle reopen.
- Error details expose business-readable allowed action, not `administrative`.
- Readonly preview endpoints remain available where non-mutating.

Merge Gate draft:

- Reviewer backend gate pass.
- Integrator reruns focused write guard tests and affected API smoke tests.

### TASK_345D_TEMPORARY_PROJECT_LTR_REGISTRATION_ENTRYPOINT

Type: backend/API plus possible frontend entrypoint, likely split after contract
Status recommendation: proposed, blocked by TASK_345A and user answer on LTR authority path

Goal:
Define and implement how a temporary/no-LTR project applies/registers an LTR and becomes a formal registered project without creating a duplicate project.

May Touch draft:

- To be narrowed by TASK_345A and user answer.
- Likely backend application/API files for project creation completion, LTR registration, project identity, registry summary, and temporary context.
- Possibly frontend Workbench temporary action files after backend API is stable.
- focused LTR/project identity tests
- lane task/plan/evidence files

Must Not Touch draft:

- public-drive LTR workbook authority unless explicitly approved for this lane
- Office gateway internals unless explicitly approved
- lifecycle close/reopen UI except reading the new lifecycle contract
- Matrix/Fee/Folder/Report/StepInstance/future scope

Locked Paths draft:

- To be defined after user confirms whether public-drive LTR workbook writeback is in scope.

Validation Gate draft:

- Temporary project can apply/register LTR to the same project.
- Registry identity changes from temporary to registered.
- Temporary context disposition is explicit.
- LTR authority path is preserved.
- No duplicate project is created.

Merge Gate draft:

- Reviewer gate and QA smoke required.
- Integrator confirms no public-drive authority regression.

### TASK_345E_WORKBENCH_SINGLE_PRIMARY_LIFECYCLE_ACTION_UX

Type: frontend Workbench UX/tests
Status recommendation: proposed, blocked by TASK_345B and TASK_345C; may also depend on TASK_345D for temporary LTR button

Goal:
Implement one primary Workbench lifecycle action per state using the new business model.

May Touch draft:

- `frontend/src/api/client.ts` only if TASK_345B adds accepted DTO/client endpoints
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx` or replacement close component
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- focused Workbench lifecycle tests
- `frontend/src/workbench.css` only for necessary layout/state styling
- lane task/plan/evidence files

Must Not Touch draft:

- backend/API/schema unless separately approved
- Projects registry implementation
- Matrix Editor business logic
- Fee/Folder/Basic Information/LTR authority behavior except temporary LTR entrypoint if explicitly included
- StepInstance, Report, AI, permissions, LAN/server, multi-user
- unrelated governance residuals

Locked Paths draft:

- Workbench lifecycle UI/model files listed above during implementation

Validation Gate draft:

- Active shows one primary `Close project`.
- Stopped shows one primary Activate/Reopen action per approved copy.
- Closed shows one primary Reopen/Activate action per approved copy.
- Temporary shows Apply/Register LTR entrypoint if TASK_345D is available, otherwise explicitly disabled/withheld per contract.
- UI has no user-facing `administrative` text.
- Audit/result messages are business-readable.
- Existing Matrix/Folder/Fee readonly behavior does not regress.

Merge Gate draft:

- Reviewer frontend gate pass.
- QA browser smoke for active, stopped, closed, temporary/no-LTR, registered/no-Matrix, active Matrix states.
- Integrator verifies no backend or registry scope leakage.

### TASK_345F_PROJECTS_REGISTRY_LIFECYCLE_COPY_ROUTING_REALIGNMENT

Type: frontend Projects registry UX/tests
Status recommendation: proposed, blocked by TASK_345B and likely TASK_345E

Goal:
Align `/projects` list status, next step, and action copy with reopenable closed/stopped semantics while preserving routing-only authority.

May Touch draft:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css` only if copy/layout requires adjustment
- lane task/plan/evidence files

Must Not Touch draft:

- backend/API/schema
- frontend API client unless TASK_345B accepted DTO changes are not yet reflected
- Workbench lifecycle behavior
- lifecycle mutation controls in Projects list
- TASK_345D temporary LTR implementation
- future scope and unrelated governance residuals

Locked Paths draft:

- Projects registry helper/page/test/CSS files approved for this lane

Validation Gate draft:

- Closed rows no longer imply irreversible archive.
- Stopped rows route to Workbench with Activate/Reopen next step copy.
- Active rows route to Workbench with close-ready or current-work copy as defined by contract.
- Temporary rows route to Workbench and expose Apply/Register LTR only in Workbench, not direct registry mutation, unless explicitly approved otherwise.
- No direct Stop/Close/Reopen mutation controls are added to Projects list.

Merge Gate draft:

- Reviewer frontend gate pass.
- Browser smoke for `/projects` around 514px and normal desktop width.
- Integrator verifies registry remains routing-only.

### TASK_345G_LIFECYCLE_MODEL_MIGRATION_AUDIT_QA_CLOSEOUT

Type: QA/integration/migration evidence
Status recommendation: proposed, final serial closeout after TASK_345B to TASK_345F

Goal:
Validate the full lifecycle model after backend, guards, Workbench, registry, and temporary LTR entrypoint decisions.

May Touch draft:

- QA evidence under `docs/lane_evidence/`
- optional docs-only smoke matrix under `docs/qa_smoke/` if approved
- board closeout only by Integrator after gates

Must Not Touch draft:

- product code
- production/user data
- public-drive/Office/LTR authority files unless a fixture procedure explicitly approved safe access
- future scope

Locked Paths draft:

- QA artifacts/evidence for this lane

Validation Gate draft:

- Backend tests pass for lifecycle/API/audit/write guards.
- Frontend tests pass for Workbench and Projects registry.
- Browser smoke covers active, stopped, closed completed, closed non-completed reason, temporary/no-LTR, registered/no-Matrix, and active Matrix.
- Audit history check verifies close and reopen events with reason/operator/time/previous close type.
- Migration smoke verifies old administrative rows render with business-safe compatibility copy.
- Regression matrix checks no StepInstance/Report/AI/permissions/LAN/server/multi-user surfaced.

Merge Gate draft:

- QA pass.
- Reviewer or Integrator confirms no unresolved blocking findings.
- `docs/task_board.md` closeout by Integrator only.

## Serial Dependencies

1. TASK_345A contract must be first.
2. TASK_345B backend lifecycle model/API/audit must follow the contract.
3. TASK_345C write guard update should follow TASK_345B because it depends on final allowed actions and error details.
4. TASK_345E Workbench UX should wait for TASK_345B/TASK_345C. It should also wait for TASK_345D if the temporary Apply/Register LTR button is expected in the same Workbench pass.
5. TASK_345F Projects registry copy/routing should wait for stable lifecycle response semantics and preferably Workbench primary action semantics.
6. TASK_345G QA/migration/audit closeout is final.

## Parallel Candidates

- After TASK_345A, backend TASK_345B and a narrower TASK_345D planning-only lane could be explored in parallel only if TASK_345D is kept to planning/contract and does not touch LTR authority implementation.
- After TASK_345B stabilizes API shape, frontend Workbench planning and Projects registry planning can proceed in parallel, but implementation should avoid overlapping `frontend/src/api/client.ts` and shared lifecycle display helpers.
- QA fixture/procedure planning can prepare the regression matrix in parallel after TASK_345A, but execution waits for implementation lanes.

## Validation Recommendations

Backend:

- `tests/unit/test_project_lifecycle_state_service.py`
- `tests/integration/test_project_lifecycle_api.py`
- `tests/integration/test_project_lifecycle_migration.py`
- `tests/unit/test_project_lifecycle_write_guard.py`
- affected Matrix/Fee/Folder/LTR/Basic Information readonly integration tests

Frontend:

- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx` or successor tests
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `npm run build`

Browser/manual smoke:

- Active registered with Matrix: primary `Close project`, Matrix remains main surface.
- Active registered/no-Matrix: primary `Close project`, Matrix Editor remains available.
- Stopped project: primary Activate/Reopen action, business writes blocked until activation.
- Closed Completed: primary Reopen, no irreversible archive copy.
- Closed Failed/Cancelled/Cannot test/Duplicate/Other: primary Reopen, business-readable reason.
- Temporary/no-LTR: Apply/Register LTR entrypoint behavior per approved contract.
- `/projects` at 514px and desktop: status/next step/action visible, no internal enum copy.

Audit/history:

- Close event records reason category, note/reason, operator, timestamp.
- Reopen/activate event records previous close reason/type and previous lifecycle state.
- Repeated close/reopen conflict behavior is deterministic.
- Migration of old `administrative` rows has compatibility handling without exposing `administrative` in UI.

Regression matrix:

- No StepInstance, Report generation, AI, permissions, LAN/server, multi-user scope.
- Public-drive LTR workbook authority unchanged unless TASK_345D explicitly includes it.
- Readonly preview endpoints remain available where non-mutating.

## Blocking Clarification Questions

1. For stopped and closed states, should the one primary button labels be state-specific (`Activate project` for stopped, `Reopen project` for closed), or should both use one label?
2. Should `Completed` remain a special close path requiring output status summary acknowledgement and close note, while other close reasons use a simpler reason/note flow?
3. When a temporary project applies/registers an LTR, should this lane write through the current public-drive LTR workbook authority immediately, or only prepare a local formalization step for a later LTR authority lane?

## Recommendation

- Create no approved lane in this turn.
- Treat this checkpoint as the basis for user review.
- If the user answers the three blockers, Planner can create `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT` as a proposed/planned contract lane.
- Do not route Developer until TASK_345A is created, reviewed, accepted, and a downstream implementation lane is separately approved.

## Files Changed By This Discovery

- `docs/lane_evidence/DISCOVERY_project-lifecycle-business-model-rework_planner.md`

## Stop Point

Planner Discovery Gate complete. Stop after callback. Await user direction on the blocking questions and whether to create TASK_345A as a planned contract lane.
