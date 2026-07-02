# TASK_348B Local LTR Duplicate Cancel State Recovery Plan

> Status: complete/accepted by Integrator
> Task: `TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY`
> Lane: `local-ltr-duplicate-cancel-state-recovery`
> Created: 2026-07-03

---

## 1. Discovery Summary

User-reported post-acceptance finding:

- In New Project / Intake, a `LOCAL LTR CONFLICT` panel appears after TASK_348A duplicate handling.
- The panel offers `Open existing project`, `Cancel`, and `Continue with this LTR number`.
- After clicking `Cancel`, the page returns to the intake screen but appears locked or incomplete: the operator can effectively only choose `Import`.
- Expected behavior: Cancel cancels only the duplicate-resolution flow and restores the current imported application to its normal editable/apply state.

Repository facts:

- `LocalLtrDuplicateConflictPanel` delegates Cancel through `onCancel`.
- `useNewProjectCompletion.clearLocalDuplicateConflict` only clears `localDuplicateConflict`.
- No backend write is performed by the Cancel handler.
- `IntakeInboxPage` controls editability through parent state including `packageImport`, `activeCase`, `completionLoading`, `editorLoading`, `confirmed_project_id`, required-field readiness, and setup-field readiness.
- Existing TASK_348A frontend tests cover duplicate confirmation busy-lock and panel callback wiring, but do not cover Cancel recovery at the parent page/state boundary.

Definition of Ready:

- Satisfied for a planned lightweight frontend follow-up lane.
- No blocker questions are required for planning.
- Implementation was completed and accepted after Reviewer implementation gate, QA gate, and Integrator packaging/readiness.

---

## 2. Current-State Analysis

Confirmed behavior from code:

- Cancel is a local UI action and should not call backend duplicate-resolution endpoints.
- Current hook behavior closes the conflict panel but does not explicitly restore or snapshot page readiness state.
- The parent page can still render disabled or empty surfaces if its active intake case/session/setup state has changed or if stale loading/confirmed/missing-key gates remain active.

Planner inference for Developer discovery:

- Developer should reproduce which exact parent condition remains false after Cancel in the accepted package: selected source/session, `activeCase`, setup values, required field readiness, completion loading, editor loading, or confirmed-project state.
- The fix should live at the smallest frontend state boundary that preserves the current imported application after a duplicate conflict is dismissed.
- If Developer discovers that backend API semantics are required for Cancel recovery, stop and return to Planner; this lane does not authorize backend changes.

---

## 3. Target UX Contract

Cancel must behave as a dismiss/recover action:

- Close the conflict panel.
- Preserve the imported request package, selected asset, selected intake case, parsed form field state, setup confirmation values, and draft edits.
- Restore the same Apply LTR / Create Temporary availability that existed before the duplicate conflict, subject to the existing readiness rules.
- Release any local busy/confirmation lock.
- Leave success/failure feedback clear if a later Apply attempt still fails.
- Avoid forcing a re-import when the current request is already loaded.

Cancel must not:

- Send `duplicate_resolution`.
- Call confirm/replace APIs.
- Retire, supersede, delete, or overwrite any local LTR/project record.
- Change public workbook authority.
- Clear the intake session.
- Create a temporary project.

---

## 4. Planned Implementation Shape

Developer planning-first should:

1. Reproduce the defect with a focused fixture or component/hook test.
2. Identify the exact state gate that leaves the intake page in an import-only state after Cancel.
3. Patch the minimal frontend state boundary.
4. Add regression coverage that fails on the current accepted behavior and passes after the fix.
5. Keep backend/API/storage semantics untouched.

Likely implementation areas:

- `useNewProjectCompletion` for local conflict clear/recovery state if the hook owns the stale state.
- `IntakeInboxPage` if the page loses or fails to restore the selected intake/session/setup state after duplicate conflict dismissal.
- `NewProjectCompletionDock` only if its disabled calculation receives stale props after Cancel.

---

## 5. May Touch

Future Developer implementation may touch:

- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.test.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
- `frontend/src/intake-inbox.css` only for a small recovery/error hint if required.
- `tasks/TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY.md`
- `docs/task_348b_local_ltr_duplicate_cancel_state_recovery_plan.md`
- `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_*.md`
- `docs/task_board.md` through normal lane flow.

---

## 6. Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- Basic Information residual files
- Settings/LTR helper residual files
- release/packaging files and residuals
- real public-drive LTR workbook/data
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- `.agents/**`
- `docs/project_management/**`
- `temp_agents_stash.md`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

---

## 7. Locked Paths

Locked unless a separate approved lane exists:

- `backend/application/ltr_*`
- `backend/application/new_project_completion_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/infrastructure/storage/**`
- `frontend/src/api/client.ts`
- real workbook files and public-drive paths
- Workbench Folder Actions / public folder workflow files
- Matrix Editor and Projects registry files
- `.agents/**`
- `docs/project_management/**`
- release/packaging residuals

---

## 8. Validation Plan

Focused frontend tests:

- Conflict appears after a mocked `LOCAL_LTR_DUPLICATE` response.
- Clicking Cancel hides the conflict panel.
- The imported source/session/case remains selected.
- The form remains editable when it was editable before the conflict.
- Apply LTR / Create Temporary disabled state after Cancel matches the original readiness rules.
- Cancel performs no second `completeNewProject` call and sends no `duplicate_resolution`.
- Cancel clears stale busy/duplicate-confirming lock.

Build/smoke:

- Run the closest focused frontend test command for `useNewProjectCompletion`, `LocalLtrDuplicateConflictPanel`, `IntakeInboxPage`, and `NewProjectCompletionDock`.
- Run `npm run build`.
- Browser smoke New Project / Intake with safe mocked or fixture local duplicate conflict. Verify Cancel returns to editable current application state and does not require re-import.

Safety checks:

- No backend/API/storage diffs.
- No real workbook/folder mutation.
- No Basic Information, Settings/LTR, release/packaging, `.agents`, or `docs/project_management` changes.

---

## 9. Risks

- Page-level state may require a heavier test harness than the existing panel/hook tests.
- The visible symptom may depend on an integration state sequence that is not fully captured by current tests.
- If the issue is caused by backend response/session mutation rather than frontend state, this lane should stop and return to Planner.

---

## 10. Recommendation

Create `TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY` as a planned lightweight frontend follow-up lane.

Recommended next role: Orchestrator/User for next routing decision.

Integrator gate: accepted.

---

## 11. Developer Planning-First Refinement

Status: developer planning-first complete - pending Reviewer implementation-readiness gate.

Developer discovery read the current accepted TASK_348A frontend state flow after Integrator closeout.

Code-proven state flow:

- `LocalLtrDuplicateConflictPanel` Cancel calls only `onCancel`.
- `IntakeInboxPage` passes `clearLocalDuplicateConflict` as that `onCancel`.
- `useNewProjectCompletion.clearLocalDuplicateConflict` currently only clears `localDuplicateConflict`.
- Cancel does not call `confirmDuplicateResolution`, does not call `completeNewProject`, does not send `duplicate_resolution`, and does not touch backend state.
- `IntakeInboxPage` renders the editor and completion dock only when both `packageImport` and `activeCase` are present.
- `activeCase` is derived from `review` plus `selectedCaseId`.
- Normal Apply eligibility is still derived from `requiredState`, `setupMissingKeys`, `completionLoading`, `editorLoading`, and `activeCase.confirmed_project_id`.

Root-cause candidates that must be proven during implementation:

1. Parent state loss: after conflict and cancel, `packageImport`, `review`, `selectedCaseId`, or `activeCase` may no longer be present, causing the page to show only import/start surfaces.
2. Readiness reset: imported application remains loaded, but `setupValues`, `fieldValues`, `sampleRows`, or `requestedTestingRows` are reset from an empty or stale `activeCase`, leaving Apply/Create Temporary disabled by normal readiness rules.
3. Stale lock: `completionLoading`, `duplicateConfirming`, or `editorLoading` remains true after cancel, keeping import/editor/dock disabled.
4. Missing page-level regression: current tests cover hook busy state and conflict panel callbacks, but not the parent page recovery contract.

Implementation strategy:

- Add a focused page or hook/page-boundary test that reproduces a ready New Project state, forces a `LOCAL_LTR_DUPLICATE` conflict from the Apply LTR path, clicks Cancel, and asserts:
  - conflict panel disappears;
  - imported source/session/case remains selected;
  - setup values and editable form values remain present;
  - Apply LTR and Create Temporary availability match the pre-conflict readiness state;
  - no second `completeNewProject` call is made and no request contains `duplicate_resolution`.
- If the failing regression shows only hook state is stale, fix `useNewProjectCompletion.clearLocalDuplicateConflict` to clear only local duplicate flow state and any stale duplicate-confirming/completion-error state needed for recovery.
- If the failing regression shows page state is lost, fix `IntakeInboxPage` at the smallest state boundary that preserves the loaded `packageImport`, `selectedAssetId`, `selectedPrecheckCaseId`, `review`, `selectedCaseId`, and setup/form state after cancel.
- If the failing regression shows readiness values are reset, preserve the current setup/form refs or avoid resetting them when cancel only dismisses the duplicate conflict.
- If implementation discovery proves backend or API contract changes are required, stop and return to Planner. TASK_348B does not authorize backend changes.

Exact future implementation May Touch:

- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.test.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx` only if Cancel needs an explicit disabled/recovery affordance
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx` only if readiness/disabled propagation is proven wrong
- `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
- `frontend/src/intake-inbox.css` only if a small restrained recovery hint is required
- `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_developer.md`

Implementation Must Not Touch:

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- Basic Information residual files
- Settings/LTR helper residual files
- release/packaging files and residuals
- real public-drive LTR workbook/data
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- `.agents/**`
- `docs/project_management/**`
- `temp_agents_stash.md`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

Focused validation for implementation:

- `npm test -- useNewProjectCompletion LocalLtrDuplicateConflictPanel IntakeInboxPage NewProjectCompletionDock --run`
- `npm run build`
- `git diff --check` on the TASK_348B package files
- trailing whitespace scan on touched files
- forbidden-scope status proving no backend/API/storage/workbook/folder/Matrix/Workbench/Projects/Settings/release residual changes
- browser smoke on New Project / Intake using a safe mocked or fixture duplicate conflict, if QA has a safe harness. Do not use real public-drive workbook mutation to create the smoke state.

Developer planning decision:

- Developer planning gate: ready.
- Reviewer implementation-readiness gate: passed per current Orchestrator/User delegation.
- User approval: explicit approval received for TASK_348B reconciliation and Developer implementation.
- Recommended next role: Developer implementation pass after board/source-of-truth reconciliation.

---

## 12. Source-of-Truth Reconciliation

Status: implementation authorized / pending Developer implementation.

Fact chain:

1. Planner planned lane creation completed in `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_planner.md`.
2. Reviewer plan gate passed.
3. User approved Developer planning-first.
4. Developer planning-first completed in `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_developer.md`.
5. Reviewer implementation-readiness gate passed.
6. User explicitly approved TASK_348B reconciliation and Developer implementation.

Scope remains limited to frontend local duplicate Cancel state recovery. This reconciliation does not authorize backend duplicate/token/audit/current-owner changes, public workbook authority changes, real workbook/folder mutation, Matrix Editor, Folder Actions/public folder workflow, Project Workbench unrelated behavior, Basic Information residual cleanup, Settings/LTR helper cleanup, release/packaging cleanup, `.agents/**`, `docs/project_management/**`, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.
