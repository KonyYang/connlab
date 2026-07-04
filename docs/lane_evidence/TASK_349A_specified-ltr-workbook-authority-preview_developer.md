# TASK_349A Developer Evidence - Specified LTR Workbook Authority Preview

Status: package isolation complete - pending Reviewer/QA re-gate

Task: `TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW`
Lane: `specified-ltr-workbook-authority-preview`
Role: Developer
Date: 2026-07-04

---

## 1. Gate And Scope

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Allowed reason:

- Orchestrator delegated TASK_349A Developer implementation.
- Repository source-of-truth records TASK_349A as `implementation_authorized / pending Developer implementation`.
- Reconciliation evidence exists at `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_reconciliation_planner.md`.
- Scope is limited to specified-LTR workbook authority preview before New Project Apply LTR completion.

Locked scope preserved:

- No database schema or migration.
- No Workbench LTR update preview semantic changes.
- No real workbook/public-drive mutation in tests or implementation.
- No Matrix, Fee, Folder Actions, Projects registry, Settings/LTR, Basic Information, release/packaging, `.agents`, or `docs/project_management` cleanup.

---

## 2. Changed Files

Backend:

- `backend/application/specified_ltr_workbook_authority_preview_service.py`
- `backend/application/new_project_completion_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/api/dependencies.py`

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`

Tests:

- `tests/unit/test_specified_ltr_workbook_authority_preview_service.py`
- `tests/integration/test_new_project_completion_api.py`
- `frontend/src/pages/IntakeInboxPage.test.tsx`

Evidence:

- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`

---

## 3. Implementation Summary

Backend:

- Added a read-only `SpecifiedLtrWorkbookAuthorityPreviewService`.
- Added `POST /api/intake-cases/{case_id}/specified-ltr-workbook-authority-preview`.
- Preview parses full `DL-YYYY-MM-NNN...` numbers, looks up the parsed-year workbook sheet, and returns `found`, `not_found`, or `blocked`.
- Found preview returns the requested workbook row fields:
  - `Project Type`
  - `Description P/N`
  - `Test Item`
  - `Test Type`
  - `Requested by`
  - `Location`
  - `Project Leader`
  - `Test Result`
  - `Failed item`
  - `Sample deposition`
  - `Sub-contract`
  - `Test Fee`
  - `Remarks (PO)`
- Not found returns the required message `LTR workbook 中不存在该编号` and no continuation ack.
- Added stateless preview acknowledgement verification before `NewProjectCompletionService` confirms or creates a local project.
- Preview acknowledgement is rechecked read-only against workbook row identity/fingerprint before local project/LTR writes.
- Suffix-only specified LTR values keep the existing completion path.
- TASK_348A local duplicate remains the second-layer conflict after workbook acknowledgement.

Frontend:

- Added typed API client contract for specified-LTR workbook authority preview.
- Full specified DL Apply now opens workbook preview first.
- Found rows render in a compact operational confirmation panel; blank/partial/full rows all require confirmation.
- Not found blocks completion and only allows closing back to Intake.
- Confirming the workbook row calls the existing completion flow with preview acknowledgement.
- Preview cancel/close preserves Intake source, form, setup, and readiness state.
- Preview loading/confirmation participates in the existing New Project page-level busy lock.
- If completion returns `LOCAL_LTR_DUPLICATE`, the workbook preview closes and the existing duplicate conflict panel becomes the second layer.

---

## 4. Validation Results

Backend focused tests:

- `py -m pytest tests\unit\test_specified_ltr_workbook_authority_preview_service.py tests\integration\test_new_project_completion_api.py -q`
- Result: `17 passed`

Frontend focused tests:

- `npm test -- NewProjectCompletionDock IntakeInboxPage --run`
- Result: `2 passed` test files, `7 passed` tests

Build and compile:

- `py -m py_compile backend\application\specified_ltr_workbook_authority_preview_service.py backend\application\new_project_completion_service.py backend\api\routes_new_project_completion.py backend\api\dependencies.py`
- Result: passed
- `npm run build`
- Result: passed, with existing Vite chunk-size warning only

Diff and whitespace:

- `git diff --check` on TASK_349A package files passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_349A package files returned no matches.

No-real-workbook/static scan:

- Searched TASK_349A package files for real path/write indicators including `D:/`, `D:\`, `PublicProject`, `Test Project`, `open_transaction(`, `open_write_session`, `save(`, `write_registration_row`, and `append_registration_row`.
- Matches are limited to fake test fixture paths and a fake safety helper in unit tests.
- No production workbook write path was added by TASK_349A.

UI anti-pattern scan:

- Searched TASK_349A preview panel/CSS for side-stripe borders over 1px, gradient text, backdrop filter, and glass copy.
- TASK_349A preview styles produced no matching anti-patterns.
- One pre-existing `linear-gradient` background remains in `frontend/src/intake-inbox.css`; it is outside the new preview panel styling and was not changed for TASK_349A.

Forbidden-scope status:

- Targeted status for locked areas showed only pre-existing release/temp residuals:
  - `dist_release/`
  - `packaging/`
  - release scripts under `scripts/`
  - `temp_agents_stash.md`
- No backend storage/schema, Workbench, Matrix, Projects registry, `.agents`, or `docs/project_management` changes were made for TASK_349A.

---

## 5. Residuals And Notes

- Browser smoke was not run in this Developer pass; QA can smoke the New Project specified-LTR preview flow against localhost.
- Existing release/packaging/temp residuals remain excluded and were not cleaned or packaged.
- Existing LF/CRLF warnings appeared during diff checks; no diff-check errors were reported.

---

## 6. Stop Point

Developer implementation and package isolation are complete.

Recommended next role:

- Reviewer/QA re-gate for package isolation and regression.

---

## 7. QA B1 Fix/Triage Pass

Date: 2026-07-04

Input:

- QA reported B1: actual product diff includes adjacent intake/precheck/parser/duplicate-summary files outside the clearly documented TASK_349A package.
- Functional validation passed, but package readiness is blocked by scope/evidence mismatch.

Triage result:

- The adjacent files are not required for TASK_349A specified-LTR workbook authority preview.
- TASK_349A implementation depends on the new read-only workbook preview service/API, completion preview acknowledgement enforcement, API client preview DTO/helper, New Project preview orchestration, Intake page composition, preview panel styling, and focused tests.
- The following B1 files do not participate in TASK_349A workbook-first preview, read-only workbook access, preview acknowledgement verification, not-found blocking, or the preview-confirm-to-completion handoff:
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

Why product edits were not reverted in this fix pass:

- These adjacent diffs appear to be pre-existing or separately user-requested New Project/Intake/Precheck improvements from earlier lane work.
- The user previously instructed that the functionality implemented in thread `019f2347-8027-7980-9f27-46c19284f7d9` is wanted and should be received.
- Reverting those hunks here would risk deleting user-approved adjacent behavior and would violate the instruction not to roll back unknown/user work.
- They are not TASK_349A dependencies, so Developer also did not request expanding TASK_349A May Touch to include them as implementation scope.

Decision:

- No product code was changed in this B1 fix/triage pass.
- TASK_349A should remain blocked for package readiness until Planner/Integrator isolates or reconciles the adjacent residual diffs outside the TASK_349A package.
- Recommended route is Planner package/scope reconciliation, not Reviewer/QA re-gate yet.

Validation for this B1 triage pass:

- Read TASK_349A task/plan/developer evidence and QA evidence.
- Inspected actual `git status --short`.
- Inspected targeted `git diff --stat` for QA B1 files.
- Inspected targeted diffs for intake parser/selection, precheck UI/selectors/CSS, duplicate resolution, and New Project adjacent files.
- `git diff --check` on the B1 triage/evidence files passed with LF/CRLF warnings only.
- Trailing whitespace scan on the B1 triage/evidence files returned no matches.
- Targeted status still shows the adjacent B1 files as dirty; this confirms the package blocker remains unresolved until Planner/Integrator isolates or reconciles those residuals.
- No backend/frontend/tests product edits were made during this fix/triage pass.

---

## 8. Package-Isolation Fix Pass

Date: 2026-07-04

Input:

- Planner package-isolation decision selected Option A.
- Developer/package-isolation owner must split mixed hunks so TASK_349A is self-contained without adjacent residuals.

Isolation changes:

- `backend/api/dependencies.py`
  - Kept TASK_349A `SpecifiedLtrWorkbookAuthorityPreviewService` dependency wiring.
  - Removed `_ltr_duplicate_resolution_service(...)` constructor arguments for excluded duplicate-summary residual dependencies:
    - `temporary_context_store`
    - `folder_store`
  - Current TASK_349A diff for `dependencies.py` now contains only preview-service import, preview-service provider, and completion-service injection.
- `frontend/src/pages/IntakeInboxPage.tsx`
  - Kept TASK_349A specified-LTR workbook preview wiring and interaction lock.
  - Removed hard dependency on excluded New Project residual prop shape by no longer passing `completionError` directly to `NewProjectCompletionDock`.
  - Added a compatibility spread for `NewProjectApplicationEditor` so the TASK_349A package can work with the pre-residual editor contract without depending on the residual moved-error UI.
  - Added a compatibility wrapper around `buildNewProjectRequiredState` so TASK_349A no longer requires the excluded five-argument required-state helper signature.
  - Removed `flushSync` and `saveIntakeSession` imports/usages from the TASK_349A candidate file.
- `tests/integration/test_new_project_completion_api.py`
  - Removed TASK_349A test assertions that depended on excluded duplicate-summary residual fields from `LocalLtrDuplicateResolutionService`.
  - Kept the TASK_349A assertion that workbook preview acknowledgement still reaches the `LOCAL_LTR_DUPLICATE` second-layer conflict.

Candidate package after isolation:

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
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`

Excluded residuals remain outside TASK_349A:

- intake parser/selection residuals
- precheck UI/selectors/CSS residuals
- duplicate-summary residuals
- New Project residual files not listed in the candidate package
- Settings/LTR, Basic Information, release/packaging, `.agents`, and `docs/project_management` residuals

Validation after isolation:

- `npm test -- NewProjectCompletionDock IntakeInboxPage --run`: 2 test files passed, 7 tests passed.
- `py -m pytest tests\unit\test_specified_ltr_workbook_authority_preview_service.py tests\integration\test_new_project_completion_api.py -q`: 17 passed.
- `npm run build`: passed with existing Vite chunk-size warning only.
- `py -m py_compile backend\application\specified_ltr_workbook_authority_preview_service.py backend\application\new_project_completion_service.py backend\api\routes_new_project_completion.py backend\api\dependencies.py`: passed.
- `git diff --check` on TASK_349A package files passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_349A package files returned no matches.
- Candidate dependency scan:
  - `git diff -- backend/api/dependencies.py | rg "temporary_context_store=|folder_store="`: no matches.
  - `rg "completionError=\{|buildNewProjectRequiredState\(\s*projectFields|saveIntakeSession|flushSync" frontend/src/pages/IntakeInboxPage.tsx`: no matches.
- No-real-workbook/static scan found only fake test fixture paths and the fake unit-test safety helper; no production workbook write path was added.

Residual note:

- `frontend/src/pages/IntakeInboxPage.tsx` still contains local duplicate lock/recovery behavior from prior accepted adjacent work because removing it would risk deleting user-requested behavior. The package-isolation fix specifically removed dependencies on excluded residual files and constructor/API shapes, which was the Planner-identified mixed-hunk blocker.

---

## 9. Integrator Packaging Closeout

Date: 2026-07-04

Integrator result:

- `Integrator gate: accepted`.
- Package isolation was rechecked against the Planner decision, Developer package-isolation fix, Reviewer re-gate callback, and QA re-gate evidence.
- The TASK_349A commit diff for `backend/api/dependencies.py` does not add `temporary_context_store=` or `folder_store=` dependency hunks.
- `frontend/src/pages/IntakeInboxPage.tsx` no longer depends on excluded direct `completionError={` dock wiring, direct five-argument `buildNewProjectRequiredState(projectFields, ...)`, `saveIntakeSession`, or `flushSync` patterns.
- Staged package was limited to the reconciled TASK_349A candidate product/test/docs/evidence files plus TASK_349A board closeout.
- Excluded B1 adjacent residuals, Settings/LTR residuals, Basic Information residuals, release/packaging residuals, `.agents/**`, `docs/project_management/**`, real workbook/public-drive data, Workbench, Matrix, Projects, and `temp_agents_stash.md` were not staged.

Validation summary:

- Backend focused tests: 17 passed.
- Frontend focused tests: 2 files / 7 tests passed.
- Preservation sweep: 5 files / 11 tests passed.
- Frontend build passed with the existing Vite chunk-size warning only.
- Backend `py_compile` passed for touched TASK_349A backend modules.
- Staged `git diff --cached --check`, staged whitelist/forbidden-path checks, trailing whitespace scan, and no-real-workbook/folder mutation scan passed.

Remote push was intentionally not performed.
