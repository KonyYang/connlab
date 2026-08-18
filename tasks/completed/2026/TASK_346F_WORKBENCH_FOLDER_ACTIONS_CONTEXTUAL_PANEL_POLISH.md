# TASK_346F Workbench Folder Actions Contextual Panel Polish

Status: complete/accepted after Reviewer implementation gate, QA gate, and Integrator packaging/readiness
Lane: workbench-folder-actions-contextual-panel-polish
Owner Roles: Frontend Developer / Reviewer / QA / Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-29
Last Updated: 2026-06-30

## 1. Purpose

Create a formal planning-first lane for a light frontend UI polish pass on the accepted TASK_346B Folder Actions surface.

TASK_346F should adjust the right-side Workbench Folder Actions area from a pure disabled button grid into a contextual file-operation panel:

- one vertical panel
- four file operation entries
- each entry uses icon, title, short contextual helper, and right-side action/control
- thin separators between entries
- one bottom short blocker only when configuration or workflow state is missing

This is not a return to the old readiness/status card system. It is also not backend workflow implementation.

## 2. Numbering Decision

`TASK_346C` is not used for this polish lane.

Reason:

- `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT` explicitly reserves `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` for backend public folder workflow.
- Discovery evidence also records `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` and states that TASK_346D functional wiring depends on TASK_346C.
- Reusing TASK_346C for frontend polish would create source-of-truth ambiguity.

Therefore the contextual panel polish lane uses:

- Task ID: `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`
- Lane: `workbench-folder-actions-contextual-panel-polish`

## 3. Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product UI guidance
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_qa.md`
- Current Workbench Folder Actions frontend code, tests, and CSS

## 4. User-Confirmed UI Direction

- Folder Actions should feel like a file operation panel.
- It should not be the old state/readiness panel.
- It should not be a context-free toolbar.
- The target is a single-column panel where each operation group has:
  - icon
  - title
  - short helper/context line
  - right-side button or control
  - thin separator
- The Matrix table remains the primary visual surface. Folder Actions remains a secondary right-side operation panel.
- The panel may keep necessary context such as path fragments, Open/Closed year text, file count, last sync, `keep local history`, and `after confirmation`.
- If backend data is not currently available, TASK_346F must use safe placeholder/hidden context instead of inventing live facts.

## 5. Scope

TASK_346F may plan and later implement only frontend UI polish on top of TASK_346B:

- reshape `ProjectFolderActionsSurface` into a single-column contextual panel
- add or reuse existing `UiIcon` icons without new dependencies
- display concise helper context for each operation
- keep disabled or safe-placeholder behavior where backend workflow data is unavailable
- keep one bottom short blocker area for missing configuration or unavailable workflow state
- update focused component/selector/layout tests
- update scoped Workbench CSS

## 6. Context Rules

Allowed contextual helper examples:

- Project folder: local path fragment when already available in the frontend model, otherwise a short safe placeholder.
- Public working copy: `Open\<year>` / file count / last sync only when real backend/frontend fields exist; otherwise hide those facts or show a safe workflow placeholder.
- Approval package: `Moves Open package to Closed after confirmation`.
- Approved folder: `Closed\<year> · keep local history` only when year is known; otherwise `Closed package · keep local history`.

Do not invent:

- real file counts
- real last sync timestamps
- real public folder years
- real local or public paths
- real sync/submit/pull availability

## 7. Out Of Scope

TASK_346F must not implement:

- backend public folder workflow
- public folder resolver
- `public_folder_year` resolver
- Sync/Submit/Pull preview or execute behavior
- real file count or last-sync calculation
- public-drive authority writes
- `frontend/src/api/client.ts` changes
- Projects list changes
- Matrix Editor business logic
- StepInstance, Report generation, AI review, permissions, LAN/server, or multi-user scope
- changes to accepted TASK_346B behavior beyond the planned polish

## 8. May Touch

For the authorized Developer implementation pass:

- `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_planner.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_reconciliation_planner.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_qa.md` if QA is routed
- `docs/task_board.md`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`

## 9. Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `AGENTS.md`
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 10. Locked Paths

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`

## 11. UI Acceptance

Future implementation should satisfy:

- Folder Actions visually reads as a single-column contextual file operation panel.
- Four groups render in order:
  - Project folder
  - Public working copy
  - Approval package
  - Approved folder
- Each group has icon, title, short helper/context line, and right-side action/control.
- Thin separators separate groups.
- Matrix table remains the main visual priority.
- Necessary context is allowed, but only if it is either real existing data or an explicit safe placeholder.
- Bottom blocker appears only for configuration/workflow blockers.
- No old readiness/status vocabulary appears in the Folder Actions surface:
  - `Ready`
  - `Partial`
  - `Waiting`
  - `Not current`
  - `Already current`
  - `Ready to upload`
- No old workflow/card copy appears:
  - `Request material`
  - `Source material`
  - `Project Folder progress`
  - `Next step`
  - `Public drive upload`
  - `Upload to public drive`
  - `Refresh public-drive preview`
- Sync/Submit/Pull remain disabled or safe placeholders and do not call old public-drive upload helpers.

## 12. Validation Gate

Reviewer plan gate must confirm:

- The lane is UI polish only and does not reopen TASK_346B implementation broadly.
- TASK_346C is preserved for backend public folder workflow.
- Context helpers do not invent real backend facts.
- `frontend/src/api/client.ts`, backend, Projects list, and Matrix Editor remain locked.
- The May Touch file list is narrow enough for a light frontend polish.
- UI acceptance and browser smoke expectations match the user-confirmed panel direction.

Reviewer plan gate status: passed.

## 13. Merge Gate

Implementation can merge only after:

- Developer implementation evidence proves scoped frontend-only polish changes.
- Focused frontend tests pass.
- `npm run build` passes or existing warnings are classified.
- Browser smoke verifies the active Matrix Workbench right-side Folder Actions panel.
- Reviewer implementation gate passes.
- QA gate runs if routed.
- Integrator confirms no backend/API/client/Projects/Matrix/future-scope or unrelated residuals are packaged.

## 14. Reconciliation Checkpoint

Source-of-truth alignment on 2026-06-30 records:

- Planner Discovery/formal lane creation completed.
- Reviewer plan gate passed.
- User approved TASK_346F entering Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness gate passed with no readiness blocking finding.
- User approved continuing after readiness.
- `docs/task_board.md`, this task file, the plan, and reconciliation evidence now authorize Developer implementation within the scoped TASK_346F frontend UI polish May Touch list.

Current stop point: Developer implementation pass. Do not route Reviewer/QA/Integrator until Developer evidence is updated to ready_for_review.
