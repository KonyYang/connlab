# TASK_293 Fee Evaluation Excel Preview UI Plan

## Execution Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: TASK_293_FEE_EVALUATION_EXCEL_PREVIEW_UI.
- Current status: Planned; awaiting explicit approval.
- Allowed reason: TASK_292 is complete, and the user approved creating this next controlled task/plan after comparing the current Fee Evaluation page with the real Excel fee form.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for executing this plan because TASK_293 is a scoped React/TypeScript UI reshaping task using existing API client data and existing Vitest/static shell test patterns. It does not require backend data modeling, Excel COM changes, or new calculation rules. The model should still follow the plan task-by-task because the UX wording distinction between on-page preview and generated workbook output is important.

## Goal

Reshape the Fee Evaluation route into a preview-first operator surface that answers the user's practical question first: "What will the final Testing Prices sheet look like, and what is still pending before the fee is confirmed?"

The existing rule review table is retained as supporting detail, not the default visual focus.

## Current Reality

Current route:

```text
/projects/:projectId/fee-evaluation
```

Current primary component:

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
```

Current behavior:

- topbar shows project identity and review count
- summary strip shows draft/rule/output metadata
- export panel is prominent
- main table is a rule-review table:
  - group
  - Matrix source
  - matched rule
  - price basis
  - calculated fee
  - status/reason

Observed issue:

- This is useful for debugging/matching, but it does not resemble the actual `Testing Prices` Excel form the user wants to preview.

Reference workbook inspection:

```text
C:/Users/White/Desktop/AI information/Fee/DL-2025-11-073 Form for Testing Fee Evaluation.xls
```

`Testing Prices` expected operator mental model:

```text
LTR / Test Description / Requestor / Site
Group / Spend Time / Description / Unit Price / Unit Type / Units / Base Fee / Discount / Testing Fee
Test Fee Total / Working hours / Lab manpower cost / External Cost / Grand Cost
Prepared by / Approved by
```

V1 header source constraint:

- Use only current frontend-available data: Project, latest LTR, fee draft header, output status, and latest folder.
- Do not add backend fields for requestor/site/test description in TASK_293.
- If a formal Excel header field is unavailable, render a clear pending/blank display in the preview.
- If richer header metadata is required later, open a separate backend/API task.

## Data Design

No backend schema change in TASK_293.

Create frontend-only view models from existing `FeeEvaluationDraft`.

### Preview View Model

```ts
type FeeEvaluationPreviewRow = {
  lineId: string;
  groupLabel: string;
  spendTime: string;
  description: string;
  unitPrice: string;
  unitType: string;
  units: string;
  baseFee: string;
  discount: string;
  testingFee: string;
  status: "confirmed" | "pending";
  reviewReason: string | null;
};
```

V1 mapping:

- `lineId` = `line.line_id`
- `groupLabel` = `line.group_label`
- `spendTime` = `"Pending"`
- `description` = `line.test_item`
- `unitPrice` = `line.unit_price ?? "Pending"`
- `unitType` = `line.unit_label || line.calculation_strategy || "Pending"`
- `units` = `line.units ?? "Pending"`
- `baseFee` = `line.base_fee ?? ""`
- `discount` = `line.discount_percent ? `${line.discount_percent}%` : ""`
- `testingFee` = `line.testing_fee ?? "Pending"`
- `status` = `line.review_required ? "pending" : "confirmed"`
- `reviewReason` = `line.review_reason`

### Totals View Model

```ts
type FeeEvaluationPreviewTotals = {
  testFeeTotal: string;
  workingHours: string;
  labManpowerCost: string;
  externalCost: string;
  grandCost: string;
  preparedBy: string;
  approvedBy: string;
  confirmationLabel: string;
};
```

V1 mapping:

- `testFeeTotal` = `draft.total_fee ?? "Pending Excel confirmation"`
- `workingHours` = `"Pending"`
- `labManpowerCost` = `"Pending"`
- `externalCost` = `"Pending"`
- `grandCost` = `"Pending"`
- `preparedBy` = `"Windows/ConnLab user on export"` or `"Default on export"` as copy, not a persisted value.
- `approvedBy` = current local export field value or `"Pending"`
- `confirmationLabel` = `draft.draft_status === "ready" ? "Pricing confirmed" : "Pricing needs completion"`

## File-Level Plan

### Modify

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
```

Responsibilities after TASK_293:

- keep route-level fetch/export state
- build preview and totals view models
- render preview-first layout
- keep review details as secondary surface
- keep export action wired to existing API

Implementation should split small local components inside the same feature file unless the file becomes too large. If the file approaches 500 lines, split:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx
frontend/src/features/fee-evaluation/FeeEvaluationReviewDetails.tsx
```

Preferred split if implementing cleanly:

- `feeEvaluationPreviewModel.ts`
  - pure selectors/mappers
  - easy unit tests
- `FeeEvaluationPreviewTable.tsx`
  - display-only preview table
- `FeeEvaluationReviewDetails.tsx`
  - current review table/filter UI moved here
- `FeeEvaluationReviewExportPage.tsx`
  - orchestration and page layout

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

Update tests to assert preview-first behavior and preserve export behavior.

```text
frontend/src/workbench.css
```

Add styling for:

- preview summary strip
- Excel-like preview table
- totals band
- secondary review details

```text
tests/unit/test_frontend_shell_files.py
```

Add static assertions for TASK_293:

- preview model/table exists
- preview columns exist
- review details are secondary
- no persistent editing API introduced

### Do Not Modify

```text
backend/**
```

No backend change in TASK_293 unless an implementation blocker proves the current API cannot support preview-only display. If that happens, stop and request a separate backend task.

## Implementation Tasks

### Task 1: Add Preview View Model Tests

Files:

```text
Create: frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
Create or Modify: frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

Steps:

1. Add or update test fixture with:
   - one calculated line
   - one review-required line
   - one no-rule-match line
2. Assert preview rows map to:
   - `Group`
   - `Spend Time`
   - `Description`
   - `Unit Price`
   - `Unit Type`
   - `Units`
   - `Base Fee`
   - `Discount`
   - `Testing Fee`
3. Assert pending values display as `Pending`.
4. Assert `draft.total_fee === null` maps to `Pending Excel confirmation`.

Expected command:

```text
cd frontend; npm test -- --run FeeEvaluation --watch=false
```

Expected first run before implementation:

```text
FAIL, preview model/table not implemented
```

### Task 2: Implement Pure Preview Mappers

Files:

```text
Create: frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
```

Functions:

```ts
export function buildFeeEvaluationPreviewRows(
  draft: FeeEvaluationDraft | null
): FeeEvaluationPreviewRow[]

export function buildFeeEvaluationPreviewTotals(
  draft: FeeEvaluationDraft | null,
  approvedBy: string
): FeeEvaluationPreviewTotals
```

Rules:

- Do not mutate API DTOs.
- Keep all missing monetary values as readable pending labels.
- Keep rule-review reason available on row model, but do not render it as a primary column in preview table.

### Task 3: Build Excel-Like Preview Table

Files:

```text
Create: frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx
Modify: frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
Modify: frontend/src/workbench.css
```

Component signature:

```ts
type FeeEvaluationPreviewTableProps = {
  rows: FeeEvaluationPreviewRow[];
};
```

UI:

- table aria-label: `Testing Prices preview rows`
- columns:

```text
Group | Spend Time | Description | Unit Price | Unit Type | Units | Base Fee | Discount | Testing Fee
```

Visual behavior:

- group labels appear once per group visually if simple to implement; otherwise repeat group label per row for V1 readability.
- pending rows use restrained background tint.
- `Pending` values are visible but not alarmist.
- table is horizontally scrollable on narrow viewport.

### Task 4: Add Totals And Export Summary

Files:

```text
Modify: frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
Modify: frontend/src/workbench.css
```

UI:

- top summary should answer:
  - Total fee
  - Working hours
  - Grand cost
  - Pricing status
- export panel should be compact:
  - `Generate Excel file`
  - output directory
  - approved by
  - file name

Copy:

- `Generate Matrix basic fill` becomes `Generate Excel file`.
- The on-page area is named `Testing Prices preview`.
- Keep technical `Matrix basic fill` out of the primary button label.
- Avoid using `Generate Excel preview` because it sounds like it only refreshes the page preview, while the action actually creates a workbook file.
- Keep blocker copy for missing project folder.

### Task 5: Move Review Table To Secondary Details

Files:

```text
Create: frontend/src/features/fee-evaluation/FeeEvaluationReviewDetails.tsx
Modify: frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
Modify: frontend/src/workbench.css
```

Behavior:

- The current rule review table moves into a secondary section named `Review details`.
- Default expanded/collapsed choice:
  - V1 default can be expanded below the preview for discoverability.
  - It must not appear before the preview table.
- Preserve:
  - All / Review required / Calculated / No rule match filters
  - group filter
  - search
  - matched rule/version
  - review reason/warnings

### Task 6: Update Export Tests

Files:

```text
Modify: frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

Test cases:

- Page renders preview table before review details.
- Preview table shows attachment-like columns.
- Pending line shows `Pending` in unit/fee columns.
- Export button calls existing endpoint with:

```ts
fill_mode: "matrix_basic"
allow_review_required: true
template_path: "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls"
```

- Missing project folder disables export.
- Timeout/detail errors remain actionable.

### Task 7: Static Shell Checks

Files:

```text
Modify: tests/unit/test_frontend_shell_files.py
```

Add assertions:

- `Testing Prices preview rows` exists in fee feature source.
- `Generate Excel file` exists.
- `Review details` exists.
- `Generate Matrix basic fill` is not the primary visible button copy.
- No backend file is required for TASK_293.

### Task 8: Browser Smoke

Manual/browser verification:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation
```

Expected:

- First screen shows final-form preview intent.
- Total status is visible without reading rule rows.
- Preview table resembles `Testing Prices`.
- Review details are secondary.
- Export action remains available or has clear project-folder blocker.

## Validation Commands

Run after implementation:

```text
cd frontend; npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

## Risk Notes

- Current backend draft does not expose spend-time for each line. TASK_293 must display `Pending` instead of inventing values.
- Current backend draft does not expose requestor/site in fee draft header. The page may use available Project/LTR context only; do not add backend fields in this task.
- Preview is not a persisted fee draft editor. Editable UI affordances should be avoided or clearly disabled/read-only.
- Export remains the existing Matrix basic-fill route. TASK_293 changes user-facing copy and layout, not export semantics.

## Self-Review Checklist

- Scope is frontend-only.
- No backend calculation or Excel gateway change.
- Preview columns match the real `Testing Prices` user mental model.
- Review details remain available.
- Export path remains TASK_291/TASK_290 behavior.
- Missing values are shown as pending, not guessed.
- Plan stops after TASK_293 and waits for approval before implementation.
