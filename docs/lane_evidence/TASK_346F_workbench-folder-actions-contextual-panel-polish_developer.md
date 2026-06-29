# TASK_346F Workbench Folder Actions Contextual Panel Polish - Developer Evidence

Task: `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`
Lane: `workbench-folder-actions-contextual-panel-polish`
Role: Developer
Status: implementation complete - ready_for_review
Created: 2026-06-30
Last Updated: 2026-06-30

## 1. Current Phase / Task / Lane

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
- Current task: `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`
- Current lane: `workbench-folder-actions-contextual-panel-polish`
- Current role: Developer planning-first
- Allowed reason: user delegated Developer planning-first after Reviewer plan gate pass. This is not implementation approval.

## 2. Role Boundary

This pass is documentation-only.

May Touch in this pass:

- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`

Must Not Touch in this pass:

- `frontend/**` product source, tests, and CSS
- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- real folders under `D:\Test Project/**` or `D:\PublicProject/**`
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`
- `docs/task_board.md`
- merge, commit, push, destructive git operations

## 3. Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` skill guidance and product register context
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_planner.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`
- Current read-only Workbench Folder Actions files:
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - `frontend/src/workbench.css`
  - `frontend/src/components/common/UiIcon.tsx`

## 4. Current Code Findings

- `ProjectFolderActionsSurface` already centralizes the accepted TASK_346B Folder Actions surface.
- `deriveProjectFolderTasks` already returns the four required operation rows:
  - `Project folder`
  - `Public working copy`
  - `Approval package`
  - `Approved folder`
- Current rendering is still a two-column `.runtime-console-folder-operation-grid` of bordered tiles.
- Current CSS and component structure can be polished into a single-column contextual panel without changing backend/API or Workbench hosting components.
- `UiIcon` already has usable icons: `folder`, `refresh`, `package`, `copy`, and `upload`; no new icon dependency is needed.
- Current frontend data does not provide real public folder year, file count, last sync timestamp, submit time, pull status, public folder resolver output, or executable Sync/Submit/Pull behavior.

## 5. Future Implementation Strategy

Future implementation should remain a presentational polish over the accepted TASK_346B model.

Exact future implementation file list:

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`

Implementation shape:

- Keep `ProjectFolderActionsSurface` as the entry point.
- Replace the two-column operation grid with one vertical panel.
- Render each operation row as icon + title + compact helper/context + right-side button/control.
- Use thin separators between rows.
- Keep `Auto sync` and `Sync now` in the `Public working copy` row.
- Move repeated row blockers into one short bottom blocker when possible.
- Keep Sync/Submit/Pull disabled or placeholder-only until TASK_346C/TASK_346D supply real workflow behavior.
- Keep Project folder `Open` disabled unless an already accepted safe action target exists.

Files that should stay out of TASK_346F unless Planner/User expands scope:

- `ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `ProjectWorkbenchLifecycleSections.tsx`
- `ProjectWorkbenchLayout.tsx`
- `useProjectWorkbenchModel.ts`
- `projectWorkbenchLifecycleSelectors.ts`

TASK_346B already completed the hosting and lifecycle banner refocus. TASK_346F should not reopen that scope.

## 6. Context Helper Policy

Allowed with current data:

- operation title
- operation helper summary
- readonly reason
- existing selector blocker
- `folderReady`-derived availability copy, without old readiness/status vocabulary
- safe placeholder copy such as `Sync workflow is not connected yet.`

Hide or placeholder only:

- local folder path fragment
- public Open/Closed year
- file count
- last sync timestamp
- submit time
- pull status
- public folder resolver output
- any claim that Sync/Submit/Pull can execute

Forbidden:

- fake paths, counts, timestamps, or years
- real folder probes from frontend
- `frontend/src/api/client.ts` changes
- old public-drive upload helpers as a substitute for the TASK_346A Sync/Submit/Pull workflow

## 7. UI / Copy Rules For Future Implementation

The future panel must not show old Folder Actions vocabulary:

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

The panel should follow ConnLab product UI guidance:

- restrained product surface
- single primary visual hierarchy under the Matrix workspace
- no nested cards
- no thick side-stripe borders
- no decorative gradients or glassmorphism
- concise operational copy

## 8. Dirty Residual Classification

Targeted status before this Developer planning-first edit showed:

- `M docs/task_board.md`
- untracked TASK_346F task/plan/planner evidence files

Those are Planner/board residuals from the TASK_346F lane creation and are outside this Developer planning-first pass. No product code dirty files appeared in the targeted forbidden-scope status before this pass.

Developer planning-first changed only:

- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`

## 9. Future Test Plan

Future implementation should run focused frontend tests:

- `npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --run`

Required assertions:

- Folder Actions renders as a single-column contextual panel.
- Operation order is Project folder, Public working copy, Approval package, Approved folder.
- Each operation row has icon/title/helper/right-side controls.
- Public working copy shows Auto sync and Sync now.
- Sync/Submit/Pull remain disabled placeholders without mutation helper calls.
- One bottom blocker is shown only when needed.
- Banned old readiness/status/workflow copy is absent.
- Workbench integration still renders Folder Actions in active Matrix, registered no-Matrix, temporary/no-LTR, stopped, and closed states as applicable.

Future validation should also include:

- `npm run build` from `frontend/`
- package `git diff --check`
- trailing whitespace scan
- static banned-copy scan
- targeted forbidden-scope status
- browser smoke on a Workbench project with active Matrix if routed

## 10. Planning Validation

Validation commands for this planning-first pass:

- required docs/evidence exist
- `git diff --check -- docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`
- trailing whitespace scan on the two TASK_346F docs
- targeted forbidden-scope status for product directories and locked paths

Results:

- Required docs/evidence exist: pass.
- `git diff --check -- docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`: pass, no output.
- Trailing whitespace scan on the two TASK_346F docs: pass, no matches.
- Targeted forbidden-scope status:
  - output showed `M docs/task_board.md` as a pre-existing board residual.
  - output showed the TASK_346F plan and Developer evidence as untracked/changed docs.
  - no `frontend/`, `backend/`, root `tests/`, API client, Projects list, or Matrix Editor product files appeared in the targeted status.

No product code, tests, CSS, backend, API client, board, governance protocol, or real folder files were modified by this Developer planning-first pass.

## 11. Stop Point

Developer planning-first complete.

Recommended next role: Reviewer implementation-readiness gate.

Do not start implementation until Reviewer readiness passes and the user explicitly approves Developer implementation.

## 12. Implementation Pass

Implementation was authorized after source-of-truth reconciliation recorded Reviewer implementation-readiness pass and user approval.

### Changed Files

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`

No backend, API client, Projects list, Matrix Editor, real folder, LTR workbook, `.agents`, or `docs/project_management` files were changed.

### Implementation Summary

- Reworked `ProjectFolderActionsSurface` from a two-column disabled tile grid into a single-column contextual file operation panel.
- Kept the accepted four TASK_346B operations and order:
  - `Project folder`
  - `Public working copy`
  - `Approval package`
  - `Approved folder`
- Added existing `UiIcon` icons per operation without adding dependencies or touching shared icon code.
- Added display-only `iconName` and `context` fields to the folder task selector model.
- Kept all Sync/Submit/Pull and Project folder Open controls as disabled placeholders because no accepted backend/API workflow exists in this lane.
- Kept per-control disabled reasons in `title` attributes and moved visible blocker copy to one short bottom blocker.
- Updated CSS from a two-column operation grid to compact row presentation with thin 1px separators, restrained icon slots, and right-side controls.
- Updated focused tests for row order, contextual panel class, helper/context text, single bottom readonly blocker, disabled placeholder behavior, and Workbench integration.

### Scope Proof

- No real Sync/Submit/Pull implementation was added.
- No public folder resolver or `public_folder_year` resolver was added.
- No real file count, last sync, path, year, submit time, or pull status calculation was added.
- No `frontend/src/api/client.ts` change was made.
- No old public-drive upload behavior is called. Static scan for old upload/refresh action target assignment in the TASK_346F production files had no matches.
- `ProjectWorkbenchActiveMatrixWorkspace.tsx`, `ProjectWorkbenchLifecycleSections.tsx`, `ProjectWorkbenchLayout.tsx`, `useProjectWorkbenchModel.ts`, and `projectWorkbenchLifecycleSelectors.ts` were not edited.

### Validation Results

- Focused frontend tests:
  - `npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --run`
  - Result: pass, `3` files / `49` tests.
- Frontend build:
  - `npm run build`
  - Result: pass. Existing Vite chunk-size warning remains for the main JS bundle.
- Package diff check:
  - `git diff --check -- frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`
  - Result before this evidence update: pass with LF/CRLF normalization warnings only.
- Trailing whitespace scan:
  - `Select-String` over TASK_346F package files with `[ \t]+$`
  - Result before this evidence update: pass, no matches.
- Static banned-copy scan:
  - Scanned TASK_346F production files for string literals containing `Ready`, `Partial`, `Waiting`, `Not current`, `Already current`, `Ready to upload`, `Request material`, `Source material`, `Project Folder progress`, `Next step`, `Public drive upload`, `Upload to public drive`, and `Refresh public-drive preview`.
  - Result: pass, no matches.
  - A broad naked `Ready` scan was intentionally not used as the final check because it matches internal identifiers such as `folderReady`.
- Mutation/action-target scan:
  - Scanned TASK_346F production files for assignment/call usage of old public-drive or legacy folder action targets.
  - Result: pass, no matches.
- Targeted forbidden-scope status:
  - `docs/task_board.md` remains a source-of-truth residual from Planner reconciliation and was not edited by this implementation pass.
  - TASK_346F package files appear as expected.
  - No backend, API client, Projects list, Matrix Editor, real folder, `.agents`, or `docs/project_management` product/governance locked-path changes appeared.

Final package checks after this evidence update:

- `git diff --check` for TASK_346F package files: pass with LF/CRLF normalization warnings only.
- Trailing whitespace scan for TASK_346F package files: pass, no matches.
- Targeted forbidden-scope status: shows expected TASK_346F package files and the pre-existing `M docs/task_board.md` source-of-truth residual only; no backend/API client/Projects list/Matrix Editor/real folder/`.agents`/`docs/project_management` locked-path changes.

### Browser Smoke

Browser smoke was not completed in this Developer thread because tool discovery did not expose a direct in-app Browser control tool. QA should smoke `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f` and verify that the right-side Folder Actions panel is single-column, ordered, contextual, and still secondary to the Matrix table.

### Stop Point

Developer implementation complete. Stop after callback.

Recommended next role: Reviewer implementation gate.

## Integrator Packaging Checkpoint - 2026-06-30

Integrator gate: `accepted`.

### Package Scope Accepted

- Approved TASK_346F frontend Folder Actions UI/CSS/test files:
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - `frontend/src/workbench.css`
- TASK_346F task, plan, planner/developer/reconciliation/QA evidence, QA artifacts, and `docs/task_board.md` closeout.

### Excluded Scope

- No backend/API/schema/file-operation implementation.
- No `frontend/src/api/client.ts`.
- No public folder resolver, Sync/Submit/Pull execute behavior, real file count, or last-sync calculation.
- No Projects list, `ProjectListPage`, Matrix Editor business logic, public-drive authority writes, real local/public folders, LTR workbook files, TASK_346C backend workflow, StepInstance, Report, AI, permissions, LAN/server, multi-user, `.agents`, `docs/project_management`, `temp_agents_stash.md`, or unrelated governance/orchestration files.

### Integrator Validation

- Focused frontend tests rerun:
  - `npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --run`
  - Result: passed, `3` files / `49` tests.
- Frontend build rerun:
  - `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- Staged package checks:
  - `git diff --cached --check` passed with LF/CRLF normalization warnings only.
  - Staged whitelist and forbidden-path checks passed.
- QA browser smoke confirmed active Matrix Workbench `DL-2026-05-011` at `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.

### Final Stop Point

TASK_346F is packaged locally by Integrator. Remote push was intentionally not performed. Recommended next role: Orchestrator/Planner for one legal next routing action, or User if the Folder Actions series should pause.
