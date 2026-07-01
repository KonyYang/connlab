# TASK_347A New Project Apply LTR Busy Lock UX - Developer Evidence

Status: implementation complete - Reviewer/QA passed - Integrator accepted
Date: 2026-07-02
Role: Developer
Task: `TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX`
Lane: `new-project-apply-ltr-busy-lock-ux`

## 1. Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX`.
- Current lane: `new-project-apply-ltr-busy-lock-ux`.
- Current role: Developer planning-first.
- Allowed reason: Reviewer plan gate passed per Orchestrator delegation and user approved Developer planning-first only.
- Stop point: Reviewer implementation-readiness gate. Product code implementation is not authorized by this pass.

## 2. Required Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md`
- `docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/features/intake/AttachmentList.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/intake-inbox.css`
- project folder busy/progress pattern in `ProjectWorkbenchLayout.tsx`
- current `git status --short`

## 3. Code Findings

- `completionLoading` already starts immediately in `useNewProjectCompletion.complete()` before the `completeNewProject(...)` API call.
- `NewProjectCompletionDock` already disables double submit and changes button copy to `Applying LTR number...`.
- `NewProjectSetupConfirmationPanel` already receives `completionLoading` through its `disabled` prop.
- `NewProjectApplicationEditor` currently does not receive `completionLoading`; editor controls can remain available during Apply LTR.
- `IntakeSourcePanel` disables `Import` only for `importing`, and drag/drop/file-input paths are not guarded by New Project completion state.
- `AttachmentList` has no page busy lock prop for select, open, import, or duplicate-resolution actions.
- `AppShell` / `Sidebar` have no navigation-lock contract. Sidebar navigation and collapse are currently independent from New Project completion state.
- New Project styling is in `frontend/src/intake-inbox.css`, not `frontend/src/styles.css`.
- Existing frontend tests for this area are mostly static guards in `tests/unit/test_frontend_shell_files.py`; implementation should add focused React tests where feasible.

## 4. Planning Decisions

- Use `completionLoading` as the single frontend source for the Apply LTR busy lock.
- Keep the lane frontend-only. Do not add backend progress streaming or alter workbook authority writes.
- Use a New Project page-scoped lock that is lifted to `App` only to disable `AppShell` / `Sidebar` navigation while `/intake` is busy.
- Disable both visible controls and hidden event paths. Buttons alone are not enough because drag/drop, hidden file inputs, double-click open, attachment select, and handler callbacks can bypass visual disabled state.
- Show one compact status surface near the completion dock with honest copy. Do not fake operation phases.
- Preserve form/session/draft state across failure. Success should continue using the existing project-created handoff.

## 5. Future Implementation File List

Preferred May Touch for the future implementation pass:

- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/features/intake/AttachmentList.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/features/new-project/useNewProjectCompletion.ts` only if a small guard/status field is needed
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx` only if busy reason/title copy is needed
- `frontend/src/intake-inbox.css`
- focused frontend tests added or updated for intake/source/sidebar/completion lock behavior
- `tests/unit/test_frontend_shell_files.py` only for narrow static guard coverage if useful
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md`

Not preferred after code inspection:

- `frontend/src/styles.css` should stay out unless a Reviewer-approved shell-wide style need appears. The New Project busy lock belongs in `intake-inbox.css`.

## 6. Locked Scope

Do not modify:

- `backend/**`
- `frontend/src/api/client.ts`
- LTR workbook transaction, commit, preview, number allocation, local config, password, or authority services
- real LTR workbook files
- real local/public project folders
- Project Registry / Projects list
- Project Workbench Folder Actions / Sync / Submit / Pull
- Matrix Editor business logic
- release/packaging residuals
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

## 7. Validation Plan For Implementation

Future implementation should validate:

- focused React tests for `IntakeSourcePanel`, `AttachmentList`, `Sidebar`, `NewProjectCompletionDock`, and page-level `IntakeInboxPage` lock wiring where feasible;
- `Apply LTR Number` busy state starts immediately and prevents double submit;
- Import button, hidden file inputs, drag/drop, attachment select/open/import, duplicate resolution, setup fields, editor fields, and temporary project action are disabled or guarded while busy;
- sidebar navigation and collapse callbacks are ignored while busy;
- compact busy copy is rendered with accessible status semantics;
- failure clears lock and preserves input/session state;
- success keeps existing `onProjectCreated` handoff;
- frontend build passes;
- browser smoke on `/intake` with delayed/mocked completion verifies lock behavior.

## 8. Dirty Workspace Classification

Current worktree contains pre-existing residuals unrelated to this planning pass, including:

- Settings/LTR helper and API residuals;
- external resource route/test residuals;
- Office gateway/parser residuals;
- release/packaging files and `dist_release/`;
- desktop packaging files;
- `docs/task_board.md`;
- `temp_agents_stash.md`;
- existing frontend/workbench residuals from prior accepted lanes.

This Developer planning-first pass only updates:

- `docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md`

No product source, backend source, frontend tests, API client, real folders, `.agents/**`, or `docs/project_management/**` files were changed by this pass.

## 9. Validation

Completed:

- required TASK_347A task, plan, planner evidence, and Developer evidence files exist;
- `git diff --check -- docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md` passed;
- because the TASK_347A plan/evidence files are currently untracked, `git diff --check --no-index` against temporary empty files was also run for both files and passed with LF/CRLF warnings only;
- trailing whitespace scan on the TASK_347A plan/evidence returned no matches;
- targeted status shows this planning-first pass changed only TASK_347A plan/evidence. Existing backend, frontend, Settings/LTR, release/packaging, board, and test residuals are pre-existing external worktree context and remain excluded from TASK_347A.

## 10. Stop Point

Developer planning-first gate: complete.

Recommended next role: Reviewer implementation-readiness gate.

Do not start product code implementation until Reviewer readiness passes and the user explicitly routes Developer implementation.

## 11. Developer Implementation Pass

Status: implementation complete - pending Reviewer implementation gate.

Allowed reason:

- `docs/task_board.md` records `TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX` as implementation authorized.
- Planner reconciliation evidence records Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness pass, user approval, and `implementation_authorized`.

Changed files:

- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/Sidebar.test.tsx`
- `frontend/src/features/intake/AttachmentList.tsx`
- `frontend/src/features/intake/AttachmentList.test.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.test.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/styles.css`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md`

Implementation summary:

- Used existing `completionLoading` as the single Apply LTR busy source.
- Lifted New Project interaction lock to `AppShell` only while `/intake` is applying an LTR number.
- Sidebar navigation and collapse are disabled during Apply LTR with concise title copy: `Applying LTR number. Keep this page open.`
- `IntakeSourcePanel` now disables visible Import, hidden file inputs, source-mode click, and drag/drop import while locked.
- `AttachmentList` now disables select, double-click open, import, and duplicate-resolution actions while locked.
- `IntakeInboxPage` guards handler paths for file import, direct Word upload, attachment import/open/select, duplicate resolution, and temporary project creation.
- `NewProjectApplicationEditor` receives the busy state through its existing `disabled` prop, preserving form/session state while blocking edits.
- `NewProjectCompletionDock` renders a compact `role="status"` busy notice with honest copy: `ConnLab may open and update the LTR workbook. Keep this page open.`

Scope proof:

- No backend files were modified by this implementation pass.
- `frontend/src/api/client.ts` was not modified by this implementation pass.
- No Project Registry, Workbench Folder Actions, Matrix Editor, real workbook/folder path, release/packaging, `.agents/**`, or `docs/project_management/**` changes were made by this implementation pass.
- Existing Settings/LTR/backend/release/Workbench residuals remain external dirty worktree context and are excluded from TASK_347A packaging.

Validation performed:

- TDD red run: `npm test -- IntakeSourcePanel AttachmentList Sidebar NewProjectCompletionDock --run` failed before implementation because controls/status were not locked/rendered.
- Focused frontend tests: `npm test -- IntakeSourcePanel AttachmentList Sidebar NewProjectCompletionDock --run` passed: `4` files, `4` tests.
- Frontend build: `npm run build` passed with existing Vite chunk-size warning only.
- Final package diff check passed for tracked TASK_347A files with LF/CRLF warnings only.
- Final trailing whitespace scan on TASK_347A package files returned no matches.
- Targeted forbidden-scope status showed no TASK_347A changes in locked paths; visible backend/API-client/Workbench/release residuals are pre-existing external context.
- TASK_347A package status contains only approved New Project/shell busy-lock files plus Developer evidence.

Browser smoke:

- Local HTTP probe for `http://localhost:5173/intake` returned `200`.
- In-app Browser smoke could not complete because the Browser webview failed to attach after opening the localhost page. Exact blocker: `Timed out waiting for the Browser webview to attach for this browser-use page`.
- QA should re-smoke `/intake`: click `Apply LTR Number` with a delayed or safe test completion path, verify busy notice, verify sidebar/Import/drag-drop/attachment/editor/temporary actions are blocked, and verify success/failure clears the lock.

Stop point:

- Developer implementation gate complete.
- Recommended next role: Reviewer implementation gate.

## 12. Integrator Packaging / Readiness Closeout

Status: integrator_accepted.

Integrator accepted TASK_347A after Reviewer implementation gate and QA gate passed.

Package accepted:

- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/Sidebar.test.tsx`
- `frontend/src/features/intake/AttachmentList.tsx`
- `frontend/src/features/intake/AttachmentList.test.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.test.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
- `frontend/src/intake-inbox.css`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/styles.css` sidebar disabled-state style only
- TASK_347A task/plan/planner/developer/reconciliation/QA evidence and QA artifacts
- `docs/task_board.md` TASK_347A closeout only

Explicitly excluded:

- backend/API/LTR workbook authority and Settings/LTR helper residuals;
- `frontend/src/api/client.ts`;
- Project Registry, Workbench Folder Actions, Matrix Editor, release/packaging residuals, `temp_agents_stash.md`, `.agents/**`, and `docs/project_management/**`;
- real workbook/folder/public-drive paths and future StepInstance, Report, AI, permissions, LAN/server, multi-user scope.

Integrator validation:

- focused frontend tests: `npm test -- IntakeSourcePanel AttachmentList Sidebar NewProjectCompletionDock --run` passed (`4` files / `4` tests);
- `npm run build` passed with the existing Vite chunk-size warning only;
- trailing whitespace scan on the TASK_347A package returned no matches;
- fake-progress / forbidden-scope scan had no blocking matches; `async function` matches were non-blocking substring false positives;
- staged `git diff --cached --check` and staged whitelist/forbidden-path checks passed.

Remote push was intentionally not performed.
