# TASK_287 Fee Evaluation Review UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for execution tracking.

**Goal:** Add a restrained Project Workbench review surface for the Matrix-derived Fee Evaluation draft produced by TASK_286.

**Architecture:** Frontend-only consumer work. Add typed API client models for the read-only fee draft endpoint, add a compact Workbench fee status summary, add a wider in-Workbench review panel for the multi-column fee table, and reuse the existing project output status summary for `fee_evaluation` freshness. Keep Matrix authority editing in Matrix Editor and keep Excel export out of this task.

**Tech Stack:** React + TypeScript, existing frontend API client, Vitest/Testing Library, existing Workbench CSS and `$impeccable` product UI rules.

---

## Current Task Context

- Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current Active Task dependency: `TASK_286_CONFIRMED_MATRIX_TO_FEE_DRAFT`
- Why this task becomes allowed: TASK_287 can only be implemented after TASK_286 is complete and this plan is explicitly approved.
- Current planning allowance: user explicitly requested a detailed TASK_287 executable plan.
- Implementation gate: do not write implementation code until the user explicitly approves this plan and the task board marks TASK_287 as current/allowed.

## Scope Summary

### In Scope

- Add frontend API client types for `GET /api/projects/{project_id}/confirmed-matrix/fee-draft`.
- Add a Workbench Fee Evaluation review surface in the existing runtime-console visual language.
- Show fee draft header metadata:
  - LTR number when already available in Workbench model.
  - project/sample description from the current Workbench project context.
  - pricing rule version id.
  - pricing effective date.
  - generated timestamp.
- Show grouped fee draft line items:
  - group.
  - Matrix source/test item.
  - matched fee rule and matched rule version id.
  - unit price.
  - units.
  - base fee.
  - discount.
  - calculated fee.
  - review status.
- Highlight review-required rows with concise business-readable reasons.
- Keep any operator edits local to the review surface only.
- Reuse existing `ProjectOutputStatusSummary` / `WorkbenchVersionStatus` for persisted output freshness where available.
- Add frontend tests for loading, no-authority, needs-review, calculated rows, and local-only review edits.

### Out Of Scope

- No Excel export.
- No export button, disabled export control, or future-scope export affordance.
- No persisted edited fee draft.
- No price rule maintenance UI.
- No direct Matrix editing in the fee review surface.
- No backend changes unless TASK_286 response typing mismatch is discovered during implementation.
- No StepInstance, execution persistence, report generation, AI review, or Matrix Editor authority changes.

## Existing Code Fit

Relevant existing files:

- `frontend/src/api/client.ts`
  - Existing API type and request function location.
  - Existing output status types include `fee_evaluation`.
  - Existing Workbench calls already use `getProjectOutputStatusSummary()`.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Current Workbench first screen shell.
  - Right side already contains a compact fee placeholder via `FeeEstimateSurface`.
  - Current CSS uses `grid-template-columns: minmax(0, 1fr) 430px`; that side column is suitable for a summary, not the full review table.
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - Current Matrix projection/test-record controls.
  - This task should not add Excel export here.
- `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`
  - Existing derived-output freshness mapping includes `fee_evaluation`.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - Already loads `latestLtr`, `project`, and `outputStatusSummary`.

## API Contract To Consume

TASK_286 endpoint:

```text
GET /api/projects/{project_id}/confirmed-matrix/fee-draft
```

Status handling:

- `200`: render draft.
- `404`: render no-authority state.
- other errors: render concise load error.

Frontend type additions in `frontend/src/api/client.ts`:

```ts
export type FeeEvaluationDraftStatus = "ready" | "empty" | "needs_review";
export type FeeEvaluationLineStatus =
  | "calculated"
  | "review_required"
  | "no_rule_match";

export type FeeEvaluationWarning = {
  code: string;
  message: string;
  scope: string;
};

export type FeeEvaluationLineItem = {
  line_id: string;
  status: FeeEvaluationLineStatus;
  review_required: boolean;
  review_reason: string | null;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  group_key: string;
  group_label: string;
  confirmed_group_id: string;
  sample_quantity_expression: string;
  confirmed_row_id: string;
  source_row_id: string | null;
  row_order: number;
  test_item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  step_tokens: string[];
  matched_rule_id: string | null;
  matched_rule_version_id: string | null;
  matched_rule_name: string | null;
  match_reason: string;
  calculation_strategy: string | null;
  unit_label: string;
  unit_price: string | null;
  units: string | null;
  base_fee: string | null;
  discount_percent: string | null;
  testing_fee: string | null;
  warnings: FeeEvaluationWarning[];
};

export type FeeEvaluationGroup = {
  group_key: string;
  group_label: string;
  sample_quantity_expression: string;
  line_items: FeeEvaluationLineItem[];
};

export type FeeEvaluationHeader = {
  project_id: string;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  pricing_rule_version_id: string;
  pricing_source_file_name: string;
  pricing_source_hash: string;
  pricing_effective_from: string | null;
  generated_at: string;
};

export type FeeEvaluationDraft = {
  header: FeeEvaluationHeader;
  draft_status: FeeEvaluationDraftStatus;
  total_fee: string | null;
  review_required_count: number;
  groups: FeeEvaluationGroup[];
  warnings: FeeEvaluationWarning[];
};
```

Request helper:

```ts
export function fetchConfirmedMatrixFeeDraft(
  projectId: string
): Promise<FeeEvaluationDraft> {
  return requestJson<FeeEvaluationDraft>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-draft`,
    { cache: "no-store" }
  );
}
```

## UI Placement

Use the existing Workbench shell without creating a new page.

Preferred placement:

- Replace the current right-side fee placeholder (`FeeEstimateSurface`) with a compact `FeeEvaluationStatusSummary`.
- Render the multi-column `FeeEvaluationReviewPanel` as a wider Workbench panel inside the main workspace area, below the Matrix projection or in an expandable main-workspace section.
- Keep the main Matrix projection as the execution authority view.
- Keep Test Record generation in the existing Matrix toolbar.
- No active export button in TASK_287.
- Do not create a new route or separate page.

Reasoning:

- The current right column is fixed at 430px and cannot comfortably hold the required multi-column review table.
- The right column remains useful for status, totals, warning count, stale/missing state, and a review-open summary.
- The main workspace has the width needed for group/test-item/rule/price/units/fee/review columns on 14-inch workstation screens.
- The review surface is a derived-output review, not a Matrix authority surface.
- This avoids reintroducing the removed broad `Derived outputs` board as a large secondary workflow.

## UI State Model

Create a small local component state:

```ts
type FeeEvaluationReviewState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "not_ready" }
  | { kind: "ready"; draft: FeeEvaluationDraft }
  | { kind: "error"; message: string };

type LocalFeeLineOverride = {
  reviewStatus: "pending" | "accepted" | "needs_manual_price";
  units: string;
  baseFee: string;
  discountPercent: string;
};
```

Local edit policy:

- Initialize overrides from the loaded draft values.
- Allow only review-facing local inputs for ambiguous fields.
- Do not call a persistence API.
- Show a compact local-only note when any override differs from the loaded draft.
- Reset overrides when the draft is reloaded.

This satisfies the TASK_287 local edit allowance while preventing hidden draft persistence.

## Display Rules

Header:

- Identity line: LTR if available, otherwise temporary project id.
- Product/sample line: project product name, plus current Matrix source document when available.
- Pricing line: `Rule version <id>` and effective date if present.
- Generated line: concise generated timestamp.

Status summary:

- `missing`: no active confirmed Matrix or no draft available.
- `draft ready`: `draft_status === "ready"`.
- `needs review`: `draft_status === "needs_review"` or any line/root warning exists.
- `stale`: use existing `WorkbenchVersionStatus.downstream` item where `key === "fee_evaluation"` and freshness is `stale`.

Table:

- Rows grouped by fee draft group.
- Keep columns compact and scan-friendly.
- Numeric cells render `-` when null.
- Review-required rows get a restrained warning tone and inline reason.
- Matched rule version id should be visible in a small secondary line under the rule name or in a compact traceability cell.

Business-readable copy:

- Prefer `Needs review`, `No price rule`, `Check quantity`, `Manual price` over backend terms.
- Do not show stack traces, raw JSON, or implementation labels.

## File-Level Changes

### Modify

- `frontend/src/api/client.ts`
  - Add fee draft types.
  - Add `fetchConfirmedMatrixFeeDraft(projectId)`.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Pass `projectId`, `project`, `latestLtr`, `matrixAuthorityDraft`, and the fee output status item to the fee review component.
  - Replace the current fee placeholder with a compact fee summary component.
  - Place the full fee review table in the main workspace so the required columns have enough width.

- `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`
  - No major redesign expected.
  - Add helper only if needed, for example `selectFeeEvaluationStatus(status)`.

- `frontend/src/workbench.css`
  - Add compact review panel/table classes.
  - Keep typography and color consistent with current Workbench.
  - Avoid decorative cards, oversized hero text, gradients, or Excel-like dense editing surfaces.

### Create

- `frontend/src/features/project-workbench/FeeEvaluationReviewPanel.tsx`
  - Component owns fetch state and local-only review overrides.
  - Renders header, grouped table, warnings, and local-only review controls.
  - Does not render export controls, disabled export controls, or future-scope export actions.

- `frontend/src/features/project-workbench/FeeEvaluationStatusSummary.tsx`
  - Compact right-column summary of missing/ready/needs-review/stale status, total when available, warning count, and freshness reason.
  - No export action.

- `frontend/src/features/project-workbench/FeeEvaluationReviewPanel.test.tsx`
  - Component tests with mocked API responses.

## Implementation Tasks

### Task 1: Add API Client Contract

- [ ] Read TASK_286 route response model and verify field names.
- [ ] Add fee draft TypeScript types to `frontend/src/api/client.ts`.
- [ ] Add `fetchConfirmedMatrixFeeDraft(projectId)`.
- [ ] Keep Decimal-like API values as strings.

### Task 2: Build Review Component Skeleton

- [ ] Create `FeeEvaluationReviewPanel.tsx` for the wide main-workspace table.
- [ ] Create `FeeEvaluationStatusSummary.tsx` for the compact right-column status surface.
- [ ] Accept props:

```ts
type FeeEvaluationReviewPanelProps = {
  projectId: string;
  projectLabel: string;
  productName: string;
  latestLtr: string | null;
  matrixSourceName: string | null;
  feeOutputFreshness: "current" | "stale" | "missing" | "manual" | "failed" | null;
  feeOutputReason: string | null;
};
```

- [ ] Load draft on mount and when `projectId` changes.
- [ ] Render loading, no-authority, error, empty, ready, and needs-review states.
- [ ] Ensure the right-column summary never attempts to render the multi-column table.

### Task 3: Render Header And Status Summary

- [ ] Show LTR or temporary project label.
- [ ] Show product/sample description from Workbench props.
- [ ] Show rule version, pricing effective date, generated timestamp.
- [ ] Show fee output freshness from existing output status if available.
- [ ] Ensure stale state uses existing `ProjectOutputRecord` semantics and does not invent a second persistence model.

### Task 4: Render Grouped Review Table

- [ ] Flatten groups for display while keeping group labels visible.
- [ ] Render required columns from the TASK_287 task file.
- [ ] Show `matched_rule_version_id` for traceability.
- [ ] Render review-required reasons from `review_reason`, root warnings, and line warnings.
- [ ] Render `total_fee` only when provided by backend; otherwise show `Review required`.
- [ ] Render this table only in the main-workspace wide panel, not in the 430px side column.

### Task 5: Add Local-Only Review Adjustments

- [ ] Initialize local line overrides from draft values.
- [ ] Add compact controls for review status and ambiguous numeric fields.
- [ ] Keep local state in the component only.
- [ ] Show local-only notice when overrides differ from loaded draft.
- [ ] Do not add Save, Export, or persistence calls.

### Task 6: Wire Into Workbench

- [ ] Replace `FeeEstimateSurface` in `ProjectWorkbenchLayout.tsx` with `FeeEvaluationStatusSummary`.
- [ ] Insert `FeeEvaluationReviewPanel` in the main workspace, below `ProjectWorkbenchMatrixProjectionPanel` or inside a main-workspace expandable section.
- [ ] Derive `feeOutputFreshness` from `versionStatus.downstream.find(item => item.key === "fee_evaluation")`.
- [ ] Preserve existing Matrix projection and Step Workspace behavior.
- [ ] Do not add export buttons or disabled future export controls.

### Task 7: Styling

- [ ] Add Workbench CSS for the panel, compact header facts, warning rows, and horizontal table overflow.
- [ ] Keep table overflow within the wide main workspace, not inside the 430px side column.
- [ ] Ensure text wraps without overlapping.
- [ ] Keep card radius and spacing consistent with existing Workbench surfaces.
- [ ] Avoid decorative visuals and Excel-like freeform grid editing.

### Task 8: Frontend Tests

- [ ] Add tests for loading then ready state.
- [ ] Add test for `404` no active confirmed Matrix.
- [ ] Add test for `needs_review` row reason rendering.
- [ ] Add test for calculated row numeric rendering.
- [ ] Add test that local edits do not call a persistence/export API.
- [ ] Update existing Workbench static tests only if component placement changes expected text.

### Task 9: Validation And Task Closure

- [ ] Run:

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewPanel ProjectWorkbenchMatrixProjectionPanel --watch=false
```

- [ ] Run:

```powershell
cd frontend
npm run build
```

- [ ] Run relevant static guard:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or fee"
```

- [ ] Run:

```powershell
git diff --check
```

- [ ] Update `docs/task_board.md` only after implementation and validation pass.
- [ ] Stop after TASK_287 completion; do not start TASK_288 without explicit approval.

## Risks And Mitigations

- Risk: TASK_286 response changes during implementation.
  - Mitigation: verify backend route model before editing frontend types.
- Risk: Review UI grows into Excel-like editing.
  - Mitigation: local-only adjustments, bounded fields, no grid-wide freeform editing, no persistence.
- Risk: Stale status duplicates output-record logic.
  - Mitigation: reuse `WorkbenchVersionStatus` and `ProjectOutputRecord` summary only.
- Risk: Table becomes too wide.
  - Mitigation: keep table inside controlled horizontal overflow and use secondary lines for traceability.

## Acceptance Mapping

- Workbench derived output visibility: covered by status summary in `FeeEvaluationReviewPanel`.
- Opening review surface fetches draft: covered by component load behavior.
- Calculated and review-required rows: covered by grouped table.
- Concise reasons: covered by row warnings/review reason rendering.
- No export action: enforced by scope and tests.
- Operator-readable copy: enforced by display rules.
- Tests: covered by Task 8.

## Stop Rule

After this plan is approved, implementation still waits until TASK_287 is the current allowed task on `docs/task_board.md`. Completion of TASK_287 must stop before TASK_288.
