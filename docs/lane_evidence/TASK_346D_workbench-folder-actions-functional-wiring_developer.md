# TASK_346D Workbench Folder Actions Functional Wiring - Developer Evidence

Status: implementation complete - pending Reviewer implementation gate
Date: 2026-06-30
Role: Developer
Task: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
Lane: `workbench-folder-actions-functional-wiring`

## 1. Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`.
- Current lane: `workbench-folder-actions-functional-wiring`.
- Current role: Developer planning-first.
- Allowed reason: Orchestrator delegation states Reviewer plan gate passed and user approved Developer planning-first only.
- Stop point: Reviewer implementation-readiness gate.

No frontend, backend, tests, API client, CSS, board, release, real folder, LTR workbook, `.agents/**`, or `docs/project_management/**` product code was modified in this pass.

## 2. Sources Read

Governance and UI rules:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `$impeccable` product-register reference
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Task and evidence inputs:

- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_planner.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`
- TASK_346A / TASK_346B / TASK_346F accepted context from task board and plan/evidence references

Read-only code inspection:

- `backend/api/routes_public_folder_workflow.py`
- `tests/integration/test_public_folder_workflow_api.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Focused project-workbench tests for Folder Actions and layout behavior

## 3. Planning Findings

- TASK_346C backend API is stable enough for frontend consumption. It exposes context, auto-sync state, Sync/Submit/Pull previews, and Sync/Submit/Pull execute endpoints.
- Execute endpoints require `preview_hash`, `confirmed`, and optional `confirm_directory_creation`; stale/conflict/blocked execute paths return `409`.
- `frontend/src/api/client.ts` currently has old public-drive upload DTOs/helpers, but no TASK_346C public-folder-workflow helpers.
- Current Folder Actions UI remains the accepted TASK_346F quiet four-row contextual panel.
- Current `ProjectFolderTaskList.tsx` is display-focused and should stay that way.
- Current `projectFolderTaskSelectors.ts` owns the row model and placeholder blockers.
- Current `useProjectWorkbenchModel.ts` owns Workbench data/actions and still references old public-drive upload preview/upload paths.
- Folder Actions should not be wired to old `/public-drive/preview` or `/public-drive/upload`; TASK_346D should consume only accepted TASK_346C workflow endpoints.
- `Project folder / Open` should remain disabled in TASK_346D because no accepted platform-safe open-folder helper exists.

## 4. Implementation Strategy For Future Pass

Future implementation should stay frontend-only:

1. Add typed TASK_346C DTOs and helpers in `frontend/src/api/client.ts`.
2. Add a public-folder workflow slice to `useProjectWorkbenchModel.ts`.
3. Add or use a dedicated selector layer for preview/result/action enablement and concise copy.
4. Extend `projectFolderTaskSelectors.ts` so the four rows consume real workflow context and preview state.
5. Extend `ProjectFolderTaskList.tsx` with:
   - enabled Auto sync checkbox tied to backend preference;
   - row-level preview result display;
   - inline confirmation controls for ready Sync, Submit, and Pull previews;
   - short blocker/conflict/result copy.
6. Extend `ProjectWorkbenchLayout.tsx` only to route new Folder Actions action targets and preserve lifecycle readonly gating.
7. Keep CSS edits limited to existing Folder Actions confirmation/blocker/result state styling.

No backend/API/schema/file-operation logic should change in TASK_346D.

## 5. Exact Future May Touch

Future Developer implementation may touch only:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/publicFolderWorkflowSelectors.ts`
- `frontend/src/features/project-workbench/publicFolderWorkflowSelectors.test.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`

## 6. API Client Plan

Add DTOs:

- `PublicFolderWorkflowOperationType`
- `PublicFolderWorkflowPreviewStatus`
- `PublicFolderWorkflowItemAction`
- `PublicFolderWorkflowItemStatus`
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

Rules:

- Keep snake_case DTO fields matching backend response.
- Use `requestJson(...)`.
- Use `cache: "no-store"` for context and preview reads.
- Preserve `ApiRequestError.status` for `409` stale/conflict UI.

## 7. Workbench UI / Model Plan

State to add:

- context loading/error
- public-folder workflow context
- preview per operation
- result per operation
- busy operation
- pending confirmation operation
- operation message/error

Action flow:

- click Sync/Submit/Pull -> fetch preview first;
- blocked/conflict preview -> show message, no execute;
- ready preview -> show inline confirmation;
- confirm -> execute with preview hash and required confirmation flags;
- success -> refresh context and relevant Workbench state;
- `409` stale/conflict -> show message, no automatic retry.

Auto sync:

- checkbox reflects backend `auto_sync_enabled`.
- toggle calls `PUT /auto-sync`.
- no scheduler, watcher, or background sync is implied.
- disable when lifecycle readonly or Submit lock makes the row read-only.

Submit lock:

- context/result `sync_locked` disables Sync with short copy.
- Submit success refreshes context immediately.

Project folder Open:

- remains disabled until a separate approved platform-safe helper exists.

## 8. UI Copy And Visual Constraints

TASK_346D must preserve TASK_346F:

- four quiet rows in order;
- single-column right rail;
- Matrix table remains primary;
- concise business-readable copy;
- no nested cards;
- no side-stripe accent greater than 1px;
- no gradient text;
- no glassmorphism;
- no long workflow explanations.

Banned old Folder Actions copy remains banned:

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

## 9. Validation Plan For Future Implementation

Future Developer implementation should run:

- `npm test -- publicFolderWorkflowSelectors projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run`
- `npm run build`
- API helper/static tests for paths and execute request bodies.
- Workbench model tests for context load, auto-sync update, preview-first flow, execute confirmation, stale/conflict handling, submit lock refresh, and no automatic retry.
- Selector/component tests for row order, enablement, confirmation, readonly disablement, blocker copy, result copy, and banned-copy absence.
- Static banned old Folder Actions copy scan over Workbench production files.
- Static old public-drive action-target scan proving Folder Actions no longer routes to `public_drive_upload` or `public_drive_refresh`.
- Targeted forbidden-scope status.
- Browser smoke on localhost Workbench for context/blocker rendering, avoiding execute if only real roots are configured.

Backend regression expectation:

- TASK_346D should not normally rerun backend tests unless implementation discovers an API contract ambiguity. If that happens, stop and route Planner or Reviewer instead of editing backend.

## 10. Existing Dirty Worktree Classification

Observed residuals outside this pass:

- `docs/packaging_notes.md`
- `docs/task_board.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts and tests
- release task/docs
- `temp_agents_stash.md`
- TASK_346D planner task/plan/evidence files created before this Developer pass

These residuals were not touched by this Developer planning-first pass except the allowed TASK_346D plan and this Developer evidence file.

## 11. Files Changed In This Pass

- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`

No product source, product tests, backend, frontend API client, CSS, board, real folders, release residuals, `.agents/**`, or `docs/project_management/**` files were modified by this pass.

## 12. Validation

Completed:

- Required docs/evidence existence check -> all required TASK_346D task, plan, Planner evidence, and Developer evidence files exist.
- `git diff --check -- docs/task_346d_workbench_folder_actions_functional_wiring_plan.md docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md` -> passed.
- Trailing whitespace scan on the two TASK_346D docs -> no matches.
- Targeted forbidden-scope status -> no frontend product code, backend product code, product tests, API client, Projects registry, Matrix Editor, `.agents/**`, or `docs/project_management/**` files changed by this Developer planning-first pass.

Targeted status notes:

- Existing external residuals remain present and excluded: `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts/tests, and `temp_agents_stash.md`.
- Existing board/planner residuals remain present: `docs/task_board.md`, TASK_346D task/plan/planner evidence.
- This pass intentionally changed only the TASK_346D plan and Developer evidence.

## 13. Implementation Pass Update

Date: 2026-06-30

Implementation status: complete, pending Reviewer implementation gate.

### Changed files

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`

`useProjectRuntimeConsoleModel.ts`, `ProjectWorkbenchActiveMatrixWorkspace.tsx`, and `ProjectWorkbenchLifecycleSections.tsx` were necessary bridge touches: the actual Workbench runtime selector and Folder Actions surfaces would otherwise drop the new workflow handlers before they reached the right-rail panel.

### Implementation summary

- Added typed frontend helpers for TASK_346C public-folder-workflow APIs:
  - context load
  - auto-sync preference update
  - Sync/Submit/Pull preview
  - Sync/Submit/Pull execute with `preview_hash`, `confirmed`, optional directory confirmation, and operator.
- Added a Workbench public-folder workflow state slice:
  - context loading/error
  - previews/results per operation
  - busy operation
  - pending confirmation operation
  - short operation message/error
  - backend-owned Auto sync state.
- Wired Folder Actions rows to preview-first behavior:
  - `Sync now`, `Submit`, and `Pull` call preview first.
  - ready preview shows inline Confirm/Cancel.
  - execute only runs after confirmation with the current preview hash.
  - blockers/conflicts show short copy and do not execute.
  - success refreshes workflow context and adjacent Workbench state.
- Kept `Project folder / Open` disabled because no approved platform-safe open-folder helper exists.
- Preserved TASK_346F visual direction:
  - four quiet operation rows
  - Auto sync + Sync now in Public working copy
  - short blocker/result messages
  - no old readiness/source-material/public-drive upload card revival.

### Validation

Completed:

- `npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout useProjectWorkbenchModel --run` -> passed, `4 passed`, `58 passed`.
- `npm run build` -> passed. Vite emitted the existing chunk-size warning only.
- `git diff --check -- <TASK_346D package files>` -> passed, with LF/CRLF normalization warnings only.
- trailing whitespace scan on TASK_346D package files -> no matches.
- changed-lines banned old Folder Actions copy/action-target scan -> no old `public_drive_upload`, upload action target, Request material/Source material/Public drive upload copy added. New code contains API status comparisons to `ready`; user-facing Folder Actions copy uses `Preview can be confirmed.`
- production touched-file path/write scan -> no real `D:\Test Project`, `D:\PublicProject`, filesystem write/remove/unlink calls in production touched frontend files.
- targeted forbidden-scope status -> no Projects registry, Matrix Editor, or `.agents/**` / `docs/project_management/**` changes from this implementation pass. Pre-existing backend/release residuals remain outside this lane.

Browser smoke:

- In-app browser opened `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
- Folder Actions surface was present with four rows:
  - `Project folder`
  - `Public working copy`
  - `Approval package`
  - `Approved folder`
- `Auto sync`, `Sync now`, `Submit`, and `Pull` were visible.
- Current local backend data returned a safe disabled state for workflow actions, with copy such as `Public Open location will be prepared after preview.` No execute action was attempted.

### Scope proof

- No backend/API/schema/file-operation implementation was modified.
- No `frontend/src/pages/ProjectListPage.tsx`, Projects registry, Matrix Editor, real folders, LTR workbook, public-drive authority write, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope was touched.
- Existing release/packaging residuals remain excluded.

### Residuals

- Browser smoke did not execute Sync/Submit/Pull because the current local project/workflow context exposed disabled operations. QA should exercise enabled preview/confirm/execute states with a safe temp-root backend fixture.
- Existing Vite chunk-size warning remains unrelated.

## 14. Stop Point

Developer implementation gate: ready for review.

Recommended next role: Reviewer implementation gate.

Do not route QA or Integrator before Reviewer implementation gate.

## 15. Developer Fix Pass Checkpoint - Reviewer B1/B2/B3

Date: 2026-06-30

Status: blocked - needs Planner scope reconciliation before product edits.

Reviewer blockers received:

- B1: implementation/evidence includes `useProjectRuntimeConsoleModel.ts`, `ProjectWorkbenchActiveMatrixWorkspace.tsx`, and `ProjectWorkbenchLifecycleSections.tsx` outside approved TASK_346D Developer May Touch.
- B2: `frontend/src/api/client.ts` contains unrelated LTR workbook local settings helper diff.
- B3: public-folder workflow DTO operation id fields are typed as `number` while backend TASK_346C route DTO returns `str`.

Developer triage:

- B1 is a real scope mismatch, not a removable incidental edit.
- Current Workbench page passes `useProjectWorkbenchModel(...)` through `selectProjectRuntimeConsoleModel(...)` before `ProjectWorkbenchLayout`, so new workflow state and handlers are dropped unless `useProjectRuntimeConsoleModel.ts` is updated.
- Active Matrix Folder Actions are rendered inside `ProjectWorkbenchActiveMatrixWorkspace.tsx`; no-Matrix Folder Actions are rendered inside `ProjectWorkbenchLifecycleSections.tsx`. Without bridge updates there, Sync/Submit/Pull/Auto sync handlers do not reach the actual right-rail Folder Actions panel.
- Removing those bridge changes would keep implementation inside the original May Touch list but would leave TASK_346D functionally incomplete.
- Per Reviewer instruction and Orchestrator delegation, Developer must not silently include those bridge files and must not proceed with B2/B3 product edits before Planner scope reconciliation.

Files changed in this fix-pass checkpoint:

- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`

Product files changed in this fix pass:

- None.

Recommended next role:

- Planner scope reconciliation for TASK_346D May Touch.

Requested reconciliation decision:

- Either authorize the three bridge files as TASK_346D May Touch because they are required to pass workflow handlers to the existing Workbench surfaces, then route Developer fix pass for B2/B3 and any remaining packaging cleanup; or instruct Developer to remove the functional wiring from those bridge paths and accept that TASK_346D cannot complete the approved UI wiring without another implementation approach.

## 16. Developer Fix Pass - B2/B3 After Scope Reconciliation

Date: 2026-06-30

Status: fix pass complete - pending Reviewer implementation re-gate.

Scope reconciliation input:

- Planner evidence `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_scope_reconciliation_planner.md` resolves B1.
- `useProjectRuntimeConsoleModel.ts`, `ProjectWorkbenchActiveMatrixWorkspace.tsx`, and `ProjectWorkbenchLifecycleSections.tsx` are now recorded May Touch bridge files for TASK_346D.
- This fix pass therefore kept the bridge wiring intact and only handled unresolved B2/B3.

### B2 triage

`frontend/src/api/client.ts` still contains LTR workbook local settings helper diff, but this pass verified those helpers are consumed by current dirty Settings residuals:

- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
- backend residuals `backend/api/routes_settings.py` and `backend/application/local_ltr_workbook_config_service.py`

Developer attempted the safe interpretation of B2 by removing the helper hunk from `client.ts`; `npm run build` then failed because the above Settings files import those types and helpers. Those Settings/backend files are outside TASK_346D scope and were not touched by this fix pass.

Decision for this fix pass:

- Preserve the helper hunk to keep the current worktree buildable.
- Classify the LTR settings diff as pre-existing external residual to exclude from the TASK_346D package, not as TASK_346D functional wiring.
- Leave packaging/separation to Reviewer/Integrator or route a separate Settings/LTR lane if the residual must be completed.

### B3 fix

Aligned frontend public-folder workflow DTO operation ids to the accepted TASK_346C backend `str` contract:

- `PublicFolderWorkflowState.submit_operation_id: string | null`
- `PublicFolderWorkflowState.last_sync_operation_id: string | null`
- `PublicFolderWorkflowState.last_pull_operation_id: string | null`
- `PublicFolderWorkflowResult.operation_id: string`
- Updated the focused Workbench model test fixture to use a string operation id.

### Changed files in this fix pass

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`

### Validation

Completed after B3 fix and B2 triage:

- `npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout useProjectWorkbenchModel --run` -> passed, `4 passed`, `58 passed`.
- `npm run build` -> passed. Vite emitted the existing chunk-size warning only.
- `git diff --check -- <TASK_346D package files>` -> passed, with LF/CRLF normalization warnings only.
- trailing whitespace scan on TASK_346D package files -> no matches.
- B3 scan for `operation_id: number`, `submit_operation_id: number`, `last_sync_operation_id: number`, and `last_pull_operation_id: number` in `frontend/src/api/client.ts` and Workbench files -> no matches.
- changed-lines banned Folder Actions copy/action-target scan -> no old Folder Actions copy or `public_drive_upload` action target added.
- production touched-file real-folder/write scan -> no `D:\Test Project`, `D:\PublicProject`, filesystem write, mkdir, unlink, or remove commands in touched frontend production files.
- UI anti-pattern changed-lines scan -> no new gradient, >1px side stripe, glass/backdrop-filter pattern in TASK_346D UI diff.
- targeted forbidden-scope status showed no Projects registry, Matrix Editor, `.agents/**`, or `docs/project_management/**` changes from this fix pass. Existing backend/settings/release residuals remain outside this lane.

### Residuals

- B2 remains a packaging separation concern: the LTR settings hunk is visible in the broad `client.ts` diff but is required by unrelated dirty Settings files for the current worktree to build. It should not be packaged as TASK_346D unless a separate authorized Settings/LTR lane owns it.
- Known external residuals still present in targeted status include backend settings files and release/packaging files; this fix pass did not touch or clean them.

### Stop point

Developer fix pass complete.

Recommended next role: Reviewer implementation re-gate.

## 17. Integrator Packaging / Readiness Closeout

Integrator gate: accepted.

Package scope accepted:

- TASK_346D frontend public-folder workflow API-client helper hunks only.
- TASK_346D Workbench Folder Actions functional wiring files, focused tests, and CSS.
- TASK_346D task, plan, planner/developer/QA/reconciliation/scope-reconciliation evidence, QA artifacts, and `docs/task_board.md` TASK_346D closeout.

Packaging separation:

- `frontend/src/api/client.ts` contains both TASK_346D public-folder workflow helper changes and an unrelated `/api/settings/ltr-workbook` Settings/LTR helper hunk.
- Integrator staged only the TASK_346D public-folder workflow client hunk.
- The unrelated Settings/LTR helper hunk remains unstaged/uncommitted with the external Settings/LTR residuals.

Excluded residuals:

- backend/settings residuals and local LTR workbook config files/tests.
- release/packaging residuals: `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts/tasks/docs, and desktop-release tests.
- `temp_agents_stash.md`.
- `.agents/**`, `docs/project_management/**`.
- backend/API/schema/file-operation logic, Projects registry, Matrix Editor business logic, real folders, real LTR workbook files, public-drive LTR workbook authority writes, TASK_346E+ future scope, StepInstance, Report, AI, permissions, LAN/server, and multi-user scope.

Integrator validation rerun:

- `npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout useProjectWorkbenchModel --run` -> `4 passed`, `58 passed`.
- `npm run build` -> passed with existing Vite chunk-size warning only.
- trailing whitespace scan on TASK_346D package files -> no matches.
- operation id mismatch scan -> no matches.
- banned old Folder Actions copy scan -> identifier-level `Ready` matches only; no banned user-facing copy.
- diff-only old public-drive action-target scan -> old targets removed from Folder Actions path.
- production real-folder/write scan -> no matches.

Remote push: intentionally not performed.
