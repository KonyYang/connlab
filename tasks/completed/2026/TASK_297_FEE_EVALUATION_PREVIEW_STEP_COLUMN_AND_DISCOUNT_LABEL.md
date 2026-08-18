# TASK_297 Fee Evaluation Preview Step Column And Discount Label

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_296 is complete. The user reviewed the Fee Evaluation preview and clarified that the visible `Step` column is useful for understanding the workflow, and that the fee-sheet business label should show `Discount` instead of `Price Percent Off`.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. The work is a narrow frontend-only presentation adjustment: restore a visible table column that already exists in the preview row model, change one column label, and keep TASK_296 numeric step ordering intact. The task is low risk if it stays within the Fee Evaluation preview table and its tests.

## Goal

Make the Fee Evaluation preview table easier for operators to follow while keeping the official fee-form wording familiar:

- Restore visible `Step` column in the preview table.
- Continue sorting rows by step order within each group.
- Rename visible `Price Percent Off` column back to `Discount`.
- Keep existing fee-related columns unchanged.

## Scope

### Frontend Preview Table

- Restore the visible `Step` header after `Group`.
- Render `row.stepToken` as the visible Step cell.
- Keep the TASK_296 step ordering behavior:
  - numeric step tokens sort by numeric value inside each group
  - non-numeric or blank tokens remain stable after numeric tokens
  - repeated test items remain visible when they belong to different steps
- Rename the visible `Price Percent Off` header to `Discount`.

### Styling

- Update preview-table CSS column indexes after restoring the Step column.
- Keep Group centered.
- Keep Step compact and readable.
- Keep Description narrower than the wide fee/control area.
- Keep alternating group background colors.

## Out Of Scope

- No backend API/schema changes.
- No fee draft service changes.
- No Excel COM gateway or generated workbook changes.
- No direct-download route changes.
- No fee calculation changes.
- No actual editable cells or persisted fee-line edits.
- No Matrix Editor changes.
- No StepInstance, execution persistence, report expansion, AI review, permissions, or multi-user workflow.

## Required Behavior

The visible preview table columns should be:

```text
Group
Step
Spend Time
Description
Unit Price
Unit Type
Units
Base Fee
Discount
Testing Fee
```

For one group with step tokens:

```text
1, 9, 2, 4, 6, 8, 3, 7, 5
```

The rendered visible `Step` values should appear in this order:

```text
1, 2, 3, 4, 5, 6, 7, 8, 9
```

## Acceptance Criteria

- The visible preview table shows `Step`.
- The visible preview table shows `Discount`.
- The visible preview table does not show `Price Percent Off`.
- Step sorting from TASK_296 remains intact.
- Existing columns `Unit Price`, `Units`, `Base Fee`, and `Testing Fee` remain visible.
- Manual trailing rows remain at the end.
- Group background alternation and centered Group column remain intact.
- No backend/API/Excel/export/database behavior changes.

## Validation

Implementation validation completed:

```text
cd frontend; npm test -- --run feeEvaluationPreviewModel FeeEvaluationReviewExportPage --watch=false -> 15 passed
cd frontend; npm run build -> passed
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench" -> 7 passed
git diff --check -> passed, CRLF warnings only
```

Browser smoke:

- Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`.
- Confirm `Step` is visible after `Group`.
- Confirm rows are still sorted by step sequence inside each group.
- Confirm `Discount` is visible and `Price Percent Off` is not visible.
- Confirm fee columns remain visible.
