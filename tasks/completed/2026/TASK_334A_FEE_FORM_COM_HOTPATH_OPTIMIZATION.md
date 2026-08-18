# TASK_334A_FEE_FORM_COM_HOTPATH_OPTIMIZATION

## Status

Complete. Created, approved, implemented, and validated on 2026-06-24 after real profiling showed Fee Form `.xls` generation still spent roughly 23-35 seconds inside Excel COM.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

`TASK_334_PROJECT_FOLDER_EXCEL_OUTPUT_PERFORMANCE` is complete, but its real timing follow-up identified Fee Form COM generation as the dominant Excel-output bottleneck.

The user explicitly asked to analyze where the Fee Form `~22.9s` to `~25.0s` time is spent and to find a solution.

Measured profile on project `72fbbfa290294da9a507344b68ff900f`:

- `service.export.total`: about `30.5s` in one focused run, `46.2s` in another cold/proxy run.
- `basic_fill.build`: about `21ms`.
- `fee_draft.build_draft`: about `8ms`.
- `output.register_output`: about `33ms`.
- `write_matrix_basic_fill`: about `25.0s` to `35.1s`.
- `_find_optional_row`: about `11.9s` to `16.2s` for one `200 x 9` COM cell scan.
- `_find_required_row`: about `2.5s` to `3.9s` for four repeated COM scans.
- `write_basic_information_identity`: about `0.34s` to `1.08s`, mostly repeated header scans.
- `_write_matrix_detail_row`: about `8.2s` to `11.4s` across 113 rows.
- `_set_cell_comment`: about `1.5s` to `1.9s`, mostly clearing comments even when notes are blank.
- `_set_formula`: about `1.5s` to `2.0s`.
- Excel process startup/open template is real but secondary: `DispatchEx` about `2.1s`, `Workbooks.Open` about `1.7s`, `SaveAs` under `0.1s`.

## Root Cause

The bottleneck is not Customer Feedback, not Basic Information assembly, not Matrix/Fee data building, and not file save.

The bottleneck is Excel COM round-trips in the Fee Form worksheet hot path:

1. Anchor discovery scans worksheet cells one by one through COM.
2. Header identity lookup scans the same top rows repeatedly.
3. The optional `External Cost` anchor scans 1,800 cells through COM even though the target template has stable nearby anchors.
4. Detail rows still perform multiple COM calls per row for formula, fill clearing, and comment clearing.

## Goal

Reduce cold Fee Form `.xls` generation time by eliminating avoidable per-cell COM scans and reducing per-row COM calls, while keeping the output format, template behavior, header placement, formulas, and edited Fee values unchanged.

## In Scope

- Optimize Fee Form Matrix basic-fill writer hot path only.
- Keep `.xls` and Excel COM for Fee Form generation.
- Add a worksheet anchor snapshot/helper that reads small regions through range values once and reuses them.
- Replace repeated `_find_required_row`, `_find_optional_row`, and identity-label scans with cached anchor lookup.
- Avoid clearing comments for rows with empty notes when safe.
- Batch formula assignments where safe, or reduce formula writes to the minimum needed.
- Add fake-COM tests proving fewer cell reads/writes for anchor lookup and no blank-note comment clearing.
- Add focused real smoke instructions to compare before/after timings.

## Out Of Scope

- No `.xls` to `.xlsx` conversion.
- No Customer Feedback changes.
- No Application Form Word COM optimization.
- No Project Folder UI/progress redesign.
- No Basic Information schema/API/source-provider changes.
- No Fee pricing/business-rule changes.
- No Matrix authority behavior changes.
- No template redesign.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- Fee Form generation still writes:
  - Basic Information values beside existing `LTR Number`, `Requestor`, `Test Description`, and `Site` labels.
  - Matrix basic-fill detail rows into the `Testing Prices` sheet.
  - Existing edited spend time, unit price, units, base fee, discount, testing fee, and notes when present.
  - Existing formulas and group styling behavior.
- Required and optional row anchors are discovered from a cached worksheet region rather than repeated per-cell COM scans.
- The `External Cost` lookup no longer scans `200 x 9` cells one-by-one through COM.
- Blank notes do not call `ClearComments()` or `AddComment()` for every generated Matrix detail row.
- Unit tests show:
  - one cached anchor pass can find required rows, optional `External Cost`, and header identity targets;
  - repeated anchor lookups do not increase fake COM cell-read counts;
  - blank Matrix rows do not clear comments;
  - edited rows with notes still write comments;
  - existing Fee Form output assertions remain valid.
- Real timing smoke records Fee Form generation before/after with the same project and shows a material reduction in `fee_form.generate`; if Excel/Office environment variance prevents a stable target, the task documents the new measured bottleneck.

## Validation Plan

Targeted tests:

```powershell
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Real timing smoke:

1. Use project `72fbbfa290294da9a507344b68ff900f`.
2. Generate Fee Form into `tmp/fee_profile` with the same confirmed Matrix/Fee/Basic Information context.
3. Capture timings for:
   - `DispatchEx`
   - `Workbooks.Open`
   - header identity write
   - anchor lookup
   - detail row write
   - comment write
   - formula write
   - `SaveAs`
   - total `fee_form.generate`
4. Repeat once to reduce cold-start noise.

## Stop Point

Stop after optimizing and validating Fee Form COM hot-path behavior. Do not start Application Form Word COM optimization or broader Project Folder orchestration changes without separate explicit approval.

## Completion Notes

- Added a cached `FeeEvaluationAnchorSnapshot` for the `Testing Prices` worksheet so Fee Form header, required row, optional row, and template-row lookups no longer scan cells repeatedly through COM.
- `write_basic_information_identity()` now accepts the shared anchor snapshot and keeps the existing label-adjacent value placement behavior.
- `write_matrix_basic_fill()` now uses the shared snapshot, resolves `External Cost` before row insertion, adjusts the row after insertion when needed, and avoids repeated `200 x 9` COM scans.
- Unedited Matrix detail rows now write contiguous blocks through range-style seams and batch formula/fill operations where safe.
- Blank note rows no longer clear comments through COM; edited rows with nonblank notes still write comments and preserve warning behavior.
- Real timing profile on project `72fbbfa290294da9a507344b68ff900f` improved Fee Form focused export from the prior observed `~30.5s` / `~46.2s` runs to about `6.5s`; `write_matrix_basic_fill` dropped from about `25.0s` / `35.1s` to about `3.7s`.

## Validation Summary

```powershell
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py -q
```

Result: `14 passed`.

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_project_folder_required_forms_service.py -q
```

Result: `52 passed`.

```powershell
py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
```

Result: `4 passed`.
