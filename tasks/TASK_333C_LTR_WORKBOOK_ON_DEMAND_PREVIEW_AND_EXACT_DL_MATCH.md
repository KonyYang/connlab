# TASK_333C_LTR_WORKBOOK_ON_DEMAND_PREVIEW_AND_EXACT_DL_MATCH

## Status

Proposed. Task and plan created after the user explicitly approved establishing `TASK_333C` on 2026-06-23.

Implementation is not approved yet. Do not write implementation code until the user explicitly approves `TASK_333C` implementation and the task board authorizes this task as active.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

`TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC` added the Workbench `Update LTR` entry point and connected it to the existing Basic Information -> LTR workbook sync API.

`TASK_333B_LTR_WORKBOOK_UPDATE_PREVIEW_OLD_NEW_COMPARISON` made the preview show current workbook values beside pending Basic Information-derived values.

After smoke use, the user clarified that the Workbench `LTR Information` card should behave as an on-demand workbook update tool rather than an always-visible Basic Information summary. The user also required exact DL matching so a row for `DL-2026-05-011` can never be confused with `DL-2026-05-011A`.

The user approved creating a new task named `TASK_333C_LTR_WORKBOOK_ON_DEMAND_PREVIEW_AND_EXACT_DL_MATCH`.

## Plan

Detailed implementation plan:

- `docs/TASK_333C_LTR_WORKBOOK_ON_DEMAND_PREVIEW_AND_EXACT_DL_MATCH_PLAN.md`

## Goal

Turn the Workbench `LTR Information` card into a focused LTR workbook update surface:

- show no always-visible Basic Information/LTR field summary before the operator requests a preview
- fetch the public-drive LTR workbook row only when the operator clicks the preview/update action
- compare the current workbook row against the latest confirmed Basic Information-derived write values
- visually highlight fields where the current workbook value differs from the value to write
- only allow writing when the target DL row is an exact, unique match

## Core Behavior

1. The Workbench card remains visible and is titled `LTR Information`.
2. The main action remains visible even before Basic Information is confirmed, but it is disabled until Basic Information is confirmed.
3. Clicking the action performs a read-only preview against the configured LTR workbook path.
4. The preview displays workbook metadata, exact target row metadata, and current-vs-write comparison rows.
5. Rows with different current/write values are highlighted.
6. If the workbook row is already up to date, commit is disabled and the operator sees a clear up-to-date state.
7. If no exact DL row is found, or multiple exact DL rows exist, preview is blocked.
8. Commit revalidates the exact DL match and preview version/hash before writing.

## In Scope

- Workbench `LTR Information` card behavior and copy.
- Frontend preview display and difference highlighting.
- Frontend action disabled/enabled behavior for confirmed vs unconfirmed Basic Information.
- Backend exact DL lookup semantics for the LTR workbook Basic Information sync path.
- Backend duplicate exact-DL blocker.
- Backend stale/row-mismatch protection at commit time.
- API/DTO additions needed for changed-row metadata or exact-match blocker details.
- Tests for on-demand UI, disabled action, diff highlighting, exact match, duplicate match, and commit revalidation.

## Out Of Scope

- No initial New Project LTR registration behavior changes.
- No LTR workbook append/new-record behavior.
- No setup page path changes.
- No backup retention changes.
- No automatic restore/rollback UI.
- No Basic Information schema/API/persistence changes unless a preview DTO field is required.
- No Project Folder output changes.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- `LTR Information` no longer renders the Basic Information/LTR summary field list before preview.
- The preview/update action remains visible but is disabled until Basic Information is confirmed.
- Clicking the enabled action opens a read-only preview and only then reads the public-drive LTR workbook.
- Preview comparison rows follow the business LTR workbook order already established in `TASK_333B`.
- Rows where current workbook value and pending write value differ are visibly highlighted.
- Preview blocks when no exact DL row exists.
- Preview blocks when more than one exact DL row exists.
- `DL-2026-05-011` does not match `DL-2026-05-011A`, `DL-2026-05-011 ` after trimming is acceptable, but prefix/contains matching is not.
- Commit rechecks Basic Information version/source-signature hash and exact DL target row before writing.
- If the row is already up to date, the UI communicates that state and does not offer a commit button.
- Preview still creates no workbook backup and performs no save.

## Validation

Planned validation after implementation approval:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
cd frontend; npm test -- --run ProjectBasicInformationSummaryCard --watch=false
cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```

If the implementation touches the workbook transaction gateway directly, also run the focused gateway tests that cover LTR workbook row lookup and transaction behavior.

## Stop Point

Stop after task/plan review. Do not implement until the user explicitly approves `TASK_333C` implementation.
