# TASK_356A LTR Read-Only Workbook Open Existing Excel Plan

Status: Completed
Created: 2026-07-07
Task: `TASK_356A_LTR_READONLY_WORKBOOK_OPEN_EXISTING_EXCEL`

## Current Task Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task board stop point: `TASK_355C_FEE_EVALUATION_UPDATE_FEE_VALIDATION_UX` is complete.
- Why this plan is allowed now: the user reported a Workbench LTR read-only open regression from the current page. Project protocol requires a reviewable plan before implementation.
- Implementation status: completed after user approval.

## Problem

On the Project Workbench Basic Information area, `LTR update preview` can successfully read the configured LTR workbook and display row values. Clicking `Open read-only workbook` then fails with:

```text
The LTR workbook cannot be opened safely. Close Excel copies of the workbook and retry.
```

Observed page context:

- URL: `http://localhost:5173/projects/ce15026d119f408f80970ea7077f6e41`
- LTR: `DL-2026-01-002`
- workbook path shown by preview: `D:\LabShare\LTR\LTR_updated.xlsx`

## Root Cause From Code Inspection

Relevant code:

- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `backend/infrastructure/office/ltr_workbook_readonly_open_gateway.py`
- `tests/unit/test_ltr_workbook_readonly_open_gateway.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`

Current backend flow:

1. `open_readonly_at_ltr` opens a read-only workbook transaction to locate the exact DL row.
2. It then calls `ExcelComLtrWorkbookReadonlyOpenGateway.open_at_cell`.
3. The gateway calls `_raise_if_workbook_already_open(...)` before creating its own Excel read-only viewer.
4. `_raise_if_workbook_already_open(...)` scans the active Excel instance and raises if the same workbook path is already open.
5. The frontend maps `already open`, `locked`, `being used`, or `access is denied` to the generic safe-open blocker message.

This is intentionally conservative behavior from TASK_334F, but it is too strict for the operator expectation in this bug: preview has already proven the workbook is readable, and the button should help inspect the target workbook/row even when Excel already has that workbook open.

## Objective

Make `Open read-only workbook` useful when the target LTR workbook is already open in Excel by removing the pre-open `already open` blocker and always attempting ConnLab's own isolated read-only Excel inspection window first. The fix must not weaken LTR write/update safety and must not mutate or save the public-drive workbook.

## Scope

Allowed:

- Backend read-only open gateway behavior.
- Focused unit/integration tests for the read-only open path.
- Optional frontend error copy only if backend still needs a distinct operator-facing message.
- Task board update after approved implementation completes.

Not allowed:

- LTR workbook write, commit, append, backup, or public-drive authority behavior.
- LTR preview row matching semantics.
- Basic Information persistence/schema.
- Settings path/password UI.
- Fee Evaluation, Matrix, Project Folder, Report, Test Record, lifecycle, packaging, or real workbook data changes.

## Design

### Preferred Behavior

Always use ConnLab's own isolated read-only Excel inspection path:

1. Do not reuse any user-opened Excel workbook/window.
2. Do not block merely because the same workbook path is already open in another Excel instance.
3. Create a new isolated Excel instance with `DispatchEx("Excel.Application")`.
4. Open the target workbook in that ConnLab-owned instance with `ReadOnly=True`.
5. In the ConnLab-owned read-only inspection instance, clear filters, unhide rows/columns, activate the target worksheet, and jump to the exact DL cell.
6. Never call `Save`, `SaveAs`, write cell values, or alter LTR commit/update behavior.
7. Only return an error if Excel, the file lock, the password prompt, protected view, network share state, or another real Office condition prevents the read-only open/select flow.

This keeps the user-owned Excel window untouched while still giving the operator a clean inspection window where the target row is visible.

### API / Data Contract

No API contract change is required.

Existing endpoint remains:

```text
POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/open-readonly
```

Existing response shape remains unchanged:

- `project_id`
- `ltr_number`
- `workbook_path`
- `sheet_name`
- `row_number`
- `column_number`
- `selected_cell`
- `message`

### Implementation Notes

Modify `backend/infrastructure/office/ltr_workbook_readonly_open_gateway.py`:

- Remove or bypass `_raise_if_workbook_already_open(...)` from the `open_at_cell` flow.
- Keep `DispatchEx("Excel.Application")` as the only viewer path for this button.
- Keep `_open_workbook_readonly(...)` as the place that attempts `Workbooks.Open(..., ReadOnly=True, ...)`.
- Keep `_prepare_sheet_for_review(...)` after a successful ConnLab-owned read-only open.
- Preserve `LtrWorkbookReadonlyOpenError` for genuinely unsafe states.
- Avoid adding any ActiveObject/GetActiveObject reuse path for this workflow.

## Test Plan

### Unit Tests

Update `tests/unit/test_ltr_workbook_readonly_open_gateway.py`:

- Replace the old assertion that exact active workbook blocks.
- Add/adjust tests proving `open_at_cell` does not call `GetActiveObject` or any pre-open active-workbook blocker.
- Add a gateway-level fake COM test proving:
  - `DispatchEx("Excel.Application")` is still used,
  - `Workbooks.Open(..., ReadOnly=True, ...)` is attempted without inspecting or reusing any active Excel workbook/window,
  - the ConnLab-owned workbook/worksheet/cell is activated/selected,
  - viewer cleanup is applied only after the ConnLab-owned read-only open succeeds.
- Keep existing tests for:
  - A1 address generation,
  - read-only open keyword shape,
  - configured password,
  - unreadable unrelated workbook entries.

### Integration Tests

Update `tests/integration/test_ltr_workbook_basic_information_sync_api.py` only if the backend error/status behavior changes. If API contract is unchanged and errors still map correctly, no broad API test changes are needed.

### Validation Commands

```powershell
py -m pytest tests\unit\test_ltr_workbook_readonly_open_gateway.py -q
py -m pytest tests\unit\test_ltr_workbook_basic_information_sync_service.py tests\integration\test_ltr_workbook_basic_information_sync_api.py -q
```

Optional manual smoke after rebuild/restart:

1. Open the project Workbench page.
2. Click `LTR update preview`.
3. Keep `D:\LabShare\LTR\LTR_updated.xlsx` already open in Excel.
4. Click `Open read-only workbook`.
5. Expected: ConnLab opens a separate read-only Excel inspection window and selects the exact DL cell instead of showing the generic safe-open blocker.

## Risks

- Excel usually allows the same workbook to be opened in another instance as read-only, but it can still fail when the workbook is in edit mode, exclusively locked, blocked by protected view, blocked by password prompts, or unavailable through a network share problem. In that case the existing actionable error style should remain.
- A separate ConnLab-owned read-only instance avoids polluting the user's existing Excel window while still allowing filter clearing/unhide for inspection.
- Manual smoke with real Excel may require closing blocking Excel dialogs. Automated tests can cover the code path, but not every Office UI state.

## Completion Criteria

- Existing already-open workbook no longer blocks before attempting read-only open.
- The workflow always attempts ConnLab's isolated `DispatchEx` read-only open path.
- ConnLab-owned read-only inspection still clears filters/unhides and selects the exact DL cell.
- When the workbook is not already open, existing `DispatchEx`, `Workbooks.Open` arguments, view cleanup, and cell selection behavior remain unchanged.
- Focused tests pass.
- `docs/task_board.md` is updated only after approved implementation completes.

## Completion Summary

Completed: 2026-07-07

- Removed the read-only open pre-check that inspected active Excel workbooks and blocked when the target LTR workbook was already open.
- Kept the read-only viewer flow on ConnLab's isolated `DispatchEx("Excel.Application")` path.
- Preserved `Workbooks.Open(..., ReadOnly=True, ...)`, configured password behavior, best-effort filter clearing/unhide, and exact DL cell selection in the ConnLab-owned inspection window.
- Removed the unused active-workbook blocker helper to avoid reconnecting the old behavior later.

Validation:

```powershell
py -m pytest tests\unit\test_ltr_workbook_readonly_open_gateway.py -q
py -m pytest tests\unit\test_ltr_workbook_basic_information_sync_service.py tests\integration\test_ltr_workbook_basic_information_sync_api.py -q
```

Results:

- `7 passed`
- `30 passed`
