# TASK_347A New Project Apply LTR Busy Lock UX

> Status: complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness
> Created: 2026-07-02
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Lane: `new-project-apply-ltr-busy-lock-ux`

---

## 1. Purpose

Plan a controlled frontend UX lane for the New Project `Apply LTR Number` operation.

The operation writes to the authoritative external LTR workbook through the existing `complete-new-project` orchestration. It can be slow and important. Operators need a clear busy state and an interaction lock so they do not click sidebar navigation, `Import`, attachment import, setup fields, or other conflicting page actions while ConnLab is applying the LTR number.

---

## 2. Discovery Summary

Confirmed by user:

- Clicking `Apply LTR Number` can take a long time and should feel visibly in progress.
- During LTR application, the page should block conflicting user actions, including sidebar navigation and `Import`.
- The UX should be similar in spirit to the project folder creation busy lock.
- The UI should show short status copy such as the target file being opened / filled, without making the operator think the UI has frozen.

Confirmed by repository evidence:

- `frontend/src/features/new-project/useNewProjectCompletion.ts` calls only `completeNewProject(activeCase.case_id, ...)`.
- `frontend/src/api/client.ts` maps `completeNewProject` to `POST /api/intake-cases/{case_id}/complete-new-project`.
- `backend/api/routes_new_project_completion.py` calls `NewProjectCompletionService.complete`.
- `backend/application/new_project_completion_service.py` coordinates intake confirmation, setup promotion, and LTR authority commit.
- `backend/application/ltr_workbook_write_commit_service.py` performs the workbook write through a locked transaction gateway and local LTR registration.
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx` already changes the button text to `Applying LTR number...` and prevents double submit through `completionDisabled`.
- `frontend/src/features/intake/IntakeSourcePanel.tsx` disables `Import` only for `importing`, not for `completionLoading`.
- `frontend/src/components/layout/Sidebar.tsx` has no busy-lock or navigation-lock prop.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` and tests include a project folder progress dialog pattern while a folder workflow is running.

Inferred by Planner:

- First implementation should be frontend-only unless Reviewer finds that backend progress phases are required.
- The UI should avoid fake granular progress because the existing backend endpoint does not expose phases.
- The safest first behavior is a page/shell interaction lock with honest compact copy, for example `Applying LTR number. ConnLab may open and update the workbook. Keep this page open.`

---

## 3. Scope

In scope:

- Add a New Project busy/locked state for `Apply LTR Number`.
- Disable sidebar navigation and sidebar collapse while the LTR application request is running.
- Disable New Project `Import`, drag/drop import, attachment import/select/open, setup fields, editor fields, temporary project action, and the primary `Apply LTR Number` action while the operation is running.
- Show compact business-readable status/progress copy.
- Prevent double submit and conflicting actions.
- Preserve current user input and draft state.
- Preserve existing success and failure recovery behavior.
- Add focused frontend tests and static/source checks.

Out of scope:

- Backend LTR workbook write semantic changes.
- New backend progress/event streaming.
- LTR workbook transaction, locking, backup, row mapping, number allocation, or authority writes.
- Any real LTR workbook mutation in tests.
- Project folder creation behavior.
- New Project duplicate model redesign.
- Project Registry, Workbench, Matrix Editor, Reports, StepInstance, AI, permissions, LAN/server, or multi-user scope.

---

## 4. May Touch

Developer implementation May Touch:

- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
- `frontend/src/styles.css`
- focused frontend tests for New Project busy lock and shell navigation lock, including new colocated tests if needed
- `tests/unit/test_frontend_shell_files.py` only for narrow static guard coverage if useful
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md`

Planner May Touch:

- `tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md`
- `docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md`
- `docs/task_board.md`

---

## 5. Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts` unless Reviewer explicitly identifies a typed-client-only blocker during plan review
- LTR workbook transaction, commit, preview, number-rule, authority, compatibility, local-config, or password services
- real LTR workbook files and public-drive authority paths
- real `D:\Test Project/**`, `D:\PublicProject/**`, or any real project/public folder
- Project Registry / `frontend/src/pages/ProjectListPage.tsx`
- Project Workbench Folder Actions / Sync / Submit / Pull semantics
- Matrix Editor business logic
- release/packaging residuals
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

---

## 6. Locked Paths

- `backend/application/ltr_workbook_write_commit_service.py`
- `backend/application/new_project_completion_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/infrastructure/office/**`
- `backend/infrastructure/storage/**`
- `frontend/src/api/client.ts` by default
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- real LTR workbook files
- `.agents/**`
- `docs/project_management/**`
- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- `temp_agents_stash.md`

---

## 7. UX Acceptance Draft

- Clicking `Apply LTR Number` immediately enters a busy/locked state.
- The primary button cannot be clicked again and uses clear loading copy.
- Sidebar navigation and collapse controls are disabled or ignored with an accessible disabled state while busy.
- `Import`, drag/drop import, attachment import/select/open, setup controls, editor controls, and temporary project creation are disabled while busy.
- A compact status surface is visible near the New Project completion area or page shell.
- Status copy is honest and short. It must not claim exact backend phases unless the backend exposes them.
- Success still navigates to the created project through the existing flow.
- Failure leaves the operator on New Project with input preserved and an actionable error.
- No global app freeze beyond the New Project shell/page lock unless the approved design explicitly justifies it.

---

## 8. Validation Gate

Before Reviewer implementation gate:

- Focused frontend tests prove the busy state disables `Apply LTR Number`, `Import`, attachment import actions, setup/editor fields, temporary project action, and sidebar navigation.
- Focused tests prove success and failure recoveries preserve existing behavior.
- Tests verify compact busy copy is rendered while the operation is pending.
- Frontend build passes.
- Browser smoke on `/intake` verifies the visible busy/locked state during a mocked or delayed `Apply LTR Number` operation.
- Static/grep checks confirm no backend LTR workbook services, transaction gateways, real workbook files, Project Registry, Workbench Folder Actions, Matrix Editor, or release residuals are touched.
- No real LTR workbook mutation occurs in tests.

---

## 9. Merge Gate

Not implementation-approved yet.

Future merge requires:

- User approval after Reviewer plan gate.
- Developer implementation evidence.
- Reviewer implementation gate pass.
- QA/browser smoke if routed by Reviewer/Planner.
- Integrator packaging/readiness.
- Package checks excluding backend authority writes, real workbook/folder mutation, release residuals, `.agents/**`, and `docs/project_management/**`.

---

## 10. Historical Stop Point

Planner created this lane as planned only. Reviewer plan gate, Developer planning-first, Reviewer implementation-readiness, and user implementation approval have since passed. See section 11 for the current source-of-truth.

## 11. Planner Reconciliation

Planner reconciliation aligned repository source-of-truth after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness gate passed.
- User approved `TASK_347A` reconciliation and Developer implementation.

## 12. Integrator Closeout

TASK_347A is complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness.

Accepted outcome:

- New Project `Apply LTR Number` uses the existing `completionLoading` state as the page busy/interaction lock.
- Sidebar navigation/collapse, Import, drag/drop, hidden file inputs, attachment select/open/import, duplicate-resolution actions, editor fields, and temporary project action are disabled or guarded while Apply LTR is busy.
- The busy state shows compact honest copy and does not expose fake backend phases.
- No backend LTR workbook write semantics, backend progress/event streaming, API client, real workbook/folder mutation, Project Registry, Workbench Folder Actions, Matrix Editor, Settings/LTR/release residual cleanup, `.agents/**`, or `docs/project_management/**` changes are included.

Remote push is not authorized by this lane.
