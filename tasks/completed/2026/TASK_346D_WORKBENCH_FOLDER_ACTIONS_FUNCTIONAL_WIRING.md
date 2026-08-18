# TASK_346D Workbench Folder Actions Functional Wiring

Status: complete/accepted after Developer implementation, Reviewer implementation re-gate, QA gate, and Integrator packaging/readiness
Lane: workbench-folder-actions-functional-wiring
Owner Roles: Frontend Developer / Reviewer / QA / Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-30

## 1. Purpose

Create the formal planning-first lane that connects the accepted Workbench Folder Actions UI to the accepted `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` public folder workflow API.

TASK_346D is the frontend API-client and Workbench wiring lane for:

- public folder workflow context
- backend-owned Auto sync preference
- Sync preview / execute
- Submit preview / execute
- Pull preview / execute
- business-readable blockers, conflicts, preview summaries, confirmations, and result feedback

This lane is complete/accepted after Developer implementation, Planner B1 scope reconciliation, Developer B2/B3 fix pass, Reviewer implementation re-gate, QA gate, and Integrator packaging/readiness. Planner scope reconciliation accepts the Workbench bridge files as necessary to pass public-folder workflow state and handlers from `useProjectWorkbenchModel` into the actual active-Matrix and lifecycle/no-Matrix Folder Actions surfaces. The unrelated LTR workbook local settings helper diff in `frontend/src/api/client.ts` remains excluded from the TASK_346D package.

## 2. Why This Follows TASK_346C

- `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT` defines the downstream sequence: UI refocus, backend public folder workflow, frontend functional wiring, then integration QA.
- `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS` and `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH` completed the safe frontend Folder Actions shell with disabled placeholders.
- `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` completed and accepted the backend/API/file-operation foundation, including `GET /context`, `PUT /auto-sync`, preview endpoints, execute endpoints, preview hash validation, submit lock, operation audit, and temp-dir safety.
- The next missing product capability is frontend consumption of the accepted backend contract. End-to-end temp-dir QA belongs after this wiring in `TASK_346E`.

## 3. Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product UI guidance
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `tasks/TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND.md`
- `docs/task_346c_public_folder_workflow_backend_plan.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_qa.md`
- Current Workbench Folder Actions frontend code and focused tests.

## 4. User / Repository Confirmed Facts

- Folder Actions should remain a compact contextual file operation panel, not a readiness/status dashboard.
- Backend public folder workflow is accepted and preview-first.
- TASK_346C exposes typed route contracts for context, auto-sync preference, sync/submit/pull preview, and sync/submit/pull execute.
- TASK_346B/F frontend currently leaves Open, Auto sync, Sync now, Submit, and Pull disabled or placeholder-only.
- `frontend/src/api/client.ts` is the only allowed fetch boundary.
- React components must not contain filesystem business logic.
- Real `D:\Test Project`, `D:\PublicProject`, public-drive folders, and LTR workbook files must not be touched by this lane.

## 5. Scope

TASK_346D may plan and later implement frontend wiring only:

- Add typed frontend API DTOs and helper functions for `TASK_346C` endpoints.
- Load public folder workflow context in the Workbench model.
- Persist Auto sync preference through the backend `PUT /auto-sync` endpoint.
- Wire Sync, Submit, and Pull buttons to preview-first frontend flows.
- Require explicit operator confirmation before execute.
- Pass backend `preview_hash` and confirmation flags to execute calls.
- Refresh context/previews after execute.
- Render backend blockers, warnings, conflicts, and result feedback as short business-readable messages.
- Preserve TASK_346F compact contextual panel layout and avoid resurrecting old readiness/status-card copy.

## 6. Out Of Scope

TASK_346D must not implement:

- backend model/API/schema/service changes
- public folder resolver changes
- file-operation safety logic in React
- real OS folder opening for `Project folder / Open`
- old public-drive upload helper behavior as the accepted Sync/Submit/Pull workflow
- Projects list or registry changes
- Matrix Editor business logic
- real folder mutation outside backend API calls
- public-drive LTR workbook authority writes
- StepInstance, Report generation, AI review, permissions, LAN/server, or multi-user scope
- release-engineering or governance residual cleanup

## 7. Functional Wiring Contract

### 7.1 API Client

Add typed helpers in `frontend/src/api/client.ts` for:

- `getPublicFolderWorkflowContext(projectId)`
- `setPublicFolderWorkflowAutoSync(projectId, autoSyncEnabled)`
- `previewPublicFolderWorkflowSync(projectId)`
- `executePublicFolderWorkflowSync(projectId, request)`
- `previewPublicFolderWorkflowSubmit(projectId)`
- `executePublicFolderWorkflowSubmit(projectId, request)`
- `previewPublicFolderWorkflowPull(projectId)`
- `executePublicFolderWorkflowPull(projectId, request)`

DTOs must mirror accepted backend fields without exposing raw API paths in UI components.

### 7.2 Workbench Model

Extend `useProjectWorkbenchModel` or a narrow project-workbench feature hook to own:

- public folder workflow context state
- operation preview state for sync/submit/pull
- operation result state
- loading/busy/error flags per operation
- auto sync toggle busy/error state
- refresh helpers after execute

### 7.3 Folder Actions UI

The existing `ProjectFolderTaskList`/selector surface should:

- show backend context facts only when returned by TASK_346C
- keep context terse: path fragments, `Open\<year>`, `Closed\<year>`, submit lock, conflicts, or missing settings
- enable `Sync now`, `Submit`, and `Pull` only when the latest preview/context allows it
- keep `Project folder / Open` disabled unless a separate platform-safe open helper already exists and is explicitly allowed by Reviewer
- never show old Folder Actions copy such as `Ready`, `Partial`, `Waiting`, `Not current`, `Already current`, `Ready to upload`, `Request material`, `Source material`, `Project Folder progress`, `Next step`, `Public drive upload`, `Upload to public drive`, or `Refresh public-drive preview`

### 7.4 Confirmation

Execution must be preview-first:

- click operation -> fetch preview
- if preview has blockers/conflicts -> show short blocker/conflict result and do not execute
- if preview requires confirmation -> require explicit operator confirmation
- execute sends `preview_hash`, `confirmed: true`, and `confirm_directory_creation` when needed
- stale preview/conflict responses remain visible and do not retry automatically

## 8. May Touch

Planner/Reviewer may touch now:

- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_planner.md`
- `docs/task_board.md`

Developer implementation may touch only:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/publicFolderWorkflowSelectors.ts`
- `frontend/src/features/project-workbench/publicFolderWorkflowSelectors.test.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css` only for existing Folder Actions confirmation/blocker/result state styling, not panel redesign
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`
- TASK_346D task/plan/evidence/board docs via normal lane flow

## 9. Must Not Touch

- `backend/**`
- `tests/**` backend tests
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- real LTR workbook files
- public-drive LTR workbook authority writes
- `.agents/**`
- `docs/project_management/**`
- release-engineering residuals: `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts/tests, release task/docs, and `temp_agents_stash.md`
- unrelated LTR workbook local settings helpers
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 10. Locked Paths

- `backend/**`
- `tests/**` outside focused frontend tests
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`
- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests
- release task/docs
- `temp_agents_stash.md`

## 11. Validation Gate

Reviewer plan gate must confirm:

- TASK_346D is frontend API-client/Workbench wiring only.
- TASK_346C backend API contract is stable enough for frontend consumption.
- `frontend/src/api/client.ts` is allowed only for typed TASK_346C helpers.
- React components do not contain filesystem business logic.
- Sync/Submit/Pull remain preview-first and confirmation-gated.
- `Project folder / Open` remains disabled unless a platform-safe helper is already present and explicitly allowed.
- UI preserves TASK_346F compact contextual panel and does not restore old readiness/status-card vocabulary.
- Real folder and LTR workbook paths remain untouched.

Future Developer validation must include:

- Focused frontend API client/static or unit coverage for TASK_346C helper paths and request bodies.
- Focused Workbench model tests for context load, auto-sync update, preview, execute, stale/conflict/error handling, submit lock refresh, and no automatic retry.
- Focused selector/component/layout tests for enabled/disabled states, blocker copy, confirmation state, and banned old Folder Actions vocabulary.
- `npm run build`.
- Browser smoke on an accepted Workbench fixture verifying the Folder Actions panel consumes backend context without executing real Sync/Submit/Pull against real folders.
- Targeted status proving no backend, Projects registry, Matrix Editor, real folder, LTR workbook, release residual, `.agents`, or `docs/project_management` paths changed.

## 12. Merge Gate

No implementation merge is possible from this Planner pass.

Future implementation can merge only after:

- Developer evidence proves scoped frontend-only API-client/Workbench wiring changes.
- Reviewer B2/B3 are resolved without expanding scope beyond the updated May Touch list.
- Focused frontend tests pass.
- `npm run build` passes or existing warnings are classified.
- Reviewer implementation gate passes.
- QA browser smoke runs if routed.
- Integrator confirms no backend/API schema/Projects/Matrix/real-folder/LTR/future-scope/release residuals are packaged.

## 13. Definition Of Ready

Definition of Ready for planned lane and Reviewer plan gate: satisfied.

Definition of Ready for Developer implementation: satisfied after Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness pass, and explicit user approval recorded by Planner reconciliation.

Blocking clarification questions: none.

## 14. Stop Point

Current stop point: complete/accepted by Integrator. Do not start TASK_346E+ without a separate Orchestrator/Planner/user routing action.

Do not exceed the approved TASK_346D frontend API-client / Workbench wiring scope.

## 15. Scope Reconciliation For Reviewer B1

Planner scope reconciliation on 2026-06-30 added these Workbench bridge files to Developer May Touch:

- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`

Rationale:

- `useProjectRuntimeConsoleModel.ts` is the existing bridge that selects which `useProjectWorkbenchModel` fields reach the runtime console/layout.
- `ProjectWorkbenchActiveMatrixWorkspace.tsx` hosts the active Matrix right-rail Folder Actions surface.
- `ProjectWorkbenchLifecycleSections.tsx` hosts the lifecycle/no-Matrix Folder Actions surfaces.
- Without these bridge touches, Sync/Submit/Pull/Auto sync state and handlers can be created in the model but will not reach the actual user-facing Folder Actions panel, leaving TASK_346D functionally incomplete.

This reconciliation does not authorize backend/API/schema changes, Projects registry changes, Matrix Editor business logic, real folder or LTR workbook access, unrelated release residuals, or unrelated LTR workbook local settings helpers.
