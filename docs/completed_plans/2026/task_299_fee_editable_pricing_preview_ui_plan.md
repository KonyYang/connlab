# TASK_299 Fee Editable Pricing Preview UI - Executable Plan

## Execution Context

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: TASK_299_FEE_EDITABLE_PRICING_PREVIEW_UI.
- Allowed now because: TASK_298 is complete and the series plan defines TASK_299 as the next controlled step.
- Status: planned; awaiting explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The implementation is a bounded frontend-only edit-state and calculation task with explicit formulas, existing preview row data, and focused tests. It should not expand backend pricing rules or export behavior.

## Goal

Convert the Fee Evaluation preview table from read-only pricing fields to local editable pricing fields with immediate calculated `Testing Fee`, selected group fee, and Grand Cost preview.

## Scope

### In Scope

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Fee Evaluation frontend tests.
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `tasks/TASK_299_FEE_EDITABLE_PRICING_PREVIEW_UI.md`
- `docs/task_board.md`

### Out Of Scope

- `backend/`
- `frontend/src/api/client.ts`
- Excel gateway files
- Fee Form download payloads
- Persistence/reload of edits
- Rule maintenance or seed updates

## Design

### Preview Edit Model

Add a local edit-state model in the Fee Evaluation feature, preferably in `feeEvaluationPreviewModel.ts` or a small adjacent model file if that keeps responsibilities clearer.

Suggested types:

```ts
export type FeeEvaluationEditableField =
  | "spendTime"
  | "unitPrice"
  | "unitType"
  | "units"
  | "baseFee"
  | "discount";

export type FeeEvaluationRowEdits = Partial<Record<FeeEvaluationEditableField, string>>;

export type FeeEvaluationPreviewEditState = Record<string, FeeEvaluationRowEdits>;
```

Use `row.lineId` as the local edit key so expanded step rows and manual trailing rows can be edited independently.

### Row Values

When rendering a row:

1. Start from `FeeEvaluationPreviewRow`.
2. Overlay any local edits for that `lineId`.
3. Calculate `Testing Fee` from the effective values.

Do not mutate the original draft-derived row objects.

### Calculation Helpers

Add deterministic helpers:

```ts
parseEditableMoney(value: string): number | null
parseEditablePercent(value: string): number | null
calculateTestingFee(input): string
```

Rules:

- Required numeric fields: `Unit Price`, `Units`.
- Optional numeric fields: `Base Fee`, `Discount`.
- Empty `Base Fee` -> `0`.
- Empty `Discount` -> `0`.
- `10` and `10%` -> `0.10`.
- Invalid input -> `Pending`.
- Output formatting -> two decimals.

Do not support persistence-specific validation in TASK_299.

### Unit Type Select

Define a feature-local constant:

```ts
export const FEE_UNIT_TYPE_OPTIONS = [
  "per sample",
  "per reading",
  "per contact",
  "per cycle",
  "per time",
  "per hour",
  "per day",
  "per photo",
  "per report",
] as const;
```

Map backend/display values into the dropdown where straightforward:

- `sample`, `specimen` -> `per sample`
- `reading` -> `per reading`
- `contact` -> `per contact`
- `cycle` -> `per cycle`
- `time` -> `per time`
- `hour` -> `per hour`
- `day` -> `per day`
- `photo` -> `per photo`
- `report` -> `per report`

For `group`, blank, or unknown values, keep the current display text until the operator selects a dropdown option. `per time` maps to canonical `time` and means per occurrence / `每次`; it is not a duration unit and must not be converted to `hour` or `day`.

### Page State

In `FeeEvaluationReviewExportPage.tsx`:

- Add local `previewEdits` state.
- Reset edits when a new draft is loaded for a different project/draft identity.
- Pass edit state and edit callback to `FeeEvaluationPreviewTable`.
- Keep current direct download call unchanged:

```ts
generateConfirmedMatrixFeeFileDownload(projectId)
```

No edited values are sent in TASK_299.

### Table Rendering

In `FeeEvaluationPreviewTable.tsx`:

- Replace text cells with compact controls for editable columns.
- Keep `Testing Fee` as text.
- Keep `Description` inline title/reason behavior.
- Preserve current group filter, Back to Workbench, Fee Form button, header band, and totals layout.

Controls:

- inputs use `inputMode="decimal"` for numeric fields
- discount input can accept `10` or `10%`
- unit type uses a native `select`
- labels should be accessible through `aria-label`, not visible repeated text inside every cell

### Totals

Update total helpers so they consume effective edited row values:

- selected group fee: sum calculated matrix-step rows in the selected group
- all group fee: sum all calculated matrix-step rows
- grand cost: all calculated matrix-step rows + local external cost

If any included row is pending, show `Pending`.

## Test Plan

### Model Tests

Update or add tests in `feeEvaluationPreviewModel.test.ts`:

- calculates `100 * 2 * (1 - 10%) + 5 = 185.00`
- `10` and `10%` are equivalent
- empty discount and base fee default to zero
- invalid unit price/units returns `Pending`
- unit label mapping handles `sample`, `specimen`, `reading`, `time`, `hour`, and unknown values
- selected group fee uses edited values
- grand cost includes external cost and edited row totals

### Page / Component Tests

Update `FeeEvaluationReviewExportPage.test.tsx`:

- editable controls render for required columns
- changing Unit Price/Units/Discount/Base Fee updates Testing Fee
- group filter retains edited values
- Fee Form download still calls `generateConfirmedMatrixFeeFileDownload(projectId)` with no edited payload
- invalid numeric input shows `Pending`
- no Review details panel is reintroduced

### Static Shell Tests

Update `tests/unit/test_frontend_shell_files.py`:

- TASK_299 touches only frontend/UI docs/tests.
- No backend, API client, Excel gateway, or persistence route is introduced.
- Unit type option labels are present in the Fee Evaluation feature.

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

- Risk: editable controls make the dense table noisy.
  - Mitigation: style inputs as compact table cells with clear focus only.
- Risk: users think edits are saved/exported.
  - Mitigation: keep TASK_299 copy/status clear that values are preview-local; do not alter Fee Form endpoint.
- Risk: frontend calculation diverges from future backend/export formula.
  - Mitigation: centralize formula helpers in the feature model and reuse them in TASK_300 planning.
- Risk: `per time` is mistaken for duration.
  - Mitigation: map it to canonical `time`, meaning per occurrence / `每次`; keep duration units as `per hour` or `per day`.

## Stop Point

After implementation and validation, update `docs/task_board.md` to mark TASK_299 complete and stop. Do not implement TASK_300 export-with-edited-values without a separate approved task.
