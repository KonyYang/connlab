# TASK_334F_LTR_WORKBOOK_READONLY_OPEN_AT_EXACT_DL_MATCH

Status: Completed
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-25
Depends on:
- TASK_333C_LTR_WORKBOOK_ON_DEMAND_PREVIEW_AND_EXACT_DL_MATCH

Approval state: Approved and implemented on 2026-06-25.

## User Request

In the Workbench LTR update preview, make the workbook entry an operator action that opens the configured public-drive LTR workbook for manual inspection.

The workbook must open read-only, remove row/column hiding and active data filters for viewing, and place the Excel selection on the cell whose DL value exactly matches the current project LTR number.

The exact-match rule is mandatory: `DL-2026-05-011` and `DL-2026-05-011A` are different LTR numbers and must never match each other.

## Goal

Add a controlled read-only workbook-open action to the existing on-demand LTR update preview flow.

This is an operator inspection helper only. It must not update the workbook, create backups, append rows, or modify Basic Information.

## Scope

- Add a backend application use case for opening the LTR workbook read-only at the exact DL row/cell.
- Reuse the existing TASK_333C exact DL matching behavior where possible.
- Add an infrastructure Office/Excel gateway for the read-only open operation.
- Expose a typed API endpoint for the frontend action.
- Render the Workbench preview workbook entry as a clear button/action.
- Keep frontend code out of direct filesystem or Office automation access.
- Show business-readable success and failure messages.
- Add tests for exact matching, duplicate exact matches, missing rows, and frontend action states.

## Out Of Scope

- No initial LTR registration or row append behavior.
- No LTR workbook data write/update behavior.
- No workbook backup or restore behavior.
- No Basic Information schema, persistence, or editor changes.
- No Project Folder output generation changes.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- The Workbench preview still requires the user to request `LTR update preview` before workbook inspection actions appear.
- The workbook action opens the configured LTR workbook read-only through the backend.
- Excel displays the target workbook and selects the exact matching DL cell.
- Rows and columns hidden in the workbook are made visible only in a safe read-only inspection session that cannot accidentally persist view-state changes back to the shared workbook.
- Existing active filter criteria are cleared only for viewing the target row; the implementation must not remove workbook filter arrows/table filter structure.
- If the target workbook is already open in a user-controlled Excel session, ConnLab must not mutate that live session's hidden rows, hidden columns, or filter state. It must either open an isolated read-only inspection session/copy or block with an actionable message asking the operator to close the workbook and retry.
- No save operation is performed by ConnLab during this action.
- No backup file is created by this action.
- If there is no exact DL match, the action is blocked with an actionable message.
- If there are duplicate exact DL matches, the action is blocked with an actionable message.
- Prefix/suffix matches such as `DL-2026-05-011A` do not satisfy `DL-2026-05-011`.
- The UI keeps the workbook path visible and makes the action intent understandable to an operator.

## Validation Expectations

- Backend unit tests for exact target resolution and read-only open orchestration.
- Backend API tests for success, missing exact row, duplicate exact row, and unconfirmed Basic Information or unavailable preview conditions.
- Frontend component tests for the workbook action visibility, disabled/loading states, success state, and error state.
- Manual smoke on a local/public-drive workbook confirming:
  - workbook opens read-only,
  - filters/hidden rows/columns are cleared for viewing,
  - cursor lands on the exact DL cell,
  - no workbook update or backup is produced.

## Completion Notes

- Added a backend-only read-only LTR workbook open action for the Workbench preview.
- The action reuses the existing exact-DL preview target resolution, so prefix/suffix LTR numbers such as `DL-2026-05-011A` do not match `DL-2026-05-011`.
- The Excel gateway opens the workbook read-only through an isolated Excel COM session, selects the exact DL cell in column D, and performs view-only unhide/filter clearing without save, backup, append, or workbook write behavior.
- The API maps already-open or unverifiable Excel workbook states to actionable operator errors.
- The frontend exposes the workbook action only after a ready preview and keeps filesystem/Office automation behind the backend API.
- Scope boundaries held: no LTR workbook update/write/append behavior, no Basic Information schema/persistence/editor change, no Project Folder output change, no Report or execution scope.

## Validation

- `py -m pytest tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_ltr_workbook_readonly_open_gateway.py -q` (`11 passed`)
- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q` (`14 passed`)
- `cd frontend; npm test -- --run ProjectBasicInformationSummaryCard --watch=false` (`9 passed`)
- `cd frontend; npm run build` passed
- Real Excel/public-drive smoke was not run during this implementation close-out to avoid opening or mutating the operator's current Excel session; the COM action is covered by unit/API/frontend tests and should be smoke-tested manually against a disposable workbook copy before broad operator rollout.

## Stop Point

This task is complete. Stop here and wait for separate explicit user approval before starting another task.
