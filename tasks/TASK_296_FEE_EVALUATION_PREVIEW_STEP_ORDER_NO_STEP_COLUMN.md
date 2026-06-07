# TASK_296 Fee Evaluation Preview Step Order Without Step Column

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_295 is complete. The user reviewed the Fee Evaluation page and clarified that step order is needed for row ordering, but the visible `Step` column itself is not needed. The user also confirmed that the fee-related columns are already present, so TASK_296 should not expand that scope.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. The work is a small bounded frontend preview-model and table rendering adjustment: preserve step-based ordering, hide the visible `Step` column, and keep existing fee columns unchanged. The task has clear tests and a low risk profile if it remains frontend-only and does not modify backend fee draft/export behavior.

## Goal

Make the Fee Evaluation preview table read like the official fee form while still using Matrix step order:

- Do not display a separate `Step` column.
- Use step tokens only as an ordering key inside each group.
- For Group 1, rows should appear in step order such as `1,2,3,4,5,6,7,8,9`.
- For Group 2, rows should appear in step order such as `1..11` when those steps exist.
- Keep group block background colors alternating so group boundaries remain clear.
- Keep existing fee columns unchanged.

## Scope

### Frontend Preview Model

- Keep `stepToken` in the internal preview row model as a sorting/traceability field.
- Sort Matrix-derived rows by:
  1. source group order
  2. numeric step token order when the token is numeric
  3. stable fallback order for non-numeric or blank tokens
  4. source line order as a tie-breaker
- Preserve repeated test items when they belong to different steps.
- Keep manual trailing rows at the end:
  - `Report preparation`
  - `Condition confirmation`
  - `External Cost (tooling / purchase cost)`

### Frontend Table UI

- Remove the visible `Step` column from the preview table.
- Keep existing visible columns:
  - `Group`
  - `Spend Time`
  - `Description`
  - `Unit Price`
  - `Unit Type`
  - `Units`
  - `Base Fee`
  - `Price Percent Off`
  - `Testing Fee`
- Keep `Unit Price`, `Units`, `Base Fee`, `Price Percent Off`, and `Testing Fee` present as future editable-cell preparation.
- Rename any visible `Discount` header to `Price Percent Off` if it is still shown as `Discount`.
- Keep Group cells centered and group-block background alternation.

## Out Of Scope

- No backend API/schema changes.
- No fee draft service changes.
- No Excel COM gateway or generated workbook changes.
- No actual editable cells or persisted fee-line edits.
- No fee calculation changes.
- No changes to the Fee Form direct-download endpoint.
- No Matrix Editor changes.
- No StepInstance, execution persistence, report expansion, AI review, permissions, or multi-user workflow.

## Required Behavior

Given rows in one group with step tokens:

```text
1, 9, 2, 4, 6, 8, 3, 7, 5
```

The preview should render them in this visible order:

```text
1, 2, 3, 4, 5, 6, 7, 8, 9
```

But the table should not show a `Step` column. Users should simply see the rows in the expected sequence.

## Acceptance Criteria

- Preview rows are sorted by step order within each Matrix group.
- The visible preview table does not show a `Step` column.
- Existing price-related columns remain present, including `Unit Price`, `Units`, `Base Fee`, `Price Percent Off`, and `Testing Fee`.
- `Discount` is not used as the visible header if `Price Percent Off` is the intended business label.
- Group background alternation and centered Group column remain intact.
- Manual trailing rows remain at the end.
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
- Confirm no visible `Step` column.
- Confirm Group 1 rows are ordered by step sequence.
- Confirm Group 2 rows are ordered by step sequence.
- Confirm alternating group backgrounds remain visible.
- Confirm `Unit Price`, `Units`, `Base Fee`, `Price Percent Off`, and `Testing Fee` columns remain visible.
