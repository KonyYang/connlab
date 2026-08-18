# TASK_284_MATRIX_EDITOR_TEST_DAYS_AND_PROJECT_SCHEDULE_PLAN

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Add Matrix Editor planning fields for test duration and project schedule:

1. Insert a `Day` column after `Requirement`.
2. Allow each Matrix row to store a planned test-day expression such as `1`, `0.1`, or `0.5x`.
3. Add a `Test Days` summary row that calculates planned test days per selected group.
4. Add a project schedule card that calculates the planned project cycle from the critical group plus pre-test and post-test buffer days.
5. Add planned date fields used by downstream outputs, including `Date Lab Received Samples` and `Estimated Completion Date`.

This task creates planning data only. It does not create StepInstance, actual execution records, actual report completion tracking, image/evidence persistence, or report generation.

## Business Context

The Matrix is the execution authority map. The lab also needs an estimated project schedule before execution begins.

The planned schedule is used for downstream documents such as application form `SECTION 2`:

- `Date Lab Received Samples`
- `Estimated Completion Date`

These planned values are different from actual execution dates. Future execution/reporting tasks may record actual dates and compare them against the plan, but they must not overwrite the original planned dates.

## Scope

### In Scope

1. Matrix Editor UI:
   - Add `Day` column after `Requirement`.
   - Support numeric values such as `1`, `0.1`, `2.5`.
   - Support multiplier expressions ending in `x`, such as `0.5x`.
   - Add `Test Days` summary row below the Matrix group columns.
   - Add a compact `Project Schedule` planning card.
2. Calculation:
   - Plain numeric `Day` value counts once per selected group when that group has any step token on the row.
   - Multiplier `Day` value counts by step token count in that group cell.
   - Example: row `Day = 0.5x`; group cell `2,7`; result for that row/group is `0.5 * 2 = 1`.
   - Per-group total is the sum of all selected row/group row-day contributions.
   - Critical group is the selected group with the highest planned test days.
   - Total planned project cycle days = pre-test buffer days + critical group test days + post-test buffer days.
   - Calendar-day arithmetic only; V1 does not skip weekends, holidays, or lab blackout dates.
   - Date sufficiency validation uses calendar-day ceiling for decimal planned days. Example: `2.5` planned days requires at least `3` calendar days. `Test Days` summaries still display decimal values.
3. Planned date fields:
   - `sample_received_date`
   - `planned_test_start_date`
   - `planned_test_complete_date`
   - `estimated_completion_date`
   - All four planned date fields use native `<input type="date" />` controls.
4. Date validation:
   - `planned_test_start_date >= sample_received_date + pre_test_buffer_days`
   - `planned_test_complete_date >= planned_test_start_date + critical_group_test_days`
   - `estimated_completion_date >= planned_test_complete_date + post_test_buffer_days`
   - Equivalent total check: `estimated_completion_date >= sample_received_date + total planned project cycle days`
   - Invalid fields are highlighted in red.
5. Persistence:
   - Store row `day_expression` in Project Matrix Draft rows.
   - Store confirmed row `day_expression` in Confirmed Matrix authority rows.
   - Store planning buffer/date fields on Matrix draft root and Confirmed Matrix authority root.
   - Preserve these values across Matrix Editor reload and after `Confirm Matrix`.
   - Implementation must include lightweight existing-SQLite schema upgrade/ensure-column handling for all new nullable columns.
6. Tests:
   - Add backend unit/integration tests for persistence and calculation.
   - Add frontend tests for editing, summary calculation, validation, and reload preservation.

### Out Of Scope

1. No actual execution date tracking.
2. No StepInstance model.
3. No execution data persistence.
4. No image/evidence persistence.
5. No report completion workflow.
6. No Word application form `SECTION 2` writeback in this task.
7. No Test Record or report generation behavior change.
8. No AI/LLM estimation.
9. No fee engine implementation.

## Data Semantics

### Planned Versus Actual

Planned dates are saved with the Matrix authority because they are the pre-execution project plan.

Actual dates are future execution/reporting data. They belong to a later execution/reporting task and must not replace these planned values.

### Day Expression

`day_expression` is an editable string with restricted accepted formats:

- Empty: no planned day contribution.
- Decimal number: `0`, `0.1`, `1`, `2.5`.
- Decimal multiplier: `0.1x`, `0.5x`, `2x`.

Invalid values are highlighted and block `Confirm Matrix`.

Draft save may preserve transient invalid `Day` strings for operator correction. `Confirm Matrix` is the authoritative blocking point and must reject invalid planning fields.

### Buffer Days

`pre_test_buffer_days` and `post_test_buffer_days` are editable decimal-compatible planning fields.

- Empty means `0` during editing and confirming.
- Accepted values are non-negative decimals only, such as `0`, `1`, `1.5`.
- Negative values and non-numeric values are invalid.
- Multiplier suffix `x` is not allowed for buffer fields.
- Invalid buffer values are highlighted red and block `Confirm Matrix`.

Draft save may preserve transient invalid buffer strings for operator correction. `Confirm Matrix` must reject invalid buffer values.

### Information And Sample Rows

`Day` validation and test-day contribution apply only to real Test Item rows.

- Information rows do not contribute to `Test Days`.
- Sample quantity rows do not contribute to `Test Days`.
- Information/sample row `Day` values, if present in transient UI state, are ignored and never block `Confirm Matrix`.

### Step Token Count

For multiplier values, step token count is derived from the selected group cell:

- `2` -> 1 token.
- `2,7` -> 2 tokens.
- `2 7` -> 2 tokens if the existing Matrix token parser treats both as separate steps.
- Empty cell -> 0 tokens.

The implementation must reuse or mirror the existing Matrix Editor step-token parsing behavior so the visual tokens and day calculation agree.

## Acceptance Criteria

1. Matrix Editor shows `Day` immediately after `Requirement`.
2. `Day` accepts decimal numeric values and decimal multiplier values ending with `x`.
3. Invalid `Day` values receive the same visible red invalid style pattern used by existing blocking fields.
4. `Confirm Matrix` is disabled when selected rows contain invalid `Day` values.
5. A bottom `Test Days` row shows each selected group total.
6. `0.5x` with a group cell containing two step tokens contributes `1` day for that row/group.
7. Project schedule card shows:
   - critical group label.
   - critical group planned test days.
   - pre-test buffer days.
   - post-test buffer days.
   - total planned project cycle days.
8. Planned date fields validate chronological order and cycle-length sufficiency.
9. Invalid date fields are highlighted red.
10. The four planned date controls render as native date inputs.
11. Empty buffer days are treated as `0`; invalid buffer values highlight red and block `Confirm Matrix`.
12. Information rows and sample quantity rows never contribute `Day` values and never block confirmation because of `Day`.
13. Draft save/reload preserves `Day`, buffer days, and planned dates.
14. `Confirm Matrix` preserves `Day`, buffer days, and planned dates in Confirmed Matrix authority.
15. Draft save may preserve transient invalid planning strings; Confirm Matrix is the strict validation gate.
16. Decimal planned days use `ceil()` only for date sufficiency validation; visible `Test Days` totals remain decimal.
17. Existing SQLite databases are upgraded or made compatible with all new nullable planning columns.
18. Workbench/preview APIs that return active confirmed Matrix snapshots can expose these planned values for future downstream document tasks.
19. Scope boundary is held: no StepInstance, no actual execution persistence, no Word writeback, no Test Record/report generation change.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded full-stack planning-data feature with clear persistence, calculation, and UI validation rules. It needs careful schema/API/frontend coordination but does not require broad architectural redesign.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before coding and run `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until the task file and plan are reviewed and explicitly approved by the user.
