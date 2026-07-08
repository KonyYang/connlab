# TASK_358A Matrix Editor Quantity Defaults Simplification - QA Evidence

Date: 2026-07-09

Role: QA / Smoke Owner

Task: `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION`

Lane: `matrix-editor-quantity-defaults-simplification`

Result: `qa_pass`

Recommended next role: Integrator packaging/readiness

## Scope Read

QA re-read TASK_358A task, plan, Developer evidence, Reviewer evidence, reconciliation evidence, current board context, and actual diff/status. QA also checked upstream TASK_357B-E accepted context from the board/evidence because TASK_358A corrects quantity default placement after the accepted quantity authority series.

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Why this QA gate is allowed: Reviewer implementation gate passed and recommended QA because TASK_358A changes Basic Information and Matrix Editor user-facing quantity workflow behavior.

## Candidate Package Status

Observed TASK_358A candidate files:

- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md`
- `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reviewer.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reconciliation_planner.md`
- this QA evidence

External residuals remain visible and are excluded from TASK_358A packaging:

- `docs/task_board.md`
- `backend/api/dependencies.py`
- Fee rule seed/test residuals:
  - `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
  - `tests/unit/test_confirmed_matrix_fee_draft_service.py`
  - `tests/unit/test_fee_rule_matcher.py`
- Settings/LTR/template helper files and tests.
- Release/desktop/packaging files and scripts.
- Frontend New Project test residual.
- TASK_357A docs/evidence.
- `temp_agents_stash.md`.

QA verified the Fee residual diff contains fee-rule alias/test additions and is not part of the TASK_358A candidate package. Integrator must not stage those files with TASK_358A.

## Validation Commands

### Focused frontend tests

Command:

```powershell
cd frontend
npm test -- ProjectBasicInformationWorkspace MatrixEditorWorkspace --run
```

Observed result: `2 files / 60 tests passed`.

Coverage confirmed:

- Basic Information no longer renders `Quantity defaults`.
- Basic Information no longer renders `Test points / sample`, `Readings / point`, or `Contact points / sample`.
- Hidden/historical Basic Information quantity values no longer block Confirm through frontend quantity-default validation.
- Matrix Editor renders `Defaults for this group` inside Step quantity setup.
- `Apply to blank Step quantities` fills blank fields in the selected group.
- Non-blank Step quantity values are preserved.
- Applying defaults updates derived `total_readings`.
- Save still calls the existing Matrix Step quantity save flow.
- Readonly/lifecycle handling remains covered by existing focused Matrix Editor and Basic Information tests.

### Frontend build

Command:

```powershell
cd frontend
npm run build
```

Observed result: passed. Existing Vite chunk-size warning only.

### Diff and whitespace checks

Command:

```powershell
git diff --check -- <TASK_358A candidate files>
```

Observed result: passed with LF/CRLF normalization warnings only.

Command:

```powershell
Select-String -Path <TASK_358A candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

### Forbidden-scope scan

Command:

```powershell
git diff --name-only -- backend frontend/src/api/client.ts backend/modules/fee_evaluation backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_step_quantities.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_matcher.py tests/integration/test_confirmed_matrix_test_record_preview_api.py tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py .agents docs/project_management dist_release packaging scripts temp_agents_stash.md
```

Observed result:

- TASK_358A candidate package has no backend, schema, API client, Fee, Test Record, Report, `.agents/**`, `docs/project_management/**`, release/package, or real-path file.
- External Fee rule seed/test residuals appear in the broad locked-path scan and are excluded from TASK_358A packaging.

## Behavior Assessment

QA did not find a blocking TASK_358A behavior issue in tests/source/static inspection.

Basic Information:

- `Quantity defaults` is removed from the Basic Information UI field configuration.
- Focused tests assert `Quantity defaults`, `Test points / sample`, `Readings / point`, and `Contact points / sample` are not rendered.
- Basic Information frontend quantity-default validation/confirm blocking is no longer reachable.
- No backend Basic Information file, schema, or data migration was touched by the TASK_358A candidate package.
- Existing historical quantity keys remain compatibility data rather than an operator-facing authoring surface.

Matrix Editor:

- `Defaults for this group` is implemented as an inline strip in `MatrixStepQuantityPanel`, not a modal.
- The strip uses standard inputs and one action, `Apply to blank Step quantities`.
- Source inspection and tests confirm the apply action fills only blank fields in the selected group.
- Non-blank values, saved/manual override values, and existing review values are preserved.
- Changed rows are marked as `matrix_step_override`.
- `total_readings` remains derived/read-only.
- Persistence still goes through existing `Save quantities` / `saveMatrixStepQuantities`; applying defaults alone is local/transient.
- Readonly state disables the panel controls through the existing disabled path.

Downstream consumers and locked scope:

- No backend files are in the TASK_358A candidate package.
- No schema/data deletion or destructive migration was performed.
- No Fee default-fill behavior change belongs to TASK_358A.
- No Test Record/Report consumer behavior change belongs to TASK_358A.
- No Matrix parser/import, StepInstance/execution persistence, LTR/public-drive, real workbook/folder, `.agents/**`, or `docs_project_management/**` change belongs to TASK_358A.

## Browser Smoke

Live browser smoke was attempted at tooling level but could not be completed:

```text
bundled=browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system=browserType.launch: spawn EPERM
```

No screenshot artifact was captured. This is a non-blocking QA residual because the changed UI behavior is covered by focused frontend tests, build, source inspection, and static scope scans. A manual browser spot-check in an unrestricted environment would still be useful before release packaging.

## Residual Risk

- Browser-only layout issues were not directly observed in this thread due browser tooling restrictions.
- External Fee rule seed/test residuals and release/settings residuals are present in the worktree and must be excluded during Integrator packaging.

## QA Conclusion

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Integrator packaging note: stage only the TASK_358A candidate frontend/docs/evidence files and this QA evidence. Do not stage Fee seed/test residuals, Settings/LTR, release/desktop/packaging, `docs/task_board.md`, TASK_357A residuals, `temp_agents_stash.md`, or other unrelated dirty files.
