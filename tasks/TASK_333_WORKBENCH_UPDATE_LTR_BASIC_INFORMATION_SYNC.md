# TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed For Planning

`TASK_331_TEST_RECORD_AND_LTR_EXCEL_CONSUME_BASIC_INFORMATION` added backend-only LTR workbook Basic Information sync preview and commit routes. It intentionally left the frontend `Update LTR` preview/commit workflow out of scope.

The user requested a plan for making the Workbench `Update LTR` button update the same public-drive LTR registration workbook configured on the setup page.

The user approved implementation after plan review. `docs/task_board.md` must mark this task as the current active task before code changes proceed.

## Plan

Detailed implementation plan:

- `docs/TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC_PLAN.md`

## Goal

Connect the Workbench `Basic Information` card `Update LTR` button to the existing backend LTR workbook Basic Information sync preview/commit workflow so operators can refresh the already registered LTR workbook row from the latest confirmed Basic Information snapshot.

## Core Behavior

1. The `Update LTR` button remains visible in the Workbench `Basic Information` card.
2. The button is disabled until Basic Information has a latest confirmed snapshot.
3. Clicking the enabled button performs a read-only preview against the LTR registration workbook path configured in setup.
4. Preview shows workbook path, target sheet, target row, LTR number, and target row values to be written before writing.
5. Commit requires operator confirmation and uses preview version/hash to prevent stale writes.
6. Commit updates only the existing registered LTR row.
7. The flow never requests a new LTR number, never appends a workbook row, and never creates a new local LTR record.

## In Scope

- Frontend typed API client functions for existing LTR Basic Information sync preview and commit routes.
- Workbench Basic Information card UI state for preview, blocked preview, commit, success, and error feedback.
- Reuse of existing backend sync routes from TASK_331.
- Tests for disabled/enabled button behavior, preview display, commit payload, blocked preview, stale/lock error copy, and successful completion.

## Out Of Scope

- No backend Office write logic redesign.
- No setup page path UI changes.
- No initial LTR application or registration flow rewrite.
- No workbook append behavior.
- No Project Folder one-click orchestration.
- No Basic Information schema/API/persistence changes.
- No Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- `Update LTR` is always visible in the Workbench `Basic Information` card.
- `Update LTR` is disabled when Basic Information is not confirmed.
- Clicking `Update LTR` calls `GET /api/projects/{project_id}/ltr-workbook/basic-information-sync/preview`.
- Ready preview displays workbook path, target sheet, row, LTR number, and the columns that will be written.
- Blocked preview displays blockers without attempting commit.
- Confirming the preview calls `POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/commit` with `operator_confirmed`, `preview_acknowledged`, expected Basic Information version, and expected source-signature hash from preview.
- Successful commit displays row/sheet/backup feedback.
- Stale Basic Information and workbook-lock errors are shown as actionable operator messages.
- Existing backend TASK_331 sync tests continue to pass.
- Frontend Workbench and Basic Information tests cover the new button workflow.

## Validation

Planned validation after approval:

```powershell
cd frontend; npm test -- --run ProjectBasicInformation ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
git diff --check
```

## Stop Point

TASK_333 is complete. Stop here and wait for a separate explicitly approved next task.

After implementation and validation, update `docs/task_board.md` and stop. Do not proceed to Project Folder orchestration, report generation, backend Office rewrite, or any next task without separate approval.
