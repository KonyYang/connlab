# TASK_334_PROJECT_FOLDER_EXCEL_OUTPUT_PERFORMANCE

## Status

Complete. Task and plan were created on 2026-06-24 after the user reported that `Update project folder` currently takes about 70 seconds and asked to optimize the Excel-output portion first.

Implementation was approved and completed on 2026-06-24.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

`TASK_332`, `TASK_332A`, `TASK_332B`, and `TASK_332C` completed the official output header and Application Form write-back behavior needed by project folder update.

Manual smoke timing shows the complete project folder update is too slow for operator confidence. The user specifically asked to analyze whether Customer Feedback `.xlsx` and Fee Form `.xls` are both using COM, and to start a dedicated optimization task if the work is non-trivial.

The investigation found:

- Customer Feedback `.xlsx` generation already uses Python `openpyxl`, not Excel COM.
- Fee Form `.xls` generation uses Excel COM and is the likely Excel-output bottleneck.
- Application Form Word COM write-back remains a separate likely bottleneck and is intentionally out of scope for this Excel-focused task.

## Plan

Detailed implementation plan:

- `docs/task_334_project_folder_excel_output_performance_plan.md`

## Completion Notes

- Customer Feedback `.xlsx` remains on the Python `openpyxl` path; a regression test now guards against accidental Excel COM usage in that gateway.
- Fee Form reuse safety now includes the Fee template path/content hash and explicit `fee-output:matrix_basic_with_basic_information` mapping mode in Required Forms source context, so unchanged managed Fee Forms can be safely reused while template/mapping changes force regeneration.
- Required Forms generation now processes Customer Feedback before Fee Form, matching the progress display and making Fee timing easier to isolate.
- Fee Form Matrix basic-fill writing was split out of the oversized workbook gateway into focused helper modules:
  - `backend/infrastructure/office/fee_evaluation_identity_header_writer.py`
  - `backend/infrastructure/office/fee_evaluation_matrix_basic_fill_writer.py`
  - `backend/infrastructure/office/fee_evaluation_sheet_ops.py`
- The Fee Form Matrix basic-fill writer now batches contiguous row-segment writes for unedited/template rows through a range-style seam, reducing per-cell COM `Value` chatter while preserving formulas, comments, fills, group styling, and Basic Information header placement.
- `fee_evaluation_workbook_gateway.py` is now a thinner Excel lifecycle/gateway wrapper and remains under the project file-size hard limit.
- Real timing smoke follow-up found that real projects without an active Matrix draft were registering Required Forms as `manual/manual`, preventing the intended `current/system_generated` skip path. Required Forms registration now records context-bound system outputs as `CURRENT` even when there is no active draft, and `ProjectOutputRecordService` allows `CURRENT + SYSTEM_GENERATED` records without a draft only when a `source_context_signature` is present.

## Validation Summary

```powershell
py -m pytest tests/unit/test_customer_feedback_workbook_gateway.py tests/unit/test_project_folder_required_forms_service.py -q
```

Result: `38 passed`.

```powershell
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_customer_feedback_workbook_gateway.py tests/unit/test_project_folder_required_forms_service.py -q
```

Result: `50 passed`.

```powershell
py -m pytest tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Result: `75 passed`.

Additional real timing smoke follow-up validation:

```powershell
py -m pytest tests/unit/test_project_output_record_service.py tests/unit/test_project_folder_required_forms_service.py tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py tests/integration/test_project_folder_required_forms_api.py -q
```

Result: `80 passed`.

## Known Limitation

Real timing smoke on `DL-2026-05-011` measured the full API flow at roughly `43.9s` on the first run and `40.6s` on a repeat run before the Required Forms registration follow-up was applied. The largest observed costs were Fee Form COM generation (`~22.9s` to `~25.0s`) and Application Form Word COM write-back (`~14.9s` to `~15.3s`).

The follow-up fixed the registration precondition that prevented future skip/reuse, but another live smoke exposed a separate late-failure path: Fee Form generation can still spend ~35s in Excel before failing final placement with `[Errno 17] File exists` when preview treats an existing target as `generate`. That should be handled as a separate small follow-up before claiming the repeat-update fast path is fully closed.

This task still does not optimize Application Form Word COM write-back. If manual smoke remains high after the Fee Form placement/skip follow-up, the remaining bottleneck is likely Word COM and should be handled by a separate approved task.

## Goal

Shorten the `Update project folder` Excel-output portion by measuring real per-step time, keeping Customer Feedback on the fast Python path, and optimizing Fee Form `.xls` generation so repeated updates avoid unnecessary Excel COM work and cold generation performs less COM chatter.

## In Scope

- Required Forms timing observability for Excel outputs.
- Customer Feedback `.xlsx` regression protection proving it stays on the `openpyxl` path.
- Fee Form `.xls` reuse/current-output behavior before falling back to generation.
- Fee Form Excel COM generation optimization for the Matrix basic-fill export path.
- Fee Form writer decomposition if optimization would otherwise grow the existing gateway file.
- Tests proving no second Excel COM session is opened for Customer Feedback.
- Tests proving reusable/current Fee Form artifacts skip regeneration when safe.
- Tests proving the Matrix basic-fill writer reduces COM cell-write calls through a fake COM/range-write counter or equivalent observable seam.
- Manual smoke guidance for comparing before/after timings.

## Out Of Scope

- No Application Form Word COM optimization.
- No change from `.xls` Fee Form output to `.xlsx`.
- No template redesign or template migration.
- No Report generation.
- No Basic Information schema/API/persistence change.
- No Matrix/Fee business rule change.
- No Workbench layout redesign beyond logging/progress observability if needed.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- Customer Feedback generation remains implemented through `openpyxl` and does not import or instantiate Excel COM.
- Project folder update timing output distinguishes Customer Feedback generation time from Fee Form generation time.
- A pre-optimization baseline is recorded for Customer Feedback, Fee Form, and Required Forms total using the same smoke scenario planned for final validation.
- Repeated `Update project folder` skips Fee Form regeneration when the existing managed Fee Form is current and the complete Fee Form context is unchanged.
- Complete Fee Form context must include at least Basic Information version/source hash, confirmed Matrix identity/revision, confirmed Fee authority identity/version, Fee template identity/path/hash, and the Fee Form output mapping mode.
- If the Fee Form target must be regenerated, the COM path reduces cell-by-cell operations in the Matrix basic-fill writer through a measurable fake COM call-count/counter test or equivalent.
- Any Fee Form gateway implementation change that would add substantial code must first extract focused helpers so `fee_evaluation_workbook_gateway.py` does not grow further beyond the project hard limit.
- Existing Fee Form header placement remains correct: value only goes to the cell beside `LTR Number`, `Requestor`, `Test Description`, and `Site`.
- Required Forms still produces valid Fee Form `.xls` and Customer Feedback `.xlsx` files in the official project folder.
- If Office COM is unavailable, Fee Form behavior still fails with the existing actionable Office automation error rather than silently producing an invalid file.
- Performance smoke records before/after durations for Customer Feedback, Fee Form, and Required Forms total.
- Performance target: unchanged repeated updates must avoid opening Excel COM for Fee Form; cold Fee Form generation must record a materially lower duration than the current roughly 40-second smoke observation, or document the measured bottleneck and stop with evidence.

## Validation Plan

Targeted backend tests:

```powershell
py -m pytest tests/unit/test_customer_feedback_workbook_gateway.py tests/unit/test_customer_feedback_form_generation_service.py -q
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

If frontend timing/log output changes:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchLayout useProjectWorkbenchModel --watch=false
cd frontend; npm run build
```

Manual smoke:

1. Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
2. Click `Update project folder`.
3. Record displayed step durations or console timing JSON.
4. Verify Customer Feedback completes quickly and Fee Form timing is separately visible.
5. Repeat without changing Matrix/Fee/Basic Information and confirm Fee Form is reused/skipped when safe.

## Stop Point

Stop after TASK_334 completion. Do not start Application Form Word COM optimization or any later project-folder orchestration task without separate approval.
