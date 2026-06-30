# TASK_346D Workbench Folder Actions Functional Wiring Plan

Status: complete/accepted after Developer implementation, Reviewer implementation re-gate, QA gate, and Integrator packaging/readiness
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: workbench-folder-actions-functional-wiring
Created: 2026-06-30
Last Updated: 2026-06-30

## 1. Discovery Gate

Current active task/lane:

- No active implementation lane after `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` completed and was accepted by Integrator.
- Current Planner task: create the next formal planning-first Folder Actions lane.

Why Planner is allowed:

- `docs/task_board.md` states there is no active implementation lane and the next TASK_346D+ lane should be decided by Orchestrator/Planner.
- `TASK_346A` recommended `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING` after TASK_346B/C.
- `TASK_346C` accepted evidence explicitly says frontend UI wiring remains downstream TASK_346D/TASK_346E scope.
- The current delegation asks for Planner planning-first only and forbids product code and Developer routing.

## 2. User Goal Restatement

The user wants the Folder Actions series to continue after accepted frontend placeholder/polish work and accepted backend workflow implementation. The next lane should be selected from repository facts, not guesswork. The lane must keep real folder operations behind the accepted backend API and must not touch real public-drive/local folders during planning. This pass creates one formal downstream lane and stops at Reviewer plan gate.

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` product register guidance
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
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_qa.md`
- `tasks/TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND.md`
- `docs/task_346c_public_folder_workflow_backend_plan.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_qa.md`
- `backend/api/routes_public_folder_workflow.py`
- `backend/application/public_folder_workflow_service.py`
- `tests/integration/test_public_folder_workflow_api.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Focused Workbench Folder Actions tests.

## 4. Confirmed By User

- Continue the Folder Actions series with a new formal TASK_346D+ lane.
- Do only Planner planning-first work in this pass.
- Do not route Developer and do not write product code.
- Keep backend/API schema accepted in TASK_346C unless a later approved lane explicitly changes it.
- Keep real `D:\Test Project`, `D:\PublicProject`, real public-drive folders, real LTR workbook files, public-drive authority writes, future scope, release residuals, `.agents`, and `docs/project_management` locked unless separately owned.

## 5. Confirmed By Repository Evidence

- `docs/task_board.md` shows `TASK_346A`, `TASK_346B`, `TASK_346F`, and `TASK_346C` complete/accepted.
- `TASK_346A` recommended downstream lanes:
  - `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS`
  - `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`
  - `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
  - `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA`
- `TASK_346B` and `TASK_346F` intentionally left Folder Actions workflow operations disabled/placeheld and locked `frontend/src/api/client.ts`.
- `TASK_346C` implemented and accepted backend endpoints:
  - `GET /api/projects/{project_id}/public-folder-workflow/context`
  - `PUT /api/projects/{project_id}/public-folder-workflow/auto-sync`
  - `POST /sync/preview`
  - `POST /sync/execute`
  - `POST /submit/preview`
  - `POST /submit/execute`
  - `POST /pull/preview`
  - `POST /pull/execute`
- `TASK_346C` Developer evidence states frontend UI wiring is downstream TASK_346D/TASK_346E scope.
- Current `frontend/src/api/client.ts` contains old public-drive upload helpers but no typed TASK_346C public-folder-workflow helpers.
- Current `ProjectFolderTaskList` and selectors render the accepted contextual panel with placeholder blockers such as `Sync workflow is not connected yet.`
- Current `ProjectWorkbenchLayout` still has old public-drive upload/refresh action handlers, but TASK_346F no longer exposes those old action targets through active Folder Actions UI.

## 6. Planner Inferences

- `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING` is the correct next lane because the backend contract is now accepted and the UI still has placeholders.
- `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA` should remain downstream because it needs frontend wiring before meaningful end-to-end smoke.
- This should be a frontend-only lane with `frontend/src/api/client.ts` explicitly unlocked for TASK_346C typed helpers.
- OS folder opening should remain out of scope because TASK_346C did not implement a platform-safe open-folder API.
- Direct real-folder mutation is not authorized from frontend. UI may call accepted backend preview/execute APIs, but all real file safety remains backend-owned and QA should avoid real roots.

## 7. Not Yet Confirmed

None blocking for a planned lane.

Non-blocking items to be resolved during Developer planning/review:

- Whether confirmation is implemented with a small inline confirmation state or an existing app confirmation pattern.
- Whether `Project folder / Open` remains disabled through TASK_346D or uses an already existing safe non-mutating affordance, if Reviewer confirms one exists.

## 8. Lane Decision

Create exactly one next formal lane:

- Task ID: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
- Lane: `workbench-folder-actions-functional-wiring`
- Status: planned, ready for Reviewer plan gate, not approved implementation
- Recommended next role: Reviewer plan gate

This lane follows TASK_346C because it consumes accepted backend workflow APIs from the Workbench, and it precedes TASK_346E because E2E QA needs frontend wiring.

## 9. Scope Design

### 9.1 API Client

Add typed frontend DTOs and helpers for accepted TASK_346C endpoints in `frontend/src/api/client.ts`.

Required helper families:

- context
- auto-sync preference
- sync preview/execute
- submit preview/execute
- pull preview/execute

The client layer owns `requestJson(...)` calls. UI components must not call `fetch()`.

### 9.2 Workbench Model

Wire state through `useProjectWorkbenchModel` or a narrow feature hook under `frontend/src/features/project-workbench/`:

- load public folder workflow context with other Workbench setup data
- maintain preview/result/error/loading/busy state for sync, submit, and pull
- update backend-owned Auto sync preference
- call preview before execute
- pass `preview_hash`, `confirmed`, and `confirm_directory_creation` to execute
- refresh context and preview state after successful execute

### 9.3 Folder Actions Selectors / Surface

Update selectors and `ProjectFolderTaskList` to:

- consume TASK_346C context/preview state
- show compact context only when real backend fields exist
- enable actions only when preview/context permits
- show blockers/conflicts/warnings as short messages
- preserve TASK_346F layout and avoid old readiness/status vocabulary

### 9.4 Confirmation / Execute Flow

The implementation should remain preview-first:

1. Operator clicks Sync, Submit, or Pull.
2. Frontend fetches the corresponding preview.
3. If blockers or conflicts exist, show them and stop.
4. If ready, require explicit operator confirmation.
5. Execute with the latest `preview_hash`.
6. On stale/conflict response, show backend message and do not retry automatically.
7. On success, refresh context and render concise result feedback.

## 10. May Touch

Planner/Reviewer now:

- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_planner.md`
- `docs/task_board.md`

Future Developer after Reviewer/user gates:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css` only for existing Folder Actions confirmation/blocker/result state styling
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`
- TASK_346D docs/evidence/board via normal lane flow

## 11. Must Not Touch / Locked Paths

Must Not Touch:

- backend implementation, schema, API routes, services, repositories, migrations, and backend tests
- Projects list / registry
- Matrix Editor business logic
- real local/public folders
- real LTR workbook files
- public-drive LTR workbook authority writes
- release-engineering residuals
- unrelated LTR workbook local settings helpers
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

Locked Paths:

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

## 12. Validation Gate

Reviewer plan gate:

- Confirm this is the correct next lane after accepted TASK_346C.
- Confirm frontend-only scope except typed API client consumption of accepted backend endpoints.
- Confirm backend/API schema changes remain locked.
- Confirm Workbench UI remains preview-first and explicit-confirmation based.
- Confirm real folder and LTR workbook paths remain untouched.
- Confirm TASK_346E remains the later integration/QA lane.

Future Developer validation:

- Focused API client tests or static coverage for the new helper paths and execute request bodies.
- Focused Workbench model tests for context, auto-sync, preview, execute, stale/conflict, submit lock, refresh, and no automatic retry.
- Focused selector/component/layout tests for the Folder Actions panel.
- Banned old Folder Actions copy scan over production Workbench files.
- `npm run build`.
- Browser smoke on Workbench verifying context/blocker rendering and no accidental execution against real folders.
- Targeted forbidden-scope status.

## 13. Merge Gate

No merge from this Planner/reconciliation pass.

Future merge requires Developer evidence, focused frontend tests, build, Reviewer implementation gate, QA browser smoke if routed, and Integrator packaging/readiness.

Reviewer B2/B3 must be resolved before merge:

- B2: remove unrelated LTR workbook local settings helpers from `frontend/src/api/client.ts`.
- B3: align public-folder workflow DTO operation id field types with backend `str`.

## 14. Definition Of Ready

Definition of Ready for planned lane and Reviewer plan gate: satisfied.

Definition of Ready for Developer implementation: satisfied by Planner reconciliation after Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness pass, and explicit user approval.

Reasons:

- Dependencies are accepted and verified from task/plan/evidence/board.
- Existing code boundaries and API endpoints are verified.
- May Touch, Must Not Touch, Locked Paths, evidence, validation gate, and merge gate are concrete.
- Acceptance paths are testable with focused frontend tests and non-mutating browser smoke.
- Non-goals prevent backend/file-operation/future-scope creep.

Blocking clarification questions: none.

## 15. Stop Point

Current stop point: Developer implementation pass.

Do not exceed the approved TASK_346D frontend API-client / Workbench Folder Actions functional wiring scope.

## 16. Developer Planning-First Refinement

Developer planning-first status:

- Reviewer plan gate passed per Orchestrator delegation.
- User approved Developer planning-first.
- Developer planning-first completed as docs/evidence only.
- Reviewer implementation-readiness passed by conversational callback per Orchestrator delegation.
- User later explicitly approved TASK_346D reconciliation and Developer implementation.
- Product implementation remains limited to the May Touch and Locked Paths in this plan.

### 16.1 Current Code Findings

Frontend wiring should follow the current project-workbench boundaries:

- `frontend/src/api/client.ts` is the only fetch boundary.
- `useProjectWorkbenchModel.ts` is the current Workbench data and action coordinator.
- `projectFolderTaskSelectors.ts` derives the four Folder Actions row model.
- `ProjectFolderTaskList.tsx` renders the quiet four-row contextual panel and should remain display-focused.
- `ProjectWorkbenchLayout.tsx` owns Workbench action routing and readonly gating.
- Current Folder Actions still use placeholder blockers and no TASK_346C API helpers.
- Current old public-drive upload helpers may remain as legacy code, but TASK_346D should not wire Folder Actions to old `/public-drive/preview` or `/public-drive/upload`.

TASK_346C backend contract is sufficient for frontend consumption:

- `GET /api/projects/{project_id}/public-folder-workflow/context`
- `PUT /api/projects/{project_id}/public-folder-workflow/auto-sync`
- `POST /api/projects/{project_id}/public-folder-workflow/sync/preview`
- `POST /api/projects/{project_id}/public-folder-workflow/sync/execute`
- `POST /api/projects/{project_id}/public-folder-workflow/submit/preview`
- `POST /api/projects/{project_id}/public-folder-workflow/submit/execute`
- `POST /api/projects/{project_id}/public-folder-workflow/pull/preview`
- `POST /api/projects/{project_id}/public-folder-workflow/pull/execute`
- `409` responses are expected for stale preview, conflict, and blocked execute conditions.

### 16.2 Future Implementation File List

Future Developer implementation may touch only these files after Reviewer readiness and explicit implementation approval:

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
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`

Rationale for the new selector file:

- `publicFolderWorkflowSelectors.ts` should keep preview/result summary, action enablement, and short blocker copy out of `useProjectWorkbenchModel.ts` and display components.
- If implementation can keep this logic cleanly inside `projectFolderTaskSelectors.ts`, Reviewer may accept not creating the new selector file. The May Touch list permits the cleaner split.

Files that remain locked:

- `backend/**`
- backend tests
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- real local or public folders
- real LTR workbook files
- `.agents/**`
- `docs/project_management/**`
- release residuals and release task files
- unrelated LTR workbook local settings helpers

### 16.3 API Client Helper Shape

Add typed DTOs mirroring the accepted backend response names and snake_case fields:

- `PublicFolderWorkflowOperationType = "sync" | "submit" | "pull"`
- `PublicFolderWorkflowPreviewStatus = "ready" | "blocked" | "conflict" | "warning" | "current"`
- `PublicFolderWorkflowItemAction = "add" | "update" | "skip" | "conflict" | "move" | "copy_to_history"`
- `PublicFolderWorkflowItemStatus = "ready" | "current" | "conflict" | "failed"`
- `PublicFolderWorkflowItem`
- `PublicFolderWorkflowPreview`
- `PublicFolderWorkflowContext`
- `PublicFolderWorkflowState`
- `PublicFolderWorkflowExecuteRequest`
- `PublicFolderWorkflowResult`

Add helpers:

- `getPublicFolderWorkflowContext(projectId)`
- `setPublicFolderWorkflowAutoSync(projectId, autoSyncEnabled)`
- `previewPublicFolderWorkflowSync(projectId)`
- `executePublicFolderWorkflowSync(projectId, request)`
- `previewPublicFolderWorkflowSubmit(projectId)`
- `executePublicFolderWorkflowSubmit(projectId, request)`
- `previewPublicFolderWorkflowPull(projectId)`
- `executePublicFolderWorkflowPull(projectId, request)`

Execute request body:

```ts
{
  preview_hash: string;
  confirmed: true;
  confirm_directory_creation: boolean;
  operator?: string | null;
}
```

Client rules:

- Use `requestJson(...)`.
- Keep `cache: "no-store"` on context and preview reads.
- Do not hide `ApiRequestError.status`. Workbench model needs `409` to show stale/conflict feedback without retrying automatically.
- Do not expose API route strings to components.

### 16.4 Workbench Model Strategy

Extend `ProjectWorkbenchModel` with a dedicated public-folder workflow slice:

- `publicFolderWorkflowContext`
- `publicFolderWorkflowContextLoading`
- `publicFolderWorkflowContextError`
- `publicFolderWorkflowPreviews`
- `publicFolderWorkflowResults`
- `publicFolderWorkflowBusyOperation`
- `publicFolderWorkflowConfirmingOperation`
- `publicFolderWorkflowError`
- `publicFolderWorkflowMessage`
- `onRefreshPublicFolderWorkflowContext`
- `onSetPublicFolderWorkflowAutoSync`
- `onPreviewPublicFolderWorkflowOperation`
- `onConfirmPublicFolderWorkflowOperation`
- `onCancelPublicFolderWorkflowOperation`

Operation flow:

1. Load context with Workbench setup data.
2. Operator clicks Sync, Submit, or Pull.
3. Model fetches the corresponding preview.
4. If preview has blockers or conflicts, store preview and show short messages. Do not execute.
5. If preview is ready, store a pending confirmation operation and preview hash.
6. Operator confirms.
7. Model calls execute with the stored `preview_hash`, `confirmed: true`, and `confirm_directory_creation` based on preview `required_confirmations`.
8. On success, refresh public folder context, operation preview, official folder check, package preview if relevant, and visible result message.
9. On `409`, surface stale/conflict copy and do not retry automatically.

Submit lock:

- When context or result reports `sync_locked`, Sync row must be disabled with short copy.
- Submit success must refresh context so `sync_locked` appears immediately.

Readonly lifecycle:

- Existing lifecycle readonly gating still applies.
- Stopped or closed Workbench surfaces may render context, but write operations remain disabled until Activate restores editability.

### 16.5 Folder Actions UI Strategy

Preserve TASK_346F layout:

- Single-column right rail.
- Four rows in order: `Project folder`, `Public working copy`, `Approval package`, `Approved folder`.
- Matrix table remains the primary visual surface.
- No nested cards, no thick side stripes, no gradients, no glassmorphism.
- Copy stays concise and operational.

Row behavior:

- `Project folder`
  - Keep `Open` disabled in TASK_346D because there is no accepted platform-safe open-folder helper.
  - Show local official folder context only if returned by backend or existing accepted Workbench data.
- `Public working copy`
  - Auto sync checkbox reflects backend `auto_sync_enabled`.
  - Auto sync toggle persists through `PUT /auto-sync`.
  - No scheduler, watcher, or background sync is implied.
  - `Sync now` fetches Sync preview first, then requires confirmation before execute.
- `Approval package`
  - `Submit` fetches Submit preview first.
  - Block unmanaged Public Open conflicts using backend preview message from TASK_346C.
  - Execute only after explicit confirmation.
  - After Submit success, show locked Sync state.
- `Approved folder`
  - `Pull` fetches Pull preview first.
  - Execute only after explicit confirmation.
  - Result copy should say local history is preserved when backend reports success.

Inline confirmation:

- Prefer inline row-level confirmation inside `ProjectFolderTaskList`.
- Confirmation copy should be short:
  - `Review preview before Sync.`
  - `Submit moves Open to Closed after confirmation.`
  - `Pull copies Closed to local history.`
- Render `Confirm` and `Cancel` using the existing button visual vocabulary.
- Do not use modal-first confirmation unless Reviewer requires it.

Banned old copy remains banned:

- `Ready`
- `Partial`
- `Waiting`
- `Not current`
- `Already current`
- `Ready to upload`
- `Request material`
- `Source material`
- `Project Folder progress`
- `Next step`
- `Public drive upload`
- `Upload to public drive`
- `Refresh public-drive preview`

### 16.6 Selector Strategy

Selector inputs should include:

- public folder workflow context
- operation preview by operation
- operation result by operation
- busy operation
- pending confirmation operation
- lifecycle readonly reason
- existing folder readiness and Basic Information blocker context

Selector outputs should keep components simple:

- row context
- row blocker
- warnings/conflicts
- button disabled state and title
- confirmation state
- result message
- auto-sync checked/disabled state

Do not let selectors invent backend facts such as file counts, last sync time, public folder year, or path state. Display only accepted backend fields.

### 16.7 Validation Plan

Future Developer implementation should run:

- `npm test -- publicFolderWorkflowSelectors projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run`
- `npm run build`
- API helper/static tests proving:
  - helper paths match TASK_346C endpoints;
  - execute requests include `preview_hash`, `confirmed`, and `confirm_directory_creation`;
  - auto-sync PUT sends `auto_sync_enabled`.
- Workbench model tests proving:
  - context loads on Workbench setup;
  - auto-sync preference persists and updates UI state;
  - Sync/Submit/Pull preview happens before execute;
  - blockers/conflicts stop execute;
  - stale preview `409` is surfaced and not retried automatically;
  - Submit success refreshes context and locks Sync.
- Selector/component tests proving:
  - four TASK_346F rows remain in order;
  - actions are disabled with short blocker copy when context blocks;
  - ready preview opens inline confirmation;
  - no old readiness/status/source material/public-drive upload vocabulary appears;
  - readonly lifecycle disables write operations.
- Static scans:
  - banned old Folder Actions copy scan over Workbench production files;
  - old public-drive action-target scan proving Folder Actions no longer routes to `public_drive_upload` / `public_drive_refresh`;
  - mutation helper scan proving Projects list, Matrix Editor, backend, and real folder code are untouched.
- Browser smoke:
  - open a Workbench fixture on localhost;
  - verify Folder Actions loads backend context;
  - verify preview/blocker rendering without executing against real folders;
  - if only real roots are configured, stop before execute and record QA residual for temp-dir fixture smoke.

### 16.8 Existing Residual Classification

Current worktree has unrelated release or packaging residuals, including:

- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts and tests
- `temp_agents_stash.md`

Current TASK_346D planner docs and `docs/task_board.md` are existing planning/board residuals.

This Developer planning-first pass must only update:

- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`

No product code changes are part of this checkpoint.

## 17. Developer Planning Stop Point

Developer planning gate: ready.

Reviewer implementation-readiness gate: passed by conversational callback per Orchestrator delegation.

User approval for reconciliation and Developer implementation: received.

## 18. Planner Reconciliation

Planner reconciliation status:

- Reviewer plan gate passed before Developer planning-first.
- Developer planning-first completed and updated this plan plus Developer evidence only.
- Reviewer implementation-readiness passed and recommended user approval plus board/source-of-truth reconciliation before implementation.
- User explicitly approved `TASK_346D reconciliation` and entry into Developer implementation.
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_reconciliation_planner.md` records the repository authorization alignment.

Current stop point: complete/accepted by Integrator after Developer fix pass, Reviewer implementation re-gate, QA gate, and packaging/readiness.

Do not exceed the approved TASK_346D frontend API-client / Workbench Folder Actions functional wiring scope.

## 19. Planner Scope Reconciliation For Reviewer B1

Reviewer B1 found that the implementation used three Workbench bridge files outside the approved May Touch list:

- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`

Planner decision: add these files to TASK_346D May Touch instead of splitting a new lane.

Rationale:

- TASK_346D is explicitly the functional wiring lane between the accepted TASK_346C backend workflow and the accepted TASK_346F Folder Actions panel.
- `useProjectRuntimeConsoleModel.ts` is the existing runtime bridge that selects model fields and handlers before they reach the Workbench layout.
- `ProjectWorkbenchActiveMatrixWorkspace.tsx` is the active Matrix Workbench surface that hosts the right-rail Folder Actions panel.
- `ProjectWorkbenchLifecycleSections.tsx` hosts lifecycle/no-Matrix Folder Actions surfaces.
- Without these bridge files, public-folder workflow state/handlers can exist in `useProjectWorkbenchModel` but will be dropped before reaching the actual Folder Actions UI, making Sync/Submit/Pull/Auto sync functionally incomplete.

This reconciliation does not authorize broader UI redesign, backend/API/schema/file-operation changes, Projects registry, Matrix Editor business logic, real folder or LTR workbook access, public-drive authority writes, release residuals, or unrelated LTR workbook local settings helpers.

Reviewer B2/B3 resolution record:

- B2: unrelated LTR workbook local settings helper diff in `frontend/src/api/client.ts` is classified as external dirty Settings/LTR residual and must remain excluded from the TASK_346D package.
- B3: public-folder workflow DTO operation id field types are aligned with backend `str`.

## 20. Integrator Packaging Closeout

TASK_346D is complete/accepted after Reviewer implementation re-gate and QA gate.

Integrator package scope is limited to approved TASK_346D frontend API-client public-folder workflow helpers, Workbench Folder Actions wiring files, focused frontend tests/CSS, TASK_346D task/plan/evidence/reconciliation docs, QA artifacts, and `docs/task_board.md` TASK_346D closeout.

Excluded residuals include unrelated Settings/LTR helper hunks in `frontend/src/api/client.ts`, backend/settings/release residuals, release/packaging files, `temp_agents_stash.md`, real folders, LTR workbook files, `.agents/**`, `docs/project_management/**`, backend/API/schema/file-operation logic, Projects registry, Matrix Editor business logic, and future scope.
