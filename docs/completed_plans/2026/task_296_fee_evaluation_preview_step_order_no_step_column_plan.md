# TASK_296 Fee Evaluation Preview Step Order Without Step Column - Executable Plan

## Execution Context

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: TASK_296_FEE_EVALUATION_PREVIEW_STEP_ORDER_NO_STEP_COLUMN.
- Allowed now because: TASK_295 is complete and the user explicitly requested the TASK_296 task file and executable plan.
- Status: planned; awaiting explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. It is a narrow frontend-only table-model and rendering adjustment with existing unit tests, React component tests, and static shell tests. The model should be able to implement it safely with TDD while avoiding backend, Excel, and persistence scope.

## Goal

Keep the Fee Evaluation preview row sequence driven by Matrix step tokens, but remove the visible `Step` column from the Testing Prices preview table. The operator should see group rows in natural step order, not a separate step field.

## Scope

### In Scope

- Frontend model sorting in `feeEvaluationPreviewModel.ts`.
- Preview table column rendering in `FeeEvaluationPreviewTable.tsx`.
- CSS column index updates in `workbench.css`.
- Tests that lock:
  - numeric step ordering inside a group
  - stable non-numeric/blank fallback behavior
  - no visible `Step` table header
  - price columns still present
  - group tone and manual trailing row behavior preserved

### Out Of Scope

- Backend/API changes.
- Fee draft service changes.
- Excel export/download changes.
- Editable cells.
- Persisted fee-line edits.
- Fee calculation changes.
- Matrix Editor changes.
- StepInstance/execution/report expansion.

## Design

### Step Sorting Policy

The existing TASK_295 preview model already expands each `FeeEvaluationLineItem` into one preview row per `stepToken`. TASK_296 should keep `stepToken` internally but sort rows before returning them.

Sorting priority:

1. Preserve draft group order from `draft.groups`.
2. Within each group, sort numeric step tokens by numeric value.
3. Blank or non-numeric tokens should sort after numeric tokens.
4. For same numeric value or non-numeric fallback rows, preserve source line order and token index.
5. Manual trailing rows remain after all Matrix-derived rows.

Implementation detail:

```ts
type ExpandedStepRow = FeeEvaluationPreviewRow & {
  stepSortValue: number | null;
  sourceLineOrder: number;
  sourceTokenOrder: number;
};
```

The sort metadata can be local to the model function and should not leak into the exported row type unless tests or future UI need it.

Numeric parser:

- `1` -> `1`
- `09` -> `9`
- `10` -> `10`
- `1(a)`, `A`, blank, `-` -> `null`

Do not try to parse complex markers in TASK_296. The fallback order keeps those rows stable and avoids inventing ordering rules.

### Visible Table Columns

Remove the visible `Step` column from `FeeEvaluationPreviewTable.tsx`.

Final visible order:

1. Group
2. Spend Time
3. Description
4. Unit Price
5. Unit Type
6. Units
7. Base Fee
8. Price Percent Off
9. Testing Fee

Keep `Unit Type` because it explains the fee basis. The user confirmed the important fee columns are already present; TASK_296 should not add an edit mode.

### CSS Updates

`workbench.css` currently uses `nth-child` rules based on TASK_295 columns. After removing visible Step, update the index rules:

- Group column remains `nth-child(1)`, centered.
- Description becomes `nth-child(3)`.
- Fee columns shift back by one.
- Table min-width may stay close to the current value, but should not grow.
- Group tone classes and manual row classes remain unchanged.

### Copy

Rename the visible `Discount` header to `Price Percent Off` if still present.

No explanatory text should be added in-app for this change; the row order should speak for itself.

## File-Level Changes

Modify:

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Do not modify:

- `backend/`
- `frontend/src/api/client.ts`
- Excel gateway files
- route files

## Test Plan

### Model Tests

Add/update tests for:

- Step tokens such as `["1", "9", "2", "4", "6", "8", "3", "7", "5"]` return preview rows in `1..9` order.
- A second group with tokens such as `["1", "11", "2"]` returns `1,2,11` inside that group.
- Non-numeric/blank tokens remain stable after numeric tokens.
- Manual trailing rows remain last.

### Component Tests

Add/update tests for:

- `Step` is not a visible column header in `Testing Prices preview rows`.
- `Unit Price`, `Units`, `Base Fee`, `Price Percent Off`, and `Testing Fee` are visible.
- `Discount` is not used as the preview table column header.
- Existing `Fee Form` button remains unchanged.
- Group filtering still shows selected group rows plus manual trailing rows.

### Static Shell Tests

Add/update `tests/unit/test_frontend_shell_files.py` assertions:

- `Price Percent Off` appears in preview table source.
- `Step` is not a table header in preview table source.
- `stepToken` remains in preview model source.
- No backend/API/export symbols are introduced.

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

- Risk: Hiding Step could make ordering hard to audit.
  - Mitigation: Keep internal `stepToken` in model/tests and preserve review-details traceability.
- Risk: Numeric sort could mishandle marker tokens.
  - Mitigation: Only pure numeric tokens are sorted numerically; marker tokens keep source order after numeric tokens.
- Risk: CSS `nth-child` drift could mis-style columns.
  - Mitigation: Add static checks and visually smoke the table at workstation width.

## Stop Point

After implementation and validation, update `docs/task_board.md` to mark TASK_296 complete and stop. Do not proceed to editable fee cells or backend persistence without a separate approved task.
