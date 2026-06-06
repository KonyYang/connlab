# TASK_293 Fee Evaluation Excel Preview UI

Status: Planned; awaiting explicit approval.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_292 is complete. The user approved creating the next controlled plan after reviewing the current `/fee-evaluation` page and the real `Testing Prices` workbook shape.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. The work is a bounded frontend/UI restructuring task with existing typed API data, existing React/Vitest patterns, and no backend schema or Office automation changes. The main risks are UX hierarchy, preserving existing export semantics, and keeping review details available without adding persistent editing. Those are appropriate for GPT-5.3-codex as long as implementation follows the task plan and existing frontend architecture rules.

## Goal

Refocus `/projects/:projectId/fee-evaluation` from a rule-review-first screen into an Excel-preview-first Fee Evaluation surface.

The operator should immediately understand:

- what the generated `Testing Prices` sheet will look like
- whether the fee is confirmed or still pending Excel/manual completion
- what the total fee / working hours / grand cost status is
- where to export the Matrix basic-fill workbook

Review-rule details remain available, but they are secondary to the final-form preview.

## Business Reference

Reference workbook:

```text
C:/Users/White/Desktop/AI information/Fee/DL-2025-11-073 Form for Testing Fee Evaluation.xls
```

Observed `Testing Prices` structure:

- Header identity: `LTR Number`, test description, requestor, site.
- Detail columns:
  - Group
  - Spend Time
  - Description
  - Unit Price
  - Unit type
  - Units
  - Base Fee
  - Price Percent Off
  - Testing Fee
- Group sections: Group 1, Group 2, etc.
- Static/service rows: sample preparation, visual exam, LLCR, environmental/mechanical rows, report preparation where applicable.
- Totals/signature area:
  - Test Fee Total
  - Working hours
  - Lab manpower cost
  - External Cost
  - Grand Cost
  - Prepared by / Approved by

V1 header display must use only data already available to the frontend from current APIs, such as Project/LTR context and fee draft metadata. If requestor, site, or test description are not available in the current API response, show a readable pending/blank state instead of adding backend fields in this task.

## Scope

- Frontend-only UI restructuring of the existing Fee Evaluation route.
- Keep the existing backend fee draft and export APIs unchanged.
- Use the current `FeeEvaluationDraft` response as the source for preview rows.
- Add a preview-first table shaped like `Testing Prices`.
- Keep export action available, but make it support the preview-first workflow.
- Move current rule/review table into a secondary "Review details" surface.
- Preserve existing Matrix basic-fill export behavior:

```text
fill_mode = "matrix_basic"
template_path = D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls
allow_review_required = true
output_dir = latest project folder path
```

## Out Of Scope

- No backend fee calculation changes.
- No persistent fee-line edits.
- No new database tables or migrations.
- No new backend API.
- No rule maintenance UI.
- No Excel COM/template writing changes.
- No Matrix editing changes.
- No StepInstance, execution persistence, report generation, AI review, permissions, or approval package changes.

## Required UI Behavior

### Preview-First Layout

The top of the Fee Evaluation page should show:

- Back to Workbench.
- Project/LTR identity.
- Total status:
  - `Total fee: Pending Excel confirmation` when fee total cannot be trusted.
  - `Total fee: <amount>` when all lines are calculated.
- Working hours status:
  - `Pending` unless deterministic working-hour total is available from draft rows.
- Completion status:
  - `Pricing needs completion` for review-required drafts.
  - `Pricing confirmed` for fully calculated drafts.

### Main Preview Table

Default view should be an Excel-like `Testing Prices Preview`, with columns:

```text
Group | Spend Time | Description | Unit Price | Unit Type | Units | Base Fee | Discount | Testing Fee
```

Display policy:

- `Group`: from `group_label`.
- `Spend Time`: V1 uses `Pending` unless a row spend-time field is exposed by backend in a future task.
- `Description`: from `test_item`.
- `Unit Price`: from `unit_price` or `Pending`.
- `Unit Type`: from `unit_label` / calculation strategy where readable.
- `Units`: from `units` or `Pending`.
- `Base Fee`: from `base_fee` or blank/pending per row.
- `Discount`: from `discount_percent` or blank/pending per row.
- `Testing Fee`: from `testing_fee` or `Pending`.

Rows needing manual review should be visually marked, but review reasons must not dominate the preview table.

### Totals Area

Show a compact totals band below or beside the preview:

- Test Fee Total
- Working hours
- Lab manpower cost
- External Cost
- Grand Cost
- Prepared by
- Approved by

V1 policy:

- Test Fee Total uses `draft.total_fee` only when available; otherwise `Pending Excel confirmation`.
- Working hours remains `Pending`.
- Lab manpower cost / External Cost / Grand Cost remain `Pending`.
- Prepared by / Approved by are shown as export-form fields or preview metadata; only Approved by remains user-entered for export.

### Review Details

Current rule-detail content should move behind a secondary view:

- tab, segmented control, or collapsible section named `Review details`
- keeps filters for all / review required / calculated / no rule match
- keeps group filter and search
- keeps matched rule, matched version, review reason, and warnings

Review details must not be the first or primary visual on page load.

### Export Panel

Export panel should be compact and close to the preview summary:

- primary action: `Generate Excel file`
- uses existing Matrix basic-fill export endpoint
- output directory remains latest project folder
- approved-by and optional file-name fields remain allowed
- if no project folder exists, explain the blocker without asking for arbitrary output directory

## Acceptance Criteria

- Fee Evaluation route opens with a preview-first layout.
- The first full table resembles the attachment's `Testing Prices` fields rather than the current rule-review table.
- The page clearly answers:
- total fee status
  - working-hour status
  - whether pricing is confirmed
  - where to generate the Excel file
- Review count / no-rule / matched-rule details are visible only in secondary review details.
- Export still calls the existing endpoint with `fill_mode="matrix_basic"`.
- No persistent edits are introduced.
- Workbench compact summary remains unchanged except for compatibility with the new page behavior if needed.

## Validation

Expected implementation validation:

```text
cd frontend; npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Browser smoke:

- Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`.
- Confirm the first screen prioritizes final-form preview, total status, and export action.
- Confirm review-rule details are secondary.
