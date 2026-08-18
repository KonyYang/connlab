# TASK_299 Fee Editable Pricing Preview UI

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_298 is complete. The approved TASK_298-TASK_302 series defines TASK_299 as the next controlled step: frontend local editing and real-time fee calculation before export-with-edited-values or persistence.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. TASK_299 is a bounded React/TypeScript product UI task with deterministic local calculation rules, existing typed fee draft input, and focused component/model tests. It is not suitable for making pricing-policy judgments; uncertain values should remain editable/pending until the operator enters numeric values.

## Goal

Make the Fee Evaluation preview table locally editable so the operator can enter fee inputs and immediately see calculated `Testing Fee` and totals before generating a later Fee Form task.

TASK_299 is local UI only. Edits are not persisted and are not sent to the current Fee Form download endpoint.

## Scope

### In Scope

- Fee Evaluation page preview table.
- Local in-memory edit state for fee preview rows.
- Editable cells for:
  - `Spend Time`
  - `Unit Price`
  - `Unit Type`
  - `Units`
  - `Base Fee`
  - `Discount`
- Read-only calculated `Testing Fee`.
- Updated selected group fee / Grand Cost preview using local calculated values.
- Frontend model tests and page tests.
- Task-board update after implementation.

### Out Of Scope

- Backend API/schema changes.
- Exporting edited values into the Fee Form.
- Persisting or reloading fee edits.
- Database migration.
- Rule-maintenance UI.
- New fee rule extraction/update workflow.
- Excel COM gateway changes.
- Matrix Editor changes.
- StepInstance, execution persistence, report generation, AI review, permissions, or multi-user workflow.

## Required Behavior

### Editable Table Columns

The visible preview table remains:

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

Editable fields:

- `Spend Time`: text/decimal input. It does not affect TASK_299 fee calculation.
- `Unit Price`: decimal input.
- `Unit Type`: select input.
- `Units`: decimal input.
- `Base Fee`: decimal input.
- `Discount`: percent input.

Read-only field:

- `Testing Fee`: calculated display.

### Unit Type Options

The `Unit Type` dropdown options are:

```text
per sample
per reading
per contact
per cycle
per time
per hour
per day
per photo
per report
```

V1 display mapping:

- Existing backend `sample` -> `per sample`
- `reading` -> `per reading`
- `contact` -> `per contact`
- `cycle` -> `per cycle`
- `time` -> `per time`
- `hour` -> `per hour`
- `day` -> `per day`
- `photo` -> `per photo`
- `report` -> `per report`
- `specimen` may display as `per sample` for operator familiarity unless the executable plan chooses a visible fallback.
- `group`, blank, or unknown values default to the first option only if the operator edits the cell; otherwise keep the loaded display value/pending state.

`per time` maps to canonical `time` and means per occurrence / `每次`. It is not a duration unit and must not be converted to `per hour`, `per day`, or `manual_required` solely because it says `time`.

### Calculation Rule

For each row:

```text
Testing Fee = Unit Price * Units * (1 - Discount) + Base Fee
```

Parsing rules:

- Empty `Base Fee` is treated as `0` when `Unit Price` and `Units` are numeric.
- Empty `Discount` is treated as `0%`.
- `10` and `10%` both mean 10%.
- Invalid, blank required numeric fields, or non-numeric values display `Pending`.
- Calculated values display with two decimals.

### Local State

- Edits are local to the current page session.
- Edits survive group filter changes.
- Edits reset when the fee draft is reloaded, the project changes, or the page is refreshed.
- The current `Fee Form` download button remains available but still calls the existing direct download endpoint without edited values.
- The UI should not imply that edited preview values are saved or exported in TASK_299.

### Totals

- The selected group fee uses the visible/local calculated `Testing Fee` values.
- `Grand Cost` uses all local calculated matrix-step `Testing Fee` values plus local `External Cost`.
- If any required row in the selected scope cannot be calculated, the scope fee and Grand Cost remain `Pending`.
- Existing `Lab manpower cost > Grand Cost` warning remains based on local preview values when both are numeric.

## UX / Design Requirements

- Keep ConnLab dense and operator-focused; no new modal as the primary workflow.
- Inputs should feel like table cells, not large form controls.
- Preserve table scanability:
  - centered compact `Group` and `Step`
  - readable `Description`
  - numeric columns compact and aligned
  - focus states visible
- Do not add instructional copy inside the table. Use concise status text only when needed to avoid misleading the operator.

## Acceptance Criteria

- Fee preview table renders editable inputs/selects for the six editable fields.
- `Testing Fee` updates immediately when `Unit Price`, `Units`, `Base Fee`, or `Discount` changes.
- `10` and `10%` both calculate as 10%.
- Empty discount and empty base fee behave as 0 where the row is otherwise calculable.
- Invalid numeric input leaves row testing fee as `Pending`.
- Group filter retains local edits.
- Selected group fee and Grand Cost reflect local calculations.
- Existing Fee Form download does not receive edited values in TASK_299.
- No backend/API/Excel/persistence code changes.

## Validation Plan

Implementation validation:

```powershell
cd frontend
npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Browser smoke on `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation` confirmed 85 preview rows, 425 editable inputs, 85 Unit Type selects, no review-details surface, and a sample row calculation of `10 * 3 * (1 - 10%) + 2 = 29.00`.

## Stop Point

After implementation and validation, update `docs/task_board.md` and stop. Do not proceed to TASK_300 export-with-edited-values without a separate approved task.
