# TASK_333B_LTR_WORKBOOK_UPDATE_PREVIEW_OLD_NEW_COMPARISON

## Status

Complete. Implemented after explicit user approval on 2026-06-22.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Was Allowed

`TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC` connected the Workbench `Basic Information` card `Update LTR` action to the existing LTR workbook Basic Information sync preview/commit workflow.

`TASK_333A_LTR_WORKBOOK_BACKUP_RETENTION_AND_ADMIN_GUIDE` hid local backup paths from normal operator success copy and documented manual backup recovery.

The user then clarified that the current preview is still not intuitive enough because it shows only the values that will be written. The requested improvement is to show the public-drive LTR workbook's current row values beside the Basic Information values that will replace them, so operators can confirm whether the update is correct before writing.

The user explicitly approved `TASK_333B` implementation on 2026-06-22, after the task file and plan were reviewed.

## Plan

Detailed implementation plan:

- `docs/TASK_333B_LTR_WORKBOOK_UPDATE_PREVIEW_OLD_NEW_COMPARISON_PLAN.md`

## Goal

Improve the Workbench `Update LTR` preview from a write-value list into an old/new comparison view:

- left side: current values already present in the public-drive LTR workbook target row
- right side: values that ConnLab will write from the latest confirmed Basic Information snapshot

The preview should use business field names only. It should not expose Excel column letters such as A-Q in the operator-facing table.

## Core Behavior

1. The existing `Update LTR` button remains in the Workbench `Basic Information` card.
2. Preview remains read-only: no save, no backup, no row append, no new LTR record.
3. Backend preview reads the existing target row values from the configured public-drive LTR workbook.
4. Backend preview also builds the pending values from confirmed Basic Information, as TASK_333 already does.
5. Frontend preview displays the comparison as current workbook value vs value to write.
6. Commit continues to write only the pending Basic Information-derived values after operator confirmation.
7. Commit continues to validate Basic Information version/source-signature hash from preview.

## In Scope

- Backend preview DTO extension for current workbook row values.
- Backend service/gateway mapping from target workbook row cells into the same business fields used for pending write values.
- Frontend API type updates.
- Workbench `Update LTR` preview UI changed to an old/new comparison table.
- Operator-facing copy changes so users understand the left side is current workbook content and the right side is the pending write.
- Tests for current values extraction, comparison payload, ready preview UI, blocked preview stability, and commit payload unchanged behavior.

## Out Of Scope

- No LTR workbook append/new-registration behavior.
- No initial New Project LTR registration changes.
- No Basic Information schema/API/persistence changes unless a DTO-only preview response extension is required.
- No automatic restore or rollback behavior.
- No backup retention changes.
- No setup page path changes.
- No Project Folder one-click orchestration.
- No Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- No true workbook history/audit diff beyond current row value vs pending write value.

## Acceptance Criteria

- Preview response contains current public-drive workbook row values and pending write values for the supported LTR sync business fields.
- Operator preview displays current value on the left and pending value on the right.
- Operator preview labels are business labels only, not Excel column letters.
- Preview still shows workbook path, target sheet, target row, LTR number, blockers, and warnings.
- Blocked preview remains blocked and does not show a commit action.
- Commit request/behavior remains compatible with TASK_333 version/hash confirmation semantics.
- No backup is created during preview.
- No row is appended during preview or commit.
- Tests prove current workbook values are read from the existing target row.
- Tests prove frontend preview renders old/new comparison labels and values.

## Validation

Planned validation after approval:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
cd frontend; npm test -- --run ProjectBasicInformationSummaryCard --watch=false
cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```

## Stop Point

`TASK_333B` is complete. Stop here and wait for explicit approval before starting any next task.
