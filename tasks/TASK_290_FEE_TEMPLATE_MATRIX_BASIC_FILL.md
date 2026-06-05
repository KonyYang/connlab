# TASK_290_FEE_TEMPLATE_MATRIX_BASIC_FILL

## Status

Approved for implementation on 2026-06-05.

## Goal

Generate a Matrix basic-fill Fee Evaluation workbook from the active Confirmed Matrix
authority and the formal optimized fee template:

`D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls`

The output workbook fills only the `Testing Prices` sheet structure needed for
manual fee completion:

- Column A: group indication without merged cells.
- Column C: Matrix `Test item` and template static service rows.

## Scope

- Use active Confirmed Matrix authority selected/non-empty cells as the primary
  row source.
- Include malformed-token and no-valid-token Matrix cells in the basic fill.
- Use fee draft only for review warning/traceability support.
- Basic fill must still generate if fee draft metadata cannot be built; draft
  failure becomes a review warning, not an export blocker.
- If Matrix basic fill contains rows not present in fee draft, pricing review
  must be required.
- Require explicit `fill_mode = "matrix_basic"` so TASK_288 default behavior is
  unchanged.
- Keep B/D/E/F/G/H/I detail cells blank for manual completion.
- Preserve totals / Grand Cost area as template-controlled formulas.
- Generate an output copy only; never overwrite the template.

## Out Of Scope

- Automatic fee calculation for D-I detail columns.
- Rule-maintenance UI.
- Frontend export button or independent review page.
- StepInstance, execution persistence, report generation, or Matrix editing changes.
- Replacing the TASK_288 default fee-draft export behavior.

## Acceptance

- A basic-fill export can be generated from a confirmed Matrix even when fee draft
  lines require review or selected Matrix cells have malformed step tokens.
- Empty Matrix cells are not exported as detail rows.
- Each selected group starts with `Sample preparation(if needed)`.
- The group name is written only on the group static service row; A-column group
  region uses alternating background colors and no merged cells.
- C-column detail order matches Confirmed Matrix group/row order.
- `Report preparation` appears after Matrix detail rows and before totals.
- B/D/E/F/G/H/I detail cells remain blank and do not contain copied fee formulas.
- Output record notes clearly state Matrix basic fill only and pricing still
  requires review when applicable.
- Basic-fill output record notes and API line traceability include source
  `cell_value` for each selected Matrix cell.
- Basic-fill note `cell_value` is JSON-encoded so delimiter characters from
  source Matrix cells cannot corrupt the semicolon/comma note format.
- Best-effort fee draft metadata only downgrades known draft/rule-library
  failures to warnings; unexpected programming errors must still raise.
