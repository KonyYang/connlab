# TASK_350C QA Evidence - Matrix Import Remove Native Confirm Guard

Date: 2026-07-05

Role: QA / Smoke Owner

Task: `TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD`

Lane: `matrix-import-remove-native-confirm-guard`

Result: `qa_pass`

---

## 1. Gate And Role Boundary

- Current phase from `docs/task_board.md`: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Reviewer callback states implementation gate passed and QA gate is required.
- QA performed validation and evidence only.
- QA did not modify product source, tests, backend/API/client/parser code, `docs/task_board.md`, release/settings/desktop residuals, or real user data.
- QA did not stage, commit, push, package, or run destructive cleanup.

## 2. Sources Read

- `tasks/TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD.md`
- `docs/task_350c_matrix_import_remove_native_confirm_guard_plan.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_planner.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_reconciliation_planner.md`
- Reviewer implementation gate callback supplied in Orchestrator delegation
- Actual diff/status for TASK_350C candidate files and external residuals

## 3. Candidate Package / Scope Check

TASK_350C candidate product files observed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

Developer evidence observed:

- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`

Observed product diff:

- `onChangeSourceMatrix()` preserves the lifecycle readonly guard.
- The old `warning` variable and `window.confirm(warning)` branch were removed from `onChangeSourceMatrix()`.
- Editable `Import Matrix` now calls `openChooseDocx()` directly.
- The separate `onCancelEditing()` discard confirmation remains unchanged.
- Focused regression test asserts `window.confirm` is not called, the hidden file input click is invoked, and file input `accept` remains `.doc,.docx`.

External residuals still visible and excluded:

- New Project / local LTR residuals.
- `frontend/src/pages/IntakeInboxPage.test.tsx` external residual.
- Settings/LTR backend residuals.
- desktop/release/packaging residuals, `dist_release/`, and `temp_agents_stash.md`.

## 4. Focused Frontend Tests

Command:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace --run
```

Observed result:

- Passed.
- `1` test file passed.
- `36` tests passed.

Coverage confirmed:

- Import Matrix click does not call `window.confirm`.
- Existing hidden file input path is invoked.
- File input `accept` remains `.doc,.docx`.
- TASK_350B stale Replace/Reparse tests remain in the same passing focused suite.
- Existing MatrixEditorWorkspace regressions remain green.

## 5. Build

Command:

```powershell
cd frontend
npm run build
```

Observed result:

- Passed.
- Existing Vite chunk-size warning only.

## 6. Static Checks

Candidate diff check:

```powershell
git diff --check -- frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md docs/task_350c_matrix_import_remove_native_confirm_guard_plan.md tasks/TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD.md docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_planner.md docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_reconciliation_planner.md
```

Observed result:

- Passed with LF/CRLF warnings only.

Trailing whitespace scan:

```powershell
Select-String -Path <TASK_350C candidate files/docs> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result:

- No matches.

Native confirm scope scan:

```powershell
Select-String -Path frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx -Pattern 'Import Matrix will replace|Discard current Matrix edits|window\.confirm|openChooseDocx|onChangeSourceMatrix' -Encoding UTF8
```

Observed result:

- Old `Import Matrix will replace...` strings are absent from the production file.
- `onChangeSourceMatrix()` calls `openChooseDocx()` directly after readonly guard.
- The separate `Discard current Matrix edits and return to Workbench?` `window.confirm` remains present.

Forbidden-scope/status scan:

```powershell
git status --short -- backend frontend/src/api/client.ts backend/modules/test_plan/product_spec_matrix_parser.py backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx frontend/src/features/new-project frontend/src/pages/IntakeInboxPage.test.tsx frontend/src/features/project-workbench frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx .agents docs/project_management dist_release packaging temp_agents_stash.md
```

Observed result:

- TASK_350C candidate files appeared under MatrixEditorWorkspace only.
- No TASK_350C backend, API client, parser, backend preview route/service, TASK_350A conversion, TASK_350B stale Reparse semantic files beyond preserved MatrixEditorWorkspace tests, Project Workbench, Projects registry/list, `.agents/**`, or `docs/project_management/**` implementation changes appeared.
- New Project, IntakeInboxPage test, Settings/LTR, desktop/release/packaging, and temp-stash residuals remain visible and excluded.

## 7. Browser Smoke

Browser smoke was not executed.

Environment/tooling observations:

- `http://localhost:5173/projects/1ee3f8389c2243b0b324247ae5555bd3/matrix-editor` responded with status `200`.
- `frontend/package.json` has no Playwright or Puppeteer dependency.
- Available tool search did not expose a direct browser controller for reliable page click/native dialog inspection in this QA thread.

Disposition:

- Non-blocking residual because focused regression directly spies on `window.confirm`, clicks `Import Matrix`, verifies no confirm call, verifies hidden file input click, and verifies `.doc,.docx` accept.
- Future manual smoke can use the reported route and click `Import Matrix` to visually confirm the browser-native dialog no longer appears.

## 8. QA Decision

QA gate: pass.

Blocking findings: none.

Residual risks:

- Browser smoke remains unexecuted due missing browser automation in this QA thread, despite localhost route availability.
- External New Project, Intake, Settings/LTR, desktop/release/packaging, and temp-stash residuals remain dirty and must not be packaged with TASK_350C.

Recommended next role:

- Integrator packaging/readiness.

Integrator instruction:

- Stage/package only TASK_350C MatrixEditorWorkspace files/hunks and intended TASK_350C evidence/docs.
- Exclude backend/API client/parser/preview route/service/TASK_350A conversion files, TASK_350B semantic changes beyond retained tests, and all external Settings/LTR, New Project, Intake, desktop/release/packaging, and temp-stash residuals.
