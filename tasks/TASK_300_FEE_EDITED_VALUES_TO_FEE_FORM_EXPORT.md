# TASK_300 Fee Edited Values To Fee Form Export

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_298 and TASK_299 are complete. The approved TASK_298-TASK_302 series defines TASK_300 as the next controlled step: carry the current Fee Evaluation page's local edited pricing values into generated Fee Form workbooks. This task is not approved for implementation until the executable plan is reviewed and explicitly approved.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. TASK_300 is a bounded full-stack data-plumbing and Excel-template export task with an existing React edit model, typed API client, FastAPI route, timeout-protected export service, and Office gateway boundary. It is not suitable for inventing new pricing policy or long-term persistence semantics; edited values should be passed through deterministically and left non-persistent until TASK_301.

## Goal

When the operator edits Fee Evaluation preview values and clicks `Fee Form`, the generated workbook must reflect the same visible row order and editable values shown in the Fee Evaluation page.

TASK_300 is export-only. It does not persist fee edits, reload fee edits, or create a rule-maintenance workflow.

## Input Data

Frontend local-only Fee Evaluation preview state from TASK_299:

- matrix-step row values:
  - stable row identity matching the backend Matrix basic-fill step-expanded row (`source_line_id`, `confirmed_group_id`, `confirmed_row_id`, `step_token`, `step_index`)
  - `Spend Time` / `Man-hour`
  - `Unit Price`
  - `Unit Type`
  - `Units`
  - `Base Fee`
  - `Discount`
  - calculated `Testing Fee`
  - `Notes` optional row explanation; blank is valid and never blocks export
- summary values:
  - `Condition confirmation` spend time
  - `External Cost`
  - `External Cost` note, exported only when the V1 template has a stable target anchor
  - Lab manpower hourly rate

Server authoritative inputs remain:

- active Confirmed Matrix authority version
- official Fee Evaluation template
- existing TASK_291 timeout-protected export service path

## Output Data

Generated `.xls` Fee Form download using the official `Testing Prices` sheet layout, populated from current edited preview values.

The workbook should include:

- same Matrix step-expanded row order shown in the preview
- group labels and group formatting
- row-level pricing values
- formula-compatible columns for `Testing Fee`
- optional `Notes` as Excel comments on the row's final total-price cell; blank notes create no comment
- `Report preparation` row
- `Condition confirmation` spend time in the template total/manual area
- `External Cost` in the template total/manual area
- `External Cost` note only when supported by a stable V1 template anchor
- `Grand Cost` / totals formulas preserved or updated consistently

## Scope

### In Scope

- Fee Evaluation page `Fee Form` action payload.
- Frontend API client request type for edited Fee Form download.
- FastAPI direct-download endpoint request body for edited values.
- Application-service command/data model for edited Matrix basic-fill export.
- Timeout/subprocess command serialization for edited export values.
- Office gateway writes for edited pricing fields into `Testing Prices`.
- Office gateway writes row `Notes` as an optional Excel comment on that row's final total-price cell; blank notes create no comment.
- Tests covering frontend payload, API payload, service command flow, gateway writes, and timeout wrapper serialization.
- `docs/task_board.md` update after implementation.

### Out Of Scope

- Persisting edited fee values.
- Reloading previous edited fee values.
- Database migration.
- New rule-maintenance UI.
- Rule/reference update workflow.
- Changing fee-rule matching behavior.
- Replacing Excel as the delivery artifact.
- StepInstance, execution persistence, report generation, AI review, permissions, or multi-user workflow.
- Making production runtime load pricing rules from Excel/COM.

## Required Behavior

### Frontend

- Clicking `Fee Form` sends current local preview values instead of calling a no-body download endpoint.
- The page still allows generating the file without a project folder.
- The button remains disabled only for existing real blockers such as missing active fee draft/Matrix readiness.
- Local edits remain non-persistent and reset exactly as in TASK_299.
- The browser receives the generated workbook as a download.

### Backend/API

- Keep the existing JSON export endpoint unchanged for compatibility.
- Extend or add a direct-download endpoint path for edited Fee Form generation.
- If the existing direct-download endpoint is extended, its request body must be optional using FastAPI `Body(default=None)` so the no-body legacy path remains stable.
- The request body must be typed and validate:
  - row identities are non-empty and include stable lineage fields
  - duplicate row identities are rejected
  - numeric fields are normalized conservatively
  - discount accepts `10` and `10%` as 10%
  - unknown `Unit Type` values are rejected unless they are already supported by TASK_299 options
- Timeout responses keep the TASK_291 structured 503 detail shape.
- The route-level file response guard must still validate generated file path under `settings.data_dir / generated_fee_files`, `.xls` suffix, exists, and is a file.

### Export Semantics

- Edited values are matched to Matrix basic-fill lines by a stable step-expanded identity:
  - `source_line_id`
  - `confirmed_group_id`
  - `confirmed_row_id`
  - `step_token`
  - `step_index`
- The implementation must prove that frontend payload identity corresponds to backend `MatrixBasicFillLine` identity. If the existing frontend `lineId` differs from backend basic-fill `line_id`, do not use it as the only key.
- The exported workbook row order follows Matrix basic-fill step-expanded rows, not collapsed `Test item` rows.
- Missing row edit payload values fall back to the same TASK_299 defaults used in the preview:
  - `Man-hour = 0`
  - `Unit Price = 0`
  - `Unit Type = current preview/default value`
  - `Units = 1`
  - `Base Fee = 0`
  - `Discount = 0%`
  - `Notes = blank`
- `Testing Fee` V1 behavior is Excel formula first:
  - write the row's editable cells
  - write/restore the Excel-side formula in `Testing Fee`
  - if a fake/real template path cannot support formulas, write a numeric fallback and emit a gateway warning covered by tests

```text
Unit Price * Units * (1 - Discount) + Base Fee
```

### Manual Summary Rows

- `Report preparation` remains in the table as an editable/exported row when present in the preview.
- `Condition confirmation` is exported as the dedicated condition/manual spend-time value, not as a normal Matrix row.
- `External Cost` is exported as a dedicated cost value, not as a normal Matrix row.
- `External Cost note` is exported only when the V1 template exposes a stable target anchor; otherwise the gateway must return a warning and this is not a TASK_300 failure.
- `Lab manpower cost` is preview-only in TASK_300 unless the official template has an approved target field. Do not invent a new workbook section.
- Row `Notes` is an operator explanation field for discounts, special price choices, or step-specific comments. It does not affect formulas and blank notes are valid.
- In the generated Fee Form, non-empty row `Notes` must be inserted as an Excel comment on that row's final total-price cell. Empty/blank `Notes` must not create comments.

## Acceptance Criteria

- Fee Evaluation page sends edited row payload when `Fee Form` is clicked.
- Generated workbook contains edited values for `Man-hour`, `Unit Price`, `Unit Type`, `Units`, `Base Fee`, and `Discount`.
- Non-empty row `Notes` appear as comments on final total-price cells; blank row `Notes` create no comments.
- Generated workbook `Testing Fee` matches the formula for edited values.
- Generated workbook preserves Matrix step-expanded row order.
- `Condition confirmation` and `External Cost` values are exported through dedicated template fields/anchors.
- `External Cost note` is exported only if a stable V1 template anchor is available; otherwise an explicit warning is acceptable.
- Existing timeout protection remains active for production export.
- Existing unedited export behavior remains available through compatible defaults.
- Direct-download with no JSON body remains covered by regression tests and keeps current Matrix basic-fill behavior.
- No edited values are persisted to SQLite.
- No rule-reference update or rule-maintenance UI is introduced.

## Validation Plan

Implementation validation:

```powershell
cd frontend
npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py -q
py -m pytest tests/integration/test_confirmed_matrix_fee_file_download_api.py tests/integration/test_fee_evaluation_export_child_transaction.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Manual/browser smoke:

- Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`.
- Edit several row values including discount, optional notes, condition confirmation, and external cost.
- Click `Fee Form`.
- Open the downloaded `.xls`.
- Confirm row order, values, notes, and calculated fee cells match the page.

## Stop Point

After implementation and validation, update `docs/task_board.md` and stop. Do not proceed to TASK_301 persistence without a separate task file, executable plan, and explicit approval.
