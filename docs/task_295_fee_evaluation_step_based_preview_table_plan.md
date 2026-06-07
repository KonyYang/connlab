# TASK_295 Fee Evaluation Step-Based Preview Table - Executable Plan

## Execution Context

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: TASK_295_FEE_EVALUATION_STEP_BASED_PREVIEW_TABLE.
- Allowed now because: TASK_294 is complete, the user explicitly requested the next task file and executable plan, and this document is planning-only. No implementation code is included in this step.
- Status: planned; awaiting explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The work is a bounded React/TypeScript UI-model change with clear acceptance criteria, existing component and model tests, and no need for new backend behavior. The model should be able to follow the existing Fee Evaluation feature boundaries, update tests first, and keep the change frontend-only.

## Goal

Revise the Fee Evaluation page preview so it better matches how project managers and customers think about the official Testing Prices fee form:

- Preview rows are based on Matrix group steps, not only unique test-item style rows.
- Repeated test items remain visible when they belong to different steps.
- `Report preparation`, `Condition confirmation`, and independent trailing `External Cost` rows are shown at the end.
- Customer-facing emphasis is `Grand Cost`.
- Project-manager-facing emphasis is `Lab manpower cost`.
- If local preview numeric `Lab manpower cost` exceeds local preview numeric `Grand Cost`, show a clear loss warning.

## Scope

### In Scope

- Frontend-only changes under the Fee Evaluation feature and shared Workbench stylesheet.
- Preview model changes that expand fee draft lines by `step_tokens`.
- Preview table layout changes:
  - Add/display a `Step` column.
  - Center the `Group` column horizontally.
  - Narrow the `Description` column.
  - Use alternating group row colors to make group boundaries easier to scan.
  - Append fixed trailing rows.
- Cost summary display changes:
  - `Grand Cost` is the primary total label.
  - `Lab manpower cost` is visible for project-management review.
  - Local preview-only numeric inputs or compact editable fields for `Grand Cost` and `Lab manpower cost`.
  - Numeric loss warning when local preview lab manpower cost is greater than local preview Grand Cost.
- Tests for the model, preview table, and page behavior.

### Out Of Scope

- Backend fee calculation changes.
- Fee rule seed changes.
- Confirmed Matrix API changes.
- Excel COM gateway changes.
- Direct download/export route changes.
- Persisted fee-line editing.
- Reading calculated values back from Excel.
- Persisting or exporting local preview-only `Grand Cost` / `Lab manpower cost` values.
- Step execution persistence or StepInstance implementation.
- Any change to the official Excel template file.

## Design

### Preview Row Model

Extend the existing preview model in `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`.

Add row metadata:

```ts
type FeeEvaluationPreviewRowKind = "matrix_step" | "manual_trailing";

type FeeEvaluationPreviewGroupTone = "tone-a" | "tone-b" | "manual";
```

Extend `FeeEvaluationPreviewRow` with:

- `stepToken: string`
- `rowKind: FeeEvaluationPreviewRowKind`
- `groupTone: FeeEvaluationPreviewGroupTone`

V1 row expansion policy:

1. For each draft line item, use `line.step_tokens` as the step authority.
2. If `step_tokens` is non-empty, create one preview row per token.
3. If `step_tokens` is empty, create one fallback row with `stepToken: "-"`.
4. Preserve the original line description/test item on every expanded row.
5. Keep line-level values from the matched fee rule where available.
6. Assign alternating `groupTone` by group sequence, not by row index, so each group block has a stable color.

Append fixed trailing rows in this order:

1. `Report preparation`
2. `Condition confirmation`
3. `External Cost (tooling / purchase cost)`

Trailing rows use:

- `rowKind: "manual_trailing"`
- `groupLabel: ""`
- `stepToken: "-"`
- `groupTone: "manual"`
- blank or `Pending` values where the official Excel form requires later completion
- review/help text that makes clear these are manual Fee Form completion rows

### Group Filtering

The group dropdown keeps using actual Matrix groups only.

For selected group mode:

- Show rows belonging to the selected Matrix group.
- Keep the fixed trailing rows visible at the end because they are form-level completion rows.
- Compute the selected fee scope from selected Matrix rows only; trailing rows are excluded from scope totals.

For `All Group` mode:

- Show all Matrix-step rows plus trailing rows.
- Compute the fee scope from all Matrix rows only; trailing rows are excluded from scope totals.

### Cost Summary And Warning

Update the preview summary language:

- Replace generic `Fee` display with `Grand Cost`.
- Add `Lab manpower cost` as a secondary project-management metric.
- Add local preview-only numeric entry for `Grand Cost` and `Lab manpower cost`.
- Current backend/API data usually has pending values. The local fields are the V1 page-level data source for the loss warning.
- These local values reset on page reload, are not saved to the backend, are not written to Excel, and are not sent to the Fee Form download endpoint.

Add a pure helper:

```ts
buildFeeEvaluationCostRisk(values): {
  severity: "none" | "loss_warning";
  message: string;
}
```

Parsing policy:

- Only compare when both values are numeric or numeric currency-like strings.
- Ignore blank, `Pending`, `-`, and non-numeric values.
- If `labManpowerCost > grandCost`, return a warning such as:
  `Lab manpower cost exceeds Grand Cost. Review pricing before release.`
- If values are pending or safe, return `severity: "none"`.

This warning is a preview/readiness signal only. TASK_295 does not calculate missing prices, synchronize Excel-calculated totals back into ConnLab, or make local preview values official.

External Cost V1 display policy:

- Show `External Cost (tooling / purchase cost)` as an independent trailing table row.
- Do not add a separate header/totals `External Cost` metric in TASK_295; this avoids making the header busy again.
- Future tasks may add an official External Cost total source if pricing completion moves into ConnLab.

### Table Layout

Update `FeeEvaluationPreviewTable.tsx` column order:

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

UI adjustments:

- `Group` cells are horizontally centered.
- `Step` cells are compact and readable.
- `Description` column becomes narrower than the current wide version.
- Row background alternates by group block, not by every row.
- Manual trailing rows have a distinct but quiet style.
- The `Fee Form` download button remains in the preview header and keeps TASK_294 behavior.

## File-Level Changes

### Frontend Model

Modify:

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`

Expected changes:

- Extend row types.
- Expand rows by `step_tokens`.
- Append trailing manual rows.
- Keep group filter helpers aligned with Matrix groups only.
- Add cost-risk helper.

### Frontend Components

Modify:

- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

Expected changes:

- Render the new `Step` column.
- Render trailing manual rows.
- Use `Grand Cost` and `Lab manpower cost` labels.
- Add local preview-only fields/state for `Grand Cost` and `Lab manpower cost`.
- Render loss warning when helper reports one.
- Keep the header concise; do not reintroduce removed summary/export cards.

### Styles

Modify:

- `frontend/src/workbench.css`

Expected changes:

- Center group column.
- Add group-tone row classes.
- Add manual trailing row class.
- Narrow description column.
- Add compact warning style.
- Preserve responsive behavior and avoid text overlap at workstation widths.

### Tests

Modify:

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- `tests/unit/test_frontend_shell_files.py`

Expected tests:

- A line with multiple `step_tokens` expands into multiple preview rows.
- Repeated test items remain visible when tied to different step tokens.
- Empty `step_tokens` yields one fallback row.
- Fixed trailing rows appear at the end in the required order.
- Selected-group preview shows selected group rows plus trailing rows.
- Scope totals exclude trailing rows.
- Local preview-only Grand Cost / Lab manpower cost fields are not sent to export/download APIs.
- Cost-risk helper warns only when local preview numeric Lab manpower cost is greater than local preview numeric Grand Cost.
- Table renders the `Step` column.
- `Group` column centering and group-tone classes are present in CSS/source checks.
- No backend files are touched.

## Implementation Sequence

1. Add or update model tests first for step expansion, trailing rows, selected-group filtering, and cost-risk comparison.
2. Update `feeEvaluationPreviewModel.ts` until model tests pass.
3. Update `FeeEvaluationPreviewTable.tsx` to render the new model shape and table columns.
4. Update `FeeEvaluationReviewExportPage.tsx` to use Grand Cost / Lab manpower cost summary and warning.
5. Update `workbench.css` for column sizing, centering, group tones, and warning treatment.
6. Add/update page and static shell tests.
7. Run the validation commands.
8. Update `docs/task_board.md` completion notes only after implementation is complete and verified.

## Risks And Mitigations

- Risk: Multiplying rows by step tokens could make the table longer.
  - Mitigation: This matches the user's expected group/step fee form preview. Keep the header compact and preserve horizontal table scrolling.
- Risk: Cost warning could imply ConnLab calculated official pricing.
  - Mitigation: Label the values as local preview-only, do not persist/export them, and keep backend-derived pending values pending.
- Risk: Fixed rows could be confused with Matrix-derived rows.
  - Mitigation: Use distinct manual trailing row style and exclude them from group totals.
- Risk: Description narrowing could cause clipped text.
  - Mitigation: Use wrapping, not truncation, for descriptions.

## Validation

Run after implementation:

```powershell
cd frontend
npm test -- --run feeEvaluationPreviewModel FeeEvaluationReviewExportPage --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Manual browser smoke:

1. Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`.
2. Confirm preview table includes `Step`.
3. Confirm repeated test items appear when they belong to different steps.
4. Confirm `Report preparation`, `Condition confirmation`, and `External Cost (tooling / purchase cost)` appear at the end.
5. Confirm Group column is centered.
6. Confirm group blocks alternate background colors.
7. Confirm header emphasizes `Grand Cost` and `Lab manpower cost`.
8. Confirm no warning appears while local values are blank/pending.
9. Enter local preview numeric Lab manpower cost greater than Grand Cost and confirm the warning copy appears.
10. Confirm Fee Form download still sends the existing TASK_294 request shape and does not include the local preview values.
