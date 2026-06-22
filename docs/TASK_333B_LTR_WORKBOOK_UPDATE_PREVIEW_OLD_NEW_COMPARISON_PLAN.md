# TASK_333B LTR Workbook Update Preview Old/New Comparison Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

No implementation task is active after `TASK_333A_LTR_WORKBOOK_BACKUP_RETENTION_AND_ADMIN_GUIDE` completion.

`TASK_333B_LTR_WORKBOOK_UPDATE_PREVIEW_OLD_NEW_COMPARISON` is a proposed candidate task requested by the user. It must not be implemented until the user explicitly approves this task and the task board is updated to authorize it.

## Goal

Make `LTR workbook update preview` easier and safer for non-programmer lab operators by showing what will be replaced:

- current value from the public-drive `LTR.xlsx` target row
- pending value that ConnLab will write from the latest confirmed Basic Information snapshot

The UI should use business field labels and avoid exposing Excel column letters (`A-Q`) in the operator-facing comparison table.

## Existing Behavior

`TASK_333` added the Workbench `Basic Information` card `Update LTR` workflow.

Current preview:

- calls `GET /api/projects/{project_id}/ltr-workbook/basic-information-sync/preview`
- locates the existing registered LTR row
- opens the workbook read-only
- returns target sheet/row, LTR number, blockers/warnings, and values to be written
- does not write, save, append, or create backup

Current weakness:

- the operator can see the pending write values, but cannot see the existing workbook row values that will be replaced
- this makes it harder to catch wrong-row, stale-workbook, or unexpected-field mapping issues before commit

## Product Decision

The preview should become a comparison surface, not a raw Excel-column surface.

Recommended layout:

```text
Field                         Current LTR workbook value          Value to write
Test Result                   OK                                  NG
Test Fee                      12531                               12531
Sub-contract                  No                                  No
Remarks (PO)                  NA                                  PO-123
...
```

This matches ConnLab principles:

- Preview before write
- State before action
- Traceability before convenience
- No technical stack language in user-facing UI

## Supported Business Fields

Use the same supported fields as the Workbench Basic Information card and LTR sync mapping, with business labels:

1. Test Result
2. Test Fee
3. Sub-contract
4. Remarks (PO)
5. Location
6. Sample deposition
7. Project Type
8. Test Type
9. Requested by
10. Project Leader
11. Failed item

If the backend already maps more fields for LTR sync, keep the implementation table-driven so later fields can be added without duplicating UI logic, but do not expose unused A-Q column labels.

## Backend Design

### DTO Shape

Extend the existing preview response with comparison rows.

Proposed API response addition:

```python
class LtrWorkbookBasicInformationSyncComparisonValue(BaseModel):
    field_name: str
    label: str
    current_value: Any
    pending_value: Any
```

Preview response should include:

```python
comparison_values: list[LtrWorkbookBasicInformationSyncComparisonValue]
```

Keep existing `columns` or `target_row_values` fields temporarily for compatibility only if frontend or tests still consume them. New UI should prefer `comparison_values`.

### Service Flow

In `backend/application/ltr_workbook_basic_information_sync_service.py`:

1. Load latest registered LTR and confirmed Basic Information as today.
2. Open workbook read-only through the existing transaction gateway preview path.
3. Locate target sheet and row by LTR number as today.
4. Build pending write values using the existing mapper.
5. Read current workbook row values for the same mapped business fields.
6. Return `comparison_values` aligned by business field label.

### Gateway / Mapping Boundary

Do not put UI labels or ad hoc column parsing in API routes.

Preferred structure:

- keep workbook column lookup / target cell reading inside the existing infrastructure Office gateway or a narrow mapper helper already used by sync
- keep business labels in application-level DTO construction or a dedicated mapping table
- avoid duplicating column-to-field mapping in frontend

### Preview Safety

Preview must remain read-only:

- no workbook save
- no backup creation
- no lock file creation
- no row append
- no local LTR record creation

Commit remains unchanged except for any DTO compatibility needed for stale-preview validation.

## Frontend Design

### API Client

Update `frontend/src/api/client.ts` types to include:

```ts
export type LtrWorkbookBasicInformationSyncComparisonValue = {
  field_name: string;
  label: string;
  current_value: unknown;
  pending_value: unknown;
};
```

Preview DTO should expose `comparison_values`.

### Workbench UI

In `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`:

- replace raw write-column preview list with a compact comparison table
- left column header: `Current LTR workbook`
- right column header: `Value to write`
- field labels in first column
- show empty values as `-`
- keep commit button disabled for blocked previews
- keep existing lock/stale/missing-row error mapping

Avoid a modal for the first implementation. Use the existing inline preview area inside the Basic Information card so the workflow remains local to the action.

### Copy

Suggested ready preview copy:

```text
Review the current LTR workbook row before updating it.
```

Suggested confirm action:

```text
Confirm update
```

Do not mention Excel columns or A-Q labels in normal UI.

## File-Level Changes

Expected files:

- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `backend/api/routes_ltr_workbook_basic_information_sync.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `docs/task_board.md`

Optional if existing mapping boundaries require it:

- `backend/infrastructure/office/ltr_workbook_transaction_gateway.py`
- a narrow application mapper module for LTR Basic Information comparison rows

## Risks

- If workbook current-row extraction duplicates write mapping, future mapping drift could reappear. Mitigation: use one mapping table for both current and pending values.
- If current workbook cells contain formulas or formatted values, preview should display the same business-readable value users would inspect in Excel. Mitigation: use the existing workbook reading approach and add tests for plain values.
- If existing frontend tests assume the old pending-only preview list, update them to assert the comparison table instead of keeping duplicate UI paths.
- If the preview DTO keeps old fields for compatibility, clearly mark the comparison DTO as the preferred frontend path.

## Validation Plan

Backend:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
```

Frontend:

```powershell
cd frontend; npm test -- --run ProjectBasicInformationSummaryCard --watch=false
cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
```

Repository hygiene:

```powershell
git diff --check
```

Manual smoke after implementation approval:

1. Open a project with confirmed Basic Information and registered LTR.
2. Click `Update LTR` in the Workbench Basic Information card.
3. Verify preview shows current workbook values on the left and pending write values on the right.
4. Confirm update.
5. Reopen preview and verify current workbook values match the last written values.

## Scope Guard

Do not implement:

- automatic rollback
- backup restore UI
- workbook append/new LTR registration
- setup page redesign
- Basic Information persistence/schema changes unrelated to preview DTO
- Project Folder output changes
- report generation
- StepInstance or execution persistence
- AI, permissions, LAN/server, or multi-user scope

## Stop Point

This plan is complete for review only. Stop and wait for explicit approval before implementation.
