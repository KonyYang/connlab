# TASK_334F LTR Workbook Read-Only Open At Exact DL Match Plan

Status: Completed
Created: 2026-06-25
Task file: `tasks/TASK_334F_LTR_WORKBOOK_READONLY_OPEN_AT_EXACT_DL_MATCH.md`

## Current Task Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `TASK_334F_LTR_WORKBOOK_READONLY_OPEN_AT_EXACT_DL_MATCH`.
- Why this task is allowed now: the board was stopped after `TASK_334E`, the user explicitly requested and reviewed the `TASK_334F` task/plan, and then explicitly approved implementation.

## Problem

The Workbench LTR update preview shows the configured workbook path, but operators sometimes need to inspect the actual public-drive LTR workbook manually before confirming an update.

Manually opening the workbook is error-prone because the target row may be filtered, hidden, or hard to find. It is also unsafe to locate rows using prefix matching because related numbers such as `DL-2026-05-011` and `DL-2026-05-011A` are separate LTR records.

## Design Summary

Add an on-demand backend action that opens the configured LTR workbook read-only through Excel automation, resolves the exact DL row using the same business matching rule as the update preview, clears view-only hiding/filter obstacles, and selects the exact DL cell.

The action is an inspection helper, not a write/update path.

## Proposed User Experience

In the existing Workbench LTR update preview card:

- Keep `LTR update preview` as the button that fetches workbook comparison data.
- Keep the exact DL number visible in the preview area.
- Render the workbook path with an adjacent action, for example `Open workbook`.
- The action is available only after preview identifies a ready exact target.
- On click, show a short loading state.
- On success, show a short message such as `Workbook opened read-only at DL-2026-05-011.`
- On failure, show a business-readable message such as:
  - `LTR workbook was not found. Check the setup workbook path.`
  - `No exact DL row was found in the LTR workbook.`
  - `Multiple exact DL rows were found. Resolve duplicates before opening.`
  - `Excel could not open the workbook. Close blocking dialogs and try again.`

## File-Level Plan

### Backend Application

Candidate file:

- `backend/application/ltr_workbook_basic_information_sync_service.py`

Add an application method such as:

```text
open_workbook_readonly_at_ltr(project_id) -> LtrWorkbookOpenResult
```

Responsibilities:

- Load the current project/LTR/Basic Information context.
- Resolve the configured LTR workbook path.
- Reuse exact DL target-row resolution from TASK_333C.
- Reject missing and duplicate exact DL matches.
- Call an infrastructure port for Excel read-only open.
- Return a typed result with workbook path, LTR number, sheet name if available, selected cell reference, and a user-facing message.

### Backend Port / Infrastructure Boundary

Possible new port:

- `backend/application/ports.py` or the existing application port module used by LTR workbook sync.

Possible gateway:

- `backend/infrastructure/ltr_workbook_readonly_open_gateway.py`

The application layer must not import pywin32 or COM types.

### Excel Gateway Behavior

The infrastructure gateway should:

- Start or attach only through ConnLab-owned Office gateway patterns already used in the project.
- Open the workbook read-only:

```text
Workbooks.Open(path, UpdateLinks=0, ReadOnly=True, AddToMru=False, IgnoreReadOnlyRecommended=True)
```

- Make Excel visible.
- Activate the target worksheet.
- Clear active filter criteria for viewing, guarded for Excel COM errors:
  - If `FilterMode`, try `ShowAllData()`.
  - Do not remove AutoFilter/filter arrows or table filter structure. This action is an inspection helper, not a workbook view-structure cleanup.
- Unhide rows and columns only in a safe read-only inspection session that cannot accidentally persist view-state changes back to the shared workbook:
  - `worksheet.Rows.Hidden = False`
  - `worksheet.Columns.Hidden = False`
- Select or go to the exact DL cell:
  - `Application.Goto(cell, True)` or `cell.Select()`.
- Never call `Save`, `SaveAs`, backup, or write cell values.
- Leave the inspection workbook open for the operator.
- Release COM references that ConnLab no longer owns, without closing a workbook intentionally opened for inspection or quitting an Excel instance the operator is using.
- If the target workbook is already open in a user-controlled Excel session, do not mutate that live session's hidden rows, hidden columns, or filter state. Prefer opening an isolated read-only inspection session/copy; if that cannot be done reliably, block with an actionable message asking the operator to close the workbook and retry.

Important nuance: clearing filter criteria and unhiding rows/columns changes Excel view state. ConnLab must not save those view changes, and the design must avoid leaving the operator in a state where a later manual save can unintentionally persist ConnLab's inspection-only view changes to the shared LTR workbook.

### Backend API

Candidate route file:

- existing route used by LTR workbook Basic Information sync, for example `backend/api/routes_ltr_workbook_basic_information_sync.py`

Add a typed endpoint such as:

```text
POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/open-readonly
```

Response DTO should include:

- `status`
- `message`
- `workbook_path`
- `ltr_number`
- `sheet_name`
- `selected_cell`

Error mapping should be business-readable and should not expose raw COM stack traces.

### Frontend API

Candidate files:

- `frontend/src/api/client.ts`
- any existing typed API model file for project Basic Information/LTR sync

Add a typed client method for the read-only open action.

### Frontend UI

Candidate file:

- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`

Changes:

- Keep the workbook path displayed in the preview panel.
- Turn the workbook label/action into an explicit operator action, preferably a button beside or above the path.
- Disable the action while preview is loading, while the preview is not ready, or while an open request is in progress.
- Show success/error feedback near the preview, using concise business copy.
- Do not show technical COM details.

### Styling

Candidate file:

- existing Workbench/project Basic Information stylesheet.

Keep the action compact and aligned with the existing preview card. Avoid making the workbook path look like a raw hyperlink if the action is actually a backend Office automation command.

## Exact DL Matching Rule

The open action must use the same exact matching semantics as the TASK_333C preview/update path:

- Compare the full normalized DL text.
- Do not use `startswith`, substring search, or fuzzy matching.
- Treat `DL-2026-05-011` and `DL-2026-05-011A` as different values.
- If zero exact rows exist, block.
- If more than one exact row exists, block.

Implementation should avoid duplicating this rule in separate places. Prefer extracting or reusing the existing exact target resolver.

## Risk Assessment

- Excel may not be installed or may show modal dialogs.
- Public-drive paths may be unavailable.
- The workbook may already be open by the operator or another user.
- Read-only open can still affect the visible Excel session state by clearing filters and unhiding rows/columns.
- Removing AutoFilter/filter arrows is out of scope because it changes workbook view structure and may be accidentally saved by an operator.
- COM reference handling must avoid orphan Excel processes while also not closing a workbook intentionally opened for the user.
- UI wording must make clear that this is a manual inspection helper, not the update operation itself.

## Tests

Backend:

- Exact DL match opens the gateway with the expected workbook path, sheet, row, and cell.
- Prefix/suffix row does not match.
- Missing exact row returns a blocker.
- Duplicate exact rows return a blocker.
- Gateway/COM failure maps to a business-readable error.
- The application method does not invoke workbook write/backup behavior.

Frontend:

- Workbook action is hidden or disabled before preview is ready.
- Workbook action shows loading while in progress.
- Success message renders after API success.
- Error message renders after API failure.
- The preview comparison table remains unchanged by this UI action.

Manual smoke:

- Open a known workbook from the setup path.
- Confirm the file opens read-only.
- Confirm hidden rows/columns and active filter criteria do not prevent viewing the target row in the safe inspection session.
- Confirm AutoFilter/filter arrows remain intact and are not removed by the action.
- Confirm an already-open user workbook session is not mutated; if isolation is unavailable, confirm the action blocks with a clear message.
- Confirm the selected cell is the exact matching DL cell.
- Confirm no backup appears and no save is performed by ConnLab.

## Acceptance Checklist

- [x] Task remains within Workbench LTR workbook inspection scope.
- [x] No LTR write/update/append behavior is changed.
- [x] No Basic Information persistence/schema behavior is changed.
- [x] No frontend direct filesystem or Office access is introduced.
- [x] Exact DL matching is reused or centralized through the existing preview target resolution.
- [x] Already-open workbook handling blocks instead of mutating a user-controlled live Excel session.
- [x] AutoFilter/filter arrows are not removed by the inspection action.
- [x] Errors are actionable for operators.
- [x] Relevant backend and frontend tests pass.
- [ ] Manual smoke confirms read-only open and exact-cell selection.

## Implementation Summary

- Added `open_readonly_at_ltr(...)` to the LTR workbook Basic Information sync application service.
- Added `ExcelComLtrWorkbookReadonlyOpenGateway` for the read-only Excel inspection action.
- Added a typed backend endpoint at `POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/open-readonly`.
- Added a typed frontend API client method and wired the Workbench preview workbook action to the backend endpoint.
- Added regression coverage for API success/conflict mapping, A1 cell formatting, and frontend open-action error copy.

## Validation Summary

- `py -m pytest tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_ltr_workbook_readonly_open_gateway.py -q` (`11 passed`)
- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q` (`14 passed`)
- `cd frontend; npm test -- --run ProjectBasicInformationSummaryCard --watch=false` (`9 passed`)
- `cd frontend; npm run build` passed
- Manual real-Excel smoke remains the only unchecked item; use a disposable copy of the configured LTR workbook before broad operator rollout.

## Stop Point

Implementation is complete. Stop here and wait for separate explicit user approval before starting another task.
