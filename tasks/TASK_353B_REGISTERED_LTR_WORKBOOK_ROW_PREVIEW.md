# TASK_353B Registered LTR Workbook Row Preview

Status: complete/accepted - Integrator packaging/readiness accepted
Lane: `registered-ltr-workbook-row-preview`
Owner role: Developer implementation pass, then Reviewer / QA / Integrator gates
Created: 2026-07-07

## Goal

Add a read-only Project Workbench / Basic Information side action that lets an operator preview the public-drive LTR workbook row for a project that already has a registered DL/LTR number.

This is not the existing Basic Information-to-LTR workbook update flow. The new action is for registration verification only: it reads the workbook row and displays the row fields; it does not require confirmed Basic Information and it must not expose Commit/write behavior.

## Authorization Checkpoint

Repository source-of-truth is reconciled for Developer implementation:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`.
- Reviewer implementation-readiness passed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`.
- User approved reconciliation and Developer implementation.

This checkpoint authorized only the TASK_353B implementation scope below. The lane is now complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness.

## User-Confirmed Rules

- Existing `LTR update preview` is currently a confirmed Basic Information to LTR workbook sync preview and requires Basic Information confirmation.
- That existing update/sync flow is still valid, but the copy should be clarified as `Update LTR from Basic Information`.
- A separate read-only row preview should be available whenever the project has a registered DL/LTR number.
- The read-only preview should query the configured public-drive LTR Excel workbook and display a business-field table similar to the TASK_349A specified LTR authority preview.
- No Basic Information Confirm is required for the read-only row preview.
- The read-only row preview must not write to the LTR workbook, must not show Commit, and must not change local project data.

## Repository Evidence

- `backend/application/specified_ltr_workbook_authority_preview_service.py` already provides a read-only workbook row preview concept and the business labels for Project Type, Description P/N, Test Item, Test Type, Requested by, Location, Project Leader, Test Result, Failed item, Sample deposition, Sub-contract, Test Fee, and Remarks (PO).
- `backend/application/ltr_workbook_basic_information_sync_service.py` already locates an exact registered DL row through `LtrRecordRepository`, read-only workbook transactions, and exact DL matching.
- `backend/api/routes_ltr_workbook_basic_information_sync.py` currently exposes preview/commit/open-readonly routes for Basic Information sync; preview/commit are tied to confirmed Basic Information.
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx` currently labels the write-capable sync entry as `LTR update preview`, disables it until Basic Information is confirmed, and renders a comparison table plus `Confirm update`.
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx` already renders a workbook row table in a read-only confirmation modal for Intake specified LTR authority preview.
- `frontend/src/api/client.ts` already owns typed client helpers for both specified LTR authority preview and Basic Information LTR sync.

## Proposed UX / API Boundary

Backend:

- Add a project-scoped read-only preview endpoint, suggested:
  - `GET /api/projects/{project_id}/ltr-workbook/registered-row-preview`
- The endpoint resolves the latest registered local LTR record for the project, opens the configured LTR workbook read-only, finds the exact DL row in the parsed year sheet, and returns:
  - `status`: `found`, `not_found`, or `blocked`
  - `project_id`
  - `ltr_number`
  - `message`
  - `workbook_path`
  - `sheet_name`
  - `row_number`
  - `row_values` using the TASK_349A business labels
  - `blockers`
  - `warnings`
- The endpoint must not return a write/commit ack and must not call any write transaction, backup, save, or commit service.

Frontend:

- Add a read-only side action label such as `LTR workbook row preview`.
- Enable it when a registered LTR is known for the project; otherwise show disabled copy such as `Registered LTR required`.
- Render the row in a read-only table/modal/panel with no Commit button.
- Rename/clarify the existing write-capable sync action to `Update LTR from Basic Information`.
- Keep the existing update/sync flow gated by confirmed Basic Information and keep its commit controls separate.

## May Touch

Future Developer implementation may touch only the following, unless Reviewer plan gate narrows or explicitly expands scope:

- `backend/application/registered_ltr_workbook_row_preview_service.py` or equivalent new read-only application service.
- `backend/application/ltr_workbook_basic_information_sync_service.py` only for safe extraction/reuse of exact registered-DL row lookup primitives, without changing existing sync/commit behavior.
- `backend/application/specified_ltr_workbook_authority_preview_service.py` only for safe extraction/reuse of row value label mapping, without changing TASK_349A Intake semantics.
- `backend/api/routes_ltr_workbook_registered_row_preview.py` or equivalent project-scoped read-only route.
- `backend/api/dependencies.py` and `backend/api/main.py` for dependency/route registration only.
- `frontend/src/api/client.ts` for typed read-only preview DTO/client helper only.
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`.
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`.
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts` and `ProjectBasicInformationWorkspace.tsx` only if the Basic Information page itself needs the same action.
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` and `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts` only if required to pass registered-LTR presence into the side panel.
- Focused backend tests under `tests/unit/` and `tests/integration/`.
- Focused frontend tests for the summary card / Workbench side action.
- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`.
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`.
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_*.md`.
- `docs/task_board.md` through normal lane flow.

## Must Not Touch

- LTR workbook write/commit semantics except preserving existing Basic Information sync behavior.
- LTR workbook authority writeback, backup, or commit code paths for the new read-only preview.
- Intake specified LTR completion semantics or local duplicate resolution semantics.
- Basic Information persistence schema or confirmed record schema.
- Project identity authority from TASK_353A except display integration/copy needed by this lane.
- Matrix parser/import, Fee calculation/default-fill/export, Folder Actions/public folder workflow, Report, StepInstance, AI, permissions, LAN/server, multi-user.
- Real public-drive workbooks or real public-drive/user folders in tests.
- Release/settings/template residual cleanup, `.agents/**`, `docs/project_management/**`, or unrelated dirty files.
- Remote push.

## Locked Paths

- Real LTR workbook files and public-drive roots.
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` unless Reviewer explicitly accepts a backend read-only gateway bugfix.
- Database schema/migration files.
- Matrix/Fee/Folder Actions runtime modules outside focused tests.
- Release/packaging paths and current external residual files.
- `.agents/**` and `docs/project_management/**`.

## Validation Gate Draft

Backend:

- Registered LTR project can read the workbook row without confirmed Basic Information.
- Project without registered LTR returns a blocked/404-style result and frontend action stays disabled or shows a clear blocker.
- Missing workbook row returns `not_found` / readable blocker.
- Read-only preview does not call write transaction, backup, save, commit, or Basic Information confirmed snapshot requirements.
- Existing Basic Information sync preview/commit tests still pass.
- TASK_349A specified LTR authority preview tests still pass if shared row label helpers are extracted.

Frontend:

- Side action is visible and enabled when a registered LTR exists.
- Clicking opens a read-only row table with no Commit/Confirm update button.
- Existing Basic Information sync action copy is clarified as `Update LTR from Basic Information`.
- Existing update/sync remains disabled until Basic Information is confirmed and retains its commit gate.
- Not-found / blocked states are visible and do not mutate state.

Commands:

- Focused pytest for new service/API plus existing Basic Information sync and TASK_349A preview regressions.
- `npm test -- ProjectBasicInformationSummaryCard --run` and any focused Workbench tests changed by wiring.
- `npm run build`.
- `git diff --check`, trailing whitespace scan, forbidden-scope/status scan.

## Merge Gate Draft

- Reviewer plan gate must pass before Developer planning or implementation.
- Developer must update developer evidence with implementation files and validation output.
- Reviewer implementation gate must confirm the read-only/write-capable action split.
- QA/browser smoke should verify a registered project can open the row preview without Basic Information Confirm, and the update action still requires confirmed Basic Information.
- Integrator packaging must exclude release/settings/template residuals and any unrelated dirty files.
- Remote push is not authorized.

## Definition Of Ready

Reviewer plan gate: passed.

Developer planning-first: complete.

Reviewer implementation-readiness: passed.

User approval: reconciliation and Developer implementation approved.

TASK_353B is complete/accepted locally after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness. Recommended next role: Orchestrator/User routing decision for the next approved lane. Remote push is not authorized.
