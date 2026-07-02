# TASK_348B QA Evidence - local-ltr-duplicate-cancel-state-recovery

Date: 2026-07-03
Role: QA / Smoke Owner
Gate: QA
Result: qa_pass

## Scope And Board Check

- Current phase from `docs/task_board.md`: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active lane under this QA gate: `TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY` / `local-ltr-duplicate-cancel-state-recovery`.
- User delegation provided Reviewer implementation gate status as pass. The local board still showed TASK_348B as implementation authorized / pending Developer implementation, so QA records this as a board timing mismatch and did not update `docs/task_board.md`.
- QA touched only this QA evidence file. No product code, tests, backend, task board, packaging, commit, push, real public-drive LTR workbook/data, or real folders were modified by QA.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY.md`
- `docs/task_348b_local_ltr_duplicate_cancel_state_recovery_plan.md`
- `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_developer.md`
- `docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_reconciliation_planner.md`
- Current git status/diff for TASK_348B package and external residual isolation.

## Validation Commands

Focused frontend tests:

```powershell
cd frontend
npm test -- LocalLtrDuplicateConflictPanel NewProjectCompletionDock useNewProjectCompletion IntakeInboxPage --run
```

Observed result: 4 test files passed / 5 tests passed.

Key observed regression:

- `IntakeInboxPage local LTR duplicate cancel recovery > restores the imported case and apply readiness when local duplicate cancel closes the conflict` passed.
- The test starts from a ready imported application state, mocks a `LOCAL_LTR_DUPLICATE` response, simulates a review refresh without cases while the conflict is visible, clicks `Cancel`, then verifies the conflict panel closes, Apply LTR is restored/enabled, the sample/form state remains visible, and `completeNewProject` was called only once.

Frontend build:

```powershell
cd frontend
npm run build
```

Observed result: build passed. Existing Vite chunk-size warning only.

Diff check for TASK_348B tracked package file:

```powershell
git diff --check -- frontend/src/pages/IntakeInboxPage.tsx frontend/src/pages/IntakeInboxPage.test.tsx docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_developer.md
```

Observed result: passed with LF/CRLF warning only for `frontend/src/pages/IntakeInboxPage.tsx`. Note: `frontend/src/pages/IntakeInboxPage.test.tsx` and Developer evidence are currently untracked, so QA also covered them with direct text scans below.

Trailing whitespace scan:

```powershell
Select-String -Path frontend/src/pages/IntakeInboxPage.tsx,frontend/src/pages/IntakeInboxPage.test.tsx,docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_developer.md -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

No-real-workbook/folder and no-write-scope scan:

```powershell
Select-String -Path frontend/src/pages/IntakeInboxPage.tsx,frontend/src/pages/IntakeInboxPage.test.tsx,docs/lane_evidence/TASK_348B_local-ltr-duplicate-cancel-state-recovery_developer.md -Pattern 'D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|Workbooks\.Open|SaveAs|win32com|Dispatch\(|copyfile|shutil\.copy|os\.remove|unlink\(|rmtree|duplicate_resolution|retire|supersede|current_owner|audit|fetch\(|axios|requestJson' -Encoding UTF8
```

Observed result:

- No product/test matches for real workbook/folder paths, Office COM/open/save, copy/delete operations, `duplicate_resolution`, retire/supersede/current-owner/audit mutation, or direct request/fetch helpers.
- Matches appeared only in Developer evidence text documenting forbidden/negative expectations and locked real-folder examples.

Forbidden-scope status check:

```powershell
git status --short -- backend frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/matrix-editor frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry .agents docs/project_management frontend/src/features/project-basic-information backend/application/project_basic_information_service.py backend/application/project_basic_information_output_identity.py dist_release packaging scripts tasks/RELEASE_001_WINDOWS_DESKTOP_PORTABLE_EXE_PACKAGING.md tasks/RELEASE_003_LOCAL_BROWSER_SERVER_PACKAGING.md temp_agents_stash.md
```

Observed result: external residuals are still visible in backend Basic Information, Settings/LTR helper files, release/packaging files, Basic Information frontend files, `dist_release/`, `packaging/`, release scripts/tasks, and `temp_agents_stash.md`. QA did not touch them and excludes them from TASK_348B. No TASK_348B product change was found in API client, Workbench, Matrix Editor, Projects registry/list, `.agents/**`, or `docs/project_management/**`.

## Source Inspection

- `IntakeInboxPage.tsx` now captures a local duplicate cancel snapshot when `localDuplicateConflict` first appears.
- `handleLocalDuplicateCancel()` calls `clearLocalDuplicateConflict()` and restores `review`, `selectedCaseId`, `fieldValues`, sample rows, requested testing rows, setup values, import message, and related refs from the snapshot when available.
- The Cancel handler does not call `confirmDuplicateResolution`, `completeNewProject`, `duplicate_resolution`, backend fetch/request helpers, retire/supersede, audit, or current-owner write code.
- `IntakeInboxPage.test.tsx` mocks `completeNewProject` to throw `LOCAL_LTR_DUPLICATE`, clicks `Cancel`, verifies conflict removal and restored readiness, and asserts `completeNewProject` was called once, which protects against a second duplicate-resolution request on Cancel.

## Browser Smoke

Live browser duplicate Cancel smoke was not executed. Reproducing the conflict in the running `/intake` UI would require exercising Apply LTR against the live app configuration, which can touch real public-drive LTR authority data. No safe mocked browser harness or disposable duplicate fixture was available in this QA thread.

This is recorded as a non-blocking residual because the focused page-level React test safely reproduces the user-reported state sequence without real workbook/folder mutation: imported application ready, `LOCAL_LTR_DUPLICATE` conflict visible, active review/case temporarily lost, Cancel clicked, conflict closes, imported form/sample state and Apply readiness restored, and no second backend completion call is sent.

## Residuals And Isolation

- External residuals remain present in the worktree: backend Basic Information, Settings/LTR helper files, release/packaging files, `docs/task_board.md`, `frontend/src/workbench.css`, shell guard tests, release artifacts/scripts/tests, and `temp_agents_stash.md`.
- These residuals were not modified, staged, packaged, or validated as TASK_348B by QA.
- TASK_348B implementation package observed by QA is limited to `frontend/src/pages/IntakeInboxPage.tsx`, `frontend/src/pages/IntakeInboxPage.test.tsx`, and Developer evidence.

## QA Decision

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Blocking findings: none.

Residual risk: no live browser duplicate Cancel smoke was performed because a safe mocked browser harness was unavailable and the real Apply LTR path could mutate real LTR authority data. If full browser duplicate recovery must be observed, route a separate safe fixture/harness lane rather than using real workbook data.
