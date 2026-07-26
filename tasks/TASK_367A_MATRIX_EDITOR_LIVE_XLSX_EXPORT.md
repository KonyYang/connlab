# TASK_367A_MATRIX_EDITOR_LIVE_XLSX_EXPORT

Status: implementation authorized / pending controlled docs-only governance checkpoint
Lane: `matrix-editor-live-xlsx-export`
Owner role: Planner / Orchestrator governance checkpoint
Implementation authorization: authorized; execution blocked pending governance checkpoint and clean-primary gate
Date: 2026-07-26

## Current Phase / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current work: Planner final source-of-truth reconciliation after Reviewer
  implementation-readiness pass.
- Why allowed: Reviewer passed implementation-readiness and the User explicitly approved
  TASK_367A product/test implementation.
- This Planner pass remains docs-only. Product/test edits and implementation worktree creation
  must wait for the controlled governance checkpoint and clean-primary verification.

## Frozen Implementation-Readiness Contract

Developer planning-first completed the required refinement without expanding May Touch:

1. Endpoint and DTO are exact in the plan: ordered Groups, ordered rows, and rectangular ordered
   per-Group cells. Caps are 64 Groups, 512 qualifying rows, 16,384 total Group cells, plus
   explicit per-string limits. Oversized, empty, nonqualifying, duplicate, or nonrectangular
   input returns typed `422` before gateway invocation and produces no workbook bytes.
2. Filename ownership and sanitization:
   - use the read-only `deriveProjectReference()` precedence:
     latest LTR, then `project_no`, then `TMP-<first 8 project-id characters uppercased>`;
   - do not invent a second project-reference fallback;
   - the backend applies the frozen Windows-invalid/control replacement, trailing space/period,
     reserved-device-name, 120-code-point, and deterministic `Project` fallback rules;
   - keep the frozen `Matrix Draft <local YYYYMMDDHHmmss>.xlsx` suffix.
3. Export availability:
   - reuse the existing selected-Group step-format/sequence gate;
   - disabled-reason priority is lifecycle message, busy, no Group, existing step error, then
     no qualifying row;
   - lifecycle read-only disables export, uses `lifecycleReadonlyView.message` as the visible or
     tooltip reason, and must not dispatch a request;
   - autosave/CAS state is not an enablement dependency.
4. Exact bounded RED/GREEN nodes, line budgets, rollback, and package isolation are frozen in
   the plan and Developer evidence.

## Goal

Add `导出 Matrix` beside `Import Matrix`. It exports a click-time snapshot of the current
unconfirmed Matrix Editor state as `.xlsx`, without requiring Confirm Matrix.

The export must follow the observed reference workbook, include only checked Groups, map
`Samples Quantity (PCS)` to `Sample size`, map `Test Days` to `Time`, retain a `Fee` row with all
Fee values blank, and never write Matrix, project, database, or source-workbook state.

## User-Confirmed Contract

1. Export current UI state; Confirm Matrix is not a prerequisite.
2. The reference workbook is read-only:
   `D:\TestFlowManager\Projects\DL-2025-02-054 EK500 Connector Qualification Testing\matrix.xlsx`.
3. Export only checked Groups, matching `Test record`.
4. Keep `Fee` but leave all Fee values empty.
5. Map Samples Quantity to `Sample size` and Test Days to `Time`.
6. Place the command beside Import Matrix without desktop or 514 px overflow.
7. Use the same browser Blob download mechanism as Test Record. Do not add a native Save As
   bridge.
8. `Time` must equal the Matrix Editor's current displayed `Test Days` text; it must not be
   converted into a separate numeric contract.
9. Include only non-information test rows that contain steps in at least one checked Group.

## Confirmed Repository Facts

1. Discovery baseline is clean `master` at
   `033e530c2d6a9c01c210f35b938678672b6449ad`; the index is empty.
2. `MatrixEditorWorkspace.tsx` owns current `editableRows`, `groupColumns`, `sampleValues`,
   schedule calculation, and session/CAS state.
3. `showSelectedGroupsOnly` is view filtering only. Export selection must use
   `group.isSelected`.
4. Existing Test Record builds a checked-Group request from current local UI state and triggers
   a browser Blob download without requiring Confirm Matrix.
5. `Test Days` is calculated deterministically from current row `dayExpression` values and
   checked Group step tokens.
6. Desktop integration supports open/folder dialogs only; there is no native Save As bridge.
7. No Matrix XLSX export endpoint, projection, or writer exists.

## Reference Workbook Baseline

Read-only artifact-tool inspection found:

- one sheet `Sheet`, used range `A1:G5`;
- no formulas, drawings, or merged cells;
- headers `Test Item`, `Section`, `Test Method`, `Condition`, `Requirement`, `1`, `Notes`;
- one example test row, then `Sample size`, `Time`, `Fee`;
- Fee has only its A-column label and otherwise blank cells;
- gray `#CCCCCC` header/A labels, Calibri 11, centered/wrapped cells, thin borders;
- widths A 20, B 8, D/E 20, remaining columns at workbook defaults; row height 15.

The reference is a one-time layout authority. It must not become a runtime dependency,
configured template, copied source, or writable artifact.

## Frozen Zero-Write And Snapshot Contract

- Clicking export captures one immutable JSON snapshot from the current React render.
- It consumes local values even when autosave is pending or the last saved session is older.
- It does not call draft/session save, Confirm Matrix, source replacement, audit, or output
  registration.
- No draft id, saved signature, confirmed revision, generation, or CAS token is required because
  the operation writes no authority.
- Edits after the click do not alter the in-flight output.
- The backend constructs XLSX bytes in memory and returns them directly. It must not write to
  `data/**`, project folders, public drives, temporary project outputs, or the reference file.

## Reconciled User Decisions

1. Delivery uses the existing browser Blob download path and `Content-Disposition` handling.
   PyWebView, Windows native Save As, and desktop bridge changes are locked.
2. Each selected Group's `Time` cell is the exact page display:
   ```${formatPlanningDays(scheduleCalculation.groupDays[group.id] ?? 0)} d```.
   - integers display without decimals;
   - non-integers display at most two decimals with trailing zeros removed;
   - selected Groups are initialized to zero, so blank/no contributing Day values display and
     export as `0 d`;
   - the backend receives this display string and must not parse, convert, round, or recompute it.
3. Export only rows where `isSampleRow` is false and at least one checked Group's current cell
   contains a step.
   - The existing selected-Group step-format/sequence gate remains authoritative.
   - When that gate passes, nonblank selected-Group cells are valid step cells and can drive row
     inclusion without introducing a second parser.
   - Unchecked Groups, information/sample rows, and rows unrelated to checked Groups are omitted.
4. `Show selected groups only` remains presentation-only and never changes export authority.

## Proposed Workbook Contract

1. Sheet name is `Sheet`.
2. Columns A:E are the five fixed fields, F onward are checked Groups in current order, and the
   final column is `Notes`.
3. Group headers use trimmed current labels, with current Group key as fallback.
4. Only checked-Group step rows are written, in current Matrix row order.
5. `Sample size`, `Time`, and `Fee` follow data rows in that order.
6. Sample value is the current Group sample expression; blank stays blank and nothing is inferred.
7. Time is the exact current page display string defined above, including `0 d`.
8. Every non-label Fee cell is truly blank: no zero, formula, cached value, comment, or metadata.
9. Notes remains blank because Matrix Editor has no matching editable Notes field.
10. No formulas, macros, links, drawings, hidden sheets, or defined names are added.
11. Default filename follows the existing Fee/Test Record browser-download vocabulary:
    `<latest LTR or project_no or projectId> Matrix Draft <local YYYYMMDDHHmmss>.xlsx`, with
    Windows-invalid filename characters replaced by `_`.

## Proposed Future May Touch

This is the exact future scope for Reviewer plan review. Implementation remains unauthorized.

### Frontend

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - exact import/current-state/button wiring only; current size 4093 lines.
- `frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.ts` (new, <=220).
- `frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.ts` (new, <=180).
- `frontend/src/features/matrix-editor/MatrixEditorXlsxExportButton.tsx` (new, <=100).
- `frontend/src/api/client.ts`, exact DTO/download hunk only; current size 4600 lines.
- `frontend/src/workbench.css`, optional exact target-action responsive hunk <=20 additions only
  if controlled 514 px validation proves it necessary.
- `frontend/src/features/projectIdentity.ts` remains read-only; its exported project-reference
  precedence may be consumed but not changed.

### Backend

- `backend/api/main.py`, exact router registration hunk.
- `backend/api/routes_matrix_editor_live_xlsx_export.py` (new, <=220).
- `backend/api/dependencies_matrix_editor_live_xlsx_export.py` (new, <=100).
- `backend/application/matrix_editor_live_xlsx_export_service.py` (new, <=300).
- `backend/infrastructure/office/matrix_editor_live_xlsx_workbook_gateway.py` (new, <=300).

`backend/api/dependencies.py` is excluded; bounded composition avoids its 2248-line surface.

### Tests

- `tests/unit/test_matrix_editor_live_xlsx_export_service.py` (new, <=300).
- `tests/unit/test_matrix_editor_live_xlsx_workbook_gateway.py` (new, <=300).
- `tests/integration/test_matrix_editor_live_xlsx_export_api.py` (new, <=350).
- `frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.test.ts` (new, <=280).
- `frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.test.tsx` (new, <=250).
- `frontend/src/features/matrix-editor/MatrixEditorXlsxExportButton.test.tsx` (new, <=220).

The existing 1934-line `MatrixEditorWorkspace.test.tsx` is read-only and only rerun.

### Governance

- this task;
- `docs/task_367a_matrix_editor_live_xlsx_export_plan.md`;
- `docs/lane_evidence/TASK_367A_matrix-editor-live-xlsx-export_planner.md`;
- `docs/lane_evidence/TASK_367A_matrix-editor-live-xlsx-export_reconciliation_planner.md`;
- exact TASK_367A board hunks.

## Must Not Touch / Locked Paths

- Matrix persistence, autosave, CAS, discard, revision, source replacement, and Confirm Matrix.
- Confirmed Matrix, Method authority, Measurement Plan, Point Profile, Fee, Test Record, LTR,
  project lifecycle, output registration, schema/database/migrations, Settings, seeds/manifests.
- `MatrixWorkspaceActionGroups.tsx`; it is unused and must not be revived opportunistically.
- `backend/desktop/**` and every native path-picker/Save-As bridge.
- Existing oversized tests except read-only regression execution.
- The source workbook and all real DB/project/public-drive files, attachments, generated
  artifacts, `dist_release/**`, external residuals, cleanup, restore, discard, stage, commit,
  and push.

## Future Validation Gate

1. Projection tests: checked-Group order, current unsaved values, valid-step row inclusion,
   information/unrelated-row exclusion, fallback labels, exact `0 d`/integer/decimal display
   strings, and blank Fee cells.
2. Workbook tests reload bytes and assert sheet/dimensions/headers/dynamic Groups/styles/widths,
   no formulas/macros/links, and all Fee values blank.
3. API tests use in-memory payloads and prove no DB/file/output mutation.
4. Frontend tests prove one request, busy/error/retry, Blob revoke, filename, and no save/confirm.
5. Read-only Matrix Editor regressions, frontend build, and backend py_compile.
6. Controlled disposable browser smoke at desktop and 514 px: adjacent command, keyboard access,
   no overlap/overflow, clean console, successful download, and typed error.
7. Clean worktree/package whitelist, diff/trailing, line budgets, no-real-data, and staging checks.

## Future Worktree / Branch Plan

Reviewer implementation-readiness and explicit User product/test implementation approval are
complete. Before implementation:

- first assemble and create a controlled local docs-only governance checkpoint containing the
  approved task/plan/evidence/board state;
- verify the primary worktree and index are clean;
- only then may Orchestrator create or reuse branch
  `lane/task-367a-matrix-editor-live-xlsx-export` and sibling worktree
  `D:\PythonProject\connlab-task-367a-matrix-editor-live-xlsx-export`;
- base is the then-current accepted `master`;
- primary remains Planner/Integrator only;
- Reviewer reviews base-to-lane HEAD, QA validates the reviewed clean commit, and Integrator
  records residual ownership.

No implementation worktree is created before the controlled governance checkpoint and clean
primary verification.

## Rollback

Remove the new bounded route/service/gateway/frontend/tests and exact wiring hunks. There is no
data migration, persistent artifact, or authority rollback.

## Definition Of Ready / Stop Point

The selected-Group/row rules, exact Time display mapping, browser delivery, reference layout,
live-state ownership, zero-write boundary, candidate architecture, locks, tests, rollback, and
worktree plan are repository-backed. Definition of Ready is complete for plan review.

Stop after this final source-of-truth reconciliation and route the exact docs-only governance
checkpoint package gate. Product/test implementation is authorized but cannot start, and no
implementation worktree may be created, until the governance checkpoint exists and the primary
worktree/index are clean.
