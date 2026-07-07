# TASK_353B Registered LTR Workbook Row Preview - Developer Evidence

Task ID: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`
Lane: `registered-ltr-workbook-row-preview`
Role: Developer
Date: 2026-07-07
Status: correction fix pass complete - pending Reviewer re-gate

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`.
- Why allowed: User/Orchestrator issued a scope correction after QA and before acceptance, superseding the prior over-scoped implementation package.

## User Scope Correction

The user rejected the prior split-action implementation as over-scoped. Corrected behavior:

- Do not keep the separate `LTR workbook row preview` button/card/API.
- Preserve the original `LTR update preview` experience as much as possible.
- Minimal change: if a project already has a registered LTR/DL number, the existing `LTR update preview` button is clickable even when Basic Information is not confirmed.
- Preview uses initial/current Basic Information values as the left-side update source.
- Commit/update remains safely gated by confirmed Basic Information context.

## Removed From Prior Over-Scoped Package

- Deleted the separate registered-row preview backend service and route:
  - `backend/application/registered_ltr_workbook_row_preview_service.py`
  - `backend/api/routes_ltr_workbook_registered_row_preview.py`
- Deleted separate registered-row preview tests:
  - `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
  - `tests/integration/test_registered_ltr_workbook_row_preview_api.py`
- Removed registered-row API client DTO/helper.
- Removed the separate `LTR workbook row preview` button/panel from `ProjectBasicInformationSummaryCard`.
- Removed route registration and dependency provider for the rejected endpoint.

## Corrected Implementation Summary

- Extended `ProjectBasicInformationSnapshotReader` with `get_preview_snapshot(...)`.
  - Confirmed Basic Information remains preferred.
  - If no confirmed record exists, current draft/initial Basic Information values can be used for preview only.
  - Draft/initial preview snapshots carry `version = null` and `source_signature_hash = null`.
- Updated `LtrWorkbookBasicInformationSyncService.preview(...)` to use preview snapshot values.
- Left `LtrWorkbookBasicInformationSyncService.commit(...)` unchanged:
  - It still calls `_require_basic_information(...)`.
  - It still requires confirmed version/hash and existing preview ack fields.
- Updated `ProjectBasicInformationSummaryCard` to keep one action label: `LTR update preview`.
  - The button is enabled when either confirmed Basic Information is ready or a registered LTR number is available.
  - Unconfirmed previews can show comparison values, but `Confirm update` remains disabled because confirmed version/hash are null.
- Kept Workbench wiring that passes the registered project reference into the SummaryCard.

## Current TASK_353B Files Changed

- `backend/application/project_basic_information_output.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/api/client.ts` only to remove the rejected registered-row helper from the prior package.
- `backend/api/dependencies.py` and `backend/api/main.py` only to remove the rejected registered-row route/provider from the prior package.
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`

Deleted from the prior over-scoped package:

- `backend/application/registered_ltr_workbook_row_preview_service.py`
- `backend/api/routes_ltr_workbook_registered_row_preview.py`
- `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
- `tests/integration/test_registered_ltr_workbook_row_preview_api.py`

## Scope Locks Preserved

- No new LTR workbook write authority path.
- No schema/migration.
- No Intake raw parse changes.
- No Matrix, Fee, Folder Actions, Report, StepInstance, AI, permissions, LAN/server, or multi-user changes.
- No real workbook/folder mutation.
- No unrelated release/settings/template residual cleanup.

## Validation Results

- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q`
  - Result: 19 passed.
- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q`
  - Result: 34 passed.
- `npm test -- ProjectBasicInformationSummaryCard --run`
  - Result: 10 passed.
- `py -m py_compile backend/application/project_basic_information_output.py backend/application/ltr_workbook_basic_information_sync_service.py backend/api/dependencies.py backend/api/main.py`
  - Result: passed.
- `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- `git diff --check` on corrected TASK_353B package files
  - Result: passed with existing LF/CRLF warnings only.
- Trailing whitespace scan on corrected TASK_353B package files
  - Result: no matches.
- Rejected-surface scan
  - Result: no product/test references remain for `registered-row-preview`, `RegisteredLtrWorkbookRowPreview`, `LTR workbook row preview`, `previewRegisteredLtrWorkbookRow`, or `Update LTR from Basic Information`. Remaining generic "workbook row preview" hits are pre-existing LTR write-preview terminology outside this corrected surface.

## External Residuals Excluded

The worktree still contains unrelated residuals in release/settings/template/desktop packaging paths, TASK_352 PDF import files, Word/Fee output files, `frontend/src/workbench.css`, `docs/task_board.md`, and adjacent backend/frontend tests. These remain outside TASK_353B.

Non-blocking packaging note: `backend/api/dependencies.py` still contains unrelated template-resource residual hunks in the same file. TASK_353B owns only the removal of the rejected registered-row provider from that file plus the corrected Basic Information preview behavior.

## Next Role

Recommended next role: Reviewer implementation re-gate.

## Blocking Summary

None.
