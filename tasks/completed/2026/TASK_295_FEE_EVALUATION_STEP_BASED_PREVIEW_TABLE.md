# TASK_295 Fee Evaluation Step-Based Preview Table

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_294 is complete. The user reviewed the Fee Evaluation page and requested the preview table to match the real Fee Evaluation workflow more closely: show group steps like Test Record, include fixed trailing cost rows, and make Grand Cost / Lab manpower cost risk visible.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. The work is a bounded frontend preview-model and UI refinement using existing Fee Evaluation draft data (`groups`, `line_items`, `step_tokens`, fee fields) and existing React/CSS patterns. The main risks are scope creep into backend fee-rule calculation or Excel COM export behavior. Those are explicitly out of scope for TASK_295, so GPT-5.3-codex is appropriate if it follows the executable plan and stops after the preview-only implementation.

## Goal

Make `/projects/:projectId/fee-evaluation` preview the Fee Evaluation sheet in the way project managers expect:

- show fee rows by Matrix group step, not only by unique-looking test item rows
- allow repeated test items when multiple groups/steps require the same test item
- make group boundaries visually clear
- append fixed trailing rows for manual fee completion
- surface Grand Cost as the customer-facing total, while allowing a local preview-only Lab manpower cost comparison that warns project managers when Lab manpower cost exceeds Grand Cost

## Business Reason

The current table is too close to an internal fee-rule draft. Users need to preview the shape of the official fee form:

```text
Group / step-oriented rows first, then manual completion rows and cost totals.
```

Customers mainly care about `Grand Cost`. Project managers also care about `Lab manpower cost`; if Lab manpower cost is greater than Grand Cost, the project is likely losing money and should be visibly flagged.

TASK_295 V1 does not have backend-calculated or Excel-synchronized values for these totals. To make the warning real without crossing backend/export scope, the Fee Evaluation page may provide local preview-only numeric fields for `Grand Cost` and `Lab manpower cost`. These values are not persisted, not exported, and not used as official pricing authority.

## Scope

### Frontend Preview Model

- Change the Fee Evaluation preview row model from line-item-only display to step-based display.
- For each `FeeEvaluationLineItem`:
  - if `step_tokens` is non-empty, create one preview row per step token
  - if `step_tokens` is empty, keep one fallback row so no source row disappears
  - keep the same group, fee, matched status, and review reason data on the expanded step rows
- Add a `stepToken` / step display field to the preview row type.
- Preserve repeated test items when they are present in multiple groups or steps.
- Append fixed manual rows at the end of the preview table:
  - `Report preparation`
  - `Condition confirmation`
  - `External Cost (tooling / purchase cost)`
- Mark fixed manual rows as pending/manual completion rows.

### Frontend Table UI

- Add or display a Step column so users can see which group step each row represents.
- Keep the `Group` column horizontally centered.
- Make `Group` boundaries easier to scan by alternating group background colors.
- Reduce the `Description` column width so the table resembles the formal fee template more closely.
- Keep the `Fee Form` direct-download action from TASK_294 unchanged.

### Totals / Risk UI

- Treat `Grand Cost` as the customer-facing total in the totals area.
- Keep `Lab manpower cost` visible for project managers.
- Provide local preview-only numeric entry/display for `Grand Cost` and `Lab manpower cost` so the warning can trigger on the page.
- Add a loss warning when both values are numeric and:

```text
Lab manpower cost > Grand Cost
```

- If either value is pending/non-numeric, do not show the loss warning.
- Keep `External Cost` visible as an independent manual row at the end of the table. V1 should not add a separate header/totals `External Cost` metric unless later UX review approves it.

## Out Of Scope

- No backend fee-rule changes.
- No backend API schema change. If implementation finds required data is missing, stop and propose a follow-up task instead of extending the API inside TASK_295.
- No Excel COM gateway change.
- No generated workbook layout/writeback change.
- No persistent fee-line edits.
- No new database tables or migrations.
- No rule-maintenance UI.
- No StepInstance, execution persistence, report expansion, AI review, permissions, or multi-user workflow.
- No automatic calculation of `External Cost`, tooling purchase cost, Lab manpower cost, or Grand Cost.
- No persistence or export of local preview-only `Grand Cost` / `Lab manpower cost` inputs.

## Required Behavior

### Step-Based Rows

Example:

If one draft line has:

```text
group_label = "1"
test_item = "Contact Resistance (Low Level)"
step_tokens = ["1", "2"]
```

The preview should render two rows:

```text
Group  Step  Description
1      1     Contact Resistance (Low Level)
1      2     Contact Resistance (Low Level)
```

This repetition is intentional. The preview is a fee form workflow view, not a de-duplicated test-item summary.

### Fixed Trailing Rows

The end of the table must include:

```text
Report preparation
Condition confirmation
External Cost (tooling / purchase cost)
```

These rows should be visibly part of the fee form preview and remain pending/manual for V1.

### Group Visuals

- `Group` column values should be centered.
- Rows belonging to adjacent groups should use alternating subtle backgrounds.
- Fixed trailing rows should use a distinct but restrained manual-row style.
- Description column should be narrower than the current wide layout.

### Cost Risk

- `Grand Cost` remains visible as the main total label.
- `Lab manpower cost` remains visible.
- The page may let the operator type temporary local numeric values for `Grand Cost` and `Lab manpower cost` to preview loss risk before completing the official Excel fee form.
- These temporary values must be clearly treated as preview-only and must reset on page reload.
- When both parse as numeric values and `Lab manpower cost > Grand Cost`, show a business-readable warning:

```text
Lab manpower cost exceeds Grand Cost. Review pricing before sending the fee form.
```

## Acceptance Criteria

- Fee preview rows are generated by group step, so repeated test items are allowed and expected.
- Rows with multiple `step_tokens` render one row per step.
- Rows with no `step_tokens` still render one fallback row.
- `Report preparation`, `Condition confirmation`, and `External Cost (tooling / purchase cost)` appear at the end of the preview table.
- `Group` cells are horizontally centered.
- Adjacent group blocks are visually distinguishable with alternating group colors.
- `Description` column is narrower than the current preview layout.
- `Grand Cost` is presented as the customer-facing total.
- A loss warning appears only when local preview numeric `Lab manpower cost > Grand Cost`.
- No backend fee calculation, Excel export, database, Matrix editing, StepInstance, or report generation behavior changes.
- Existing `Fee Form` direct-download behavior remains unchanged.

## Validation

Expected implementation validation:

```text
cd frontend; npm test -- --run feeEvaluationPreviewModel FeeEvaluationReviewExportPage --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Browser smoke:

- Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`.
- Confirm preview table shows group/step rows and allows repeated test items.
- Confirm fixed trailing rows are visible at the end.
- Confirm group colors alternate.
- Confirm `Group` column is centered.
- Confirm `Grand Cost` and `Lab manpower cost` are visible and warning behavior is understandable.
