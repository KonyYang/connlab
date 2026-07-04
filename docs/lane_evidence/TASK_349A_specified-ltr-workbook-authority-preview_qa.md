# TASK_349A QA Evidence - specified-ltr-workbook-authority-preview

Date: 2026-07-04
Role: QA / Smoke Owner
Gate: QA
Result: qa_pass after package-isolation re-gate

Latest checkpoint:

- Original QA gate result was `qa_blocked` for B1 scope/evidence mismatch.
- Planner package reconciliation now explicitly excludes the B1 adjacent residual files from TASK_349A package scope.
- QA re-gate verified path-level candidate package isolation and reran focused validation.
- Developer package-isolation fix removed candidate-file dependencies on excluded duplicate-summary and New Project residual signatures.
- Latest QA re-gate result: `qa_pass`.

## Scope And Board Check

- Current phase from `docs/task_board.md`: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active lane under this QA gate: `TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW` / `specified-ltr-workbook-authority-preview`.
- User delegation provided Reviewer implementation gate status as pass. The local board still showed TASK_349A as implementation authorized / pending Developer implementation; QA records this as a board timing mismatch and did not update `docs/task_board.md`.
- QA touched only this QA evidence file. No product code, tests, task board, packaging, commit, push, real public-drive LTR workbook/data, or real folders were modified by QA.

## Sources Read

- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_reconciliation_planner.md`
- `docs/task_board.md` TASK_347A/TASK_348A/TASK_348B/TASK_349A rows
- TASK_347A/TASK_348A/TASK_348B QA closeout evidence
- Actual `git status` / `git diff` for TASK_349A implementation and external residual isolation

## Validation Commands

Backend focused tests:

```powershell
py -m pytest tests\unit\test_specified_ltr_workbook_authority_preview_service.py tests\integration\test_new_project_completion_api.py -q
```

Observed result: `17 passed in 21.46s`.

Backend compile smoke:

```powershell
py -m py_compile backend\application\specified_ltr_workbook_authority_preview_service.py backend\application\new_project_completion_service.py backend\api\routes_new_project_completion.py backend\api\dependencies.py
```

Observed result: passed with no output.

Frontend focused tests from Developer evidence:

```powershell
cd frontend
npm test -- NewProjectCompletionDock IntakeInboxPage --run
```

Observed result: 2 test files passed / 7 tests passed.

Broader frontend regression sweep for TASK_347A/TASK_348A/TASK_348B preservation:

```powershell
cd frontend
npm test -- LocalLtrDuplicateConflictPanel NewProjectCompletionDock useNewProjectCompletion IntakeInboxPage newProjectRequiredState --run
```

Observed result: 5 test files passed / 11 tests passed.

Additional backend tests for modified intake parser/selection files:

```powershell
py -m pytest tests\unit\test_application_form_parser.py tests\unit\test_intake_form_selection_service.py -q
```

Observed result: `35 passed in 2.97s`.

Frontend build:

```powershell
cd frontend
npm run build
```

Observed result: build passed. Existing Vite chunk-size warning only.

Tracked diff check:

```powershell
git diff --check -- backend/api/dependencies.py backend/api/routes_new_project_completion.py backend/application/intake_form_selection_service.py backend/application/ltr_duplicate_resolution_service.py backend/application/new_project_completion_service.py backend/modules/intake/application_form_parser.py frontend/src/api/client.ts frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx frontend/src/features/new-project/NewProjectApplicationEditor.tsx frontend/src/features/new-project/NewProjectCompletionDock.test.tsx frontend/src/features/new-project/NewProjectCompletionDock.tsx frontend/src/features/new-project/newProjectRequiredState.ts frontend/src/features/new-project/useNewProjectCompletion.ts frontend/src/features/precheck/PrecheckFieldGrid.tsx frontend/src/features/precheck/precheckReviewSelectors.ts frontend/src/intake-case-review.css frontend/src/intake-inbox.css frontend/src/pages/IntakeInboxPage.test.tsx frontend/src/pages/IntakeInboxPage.tsx tests/integration/test_new_project_completion_api.py tests/unit/test_application_form_parser.py tests/unit/test_intake_form_selection_service.py
```

Observed result: passed with LF/CRLF warnings only.

Trailing whitespace scan across observed TASK_349A/package-adjacent files and untracked new files:

```powershell
Select-String -Path <observed TASK_349A/package-adjacent files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

Production no-real-workbook/folder mutation scan:

```powershell
Select-String -Path <observed production files> -Pattern 'D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|Workbooks\.Open|SaveAs|win32com|Dispatch\(|open_write_session|write_registration_row|append_registration_row|\.save\(|copyfile|shutil\.copy|os\.remove|rmtree' -Encoding UTF8
```

Observed result: no matches in production files.

Broader scan notes:

- Test fixtures intentionally include fake `D:/PublicProject/LTR.xlsx` paths and tmp-path `document.save(...)` calls.
- `tests/unit/test_specified_ltr_workbook_authority_preview_service.py` includes a fake `open_transaction` safety helper that raises if a write transaction is used.
- Existing `backend/api/dependencies.py` and `frontend/src/api/client.ts` contain pre-existing Matrix/Fee/Folder type/function names; locked-path status below found no TASK_349A changes in those feature folders.

Forbidden-scope status check:

```powershell
git status --short -- backend/infrastructure/storage frontend/src/features/project-workbench frontend/src/features/matrix-editor frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry frontend/src/features/project-basic-information backend/application/project_basic_information_service.py backend/application/project_basic_information_output_identity.py backend/application/public_folder_workflow_service.py backend/api/routes_public_folder_workflow.py .agents docs/project_management dist_release packaging scripts tasks/RELEASE_001_WINDOWS_DESKTOP_PORTABLE_EXE_PACKAGING.md tasks/RELEASE_003_LOCAL_BROWSER_SERVER_PACKAGING.md temp_agents_stash.md
```

Observed result: only external release/packaging residuals and `temp_agents_stash.md` appeared in this targeted check. No TASK_349A changes were observed in storage schema/migrations, Workbench, Matrix Editor, Projects registry/list, Basic Information files, public-folder workflow routes/services, `.agents/**`, or `docs/project_management/**`.

## Behavioral Coverage Observed

Backend:

- Preview found returns workbook path/sheet/row/row values and preview acknowledgement without write.
- Preview not found returns `not_found`, message `LTR workbook 中不存在该编号`, no row values, and no preview ack.
- Stale/changed ack is rejected before completion can continue.
- Completion with full specified DL requires preview ack before local project confirmation.
- TASK_348A local duplicate remains the second-layer response after preview ack.

Frontend:

- Full specified DL Apply opens workbook preview before `completeNewProject`.
- Found preview confirm sends `specified_ltr_workbook_preview_ack` to completion.
- Not found shows `LTR workbook 中不存在该编号` and does not call completion.
- TASK_348A duplicate conflict handoff remains covered after preview confirmation.
- TASK_348B cancel/recovery test remains passing.
- TASK_347A busy-lock path is represented through `completionLoading` and focused New Project tests; no fake progress copy was observed in source/static checks.

## Browser Smoke

Live browser smoke was not executed. Reproducing the specified-LTR workbook preview flow in the running app requires either a mocked preview backend state or a disposable LTR workbook authority fixture. No safe mocked browser harness or disposable fixture was available in this QA thread, and using the live Apply LTR path could touch real authority data. QA relied on focused safe backend/API and frontend tests plus source/static checks.

## Blocking Finding

B1 - Actual product diff contains unrecorded / unreconciled scope outside the TASK_349A Developer evidence changed-file list and outside the clearly approved TASK_349A May Touch boundary.

Evidence:

- Developer evidence lists changed backend files as `specified_ltr_workbook_authority_preview_service.py`, `new_project_completion_service.py`, `routes_new_project_completion.py`, and `dependencies.py`; frontend files as `frontend/src/api/client.ts`, `frontend/src/features/new-project/useNewProjectCompletion.ts`, `SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`, `frontend/src/pages/IntakeInboxPage.tsx`, and `frontend/src/intake-inbox.css`; tests as `test_specified_ltr_workbook_authority_preview_service.py`, `test_new_project_completion_api.py`, and `IntakeInboxPage.test.tsx`.
- Actual `git status` / `git diff --stat` also shows product/test changes in:
  - `backend/application/intake_form_selection_service.py`
  - `backend/modules/intake/application_form_parser.py`
  - `tests/unit/test_application_form_parser.py`
  - `tests/unit/test_intake_form_selection_service.py`
  - `frontend/src/features/precheck/PrecheckFieldGrid.tsx`
  - `frontend/src/features/precheck/precheckReviewSelectors.ts`
  - `frontend/src/intake-case-review.css`
  - `backend/application/ltr_duplicate_resolution_service.py`
  - `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx`
  - `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx`
  - `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
  - `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
  - `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
  - `frontend/src/features/new-project/newProjectRequiredState.ts`
  - `frontend/src/features/new-project/newProjectRequiredState.test.ts`
- Some New Project files are inside the broad `frontend/src/features/new-project/**` May Touch and may be legitimate, but they are still omitted from Developer evidence. The intake parser/selection and precheck files are not clearly authorized by the TASK_349A task/plan/evidence reviewed by QA.

Impact:

- Functional validation passed, but packaging/readiness cannot safely proceed while the product package contains unexplained adjacent intake/precheck/parser and duplicate-summary modifications.
- This is a scope/evidence integrity blocker, not a test failure.

Recommended fix:

- Developer fix pass if these files are accidental: remove/exclude unrelated diffs from TASK_349A package and update Developer evidence.
- Planner/source-of-truth reconciliation first if these files are intentional TASK_349A dependencies: explicitly expand May Touch, explain why each adjacent file is necessary, then re-run Reviewer/QA as appropriate.

## Residuals And Isolation

- External Basic Information, Settings/LTR helper, release/packaging, desktop, `dist_release/`, `packaging/`, release scripts/tasks/tests, and `temp_agents_stash.md` residuals remain visible in the worktree and were not modified by QA.
- QA did not stage, commit, package, push, or touch real workbook/public-drive/folder data.

## QA Decision

Original QA gate: blocked.

Recommended next role: Developer fix pass, or Planner reconciliation first if the extra intake/precheck/parser/duplicate-summary files are intended TASK_349A scope.

Blocking summary: B1 scope/evidence mismatch. Tests/build/static checks passed, but actual product diff includes unrecorded/unreconciled adjacent files outside the clearly documented TASK_349A implementation package.

---

## QA Re-Gate - Package Isolation

Date: 2026-07-04
Role: QA / Smoke Owner
Gate: QA re-gate after Planner package reconciliation
Result: qa_pass

### Sources Re-Read

- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_qa.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`
- Current `git status --short`
- Candidate package status and excluded residual status

### Package Isolation Check

Planner package reconciliation explicitly limits TASK_349A package to:

- `backend/application/specified_ltr_workbook_authority_preview_service.py`
- `backend/application/new_project_completion_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/api/dependencies.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `tests/unit/test_specified_ltr_workbook_authority_preview_service.py`
- `tests/integration/test_new_project_completion_api.py`
- `frontend/src/pages/IntakeInboxPage.test.tsx`
- TASK_349A task/plan/evidence/board docs

QA command:

```powershell
git status --short -- <TASK_349A candidate package files>
```

Observed candidate package status:

- Modified or untracked files appeared only from the reconciled candidate package list above.

QA command:

```powershell
git status --short -- <B1 excluded adjacent residual files>
```

Observed excluded residual status:

- B1 adjacent residual files remain dirty, including intake parser/selection, precheck UI/selectors/CSS, duplicate-summary/local-duplicate/New Project adjacent files.
- These paths are explicitly excluded by Planner package reconciliation and must not be staged or packaged with TASK_349A.

QA assessment:

- Package isolation is verifiable at path level.
- Re-gate pass is conditional on Integrator staging/package selection using only the reconciled TASK_349A package list.
- Integrator must not stage the full worktree and must not stage B1 adjacent residual files.

### Re-Run Validation

Backend focused tests:

```powershell
py -m pytest tests\unit\test_specified_ltr_workbook_authority_preview_service.py tests\integration\test_new_project_completion_api.py -q
```

Observed result: `17 passed in 10.55s`.

Backend compile smoke:

```powershell
py -m py_compile backend\application\specified_ltr_workbook_authority_preview_service.py backend\application\new_project_completion_service.py backend\api\routes_new_project_completion.py backend\api\dependencies.py
```

Observed result: passed with no output.

Frontend focused tests:

```powershell
cd frontend
npm test -- NewProjectCompletionDock IntakeInboxPage --run
```

Observed result: 2 test files passed / 7 tests passed.

TASK_347A/TASK_348A/TASK_348B preservation sweep:

```powershell
cd frontend
npm test -- LocalLtrDuplicateConflictPanel NewProjectCompletionDock useNewProjectCompletion IntakeInboxPage newProjectRequiredState --run
```

Observed result: 5 test files passed / 11 tests passed.

Frontend build:

```powershell
cd frontend
npm run build
```

Observed result: build passed. Existing Vite chunk-size warning only.

### Static Checks

Candidate tracked diff check:

```powershell
git diff --check -- backend/application/new_project_completion_service.py backend/api/routes_new_project_completion.py backend/api/dependencies.py frontend/src/api/client.ts frontend/src/features/new-project/useNewProjectCompletion.ts frontend/src/pages/IntakeInboxPage.tsx frontend/src/intake-inbox.css tests/integration/test_new_project_completion_api.py frontend/src/pages/IntakeInboxPage.test.tsx docs/task_board.md
```

Observed result: passed with LF/CRLF warnings only.

Candidate package trailing whitespace scan:

```powershell
Select-String -Path <TASK_349A candidate package files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

Candidate production no-real-workbook/folder mutation scan:

```powershell
Select-String -Path <TASK_349A production package files> -Pattern 'D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|Workbooks\.Open|SaveAs|win32com|Dispatch\(|open_write_session|write_registration_row|append_registration_row|\.save\(|copyfile|shutil\.copy|os\.remove|rmtree' -Encoding UTF8
```

Observed result: no real workbook/folder mutation matches.

Broader forbidden-scope scan note:

- `backend/api/dependencies.py` and `frontend/src/api/client.ts` contain existing Matrix/Fee/Folder type names and helpers; those are broad shared files and produced false-positive string matches.
- Targeted locked-path status found no TASK_349A changes in storage schema/migrations, Workbench feature folders, Matrix Editor feature folders, Projects registry/list, Basic Information files, public-folder workflow routes/services, `.agents/**`, or `docs/project_management/**`.
- External release/packaging residuals and `temp_agents_stash.md` remain visible and excluded.

### Browser Smoke

Live browser smoke was not executed. The specified-LTR preview flow needs a mocked/disposable workbook context to avoid touching real public-drive authority data. No safe browser harness was available in this QA thread. This remains a non-blocking residual because focused backend/API and frontend tests cover found, not-found, preview acknowledgement, completion handoff, local duplicate second layer, and cancel/recovery behavior without real workbook mutation.

### Re-Gate Decision

QA re-gate: pass.

Recommended next role: Integrator packaging/readiness.

Blocking findings: none remaining after package reconciliation, provided Integrator stages/packages only the reconciled TASK_349A candidate package files.

Integrator instruction:

- Stage/package only the TASK_349A package list from `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`.
- Exclude all B1 adjacent residual files, including intake parser/selection, precheck UI/selectors/CSS, duplicate-summary/local-duplicate/New Project adjacent residuals, Basic Information residuals, Settings/LTR helper residuals, release/packaging/desktop residuals, `.agents/**`, `docs/project_management/**`, and `temp_agents_stash.md`.

---

## QA Re-Gate - After Package Isolation Fix

Date: 2026-07-04
Role: QA / Smoke Owner
Gate: QA re-gate after Developer package-isolation fix and Reviewer re-gate pass
Result: qa_pass

### Sources Re-Read

- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_qa.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_isolation_decision_planner.md`
- Current `git status --short`
- Candidate and excluded residual status checks

### Package-Isolation Dependency Checks

Backend candidate dependency scan:

```powershell
git diff -- backend/api/dependencies.py | Select-String -Pattern 'temporary_context_store=|folder_store=' -Encoding UTF8
```

Observed result: no matches.

Frontend candidate dependency scan:

```powershell
Select-String -Path frontend/src/pages/IntakeInboxPage.tsx -Pattern 'completionError=\{|buildNewProjectRequiredState\(\s*projectFields|saveIntakeSession|flushSync' -Encoding UTF8
```

Observed result: no matches.

QA assessment:

- `backend/api/dependencies.py` no longer pulls excluded duplicate-summary constructor args into the TASK_349A package.
- `frontend/src/pages/IntakeInboxPage.tsx` no longer depends on the excluded New Project residual prop/signature shapes identified in Planner package-isolation decision evidence.
- Candidate package remains separable at path level; excluded residual files are still dirty but not required for TASK_349A package.

Candidate package status command:

```powershell
git status --short -- <TASK_349A candidate package files>
```

Observed result: only reconciled TASK_349A candidate files and TASK_349A docs/evidence/board appeared in the candidate status output.

Excluded residual status command:

```powershell
git status --short -- <B1 excluded adjacent residual files>
```

Observed result: B1 excluded residual files remain dirty, including intake parser/selection, precheck UI/selectors/CSS, duplicate-summary/local-duplicate/New Project adjacent files. These remain excluded and must not be staged for TASK_349A.

### Re-Run Validation

Backend focused tests:

```powershell
py -m pytest tests\unit\test_specified_ltr_workbook_authority_preview_service.py tests\integration\test_new_project_completion_api.py -q
```

Observed result: `17 passed in 9.81s`.

Backend compile smoke:

```powershell
py -m py_compile backend\application\specified_ltr_workbook_authority_preview_service.py backend\application\new_project_completion_service.py backend\api\routes_new_project_completion.py backend\api\dependencies.py
```

Observed result: passed with no output.

Frontend focused tests:

```powershell
cd frontend
npm test -- NewProjectCompletionDock IntakeInboxPage --run
```

Observed result: 2 test files passed / 7 tests passed.

TASK_347A/TASK_348A/TASK_348B preservation sweep:

```powershell
cd frontend
npm test -- LocalLtrDuplicateConflictPanel NewProjectCompletionDock useNewProjectCompletion IntakeInboxPage newProjectRequiredState --run
```

Observed result: 5 test files passed / 11 tests passed.

Frontend build:

```powershell
cd frontend
npm run build
```

Observed result: build passed. Existing Vite chunk-size warning only.

### Static Checks

Candidate tracked diff check:

```powershell
git diff --check -- backend/application/new_project_completion_service.py backend/api/routes_new_project_completion.py backend/api/dependencies.py frontend/src/api/client.ts frontend/src/features/new-project/useNewProjectCompletion.ts frontend/src/pages/IntakeInboxPage.tsx frontend/src/intake-inbox.css tests/integration/test_new_project_completion_api.py frontend/src/pages/IntakeInboxPage.test.tsx docs/task_board.md
```

Observed result: passed with LF/CRLF warnings only.

Candidate package trailing whitespace scan:

```powershell
Select-String -Path <TASK_349A candidate package files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

Candidate production no-real-workbook/folder mutation scan:

```powershell
Select-String -Path <TASK_349A production package files> -Pattern 'D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|Workbooks\.Open|SaveAs|win32com|Dispatch\(|open_write_session|write_registration_row|append_registration_row|\.save\(|copyfile|shutil\.copy|os\.remove|rmtree' -Encoding UTF8
```

Observed result: no matches.

Forbidden-scope status command:

```powershell
git status --short -- backend/infrastructure/storage frontend/src/features/project-workbench frontend/src/features/matrix-editor frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry frontend/src/features/project-basic-information backend/application/project_basic_information_service.py backend/application/project_basic_information_output_identity.py backend/application/public_folder_workflow_service.py backend/api/routes_public_folder_workflow.py .agents docs/project_management dist_release packaging scripts tasks/RELEASE_001_WINDOWS_DESKTOP_PORTABLE_EXE_PACKAGING.md tasks/RELEASE_003_LOCAL_BROWSER_SERVER_PACKAGING.md temp_agents_stash.md
```

Observed result: only external release/packaging residuals and `temp_agents_stash.md` appeared. No TASK_349A changes were observed in storage schema/migrations, Workbench, Matrix Editor, Projects registry/list, Basic Information files, public-folder workflow routes/services, `.agents/**`, or `docs/project_management/**`.

### Browser Smoke

Live browser smoke was not executed. No safe mocked/disposable workbook context was available, and using the live Apply LTR path could touch real authority data. This is non-blocking because focused safe backend/API and frontend tests cover found, not-found, preview acknowledgement, completion handoff, local duplicate second layer, and cancel/recovery behavior.

### Re-Gate Decision

QA re-gate after package isolation fix: pass.

Recommended next role: Integrator packaging/readiness.

Blocking findings: none.

Integrator instruction:

- Stage/package only the reconciled TASK_349A candidate files from `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`.
- Exclude all B1 adjacent residual files and external residuals.
- Do not stage the full worktree.
