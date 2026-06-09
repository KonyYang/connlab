# TASK_305 Fee Evaluation Preview / Export Parity Hardening

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_298 through TASK_302 are complete, and the Fee Evaluation page/export flow has received multiple post-task usability and workbook-parity refinements. The current task board has no active implementation task and requires an explicit task file/plan review before the next implementation task.

TASK_305 was approved for implementation and completed on 2026-06-09.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because the work is a bounded parity-hardening pass across existing deterministic frontend preview models, existing edited-value export payloads, and the existing Excel gateway. It is suitable for comparing rendered preview rows against generated workbook rows, adding regression tests, and tightening traceability/validation around known anchors. It is not suitable in this task for inventing new pricing policy, changing fee-rule source data, adding AI pricing judgement, creating a rule-maintenance UI, or redesigning the Project Workbench beyond the existing Fee Evaluation preview/export surface.

## Goal

Make the Fee Evaluation webpage preview and generated Fee Form workbook behave as one coherent operator surface:

- What the operator sees in the `Fee Evaluation` preview should map predictably to the generated `Testing Prices` sheet.
- Manual/static rows such as `Sample preparation`, `Report preparation`, `Condition confirmation`, and `External Cost` should have explicit parity rules.
- Row notes and External Cost notes should have clear comment-export behavior.
- Any remaining gaps between preview and export should be documented as intentional V1 limits rather than accidental divergence.

## Input Data

Inputs:

- Active Confirmed Matrix authority for the project.
- Current Fee Evaluation draft from TASK_286.
- Local Fee Evaluation preview edits from TASK_299.
- Saved pricing draft data from TASK_301, when present.
- Existing TASK_300 direct-download edited export payload.
- Formal optimized workbook template:
  - `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls`

The template path is a current business baseline for verification and manual smoke only. Production code must continue to use the existing configured/requested template path and must not introduce a new hardcoded absolute dependency.

## Output Data

Outputs:

- Hardened frontend preview rows and edit payload behavior where needed.
- Hardened Excel gateway behavior where needed.
- Regression tests proving preview/export parity for the defined V1 rows and columns.
- Browser/manual smoke checklist for the Fee Evaluation page.
- Workbook smoke checklist for generated `Testing Prices`.
- Updated `docs/task_board.md` completion notes after implementation.

## Scope

In scope:

- Verify and harden parity for:
  - Matrix step rows
  - per-group `Sample preparation`
  - trailing `Report preparation`
  - `Condition confirmation`
  - `External Cost`
  - `Grand Cost`
  - row `Notes`
  - `External Cost note`
- Ensure webpage preview shows one `Sample preparation` row per group with `Step=0`.
- Ensure generated Fee Form shows per-group `Sample preparation` rows with the same default editable-column initial values as ordinary preview/test-item rows:
  - Man-hour / Spend Time: `0`
  - Unit Price: `0`
  - Unit Type: `per sample`
  - Units: `1`
  - Base Fee: `0`
  - Discount: `0`
  - Testing Fee: formula-backed result
- Treat `Sample preparation` as a real editable row in TASK_305 V1, not as display-only text.
- Add a stable Sample preparation row identity that can round-trip through:
  - frontend preview edits
  - TASK_300 direct-download edited export payload
  - TASK_301 pricing draft save/load
  - Fee Form workbook writing
- Ensure non-empty row Notes export as Excel comments on the corresponding row `Testing Fee` cell.
- Ensure non-empty External Cost note exports as an Excel comment on the `External Cost` amount cell in column D.
- Ensure External Cost amount is written only to the stable External Cost amount cell and does not overwrite the formula-driven I column.
- Ensure preview totals and selected-group totals remain business-readable and consistent with local editable preview values.
- Add regression tests around the exact parity behavior above.

Out of scope:

- No new fee-rule matching policy.
- No automatic pricing inference beyond existing fee-rule/default behavior.
- No new Unit Price Reference refresh workflow.
- No new frontend rule-maintenance UI.
- No database migration.
- No StepInstance, execution persistence, report generation, AI review, permissions, or LAN/multi-user scope.
- No automatic save/autosave changes.
- No broad redesign of the Fee Evaluation page outside parity fixes.
- No replacement of the Excel COM gateway or new workbook-writer dependency.

## V1 Parity Rules

### Matrix Step Rows

- Preview rows are expanded by Matrix step order.
- Editable columns remain:
  - Man-hour
  - Unit Price
  - Unit Type
  - Units
  - Base Fee
  - Discount
  - Notes
- Testing Fee remains read-only and formula-derived in the UI.
- Export writes edited values into the corresponding workbook detail row and keeps/restores the Testing Fee formula where supported.
- Non-empty row Notes become comments on the Testing Fee cell.

### Sample Preparation Rows

- Preview inserts one `Sample preparation` row at the start of every group.
- `Step` is `0`.
- The row uses the same group label and group tone as its group.
- V1 default values are:
  - Man-hour: `0`
  - Unit Price: `0`
  - Unit Type: `per sample`
  - Units: `1`
  - Base Fee: `0`
  - Discount: `0`
  - Testing Fee: `0` in preview and formula-backed in export.
- V1 contract decision: `Sample preparation` is editable, saveable, reloadable, and exportable.
- Sample preparation identity must be stable per active Confirmed Matrix group and fee rule version.
- The identity must not collide with Matrix step rows or `Report preparation`.
- Direct-download payload must carry Sample preparation edits explicitly; do not hide them inside ordinary Matrix step rows.
- Saved pricing draft load must rehydrate Sample preparation edits only when the current Confirmed Matrix id/revision and fee rule version match.

### Report Preparation

- Remains a trailing editable/manual row in preview.
- Export continues to use the existing `manual_rows.row_kind = "report_preparation"` contract.
- Non-empty notes export as a Testing Fee cell comment.

### Condition Confirmation

- Remains outside the detail table.
- Preview/edit field represents spend time only.
- Export writes it to the stable Condition confirmation spend-time cell.
- It does not create a Testing Fee row.

### External Cost

- Remains outside the detail table.
- Preview/edit field represents amount.
- External Cost note is independent from row Notes.
- Export writes amount to the stable External Cost amount cell in column D.
- Export writes non-empty External Cost note as a comment on that same column D cell.
- Export does not write External Cost amount into column I because the template uses formulas there.

## Acceptance Criteria

- Fee Evaluation webpage preview contains exactly one `Sample preparation` row per displayed Matrix group.
- Each Sample preparation preview row appears before the group step rows and shows `Step=0`.
- Sample preparation row edits for Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, and Notes are included in the direct-download edited export payload.
- Sample preparation row edits are saved through TASK_301 pricing draft persistence and rehydrated after page reload when the draft is current.
- Stale saved Sample preparation edits are not applied when Confirmed Matrix id/revision or fee rule version changes.
- Generated Fee Form contains Sample preparation rows with default B/D/E/F/G/H values aligned with ordinary preview defaults.
- Generated Fee Form applies edited Sample preparation B/D/E/F/G/H values when present.
- Generated Fee Form keeps Testing Fee formulas for Sample preparation and Matrix detail rows.
- Non-empty row Notes are exported as comments on row Testing Fee cells.
- Non-empty External Cost note is exported as a comment on the External Cost amount cell in column D.
- Empty Notes and empty External Cost note do not create comments.
- External Cost export does not overwrite formula-driven I-column content.
- Selected group totals and bottom summary totals remain based on current local preview values.
- Existing TASK_299/TASK_300/TASK_301/TASK_302 tests remain passing.

## Validation

Expected implementation validation:

- `cd frontend; npm test -- --run FeeEvaluation --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py -q`
- `py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/integration/test_confirmed_matrix_fee_file_download_api.py -q`
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"`
- Real-template Excel smoke, if run, must use the existing timeout-protected production export path or the TASK_290A subprocess smoke harness. TASK_305 must not run naked Excel COM in the main test/process path.
- `git diff --check`

Manual/browser smoke:

- Open `/projects/{project_id}/fee-evaluation`.
- Confirm each group starts with `Step=0 / Sample preparation`.
- Edit one Sample preparation row and save/reload the pricing draft to confirm the edit returns.
- Generate Fee Form and confirm the Sample preparation edit is present in the corresponding row.
- Edit representative Matrix row values and Notes.
- Edit Report preparation values and Notes.
- Edit Condition confirmation, External Cost, External Cost note, and lab manpower hourly rate.
- Generate Fee Form.
- Inspect generated `Testing Prices`:
  - Sample preparation rows have default values.
  - Matrix/Report values match preview edits.
  - row Notes appear as comments on Testing Fee cells.
  - External Cost note appears as a comment on the External Cost amount cell.
- Any real-template Excel smoke must run through the existing timeout-protected production export path or the TASK_290A subprocess smoke harness. Do not run naked Excel COM from the main process.

## Stop Point

After TASK_305 implementation and validation, stop. Do not start rule-refresh UI, new pricing policy, StepInstance execution, report generation, or server/multi-user work from this task.
