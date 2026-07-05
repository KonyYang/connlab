# TASK_350B Developer Evidence - Matrix Import Stale Preview Reparse Guard

Status: implementation complete - pending Reviewer implementation gate

Task: `TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD`
Lane: `matrix-import-stale-preview-reparse-guard`
Role: Developer
Date: 2026-07-05

---

## 0. Developer Implementation Pass

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Allowed reason:

- Orchestrator delegated TASK_350B Developer implementation after source-of-truth reconciliation recorded `implementation_authorized / pending Developer implementation`.
- Scope remained frontend-only Matrix import stale preview behavior and focused tests.

Changed files:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`

Implementation summary:

- Added an `ImportLocatorSnapshot` and `lastParsedLocator` state for the import modal.
- Recorded the parsed locator after initial file preview success and manual Reparse success.
- Derived stale preview status from Page / Table on page / Keyword edits versus the last parsed locator.
- Kept non-stale Replace as the existing direct commit path.
- Changed stale Replace to run an auto-Reparse with current locator fields before commit.
- Auto-Reparse success with usable groups updates `importPreview` and `lastParsedLocator`, then commits the refreshed preview.
- Auto-Reparse validation failure, preview failure, page/table mismatch, blockers, or no groups leaves the dialog open and prevents commit.
- During manual Reparse, stale Replace auto-Reparse, and commit, locator inputs and import actions are disabled to prevent double submit.
- Preserved `.doc,.docx` selector compatibility and Append-disabled behavior.

Validation results:

- Red check before implementation:
  - `npm test -- MatrixEditorWorkspace --run`
  - Result: failed as expected; stale Replace committed without a second preview/reparse.
- Focused frontend tests:
  - `npm test -- MatrixEditorWorkspace --run`
  - Result: passed, 1 file / 35 tests.
- Frontend build:
  - `npm run build`
  - Result: passed; Vite reported the existing chunk-size warning.
- Diff check:
  - `git diff --check -- frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
  - Result: passed; Git reported existing LF/CRLF warnings for the two touched frontend files.
- Trailing whitespace scan:
  - `Select-String -Path 'frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx','frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx','docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md' -Pattern '[ \t]+$' -Encoding UTF8`
  - Result: no matches.
- Targeted scope/status:
  - `git status --short -- backend frontend/src/api/client.ts frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx frontend/src/features/project-workbench frontend/src/features/projects-registry frontend/src/pages .agents docs/project_management docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
  - Result: TASK_350B changed only `MatrixEditorWorkspace.tsx`, `MatrixEditorWorkspace.test.tsx`, and this evidence file. Backend Settings/LTR and desktop files are pre-existing external residuals and remain excluded.

Browser smoke:

- Not run in Developer thread. No safe browser/dev-server smoke was started in this pass; QA should smoke the Matrix import modal if needed.

Scope and residuals:

- No backend, API client, parser/preview service, TASK_350A conversion backend, Folder/Intake/Projects, `.agents/**`, or `docs/project_management/**` changes were made for TASK_350B.
- Existing external residuals remain excluded: modified `docs/task_board.md`, New Project residuals, Settings/LTR backend residuals, release/desktop/packaging residuals, TASK_350B Planner docs/evidence, and `temp_agents_stash.md`.

Stop point:

- Developer implementation complete.
- Recommended next role: Reviewer implementation gate.

---

## 1. Gate And Scope

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Allowed reason:

- Orchestrator delegated TASK_350B Developer planning-first after Reviewer plan re-gate pass and user approval.
- This pass is planning/evidence only. No product code, tests, backend, API client, parser, or CSS implementation was changed.

Source-of-truth note:

- Local `docs/task_board.md`, TASK_350B task file, plan header before this pass, and Planner evidence still recorded TASK_350B as planned / ready for Reviewer plan re-gate only.
- Developer planning-first is complete, but implementation must wait for Reviewer implementation-readiness, explicit user implementation approval, and source-of-truth reconciliation.

---

## 2. Sources Read

Governance and product/UI context:

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` context from `PRODUCT.md` / `DESIGN.md`
- `$impeccable` product register reference
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

TASK_350B:

- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_planner.md`

Related context:

- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`
- Current `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Current `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Current `git status --short`

---

## 3. Current Code Findings

- TASK_350A is complete/accepted and `MatrixEditorWorkspace.tsx` currently has the accepted `accept=".doc,.docx"` file selector behavior.
- Current `MatrixEditorWorkspace.tsx` is clean for TASK_350B planning: no product diff exists in that file at this checkpoint.
- Import modal state already includes `importPreview`, `importPreviewPdfToken`, `importingPreview`, `importError`, `importLookupMessage`, `importLookupTone`, `showImportDialog`, `committingImport`, `importFile`, `locatorPage`, `locatorTableOnPage`, and `locatorKeyword`.
- Initial file preview success sets `importPreview`, `importPreviewPdfToken`, locator fields, and opens the dialog.
- `reparseImportPreview` already validates Page / Table on page as positive integers, calls `previewProjectTestPlanMatrixFromUpload` with current locator values, handles mismatch, updates preview, and displays in-dialog lookup messages.
- `applyImportedMatrixDirectly` currently commits the current `importPreview` directly and does not guard against stale locator edits.
- Replace currently remains enabled when preview groups exist, even if locator fields changed after the preview was generated.
- Locator fields are currently disabled only by lifecycle readonly, not by Reparse/Replace busy state.
- Focused tests already mock `previewProjectTestPlanMatrixFromUpload` and `commitMatrixImport`, and cover the import selector accept value, Append disabled behavior, and direct Replace commit behavior.

---

## 4. Implementation Strategy For Later Pass

Future implementation should be frontend-only and local to MatrixEditorWorkspace plus focused tests.

State model:

- Add `ImportLocatorSnapshot` with `page`, `tableOnPage`, and `keyword`.
- Add `lastParsedLocator: ImportLocatorSnapshot | null`.
- Build current snapshots from trimmed UI fields.
- Record snapshots after initial preview success and manual Reparse success.
- Derive `isPreviewStale` from current locator values versus the last successful parsed locator.

Shared preview helper:

- Extract a local helper that validates locator inputs and calls `previewProjectTestPlanMatrixFromUpload` with current Page / Table on page / Keyword.
- Use the helper from both manual Reparse and stale Replace auto-Reparse.
- Preserve current positive integer validation and page/table mismatch messaging.

Replace behavior:

- Non-stale Replace commits the current `importPreview` directly and must not call preview/reparse again.
- Stale Replace remains clickable when there is a current preview with usable groups and no readonly/busy blocker.
- Stale Replace first runs Reparse with the current locator fields.
- If auto-Reparse succeeds with usable groups, update `importPreview`, update `lastParsedLocator`, then call `commitMatrixImport` with the refreshed preview.
- If auto-Reparse fails, locator validation fails, page/table mismatch occurs, or no usable groups are found, keep the dialog open, show the in-dialog result/error, and do not call `commitMatrixImport`.

Busy behavior:

- Derive `importActionBusy = importingPreview || committingImport`.
- Disable locator inputs while readonly or busy.
- Disable Reparse while readonly, busy, or no file exists.
- Disable Replace while readonly, busy, no preview exists, or preview has no groups.
- Do not disable Replace merely because the preview is stale.

UX/copy:

- Keep copy concise and operational.
- Reuse existing in-dialog error/lookup text where possible.
- Do not add long explanatory copy or new visual structure.
- Keep `$impeccable` product constraints: restrained, dense, familiar, no gradient text, no glassmorphism, no thick side stripes, no nested cards, no raw backend tokens.

---

## 5. Exact Future Implementation File List

May Touch after later gates:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`

Docs/board through normal lane flow only:

- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_board.md`

Must Not Touch / locked:

- `backend/**`
- `frontend/src/api/client.ts`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- TASK_350A `.doc` conversion backend flow
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, lifecycle semantics
- Folder Actions / public folder workflow
- Intake / LTR workflow
- Projects registry/list
- Release/settings cleanup and unrelated residuals
- `.agents/**`
- `docs/project_management/**`

---

## 6. Focused Test Plan

Add/update `MatrixEditorWorkspace.test.tsx` coverage:

- Stale Page edit: clicking Replace auto-Reparses with the current Page, updates preview/snapshot, and commits refreshed preview.
- Stale Table on page edit: same auto-Reparse then commit path.
- Stale Keyword edit: same auto-Reparse then commit path.
- Auto-Reparse failure: no commit, visible in-dialog error/lookup state remains.
- Invalid Page or Table on page: no reparse request beyond validation, no commit, visible validation copy.
- No usable Matrix groups after auto-Reparse: no commit, dialog remains open with existing no-match state.
- Non-stale Replace: commits directly and preview upload is called only once.
- Manual Reparse success: updates preview/snapshot, then Replace commits directly without a second reparse.
- Busy states: locator inputs, Reparse, and Replace disabled during manual Reparse or stale Replace auto-Reparse/commit; Append remains disabled.
- Existing `.doc,.docx` accept, Append disabled, and Replace direct commit tests remain green.

---

## 7. Package Isolation Plan

- Implementation must start from the clean current `MatrixEditorWorkspace.tsx` baseline.
- Candidate package should include only stale-preview snapshot/auto-Reparse hunks and focused tests.
- Do not reintroduce TASK_350A package-isolation residuals or mix `.doc` backend conversion changes into TASK_350B.
- If `MatrixEditorWorkspace.tsx` is dirty with external hunks before implementation, stop and request Planner/User package reconciliation.
- Existing release/settings/desktop/New Project residuals shown by `git status --short` remain excluded from this lane.

---

## 8. Planning Validation Results

- Required TASK_350B task, plan, and Planner evidence files exist.
- Developer evidence created at `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`.
- Product code was inspected read-only. No frontend/backend/tests/API-client product file was modified by this planning-first pass.
- External residuals observed and excluded: modified `docs/task_board.md`; untracked release/desktop/settings files; untracked TASK_350B Planner task/plan/evidence; New Project required-state test residual; packaging/dist release scripts; `temp_agents_stash.md`.

Validation commands run for this pass:

- `git diff --check -- docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
  - Result: passed with no output.
- trailing whitespace scan on the same two docs
  - Result: no matches.
- targeted forbidden-scope status proving no product code changed by this planning-first pass
  - Result: no `MatrixEditorWorkspace.tsx`, `MatrixEditorWorkspace.test.tsx`, backend product, API-client, parser, `.agents/**`, or `docs/project_management/**` changes from this pass. Existing `docs/task_board.md`, release/desktop/settings, New Project required-state test, and TASK_350B Planner docs remain visible as external residuals or Planner-created inputs.

---

## 9. Stop Point

Developer planning-first is complete.

Recommended next role:

- Reviewer implementation-readiness gate after source-of-truth reconciliation if required by board/evidence.

Blocking summary:

- No implementation-design blocker.
- Source-of-truth reconciliation remains required before product code because local board/task evidence still records planned / Reviewer plan re-gate state.

---

## 10. Integrator Packaging Closeout

Date: 2026-07-05

Integrator gate: accepted.

Accepted package:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_planner.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_qa.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_reconciliation_planner.md`
- `docs/task_board.md`

Packaging notes:

- Package stayed frontend-only for Matrix import stale-preview snapshot / auto-Reparse behavior and focused tests.
- No backend, API client, parser/preview route/service, TASK_350A conversion backend, Workbench/Projects/New Project, Settings/LTR, desktop/release/packaging, temp-stash, `.agents/**`, or `docs/project_management/**` files were staged or committed for TASK_350B.

Integrator validation:

- `npm test -- MatrixEditorWorkspace --run`: passed, `35 passed`.
- `npm run build`: passed with the existing Vite chunk-size warning only.
- `git diff --cached --check`: passed with LF/CRLF warnings only.
- Staged whitelist/forbidden-path, trailing whitespace, backend/API-client/parser/preview-route/service/TASK_350A conversion, future-scope, and release/settings/New Project residual scans passed.

Residual:

- Browser smoke remains non-blocking because QA lacked direct browser control and a prepared disposable Matrix import fixture. Focused component tests and source/static checks cover stale detection, stale Replace auto-Reparse success/failure, invalid locator, manual Reparse, non-stale direct commit, and busy disabled behavior.
