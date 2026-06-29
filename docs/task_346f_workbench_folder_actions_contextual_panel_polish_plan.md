# TASK_346F Workbench Folder Actions Contextual Panel Polish Plan

Status: complete/accepted after Reviewer implementation gate, QA gate, and Integrator packaging/readiness
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: workbench-folder-actions-contextual-panel-polish
Created: 2026-06-29
Last Updated: 2026-06-29

## 1. Goal

Create a light frontend UI polish lane for the accepted TASK_346B Folder Actions surface.

The target is a contextual file operation panel, not a readiness/status panel and not a context-free toolbar. The Workbench right side should show four file operations as single-column rows with icons, labels, compact helper text, and right-side controls.

## 2. TASK_346C Numbering Check

TASK_346C must remain reserved for backend public folder workflow.

Evidence:

- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md` lists `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`.
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md` lists `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` and makes functional wiring depend on TASK_346C.
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md` lists `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` and recommends backend before functional UI wiring.
- `docs/task_board.md` treats TASK_346C+ as future lanes and records TASK_346B as excluding TASK_346C+ workflow execution.

Decision:

- Do not reuse TASK_346C for this frontend polish lane.
- Use `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`.

## 3. Current Fact Summary

### User-Confirmed Facts

- The desired UI is a "file operation panel" style.
- It should use a single-column panel with one row per operation group.
- Each row should have icon, title, helper/context text, and right-side button/control.
- Thin separators should divide the groups.
- The UI may show necessary operational context such as path fragments, Open/Closed year, file count, last sync, `keep local history`, and `after confirmation`.
- It must not restore old readiness/status card behavior.
- It must not become a long explanatory panel.
- If backend data is not available, context must be hidden, disabled, or marked as safe placeholder rather than invented.

### Repository-Proven Facts

- TASK_346A and TASK_346B are complete/accepted.
- TASK_346B implemented the quiet four-action model and kept Open/Auto sync/Sync/Submit/Pull disabled or blocked placeholders.
- Current `ProjectFolderTaskList.tsx` exposes `ProjectFolderActionsSurface`.
- Current `ProjectFolderActionsSurface` renders a `Folder Actions` region and maps rows through `FolderOperation`.
- Current selectors return four rows:
  - `Project folder`
  - `Public working copy`
  - `Approval package`
  - `Approved folder`
- Current CSS uses a two-column `.runtime-console-folder-operation-grid`, small bordered operation tiles, and per-row blocker text.
- Existing `UiIcon` supports reusable icon names including `folder`, `upload`, `refresh`, and `package`, so no new icon dependency is needed.
- Current targeted status before this Developer planning-first edit showed no `frontend/`, `backend/`, root `tests/`, API client, Projects list, or Matrix Editor product file changes. Existing TASK_346F task/plan/planner evidence and `docs/task_board.md` are Planner/board residuals outside this Developer planning-first scope.

### Planner Inferences

- This is a new formal lane because TASK_346B is already accepted and packaged. Continuing to edit TASK_346B would mix a post-acceptance polish request into a closed implementation package.
- The lane can stay frontend-only if it treats context helpers as presentation derived from existing frontend model fields or safe placeholders.
- Backend public folder workflow remains necessary later for real Open/Closed year, file count, last sync, sync/submit/pull preview and execute, and `public_folder_year`.

## 4. Design Direction

Visual structure:

- A single bordered panel named `Folder Actions`.
- Four vertical rows with thin separators, replacing the current two-column operation grid.
- Each row:
  - left icon in a quiet square or inline icon slot
  - title
  - compact helper/context text
  - right-side action or control
- Public working copy row includes `Auto sync` toggle and `Sync now`.
- Bottom blocker area appears once at panel level only if configuration/workflow state needs one short message. Per-row blockers should move into button `title` or concise disabled context unless the row itself is the only blocked item.

Icon strategy:

- Use existing `UiIcon` where available:
  - `folder` for Project folder
  - `upload` or `refresh` for Public working copy
  - `package` for Approval package
  - `refresh`, `copy`, or another existing close-enough icon for Approved folder
- Do not add a dependency.
- Do not expand shared `UiIcon` unless Reviewer explicitly accepts it; current plan does not include `UiIcon.tsx` in May Touch.

## 4.1 Developer Implementation Strategy

Future implementation should stay inside the existing TASK_346B feature boundary and should not change Workbench hosting components unless a Reviewer/User gate expands May Touch.

Exact implementation strategy:

1. `ProjectFolderTaskList.tsx`
   - Keep `ProjectFolderActionsSurface` as the only rendered entry point.
   - Import existing `UiIcon` and map the four task keys to existing icon names:
     - `project_folder` -> `folder`
     - `public_working_copy` -> `refresh`
     - `approval_package` -> `package`
     - `approved_folder` -> `copy` or `folder`
   - Replace `.runtime-console-folder-operation-grid` rendering with a single-column list.
   - Render each operation as one row with icon slot, title/helper block, and right-side control group.
   - Keep controls non-executing unless `task.actionTarget` is already present and safe. With current TASK_346B model, Sync/Submit/Pull remain disabled placeholders.
   - Derive one bottom blocker from the first meaningful blocker across rows or `readonlyReason`; do not show repeated blocker paragraphs under every row.

2. `projectFolderTaskSelectors.ts`
   - Preserve the four-row model and existing keys.
   - Add display-only fields only if they are necessary for contextual helper text, for example `helper`, `context`, or `operationKind`.
   - Do not add persistent business state or fake backend data.
   - Keep `actionTarget` null for Sync/Submit/Pull until TASK_346C/TASK_346D supply approved backend/API behavior.

3. `frontend/src/workbench.css`
   - Replace the two-column grid styling with compact single-column rows and dividers.
   - Use restrained full borders, muted surfaces, and stable button/control sizing.
   - Do not use thick side stripes, decorative gradients, glassmorphism, nested cards, or large marketing-style panels.

4. Tests
   - Update only focused tests listed in May Touch.
   - Assert row order, icon-accessible structure where practical, right-side controls, single bottom blocker behavior, and banned-copy absence.

No future implementation should touch `ProjectWorkbenchActiveMatrixWorkspace.tsx`, `ProjectWorkbenchLifecycleSections.tsx`, or `ProjectWorkbenchLayout.tsx` for TASK_346F. TASK_346B already hosts the shared Folder Actions surface in the needed Workbench locations. If a hosting gap is discovered, stop and route back to Planner/User because those files are not in the TASK_346F future implementation May Touch list.

## 5. Context Helper Policy

Allowed:

- local project folder path fragment if already available from `officialFolderCheckPreview` or existing frontend model fields
- `Open\<year>` only if a real year is available from existing accepted data
- file count and last sync only if existing model fields already contain real values
- fixed business helper copy:
  - `Moves Open package to Closed after confirmation`
  - `Closed package · keep local history`
- existing boolean readiness such as `folderReady`, when shown as concise context rather than old readiness vocabulary

Required fallback:

- If a real data field does not exist, hide that data fragment or use a safe placeholder such as:
  - `Local folder access not connected yet`
  - `Public workflow not connected yet`
  - `Closed package · keep local history`

Forbidden:

- fake paths
- fake file counts
- fake last sync timestamps
- fake Open/Closed years
- old public-drive upload facts masquerading as new Sync/Submit/Pull workflow data

Current field availability decision:

- Available now:
  - four operation keys and titles from `deriveProjectFolderTasks`
  - short operation summaries
  - existing blockers from selector inputs
  - `folderReady` and Basic Information blocker derived from required forms preview/error
  - readonly reason passed into `ProjectFolderActionsSurface`
- Not available now and therefore hidden or placeholder-only:
  - real local project folder path fragment for display
  - real public `Open` / `Closed` year
  - real public working copy file count
  - real last sync timestamp
  - real submit time
  - real pull status
  - public folder resolver output
  - executable Sync/Submit/Pull operations

## 6. May Touch

For future implementation after Reviewer/user gates:

- `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_planner.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_qa.md` if QA is routed
- `docs/task_board.md`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`

## 7. Must Not Touch

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

## 8. Locked Paths

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

## 9. UI Acceptance Criteria

Future implementation should satisfy:

1. Folder Actions visually matches the contextual panel direction: single-column, four rows, icon + title + helper + right-side control.
2. Operation order is `Project folder`, `Public working copy`, `Approval package`, `Approved folder`.
3. Rows are compact and divided by thin separators.
4. Matrix remains the primary visual surface.
5. Necessary context is present where real/safe data exists.
6. No old readiness/status vocabulary appears in the Folder Actions surface.
7. No `Request material`, `Source material`, `Project Folder progress`, `Next step`, or `Public drive upload` old workflow appears.
8. Bottom short blocker appears only when needed.
9. Disabled or placeholder controls do not invoke old `public_drive_upload` behavior.
10. The panel follows ConnLab restrained, dense, operational product UI.

## 10. Validation Plan

Future Developer validation:

- focused tests:
  - `ProjectFolderTaskList`
  - `projectFolderTaskSelectors`
  - `ProjectWorkbenchLayout`
- source scan for banned old Folder Actions copy
- source scan proving no `frontend/src/api/client.ts`, backend, Projects list, or Matrix Editor changes
- `npm run build`
- `git diff --check` for TASK_346F package files
- trailing whitespace scan for TASK_346F package files
- targeted forbidden-scope status check for backend, API client, Projects registry/list, Matrix Editor, real folders, and governance residuals

Future QA/browser smoke:

- use `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`
- confirm right-side Folder Actions matches contextual panel direction
- confirm four rows and operation order
- confirm Matrix remains primary
- confirm disabled placeholders remain safe
- confirm no old readiness/status panel copy appears
- check narrow width wrapping if routed

## 11. Backend Workflow Lane

This polish lane does not replace backend workflow work.

Backend public folder workflow is still needed for:

- real `public_folder_year`
- Open/Closed path resolution
- file count
- last sync timestamp
- Sync/Submit/Pull preview
- Sync/Submit/Pull execute
- operation history

That remains the reserved `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` direction from TASK_346A.

## 12. Blocking Clarification Questions

None.

Definition of Ready for planned lane and Reviewer plan gate: satisfied.

Definition of Ready for Developer implementation: satisfied after Reviewer plan gate pass, user-approved Developer planning-first, Developer planning-first completion, Reviewer implementation-readiness pass, and user approval to continue.

## 13. Validation Gate

Reviewer plan gate should verify:

- TASK_346C numbering is preserved for backend workflow.
- TASK_346F is the correct lightweight frontend polish lane.
- Context helpers are not fake backend state.
- The May Touch list is narrow.
- Backend/API/client/Projects/Matrix paths remain locked.
- UI acceptance matches the user-confirmed contextual panel direction.

## 14. Merge Gate

Implementation is now authorized but not complete.

Future merge requires:

- Developer evidence with scoped frontend-only changes.
- Focused tests and build.
- Reviewer implementation gate.
- QA if routed.
- Integrator packaging/readiness.

Current stop point: Developer implementation pass.

## 15. Developer Planning-First Refinement

Developer planning-first result on 2026-06-30:

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current task/lane: `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH` / `workbench-folder-actions-contextual-panel-polish`.
- Allowed reason: user delegated Developer planning-first only after Reviewer plan gate pass; implementation was not approved in that pass.
- Role boundary: Developer may update this plan and Developer evidence only. No product code, tests, board, backend, API client, Projects list, Matrix Editor, real folders, or governance protocol files may be changed in this pass.

Planning-first conclusions:

- The current TASK_346B surface is adequate as the implementation base. It already centralizes Folder Actions in `ProjectFolderActionsSurface` and selectors.
- TASK_346F should be a presentational polish over the existing four-action model, not a new workflow model.
- The future implementation file list should remain:
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - `frontend/src/workbench.css`
  - TASK_346F Developer evidence
- TASK_346F should not edit Workbench hosting/layout components. If the future implementation cannot meet acceptance without those files, stop for Planner/User scope decision.
- No real Sync/Submit/Pull, public-folder resolver, file count, last sync, or folder path behavior is available in current frontend data. Those facts must stay hidden or be represented as safe disabled placeholders.

## 16. Planner Reconciliation

Planner source-of-truth reconciliation on 2026-06-30 records:

- Planner Discovery/formal lane creation completed.
- Reviewer plan gate passed.
- User approved TASK_346F entering Developer planning-first.
- Developer planning-first completed and changed docs/evidence only.
- Reviewer implementation-readiness gate passed with no readiness blocking finding.
- User approved continuing after readiness.
- TASK_346F is now implementation authorized and ready for Developer implementation pass.

This authorization remains limited to the accepted TASK_346F frontend UI polish scope. It does not authorize backend/API/file operations, `frontend/src/api/client.ts`, public folder resolver, Sync/Submit/Pull execute behavior, real file count or last-sync calculation, Projects list, Matrix Editor business logic, real local/public folders, public-drive authority writes, StepInstance, Report, AI, permissions, LAN/server, multi-user scope, TASK_346C backend workflow, or unrelated governance cleanup.

Current stop point: Developer implementation pass. Developer must update TASK_346F Developer evidence to ready_for_review before Reviewer implementation gate.
