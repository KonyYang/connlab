# TASK_358A Matrix Editor Quantity Defaults Simplification Developer Evidence

Status: implementation complete - ready for Reviewer implementation gate
Task: `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION`
Lane: `matrix-editor-quantity-defaults-simplification`
Date: 2026-07-09
Role: Developer

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION`.
- Why allowed: Planner reconciliation records Reviewer implementation-readiness passed and User approved Developer implementation in `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reconciliation_planner.md`.
- Stop point: Developer implementation complete. Await Reviewer implementation gate.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `.agents/skills/impeccable/reference/product.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md`
- `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reviewer.md`
- TASK_357B Developer evidence for Basic Information quantity defaults
- TASK_357C Developer evidence for Matrix Step quantity setup
- TASK_357D Developer evidence for Fee passive consumption
- TASK_357E Developer evidence for Test Record quantity projection
- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `backend/application/matrix_step_quantity_service.py`
- `tests/unit/test_matrix_step_quantity_service.py`
- current `git status --short`

## Repository Facts Confirmed

- Basic Information currently exposes a config-driven field group titled `Quantity defaults`.
- That group contains:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
- Basic Information frontend tests currently assert invalid quantity validation, layout order, readonly disabled state, and fixture response values for those fields.
- `MatrixStepQuantityPanel` already renders the operator-facing Step quantity setup table and save action.
- `matrixStepQuantitySelectors.ts` already owns local row update, derived `total_readings`, review-required calculation, and save DTO mapping.
- `MatrixEditorWorkspace.tsx` already loads Step quantities through `fetchMatrixStepQuantities`, filters them by selected group, updates local item state, and saves through `saveMatrixStepQuantities`.
- `MatrixStepQuantityService` currently reads confirmed Basic Information first, then draft Basic Information, as default source for rows without persisted Step quantity records.
- TASK_357D and TASK_357E downstream consumers use confirmed Matrix Step quantities. They do not need behavior changes for this corrective lane.

## Planning Decisions Written

Updated `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md` with:

- implementation shape narrowed to UI/source-policy correction only;
- Matrix Editor placement inside `MatrixStepQuantityPanel`;
- no modal, no new card stack, no new persisted default authority;
- transient Matrix Editor default strip for V1;
- blank-only apply semantics;
- existing `Save quantities` remains the persistence boundary;
- backend Basic Information compatibility policy;
- exact future May Touch list;
- implementation tests and validation gates;
- package isolation risks.

## Future Implementation Boundary

Recommended implementation shape:

1. Remove the Basic Information `Quantity defaults` field group from `basicInformationFieldConfig.ts`.
2. Remove or update Basic Information tests that expect quantity fields, validation status, or field order.
3. Keep Basic Information backend values-map compatibility for historical records. No schema deletion and no destructive migration.
4. Add a compact inline default strip inside `MatrixStepQuantityPanel`, above the table.
5. Keep the default strip as transient frontend state for V1.
6. Add `Apply to blank Step quantities`.
7. Fill blank Step quantity fields only. Do not silently overwrite non-blank values or saved/manual overrides.
8. Continue saving through existing Matrix Step quantity save flow.
9. Touch `MatrixStepQuantityService` only if needed to stop Basic Information from acting as the active primary default source for new rows.
10. Do not change Fee/Test Record/Report behavior except focused regression verification.

## Exact Future May Touch

Preferred implementation files:

- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `backend/application/matrix_step_quantity_service.py`, only if active default-source policy requires it
- `tests/unit/test_matrix_step_quantity_service.py`, only if backend source policy changes
- `tests/integration/test_matrix_step_quantity_api.py`, only if backend/API behavior changes
- TASK_358A evidence and board updates through normal lane flow

Avoid `frontend/src/api/client.ts` unless a future Reviewer-approved implementation proves a typed API contract change is unavoidable. Preferred V1 uses existing Matrix Step quantity API shapes.

## Must Not Touch / Locked Scope

- No product implementation in this planning-first pass.
- No schema/data deletion or destructive migration.
- No Fee default-fill behavior changes.
- No Test Record/Report consumer behavior changes.
- No Matrix Step setup/storage mutation beyond existing Step quantity save path in a future approved implementation.
- No StepInstance/execution persistence.
- No Matrix parser/import changes.
- No LTR workbook/public-drive/real workbook/folder behavior.
- No release/settings/template residual cleanup.
- No `.agents/**`.
- No `docs/project_management/**`.

## UX / Product Decision

Register: product.

The future UI should keep Matrix Editor dense and operational:

- no modal as first thought;
- no extra card clutter;
- no nested card;
- no long explanatory copy;
- no side-stripe accent, gradient text, or glassmorphism;
- use standard inputs and a quiet action button inside the Step quantity panel;
- keep Matrix table and Step setup as the primary work surface.

Suggested copy:

- `Defaults for this group`
- `Apply to blank Step quantities`
- `Defaults applied to blank Step quantities.`
- `No blank Step quantities to update.`

## Validation Plan For Future Implementation

Frontend:

- `npm test -- ProjectBasicInformationWorkspace MatrixEditorWorkspace --run`
- Basic Information no longer renders `Quantity defaults` or the three quantity fields.
- Basic Information no longer shows quantity default validation status.
- Matrix Editor renders the default strip inside Step quantity setup.
- Applying defaults fills blank fields in the selected group.
- Applying defaults preserves non-blank Step quantity fields.
- Applying defaults updates derived `total_readings`.
- Existing `Save quantities` still persists rows.
- Readonly state disables defaults and row editing.

Backend, if touched:

- focused Matrix Step quantity service/API tests.
- saved Step quantities still take priority.
- legacy Basic Information quantity values remain harmless.
- duplicate no-suffix identity protections from TASK_357C remain intact.

Regressions:

- TASK_357D Fee passive consumption tests if backend/default-source behavior changes.
- TASK_357E Test Record preview/API quantity tests if backend/default-source behavior changes.

General:

- `npm run build`
- `git diff --check`
- trailing whitespace scan
- Python line-count scan if backend touched
- forbidden-scope scan for Fee, Test Record/Report behavior, StepInstance, Matrix parser/import, LTR/public-drive, real folders/workbooks, release/settings residuals, `.agents/**`, and `docs/project_management/**`
- browser smoke for Matrix Editor if tooling/data is available.

## External Residuals Excluded

The current worktree contains external residuals that are not part of TASK_358A:

- `backend/api/dependencies.py`
- Fee rule seed/test residuals
- Settings/LTR/template helper services and tests
- backend desktop/release helper files
- `dist_release/**`, `packaging/**`, release scripts/tests/docs
- frontend New Project test residual
- TASK_357A docs/evidence residuals
- `temp_agents_stash.md`

They were not modified or cleaned by this pass.

## Validation

- Required source files and evidence were read.
- Updated only:
  - `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
  - `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`
- Product code was not modified.
- Required docs/evidence existence check passed:
  - `tasks/TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION.md`
  - `docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md`
  - `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_planner.md`
  - `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_reviewer.md`
  - `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`
- `git diff --check -- docs/task_358a_matrix_editor_quantity_defaults_simplification_plan.md docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md` passed.
- Trailing whitespace scan on TASK_358A plan/developer evidence returned no matches.
- Targeted status over TASK_358A plan/evidence plus future product May Touch and locked governance paths showed only TASK_358A plan/developer evidence. No product code was changed by this planning-first pass.

## Decision

Completion status: implementation complete - ready for Reviewer implementation gate.

Recommended next role: Reviewer implementation gate.

Blocking summary: none.

## Implementation Pass Summary

Changed files:

- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_358A_matrix-editor-quantity-defaults-simplification_developer.md`

Behavior implemented:

- Removed the Basic Information `Quantity defaults` UI group.
- Removed Basic Information frontend quantity-default validation and confirm blocking tied to those hidden fields.
- Preserved backend/data compatibility by leaving Basic Information values-map and schema untouched.
- Added a compact `Defaults for this group` strip inside Matrix Step quantity setup.
- Added transient defaults for `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`.
- Added `Apply to blank Step quantities` behavior that only fills blank fields for the currently selected Matrix group.
- Preserved existing non-blank Step quantity values and saved/manual overrides.
- Kept the existing `Save quantities` button as the only persistence boundary.
- Preserved Fee/Test Record/Report passive consumption behavior by not touching their code.

TDD / regression notes:

- Added a Basic Information regression proving `Quantity defaults` and the three quantity fields no longer render and no longer block Confirm.
- Updated Basic Information layout/readonly tests to remove expectations for the deleted UI entry.
- Added a Matrix Editor regression proving defaults fill only blank Step quantity fields, preserve existing values, derive the save payload through the existing Matrix Step save flow, and mark updated rows as Matrix Step overrides.
- Initial Matrix Editor focused test run failed before implementation because `Defaults for this group` did not exist; after implementation the focused suite passed.

## Implementation Validation

- `npm test -- ProjectBasicInformationWorkspace MatrixEditorWorkspace --run` from `frontend/` passed: 2 files / 60 tests.
- `npm run build` from `frontend/` passed. Existing Vite chunk-size warning only.
- `git diff --check -- frontend/src/features/project-basic-information/basicInformationFieldConfig.ts frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx frontend/src/workbench.css` passed with LF/CRLF warnings only.
- Trailing whitespace scan on touched frontend files returned no matches.
- Backend tests were not rerun because no backend files were touched by this implementation pass.

## Forbidden-Scope Check

- No backend files were modified by this TASK_358A implementation pass.
- No schema/data deletion or migration was performed.
- No Fee/Test Record/Report behavior was changed.
- No Matrix parser/import code was changed.
- No LTR/public-drive/real workbook/folder behavior was changed.
- No `.agents/**` or `docs/project_management/**` files were changed.
- External residuals remain visible in `git status` and were left untouched.
