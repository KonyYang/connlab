# TASK_355C Fee Evaluation Update Fee Validation UX Plan

> Status: complete after user approval on 2026-07-07.

## Anti-Skip Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT`, complete/accepted by Integrator
- Why this plan is allowed now: the user reported a release Fee Evaluation UX defect on the local browser release and explicitly approved generating a `TASK_355C` plan MD. This is a proposed hotfix plan only; it does not start implementation, update the board, or change product code.

## Discovery Gate

### User Goal Restatement

The Fee Evaluation page currently allows an operator to reach `Update Fee` with an incomplete final `Report preparation` row. The backend then reports a technical message such as `testing_fee_total must be numeric` or `Saved Fee Evaluation pricing draft totals are incomplete.`, which does not tell the operator which row or field is missing. The same error can also appear in two places at once, once near the header controls and once as a full-width alert above the totals/table. The desired improvement is to show a clear, row-level blocker before confirmation and remove duplicate alert rendering.

### Evidence Read

- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `$impeccable` product UI guidance via `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- `backend/application/confirmed_fee_version_service.py`
- `backend/api/routes_confirmed_fee_version.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`

### Confirmed By User

- The observed `testing_fee_total must be numeric` case was caused by the final report row missing data.
- The current UI is hard for operators to understand because the error does not identify the row.
- The same error appears in two places in the screenshot and should be optimized.

### Confirmed By Repository Evidence

- `FeeEvaluationReviewExportPage.handleConfirmFee()` sends `allPreviewTotal`, `allWorkingHoursLabel`, `allLabManpowerCostLabel`, `externalCost`, and `allGrandCostLabel` to `confirmFeeVersion()`.
- `feeEvaluationPreviewModel.buildFeeEvaluationPreviewScopeTotal()` returns `Pending` when any scoped row `testingFee` is non-numeric.
- `ConfirmedFeeVersionService._validate_summary()` rejects non-numeric `testing_fee_total`, `working_hours`, `lab_manpower_cost`, `external_cost`, and `grand_cost`.
- `FeeEvaluationPreviewTable` renders `FeePricingDraftSaveStatus` inside the preview header and also renders `confirmFeeActionState.kind === "error"` as a separate full-width alert below the header, allowing duplicated or competing alerts.
- The current `ReviewCue` can show backend fee-rule review reasons, but it does not describe frontend completion blockers such as "Report preparation fee fields are incomplete before Update Fee."

### Inferred By Planner

- The UX should block `Update Fee` before the API call when confirmation totals are not numeric.
- The operator needs a business-readable row label such as group, step, and description, not a raw API field such as `testing_fee_total`.
- The implementation should prefer a feature-level selector/model helper so the button blocker, banner copy, row cue, and tests use one validation source.

### Not Yet Confirmed

- Exact final English copy can be adjusted during implementation review.
- Whether the first invalid row should be auto-scrolled into view is useful but not necessary for the first hotfix.

### Continue Decision

Continue with a proposed plan because the user goal, code evidence, task boundary, and validation path are sufficient. Keep the lane proposed/planned until the user explicitly approves implementation.

## Root Cause Summary

The release error is not a Fee Form template or subprocess issue. It happens on `Update Fee` confirmation:

1. The page derives `testingFee` for each row from editable price fields.
2. If a row such as `Report preparation` still has incomplete price data, its derived `testingFee` becomes `Pending`.
3. The page-level total becomes `Pending`.
4. `Update Fee` posts `summary.testing_fee_total = "Pending"` to the Confirmed Fee API.
5. The backend correctly rejects it as non-numeric, but the UI displays a technical summary error instead of identifying the incomplete row.

The duplicate alert happens because save-state errors and confirm-action errors are rendered in separate locations without a single page-level display policy.

## Goal

Improve the Fee Evaluation `Update Fee` validation UX so operators can see exactly which row blocks confirmation and fix it without interpreting backend field names.

## Non-Goals

- No Fee default-fill rule changes.
- No pricing formula changes.
- No workbook template or Fee Form generation changes.
- No Confirmed Fee authority semantics changes.
- No backend persistence schema changes.
- No Matrix parsing, Matrix authority, Test Record, Report, StepInstance, AI, LAN/server, permissions, or multi-user work.
- No broad redesign of the Fee Evaluation page.
- No cleanup of unrelated dirty files or completed task residuals.

## Proposed UX

### 1. Pre-confirm blocker before API call

Before calling `confirmFeeVersion()`, derive update blockers from the current preview rows and cost summary fields.

Suggested primary blocker copy:

```text
Complete Fee Evaluation pricing before Update Fee. First blocker: Report preparation has incomplete Testing Fee.
```

When a group and step are available:

```text
Complete Fee Evaluation pricing before Update Fee. First blocker: Group H, Step 3, Contact Resistance, Low Level (LLCR) has incomplete Unit Price.
```

For the manual report row:

```text
Complete Fee Evaluation pricing before Update Fee. First blocker: Report preparation has incomplete fee fields.
```

### 2. Row-level review cue

Rows blocking `Update Fee` should receive a visible review cue in the Description cell, reusing the existing `ReviewCue` pattern:

```text
Review: Complete fee fields before Update Fee.
```

If a more specific field is known:

```text
Review: Complete Unit Price, Unit Type, and Units before Update Fee.
```

### 3. Disable Update Fee while blockers exist

The footer should show the blocker message and disable `Update Fee` while confirmation totals are incomplete. This prevents the backend-only `testing_fee_total must be numeric` path in normal use.

### 4. Single alert display policy

Do not show the same confirmation/save error both inside the preview header and as a full-width alert. For this task:

- Keep the full-width alert near the editable table for blocking `Update Fee` issues.
- Keep header-adjacent status for Fee Form download success/error and non-blocking save state only when it is not duplicated by the confirm blocker.
- If the same message would appear in both `saveState` and `confirmFeeActionState`, render it once.

## Design And File-Level Plan

### 1. Add confirmation validation model helper

Modify:

```text
frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts
```

Add types and helper functions, for example:

```ts
export type FeeEvaluationUpdateBlocker = {
  rowId: string | null;
  rowLabel: string;
  fields: string[];
  message: string;
};

export function buildFeeEvaluationUpdateBlockers(input: {
  rows: FeeEvaluationPreviewRow[];
  totals: {
    testingFeeTotal: string;
    workingHours: string;
    labManpowerCost: string;
    externalCost: string;
    grandCost: string;
  };
}): FeeEvaluationUpdateBlocker[];
```

Validation rules:

- Treat empty strings, `Pending`, `NaN`, non-finite numbers, and non-numeric values as blocking for numeric fee fields only.
- Validate row fields that affect confirmation:
  - `spendTime`
  - `unitPrice`
  - `unitType`
  - `units`
  - `baseFee`
  - `discount`
  - derived `testingFee`
- `unitType` is a label field, not a numeric field. It is valid when it is non-empty and not `Pending`; standard values should come from `FEE_UNIT_TYPE_OPTIONS`.
- `discount` must use the existing editable discount semantics and allow valid percentage strings such as `0%` and `100%`.
- Validate page-level summary values:
  - `testingFeeTotal`
  - `workingHours`
  - `labManpowerCost`
  - `externalCost`
  - `grandCost`
- `Notes` is not a blocker.
- The first blocker should be deterministic, table order first, then summary fields.

### 2. Wire blocker into Fee page state

Modify:

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
```

Proposed behavior:

- Build `updateFeeBlockers` from `allPreviewRows`, `allPreviewTotal`, `allWorkingHoursLabel`, `allLabManpowerCostLabel`, `externalCost`, and `allGrandCostLabel`.
- Extend `confirmFeeBlocker()` input or wrap it so row-level blockers take priority after loading/save state is ready.
- In `handleConfirmFee()`, if blockers exist, set a business-readable confirm action error and return before calling `confirmFeeVersion()`.
- Preserve lifecycle read-only, stale saved draft, saving, dirty, and missing draft blockers.

### 3. Pass row blocker metadata to table

Modify:

```text
frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx
```

Possible minimal API:

```ts
updateFeeBlockersByRowId?: Record<string, FeeEvaluationUpdateBlocker>;
primaryUpdateFeeBlockerMessage?: string | null;
```

Behavior:

- `ReviewCue` should show existing fee-rule review metadata plus update blocker text when present.
- Avoid rendering duplicate messages if the same text is already shown in the page-level alert.
- Add a row class such as `fee-evaluation-preview-row-blocked` only if needed for subtle highlighting.

### 4. Adjust error rendering policy

Modify:

```text
frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx
frontend/src/styles.css or relevant fee-evaluation CSS file
```

Behavior:

- Show one primary blocking alert for `Update Fee` validation.
- Do not render `FeePricingDraftSaveStatus` as a duplicate when its message matches `confirmFeeActionState.message`.
- Keep styling restrained and aligned with ConnLab design: light warning/error surface, clear text, no decorative side-stripe or heavy color.

### 5. Optional backend copy fallback

Modify only if needed:

```text
frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx
```

Map backend technical errors to business-readable copy:

- `testing_fee_total must be numeric.`
- `working_hours must be numeric.`
- `lab_manpower_cost must be numeric.`
- `grand_cost must be numeric.`
- `Saved Fee Evaluation pricing draft totals are incomplete.`

Suggested fallback:

```text
Fee Evaluation pricing is incomplete. Review highlighted rows before Update Fee.
```

Do not change backend validation semantics in this task unless implementation discovery proves a typed error code is required.

## May Touch

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
- Fee Evaluation CSS used by these components, if a row highlight or alert adjustment is needed

## Must Not Touch

- Fee default-fill rule data or pricing seed JSON
- Backend Fee default-fill services
- Excel workbook template writers/export child/subprocess code
- Template folder resolver from `TASK_355A`
- Packaged Fee export child entry from `TASK_355B`
- Confirmed Matrix authority, Matrix parser/import, Test Record, Report, Folder Actions, Project lifecycle state, LTR workbook authority
- Real user workbooks/folders
- `.agents/**`
- `docs/project_management/**`
- Unrelated dirty files

## Acceptance Criteria

1. When the final `Report preparation` row has incomplete fee data, `Update Fee` is disabled or blocked before the API call.
2. The page tells the operator that `Report preparation` is the blocking row.
3. At least one row-level cue appears on the blocking row.
4. The backend technical message `testing_fee_total must be numeric.` is not exposed as the primary operator-facing guidance in the normal incomplete-row path.
5. The same blocking message is not rendered twice in the header area and full-width alert area.
6. Existing valid Fee Evaluation confirmation flows still call `confirmFeeVersion()` with numeric totals.
7. Fee Form generation remains unchanged.

## Validation Plan

Focused frontend tests:

```powershell
npm test -- --run frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

Suggested new/updated test cases:

- Incomplete `Report preparation` row blocks `Update Fee` and names the row.
- The API `confirmFeeVersion()` is not called when `testing_fee_total` would be `Pending`.
- Existing valid promoted/default draft can still update Fee.
- Duplicate save/confirm error text is rendered only once.
- Backend numeric-summary errors are mapped to business-readable copy if they still occur.

Build check:

```powershell
npm run build
```

Manual smoke:

1. Open `http://127.0.0.1:8765/projects/05572089fbf54174a1c2fec572e133b1/fee-evaluation` after rebuilding/restarting the release.
2. Leave the final `Report preparation` row incomplete.
3. Confirm the footer/banner names the row and `Update Fee` does not proceed.
4. Fill the missing report row fields.
5. Confirm `Update Fee` can proceed without duplicate alerts.

## Risks

- If validation is too strict, it may block rows that intentionally have zero price and 100% discount. The helper must allow valid numeric zero values.
- If the page has group filtering active, the blocker should still validate all rows, not only the selected group.
- If a saved draft is stale or currently saving, those state blockers should still take priority over row-level validation.
- If implementation tries to solve this through backend-only copy changes, the operator will still lack row-level guidance.

## Approval Gate

Implementation must wait for explicit user approval, for example:

```text
同意按 TASK_355C 方案实施
```

After approval, the Developer should implement only this task, run the focused validation, and update `docs/task_board.md` only at completion or as directed by the Integrator/Planner lane process.

## Completion Summary

Implementation was approved by the user with:

```text
请对两点进行修改
```

Completed changes:

- Added frontend-owned `Update Fee` blockers that validate all Fee Evaluation rows before confirmation.
- The first incomplete row is named in the footer blocker message.
- Blocking rows show a `Review:` cue in the description cell and receive a subtle blocked-row highlight.
- Duplicate save/confirm error text is suppressed when both channels would show the same message.
- Technical numeric summary errors are mapped to business-readable copy if they still reach the confirm path.

Validation:

```powershell
npm test -- --run src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

Result:

```text
2 passed, 50 tests passed
```

```powershell
npm run build
```

Result:

```text
passed, with existing Vite chunk-size warning only
```
