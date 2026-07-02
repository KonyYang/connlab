# TASK_348A QA Evidence - local-ltr-duplicate-override-confirmation

Date: 2026-07-02
Role: QA / Smoke Owner
Gate: QA
Result: qa_pass

## Scope And Board Check

- Current phase from `docs/task_board.md`: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active lane under this QA gate: `TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION` / `local-ltr-duplicate-override-confirmation`.
- User delegation provided the latest Reviewer re-gate result as pass. The local board still showed TASK_348A in Reviewer re-gate timing; QA did not update `docs/task_board.md`.
- QA touched only this evidence file. No product source, tests, packaging, commit, push, real public-drive LTR workbook/data, or real folders were modified by QA.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION.md`
- `docs/task_348a_local_ltr_duplicate_override_confirmation_plan.md`
- `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_developer.md`
- `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_scope_reconciliation_planner.md`
- `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_reconciliation_planner.md`
- Current git status/diff for TASK_348A package and external residual isolation.

## Validation Commands

Backend/API duplicate and migration smoke:

```powershell
py -m pytest tests\integration\test_ltr_duplicate_resolution_migration.py tests\integration\test_new_project_completion_api.py -q
```

Observed result: `11 passed in 6.70s`.

Backend unit coverage for local commit, workbook authority, and adapter behavior:

```powershell
py -m pytest tests\unit\test_ltr_local_commit_service.py tests\unit\test_ltr_workbook_write_commit_service.py tests\unit\test_ltr_excel_authority_adapter.py -q
```

Observed result: `24 passed in 0.67s`.

Adjacent parsed-intake/setup defaults coverage:

```powershell
py -m pytest tests\unit\test_intake_case_review_service.py -q
```

Observed result: `22 passed in 0.70s`.

Frontend duplicate confirmation / busy-lock focused tests:

```powershell
cd frontend
npm test -- useNewProjectCompletion LocalLtrDuplicateConflictPanel NewProjectCompletionDock --run
```

Observed result: 3 test files passed / 4 tests passed.

Frontend build:

```powershell
cd frontend
npm run build
```

Observed result: build passed. Existing Vite chunk-size warning only.

Backend compile smoke:

```powershell
py -m py_compile backend\application\ltr_duplicate_resolution_service.py backend\application\ltr_service.py backend\application\ltr_authority.py backend\application\ltr_workbook_write_commit_service.py backend\application\ltr_excel_authority_adapter.py backend\application\ltr_local_commit_service.py backend\application\new_project_completion_service.py backend\api\routes_new_project_completion.py backend\api\routes_ltr.py backend\api\dependencies.py backend\infrastructure\storage\models.py backend\infrastructure\storage\database.py backend\infrastructure\storage\repositories\records.py backend\infrastructure\storage\repositories\ltr_duplicate_resolution.py backend\application\intake_case_review_service.py
```

Observed result: passed with no output.

Diff and static checks:

```powershell
git diff --check -- <TASK_348A package files>
```

Observed result: passed with LF/CRLF warnings only.

Trailing whitespace scan on TASK_348A package files:

```powershell
Select-String -Path <TASK_348A package files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

No-real-workbook/folder scan on TASK_348A package files:

```powershell
Select-String -Path <TASK_348A package files> -Pattern 'D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|Workbooks\.Open|SaveAs|win32com|Dispatch\(|copyfile|shutil\.copy|os\.remove|unlink\(|rmtree' -Encoding UTF8
```

Observed result: one generic `target.unlink(missing_ok=True)` match in `backend/api/dependencies.py` `_rename_staged_file`; this is a staged upload rename helper, not a real public-drive/LTR workbook/folder target. No real `D:\Test Project`, `D:\PublicProject`, workbook COM/open/save, copy, or recursive delete target was found in the TASK_348A package scan.

Forbidden-scope status check:

```powershell
git status --short -- .agents docs/project_management frontend/src/features/matrix-editor frontend/src/features/project-workbench frontend/src/features/project-folder frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx backend/application/public_folder_workflow_service.py backend/api/routes_public_folder_workflow.py
```

Observed result: no output. QA found no TASK_348A changes in `.agents/**`, `docs/project_management/**`, Matrix Editor, Workbench, Project Folder Actions/public-folder workflow, Projects registry/list, or public-folder routes/services.

## Backend/API Observations

- Local duplicate returns structured conflict: focused API tests cover `409` with `detail.code == "LOCAL_LTR_DUPLICATE"`, ltr number, existing owner/project summary, and resolution token.
- No write/retire/current-owner change without confirmation: API tests cover duplicate conflict before confirmation and local owner records remain unchanged until the second confirmation payload is submitted.
- Confirm continue with token/intent/ack succeeds: API tests cover duplicate resolution payload with token, intent, acknowledgement, and reason, then assert old owner is no longer current, new owner is current, and audit rows are written.
- Public workbook authority duplicate is not bypassed: workbook authority/service tests passed, including duplicate workbook behavior and failure/no-local-register behavior when workbook commit is rejected.
- Migration/storage smoke passed via `test_ltr_duplicate_resolution_migration.py` in the 11-test integration run.

## Frontend/API-Client Observations

- `LocalLtrDuplicateConflictPanel` tests verify existing local owner summary, Cancel, safe open-existing action, required acknowledgement and confirmation note, and explicit second confirmation before owner replacement.
- `useNewProjectCompletion` test verifies B2: `completionLoading` remains true while `duplicateConfirming` is in flight, so TASK_347A page-level busy/interaction lock participates in the duplicate second-confirmation request.
- Source inspection confirms `completionLoading: completionLoading || duplicateConfirming` in `useNewProjectCompletion.ts`.
- `NewProjectCompletionDock` renders compact busy copy with `role="status"` and `aria-live="polite"`.
- `IntakeInboxPage.tsx` wires `completionLoading` into page-level interaction lock/disabled states for import, editor/setup, dock, temporary action, and conflicting page actions.

## Adjacent Reconciled Scope Observations

- `tests/unit/test_intake_case_review_service.py` passed and covers parsed-intake defaults for setup sample/test fields and test type.
- Source inspection of `NewProjectSetupConfirmationPanel.tsx` confirms `Sample Description*` appears before `Test Item*`.
- QA saw no broad New Project setup refactor beyond the reconciled adjacent scope.

## Browser Smoke

Live browser duplicate-confirmation smoke was not executed. The only available live `/intake` path would require exercising Apply LTR behavior against the running app configuration, which may touch real public-drive LTR authority data. No safe mocked/temp browser harness was available in this QA thread. This is recorded as a non-blocking residual because backend/API temp/fixture tests and frontend component/hook tests directly cover the duplicate conflict, cancel/open-existing, second confirmation, and busy-lock behavior without mutating real workbook or folder data.

## Residuals And Isolation

- Full `git status --short` still shows external dirty residuals in Basic Information, Settings/LTR helper files, release/packaging files, `docs/task_board.md`, and `temp_agents_stash.md`. QA did not modify or include them.
- TASK_348A package includes accepted API/client/frontend/backend/test files plus the Planner-accepted adjacent setup/defaulting files. External Settings/LTR, Basic Information, release/packaging, Matrix, Folder Actions, and orchestration residuals must remain isolated during Integrator packaging.

## QA Decision

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Blocking findings: none.

Residual risk: no live browser Apply LTR duplicate smoke was performed because a safe mocked/temp browser harness was unavailable and the live path could mutate real LTR authority data. If full end-to-end browser duplicate confirmation is required, route a separate safe fixture/harness lane rather than using real public-drive workbook data.
