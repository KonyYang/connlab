# TASK_347A New Project Apply LTR Busy Lock UX Plan

Status: complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness
Date: 2026-07-02
Task: `TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX`
Lane: `new-project-apply-ltr-busy-lock-ux`
Role: Planner

## 1. Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task before this plan: none. `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING` is complete/accepted.
- Current Planner task: create a formal planned lane for New Project Apply LTR Number busy/interaction lock UX.
- Why allowed: Orchestrator/User requested Planner Discovery and formal lane planning for a new need after the prior lane closed.

## 2. User Goal

When the operator clicks `Apply LTR Number` on New Project, ConnLab should visibly enter a long-running LTR application state. The page should prevent sidebar navigation, `Import`, attachment actions, field editing, and other conflicting actions while the external workbook operation is in progress. The UI should use compact operational copy and avoid making the operator think the browser has frozen.

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/api/client.ts`
- `backend/api/routes_new_project_completion.py`
- `backend/application/new_project_completion_service.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- project folder busy-lock pattern in `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` and `ProjectWorkbenchLayout.test.tsx`
- historical tasks `TASK_156`, `TASK_159`, and `TASK_160`
- current `git status --short`

## 4. Current Behavior And Risk

Current behavior:

- New Project completion uses `completionLoading` in `useNewProjectCompletion`.
- The primary button shows `Applying LTR number...` while pending.
- The primary button is disabled while pending, preventing double submit.
- Setup fields and editor fields are partially disabled through `completionLoading`.
- `IntakeSourcePanel` still keys the `Import` button only off `importing`.
- Drag/drop in `IntakeSourcePanel` is not visibly guarded by the LTR busy state.
- Attachment import/open/select actions are not clearly blocked by `completionLoading`.
- `Sidebar` has no page busy/navigation-lock contract.
- Backend completion remains a single request with no exposed phase events.

Risk:

- The operator can try navigation or import actions during an authority workbook write.
- The existing button-level loading text may be too small to reassure the operator during a long Excel/Office operation.
- Adding fake phase progress would be misleading because the backend endpoint does not expose phases.

## 5. Scope Decision

This needs a formal lane because it touches:

- New Project authority workflow UX.
- Page-wide interaction lock.
- Side navigation behavior.
- Import/attachment interference.
- Long-running Office/Excel authority operation feedback.

Recommended first lane: frontend UX lock only.

No backend progress endpoint is required for the first lane. If Reviewer determines real operation phases are necessary, create a later backend progress/status lane instead of expanding TASK_347A.

## 6. Implementation Shape Draft

Preferred shape for Developer planning:

- Keep `completeNewProject` as the only business operation call.
- Treat `completionLoading` as the New Project LTR busy state.
- Lift busy state to `App` or a narrow shell-lock prop only while the active route is `/intake`.
- Add `navigationLocked` or equivalent to `AppShell` / `Sidebar`.
- Pass `completionLoading` into `IntakeSourcePanel`, `AttachmentList`, `NewProjectSetupConfirmationPanel`, `NewProjectApplicationEditor`, and `NewProjectCompletionDock` as a single business busy lock.
- Guard handler functions too, not only button disabled attributes, for drag/drop and hidden file input paths.
- Show one compact busy notice near the completion dock or page surface.
- Use honest copy such as `Applying LTR number. ConnLab may open and update the LTR workbook. Keep this page open.`

## 7. May Touch

Developer May Touch:

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
- focused frontend tests, including new tests if needed
- `tests/unit/test_frontend_shell_files.py` only for narrow static guard coverage if useful
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md`

Planner May Touch:

- `tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md`
- `docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md`
- `docs/task_board.md`

## 8. Must Not Touch / Locked Paths

Must not touch:

- backend LTR workbook write, preview, transaction, number allocation, compatibility, local config, password, or authority services
- backend route/service semantics for `complete-new-project`
- real LTR workbook files
- real local/public project folders
- Project Registry and Projects list
- Project Workbench Folder Actions / Sync / Submit / Pull
- Matrix Editor business logic
- release/packaging residuals
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

Locked paths include:

- `backend/**`
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

## 9. UX Acceptance Criteria

- `Apply LTR Number` enters a clear busy/locked state immediately after click.
- The primary button is disabled and cannot double-submit.
- Sidebar navigation and collapse are disabled or ignored while busy.
- `Import`, drag/drop import, attachment import/select/open, setup fields, editor fields, and temporary project creation are disabled while busy.
- The busy state shows concise operational copy.
- No fake granular progress is shown without backend phases.
- Success continues through the existing project-created route handoff.
- Failure remains on New Project, preserves input, and shows an actionable error.
- The UI remains restrained and dense, matching ConnLab product style.

## 10. Validation Gate

- Focused frontend tests for busy lock coverage.
- Focused shell/navigation test proving sidebar navigation is blocked while New Project LTR busy.
- Focused New Project tests proving `Import`, attachment actions, setup/editor inputs, temporary project, and double submit are disabled/guarded.
- Failure recovery test proving input is preserved after rejected completion.
- Frontend build.
- Browser smoke on `/intake` with delayed/mocked `completeNewProject` or manual slow LTR operation.
- Static forbidden-scope checks proving no backend authority services, real workbook/folder paths, Project Registry, Workbench Folder Actions, Matrix Editor, release residuals, `.agents/**`, or `docs/project_management/**` are included.

## 11. Definition Of Ready

Satisfied for a planned formal lane:

- User scenario is clear.
- Current board state is verified: no active lane, TASK_346G complete/accepted.
- Existing frontend and backend behavior was read from code.
- Scope, non-goals, May Touch, Must Not Touch, Locked Paths, evidence, validation, and merge gates are defined.
- Acceptance path is testable.
- Unresolved backend progress phases are explicitly out of scope.

Reviewer plan gate has passed. This historical Definition of Ready section has since been superseded by Developer planning-first, Reviewer implementation-readiness, and Planner reconciliation in section 14.

## 12. Historical Planner Stop Point

Planner stop point: planned lane created.

Reviewer plan gate has since passed. See section 14 for the current source-of-truth.

## 13. Developer Planning-First Refinement

Developer planning-first was performed after Reviewer plan gate pass and user approval for planning-first only. No product code implementation is authorized by this section.

### Current Code Findings

- `useNewProjectCompletion.ts` already sets `completionLoading` immediately before calling `completeNewProject(...)` and clears it in `finally`.
- `NewProjectCompletionDock.tsx` already disables the primary action through `completionDisabled` and changes the button text to `Applying LTR number...`.
- `NewProjectSetupConfirmationPanel.tsx` already receives `disabled={completionLoading || editorLoading || confirmed}` from `IntakeInboxPage.tsx`.
- `NewProjectApplicationEditor.tsx` does not currently receive `completionLoading` in its `disabled` prop from `IntakeInboxPage.tsx`; editor fields can remain interactive during Apply LTR.
- `IntakeSourcePanel.tsx` disables `Import` only while `importing`; hidden file inputs, drag/drop handlers, source mode selection, and file-change handlers are not guarded by `completionLoading`.
- `AttachmentList.tsx` has no page-lock prop; select, double-click open, import, and duplicate-resolution actions can remain available unless their own local operation is busy.
- `AppShell.tsx` and `Sidebar.tsx` have no shell navigation lock. Sidebar navigation and sidebar collapse remain available unless an item is independently disabled.
- New Project styles are in `frontend/src/intake-inbox.css`, not `frontend/src/styles.css`. Future implementation should prefer `intake-inbox.css` for TASK_347A busy-lock styling.
- There are no colocated React tests for `IntakeInboxPage`, `IntakeSourcePanel`, `AttachmentList`, `Sidebar`, or `NewProjectCompletionDock` in the current frontend tree. Existing `tests/unit/test_frontend_shell_files.py` provides static guard coverage only.

### Implementation Strategy

Use `completionLoading` as the single source for the New Project LTR application busy lock.

1. Page busy state:
   - Define `const ltrApplyBusy = completionLoading` in `IntakeInboxPage.tsx`.
   - Use this value to disable all New Project controls that could conflict with Apply LTR.
   - Preserve local form/input state; do not clear session, form values, setup values, selected attachment, or duplicate-draft state while busy.
2. Shell navigation lock:
   - Add a narrow shell-lock callback from `IntakeInboxPage` to `App.tsx`, for example `onInteractionLockChange`.
   - `App.tsx` stores a New Project-only lock while the active route is `/intake`.
   - Pass a scoped lock prop into `AppShell`, for example `navigationLocked` and `navigationLockReason`.
   - `AppShell` passes the lock to `Sidebar`.
   - `Sidebar` disables or ignores navigation and collapse while locked, with accessible disabled state and a short title such as `Applying LTR number. Keep this page open.`
   - The lock must clear on success, failure, route unmount, and component cleanup.
3. Import and attachment lock:
   - Add an `interactionLocked` / `disabled` prop to `IntakeSourcePanel`.
   - Disable the visible `Import` button and hidden file inputs while locked.
   - Guard `handleDragOver`, `handleDrop`, and source mode selection so drag/drop cannot start an import while Apply LTR is busy.
   - In `IntakeInboxPage`, also guard `handleMsgFileChange`, `handleDirectWordChange`, `handleImportApplicationForm`, `handleOpenAttachment`, `handleResolveDuplicateDraft`, attachment select, and temporary project creation if `ltrApplyBusy` is true.
   - Add `disabled` / `disabledReason` to `AttachmentList` so select, double-click open, import, and duplicate-resolution actions cannot run while locked.
4. Editor/setup/completion lock:
   - Pass `completionLoading` into `NewProjectApplicationEditor` through its existing `disabled` prop.
   - Keep `NewProjectSetupConfirmationPanel` and `NewProjectCompletionDock` using their existing disabled surfaces.
   - Keep `completionDisabled` as the double-submit authority for `Apply LTR Number`.
5. Busy affordance:
   - Add a compact status surface near `NewProjectCompletionDock`, not a large modal unless Reviewer explicitly requests full-page blocking.
   - Use `aria-live="polite"` and `role="status"`.
   - Add a small spinner/progress indicator and cursor/disabled affordance using existing ConnLab restrained product styling.
   - Do not show fake percent, fake step count, or backend phases.

### UX Copy

Recommended user-facing copy:

- Primary button while busy: keep `Applying LTR number...`.
- Busy notice title: `Applying LTR number`
- Busy notice body: `ConnLab may open and update the LTR workbook. Keep this page open.`
- Sidebar/nav disabled title: `Applying LTR number. Keep this page open.`
- Import/drop disabled title: `Applying LTR number. Import is paused.`

Copy rules:

- No em dash.
- No raw backend/API terms.
- No exact phase language such as `Workbook opened` or `Writing row` unless a later backend progress lane exposes real phases.
- Chinese localization may later use equivalent concise copy, for example `正在申请 LTR 编号，请保持此页面打开。`

### Future Exact May Touch

Frontend implementation May Touch should be:

- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/features/intake/AttachmentList.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/features/new-project/useNewProjectCompletion.ts` only if a small guard or status field is needed; avoid changing the `completeNewProject` call contract
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx` only if additional busy reason/title copy is needed
- `frontend/src/intake-inbox.css`
- focused frontend tests, preferably:
  - `frontend/src/features/intake/IntakeSourcePanel.test.tsx`
  - `frontend/src/features/intake/AttachmentList.test.tsx`
  - `frontend/src/components/layout/Sidebar.test.tsx`
  - `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
  - `frontend/src/pages/IntakeInboxPage.test.tsx` if page-level lock behavior can be tested without heavy API setup
- `tests/unit/test_frontend_shell_files.py` only for narrow static guard coverage if useful
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_developer.md`

Remove `frontend/src/styles.css` from the preferred implementation file list unless a Reviewer-approved shell-wide styling need is found. New Project-specific busy styling belongs in `frontend/src/intake-inbox.css`.

### Locked Scope Confirmed

Do not modify:

- `backend/**`
- `frontend/src/api/client.ts`
- LTR workbook transaction, commit, preview, number allocation, local config, password, or authority services
- real LTR workbook files
- Project Registry / Projects list
- Project Workbench Folder Actions / Sync / Submit / Pull
- Matrix Editor
- release/packaging residuals
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

### Test Plan

Future Developer implementation should include focused tests for:

- `Apply LTR Number` enters busy state immediately and cannot double-submit.
- Busy state renders compact status copy and an accessible `role="status"` / `aria-live` region.
- `Import` button and hidden file inputs are disabled while busy.
- Drag/drop during busy does not call import handlers.
- Attachment select, double-click open, import, and duplicate-resolution buttons are disabled or guarded while busy.
- Setup fields and application editor fields are disabled while busy.
- Temporary project creation is disabled/guarded while busy.
- Sidebar navigation and collapse do not fire callbacks while New Project Apply LTR is busy.
- Failure recovery clears the lock and leaves current New Project input/session state intact.
- Success follows the existing `onProjectCreated` handoff.

Validation commands:

- `npm test -- IntakeSourcePanel AttachmentList Sidebar NewProjectCompletionDock IntakeInboxPage --run` or the actual focused test filenames added by implementation.
- `npm run build` from `frontend/`.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or intake or sidebar"` if static guard coverage is added.
- `git diff --check` on the TASK_347A package.
- trailing whitespace scan on package files.
- targeted forbidden-scope status proving no backend/API client/LTR workbook authority/Projects/Workbench/Matrix/release/governance files were changed.
- browser smoke on `/intake` with a delayed or mocked `completeNewProject` request: click `Apply LTR Number`, observe lock/status, try sidebar/Import/attachment actions, verify they are blocked, then verify success/failure clears the lock.

### Developer Planning-First Stop Point

Developer planning-first gate: complete.

Historical recommended next role: Reviewer implementation-readiness gate. This gate has since passed; see section 14 for the current source-of-truth.

Do not start product code implementation unless section 14 source-of-truth authorization is present.

## 14. Planner Reconciliation

Planner reconciliation aligned repository source-of-truth after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness gate passed.
- User approved `TASK_347A` reconciliation and Developer implementation.

Implementation was limited to the approved frontend New Project Apply LTR busy/interaction lock UX scope:

- use `completionLoading` as the Apply LTR busy lock source;
- lock New Project conflicting actions and shell/sidebar navigation while busy;
- show compact honest busy copy;
- preserve current input and existing success/failure recovery;
- do not alter backend LTR workbook write semantics;
- do not add backend progress/event streaming;
- do not touch real workbook/folder authority paths or unrelated Settings/LTR/release residuals.

## 15. Integrator Closeout

Status: complete/accepted.

Integrator packaging/readiness accepted TASK_347A after Developer implementation, Reviewer implementation gate, and QA gate.

Accepted package:

- frontend New Project Apply LTR busy/interaction lock files and focused tests;
- `frontend/src/styles.css` sidebar disabled-state style only, accepted as TASK_347A-scoped shell lock styling;
- TASK_347A task/plan/planner/developer/reconciliation/QA evidence and QA artifacts;
- `docs/task_board.md` TASK_347A closeout only.

Validation summary:

- focused frontend tests passed: `4` files / `4` tests;
- frontend build passed with the existing Vite chunk-size warning only;
- trailing whitespace scan returned no matches;
- fake-progress / forbidden-scope scans had no blocking matches; `async function` matches were non-blocking substring false positives;
- staged package diff, whitelist, and forbidden-path checks passed.

Remote push was intentionally not performed.
