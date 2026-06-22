# TASK_332B Basic Information Test Type In Sheet LTR Mapping

## Status

Complete. Implemented after explicit user approval.

## Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed Now

Manual review of the Project Workbench / Basic Information surface found that the current Basic Information `test_type` field is being interpreted as the LTR workbook sheet field. That is incorrect. The existing `test_type` comes from the Application Form and should remain the Application Form `Test Type`.

New Project already has a separate required Project setup confirmation field:

```text
Test Type in sheet*
```

That field is the value that should drive the public-drive LTR workbook `"Test Type"` column. This task is a controlled Phase 11 follow-up to prevent the Application Form `Test Type` from being written to the public-drive LTR workbook during Basic Information LTR sync.

## Goal

Add a separate Basic Information field named `test_type_in_sheet`, sourced from New Project Project setup confirmation, display it in the Basic Information right-side execution card beside `Failed item`, and map the public-drive LTR workbook `"Test Type"` column to this new field instead of Application Form `test_type`.

## Problem Statement

ConnLab currently has two different business concepts that are easy to confuse:

- Application Form `Test Type`, stored as Basic Information `test_type`.
- Project setup confirmation `Test Type in sheet*`, used for the public-drive LTR workbook sheet classification.

The current Workbench Basic Information summary displays `Test Type Product/Process Qualification` and the public-drive LTR Basic Information sync reads `test_type` for the LTR workbook row data. That incorrectly couples the public-drive LTR `"Test Type"` column to the Application Form `Test Type`.

The correct behavior is:

```text
Application Form Test Type -> Basic Information test_type
Project setup confirmation Test Type in sheet* -> Basic Information test_type_in_sheet -> LTR workbook "Test Type" column
```

## In Scope

- Backend Basic Information source assembly:
  - Add `test_type_in_sheet` to Basic Information source suggestions.
  - Source it from the registered LTR audit note payload created by New Project setup confirmation.
  - Use registered-LTR selection behavior, not arbitrary list order, so draft or stale LTR records do not become the source.
  - Keep existing `test_type` unchanged as the Application Form `Test Type`.
- Frontend Basic Information editor:
  - Add `Test Type in sheet` to the right-side `Laboratory execution` card.
  - Place it beside `Failed item` in the `Result and commercial` area.
  - Reuse the existing New Project completion options endpoint for the Project setup confirmation sheet option set, so administrator-imported `project_setup_test_type_in_sheet` values do not drift.
  - Adjust `Failed item` layout as needed so `Failed item` and `Test Type in sheet` are actually adjacent in the same result/commercial grid row on normal desktop widths.
- Workbench summary:
  - Show `Test Type in sheet` instead of showing Application Form `Test Type` in the summary area selected in the browser review.
  - Keep Application Form `Test Type` available in the full confirmed field view if present.
- LTR workbook Basic Information sync:
  - Map public-drive workbook `"Test Type"` column from `test_type_in_sheet`.
  - Do not fall back to Application Form `test_type`.
  - If `test_type_in_sheet` is missing for historical or malformed data, block preview/commit with `Test Type in sheet` missing.
- Tests:
  - Cover source assembly.
  - Cover frontend field label, placement, and summary behavior.
  - Cover LTR workbook row mapping and missing-field blocker.

## Out Of Scope

- No Application Form parser changes.
- No change to the existing Application Form `test_type` field or its option set.
- No Basic Information database table schema migration.
- No forced historical JSON migration from `test_type` to `test_type_in_sheet`.
- No New Project setup confirmation UI redesign.
- No duplicate hardcoded Basic Information-only copy of the `project_setup_test_type_in_sheet` option list.
- No LTR workbook append/new-registration behavior changes.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Technical Decision

Use a minimal additive field approach:

1. Preserve `test_type` exactly as the Application Form `Test Type`.
2. Add `test_type_in_sheet` as a new Basic Information value key inside the existing draft/confirmed JSON values.
3. Source `test_type_in_sheet` from the structured New Project setup confirmation payload already stored in LTR record notes.
4. Map public-drive LTR workbook `"Test Type"` from `test_type_in_sheet`.
5. Do not introduce a SQL schema migration because Basic Information values are already JSON-backed and this task only adds a new key.

## Data Source

New Project completion already records a structured operator note with:

```json
{
  "source": "new_project_setup_confirmation",
  "test_type_in_sheet": "Qualification"
}
```

The Basic Information source assembler should reuse the existing `setup_payload_from_ltr_notes()` helper from `backend/application/project_identity.py` to read this value from the latest registered LTR record.

New Project treats `Test Type in sheet*` as a required blocking setup field. Therefore new projects should have this value. Historical or malformed data should still be handled defensively by blocking LTR sync if the value is absent.

Adding this source suggestion changes the Basic Information source signature. Existing confirmed Basic Information records that do not yet contain `test_type_in_sheet` may move to `needs_review` when the registered LTR note contains the setup value. That is expected: the operator should confirm the newly surfaced sheet field before syncing the public-drive LTR workbook.

## UI Placement

In Basic Information:

- Keep Application Form `Test Type` in the left-side product/request area as-is.
- Add `Test Type in sheet` to the right-side `Laboratory execution` card.
- Place it in the `Result and commercial` area beside `Failed item`.
- Use the same restrained product UI vocabulary as the existing Basic Information controls.

In Workbench summary:

- Replace the current summary item that displays Application Form `Test Type` with `Test Type in sheet`.
- The summary should help the operator review LTR update values, so it should prioritize the sheet mapping field.

## LTR Mapping

The public-drive LTR workbook row builder must change from:

```text
test_type <- Basic Information test_type
```

to:

```text
test_type <- Basic Information test_type_in_sheet
```

This keeps the Excel column name unchanged because the public-drive workbook authority currently names the column `"Test Type"`, but the ConnLab Basic Information source field should be `Test Type in sheet`.

## Acceptance Criteria

- Basic Information editor shows both concepts without ambiguity:
  - Application Form `Test Type` remains unchanged.
  - `Test Type in sheet` appears in the right-side execution/commercial area beside `Failed item`.
- `Test Type in sheet` is populated from New Project setup confirmation for projects created through the current flow.
- Existing confirmed Basic Information without `test_type_in_sheet` is marked for source review when the registered LTR setup payload provides the value.
- Workbench Basic Information summary displays `Test Type in sheet` rather than Application Form `Test Type`.
- LTR workbook Basic Information sync preview shows the workbook `"Test Type"` column value from `test_type_in_sheet`.
- LTR workbook Basic Information sync does not fall back to Application Form `test_type`.
- If `test_type_in_sheet` is missing, preview/commit is blocked with a missing `Test Type in sheet` message.
- Existing Application Form `test_type` tests and behavior remain valid.

## Planned Validation

After implementation approval:

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py -q
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q
cd frontend; npm test -- --run ProjectBasicInformationWorkspace ProjectBasicInformationSummaryCard ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```

## Risks

- Existing projects created before the structured setup payload may not have `test_type_in_sheet`; this should block LTR sync rather than silently using the wrong Application Form field.
- Existing confirmed records that gain a new `test_type_in_sheet` source suggestion may enter `needs_review`; this is intentional because the confirmed snapshot must explicitly include the sheet mapping before LTR sync writes.
- Tests that previously expected summary label `Test Type` in the Workbench summary need to be updated to `Test Type in sheet`.
- Basic Information currently uses static field config for several options. This task must avoid a new drift point for `Test Type in sheet` by reusing the existing `/api/new-project/completion-options` option source already used by Project setup confirmation.

## Stop Point

`TASK_332B` is implemented and validated. Stop here and wait for separate explicit approval before starting another task.

## Completion Notes

- Added Basic Information `test_type_in_sheet` as a separate JSON-backed value sourced from New Project Project setup confirmation.
- Kept Application Form `test_type` unchanged.
- Displayed `Test Type in sheet` beside `Failed item` in the right-side Basic Information result/commercial area.
- Reused the existing New Project completion-options endpoint for the `Test Type in sheet` option list.
- Updated Workbench summary to show `Test Type in sheet`.
- Updated public-drive LTR workbook Basic Information sync so the workbook `"Test Type"` column maps from `test_type_in_sheet` only, with no fallback to Application Form `test_type`.
- Added backend and frontend regression coverage for source assembly, summary/UI placement, option sourcing, LTR row mapping, and missing-field blocker.

## Validation

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py tests/unit/test_ltr_workbook_basic_information_sync_service.py -q
cd frontend; npm test -- --run ProjectBasicInformationWorkspace ProjectBasicInformationSummaryCard ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```
