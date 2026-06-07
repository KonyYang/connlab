# TASK_297 Fee Evaluation Preview Step Column And Discount Label - Executable Plan

## Execution Context

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: TASK_297_FEE_EVALUATION_PREVIEW_STEP_COLUMN_AND_DISCOUNT_LABEL.
- Allowed now because: TASK_296 is complete and the user explicitly requested the next Fee Evaluation preview adjustment.
- Status: planned; awaiting explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The task is a bounded frontend-only refinement with clear expected table headers and existing model data. It can be executed safely with focused tests without touching backend, Excel, export, or persistence paths.

## Goal

Restore the visible `Step` column in the Fee Evaluation Testing Prices preview and rename the visible discount column from `Price Percent Off` back to `Discount`, while keeping the TASK_296 row-ordering behavior.

## Scope

### In Scope

- `FeeEvaluationPreviewTable.tsx` table headers and body cells.
- `workbench.css` preview table column-index styling.
- Frontend tests for visible table headers and ordering.
- Static shell tests that guard against backend/API/export changes.
- Task-board update after implementation.

### Out Of Scope

- Backend/API changes.
- Fee draft service changes.
- Excel gateway or generated workbook changes.
- Direct-download route changes.
- Editable fee cells.
- Persisted fee-line edits.
- Fee calculation changes.
- Matrix Editor changes.
- StepInstance/execution/report expansion.

## Design

### Table Column Order

Final visible table columns:

1. Group
2. Step
3. Spend Time
4. Description
5. Unit Price
6. Unit Type
7. Units
8. Base Fee
9. Discount
10. Testing Fee

Implementation notes:

- Restore `<th>Step</th>` immediately after `Group`.
- Restore `<td>{row.stepToken}</td>` immediately after `row.groupLabel`.
- Rename `Price Percent Off` header to `Discount`.
- Do not alter the preview row type, because `stepToken` already exists and TASK_296 sorting already uses it internally.

### Sorting Policy

Do not change TASK_296 sorting logic:

- Pure numeric tokens sort numerically within each group.
- Non-numeric or blank tokens sort after numeric tokens.
- Same-value or fallback rows preserve source line/token order.
- Manual trailing rows remain after all Matrix rows.

### CSS Policy

Restoring `Step` shifts the table back to ten visible columns:

- Group: `nth-child(1)`, centered.
- Step: `nth-child(2)`, compact, nowrap.
- Spend Time: `nth-child(3)`, nowrap.
- Description: `nth-child(4)`, narrower description column.
- Fee columns: `nth-child(5)` through `nth-child(10)`, nowrap as appropriate.
- Manual row description styling should target `nth-child(4)`.

Keep group-tone classes and pending/manual row behavior unchanged.

## File-Level Changes

Modify:

- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `tasks/TASK_297_FEE_EVALUATION_PREVIEW_STEP_COLUMN_AND_DISCOUNT_LABEL.md`
- `docs/task_board.md`

Do not modify:

- `backend/`
- `frontend/src/api/client.ts`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- Excel gateway files
- route files

## Test Plan

### Component Tests

Update `FeeEvaluationReviewExportPage.test.tsx` to assert:

- `Step` is a visible column header.
- `Discount` is a visible column header.
- `Price Percent Off` is not a visible column header.
- `Unit Price`, `Units`, `Base Fee`, and `Testing Fee` remain visible.
- Existing row-order test coverage from `feeEvaluationPreviewModel.test.ts` remains passing.

### Static Shell Tests

Update `tests/unit/test_frontend_shell_files.py` to assert:

- `FeeEvaluationPreviewTable.tsx` contains `<th>Step</th>`.
- `FeeEvaluationPreviewTable.tsx` renders `{row.stepToken}`.
- `FeeEvaluationPreviewTable.tsx` contains `Discount`.
- `FeeEvaluationPreviewTable.tsx` does not contain `Price Percent Off`.
- No backend/API/export symbols are introduced for TASK_297.

### Regression

Keep existing TASK_296 model tests unchanged so step ordering remains protected.

## Validation Commands

Run after implementation:

```powershell
cd frontend
npm test -- --run feeEvaluationPreviewModel FeeEvaluationReviewExportPage --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

## Risks And Mitigations

- Risk: Reintroducing `Step` widens the table.
  - Mitigation: Keep Step compact and adjust table column indexes without increasing the table beyond the TASK_295/TASK_296 footprint.
- Risk: Header wording can drift from Excel output behavior.
  - Mitigation: TASK_297 is UI-preview wording only; it does not modify generated Excel workbook logic.
- Risk: CSS `nth-child` rules may point at the wrong column.
  - Mitigation: Update column-index tests and run the frontend build.

## Stop Point

After implementation and validation, update `docs/task_board.md` to mark TASK_297 complete and stop. Do not proceed to editable fee cells, backend persistence, or fee calculation without a separate approved task.
