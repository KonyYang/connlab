# TASK_353B Registered LTR Workbook Row Preview - Developer Evidence

Task ID: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`
Lane: `registered-ltr-workbook-row-preview`
Role: Developer
Date: 2026-07-07
Status: implementation complete - Reviewer/QA/Integrator accepted

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`.
- Why allowed: Planner reconciliation records Reviewer plan gate passed, Developer planning-first complete, Reviewer implementation-readiness passed, and user-approved implementation authorization.

## Source-Of-Truth Note

- `docs/task_board.md` and TASK_353B reconciliation evidence record `TASK_353B` as implementation authorized / pending Developer implementation.
- This Developer pass implements only the registered-LTR read-only workbook row preview and keeps existing Basic Information sync commit gating unchanged.

## Facts Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context, `PRODUCT.md`, `DESIGN.md`, and product reference
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_planner.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`
- `backend/application/specified_ltr_workbook_authority_preview_service.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `backend/api/routes_ltr_workbook_basic_information_sync.py`
- `backend/api/routes_new_project_completion.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- Focused backend tests for TASK_349A specified preview and Basic Information LTR sync.

## Planning Decisions

- Future implementation should add a new project-scoped read-only service/API instead of weakening `LtrWorkbookBasicInformationSyncService.preview(...)`.
- The new endpoint should be `GET /api/projects/{project_id}/ltr-workbook/registered-row-preview`.
- Input should be `project_id` only. Backend resolves the latest registered local LTR record and reads the public workbook row.
- The service should use `open_read_only_transaction()` only. It must not call write transactions, short transactions, backup, save, commit, or workbook authority writeback.
- The response should reuse TASK_349A-style row values and field labels but should not include `preview_ack` or any commit-oriented fields.
- UI should show two separate actions:
  - `LTR workbook row preview`: read-only, registered-LTR based, no Basic Information Confirm required.
  - `Update LTR from Basic Information`: existing Basic Information sync/update flow, copy clarified, still confirmed-state gated and write-capable only through the existing commit path.
- V1 visual treatment should stay compact in the Basic Information side card, with a read-only table and concise blocker/not-found copy. A modal is not required unless Reviewer asks for it.
- Read-only preview should remain available in stopped/closed readonly lifecycle states because it is non-mutating.

## Exact Future May Touch

Backend:

- `backend/application/registered_ltr_workbook_row_preview_service.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py` only for safe exact-DL lookup helper extraction/reuse.
- `backend/application/specified_ltr_workbook_authority_preview_service.py` only for safe row-value helper extraction/reuse.
- `backend/api/routes_ltr_workbook_registered_row_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts` only if registered-LTR availability needs an additional prop/model field.
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx` only if needed to pass that prop.
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` and `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts` only if Workbench-side wiring cannot use existing SummaryCard inputs.

Tests/docs:

- `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
- `tests/integration/test_registered_ltr_workbook_row_preview_api.py`
- Existing TASK_349A / Basic Information sync regression tests if helper extraction occurs.
- TASK_353B Developer evidence.

## Must Not Touch / Locked Confirmation

- No LTR workbook write, commit, backup, save, or authority writeback in the new read-only preview.
- No existing Basic Information sync/update confirmed-state gate change.
- No Intake specified-LTR or local duplicate semantics changes.
- No schema/migration.
- No Matrix parser/import, Fee calculation/export, Folder Actions/public folder workflow, Report, StepInstance, AI, permissions, LAN/server, or multi-user scope.
- No real workbook/folder mutation.
- No release/settings/template residual cleanup.
- No `.agents/**`, `docs/project_management/**`, remote push.

## Validation Plan

Backend:

- Registered-LTR preview returns workbook row values without confirmed Basic Information.
- No registered LTR returns a readable blocker.
- Missing workbook row returns `not_found`.
- Duplicate exact DL rows are blocked.
- Read-only preview never calls write/commit/backup/save paths.
- Existing Basic Information sync preview/commit tests still pass and still require confirmed Basic Information.
- TASK_349A specified-LTR preview tests still pass if row-value helpers are shared.

Frontend:

- Summary card renders separate read-only preview and update actions.
- Read-only row preview can be available while Basic Information is unconfirmed.
- Read-only preview table has no `Confirm update` / Commit control.
- Existing update action copy is clarified and remains confirmed-state gated.
- Blocked/not-found messages are concise and business-readable.

Commands for future implementation:

- `py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q`
- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q`
- `npm test -- ProjectBasicInformationSummaryCard --run`
- `npm run build`
- `git diff --check`
- trailing whitespace scan
- forbidden-scope/status scan

## Files Changed In This Planning-First Pass

- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`

No product source, tests, API client, backend service, route, schema, frontend component, or CSS files were changed.

## Implementation Summary

- Added a project-id-only read-only backend service and API route:
  - `GET /api/projects/{project_id}/ltr-workbook/registered-row-preview`
  - Backend resolves the latest local registered LTR record for the project.
  - The service uses `open_read_only_transaction()` only and returns TASK_349A-style workbook row values.
  - Response contains no preview ack, commit, backup, save, or workbook write fields.
- Added frontend API helper `previewRegisteredLtrWorkbookRow(...)`.
- Split the Basic Information side-card actions:
  - `LTR workbook row preview`: read-only, enabled when a registered LTR number is available.
  - `Update LTR from Basic Information`: existing write-capable sync/update flow, still gated by confirmed Basic Information.
- Wired Workbench active Matrix right rail to pass the registered project reference into `ProjectBasicInformationSummaryCard`.
- Preserved existing Basic Information sync preview/commit behavior and `Confirm update` flow.

## Implementation Files Changed

TASK_353B-owned files:

- `backend/application/registered_ltr_workbook_row_preview_service.py`
- `backend/api/routes_ltr_workbook_registered_row_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
- `tests/integration/test_registered_ltr_workbook_row_preview_api.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`

Touched and then reverted to no net diff:

- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`

## Test-First Checkpoint

- Added backend unit/API tests before service/route implementation.
- Initial backend focused test run failed on missing `registered_ltr_workbook_row_preview_service` and missing dependency provider, as expected.
- Updated frontend SummaryCard tests before component implementation.
- Initial frontend focused test run failed because only the old `LTR update preview` action existed, as expected.

## Validation Results

- `py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q`
  - Result: 6 passed.
- `py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q`
  - Result: 39 passed.
- `npm test -- ProjectBasicInformationSummaryCard --run`
  - Result: 10 passed.
- `py -m py_compile backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py backend/api/dependencies.py backend/api/main.py`
  - Result: passed.
- `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- `git diff --check -- <TASK_353B package files>`
  - Result: passed with existing LF/CRLF warnings only.
- Trailing whitespace scan on TASK_353B package files
  - Result: no matches.
- Forbidden-scope scan
  - Result: new read-only preview service/route do not call write transaction, commit, save, or backup paths. Test safety assertions verify `open_transaction()` and `run_short_transaction()` are not used.

## Forbidden Scope / External Residual Status

- No LTR workbook write/commit/backup/save endpoint or field was added for the registered row preview.
- No Basic Information sync commit gate was weakened.
- No Intake specified-LTR/local duplicate semantics, schema/migration, Matrix, Fee, Folder Actions, Report, StepInstance, AI, permissions, LAN/server, or multi-user behavior was changed by this pass.
- Existing external residuals remain visible in `git status` under TASK_352 PDF import, release/desktop packaging, settings/LTR/template resources, Word/Fee output tests, `frontend/src/workbench.css`, `docs/task_board.md`, and related untracked release/task docs. They are not owned by TASK_353B and were not cleaned or packaged here.

## Planning Validation

- Required docs/evidence exist:
  - `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
  - `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
- `git diff --check -- docs/task_353b_registered_ltr_workbook_row_preview_plan.md docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
  - Result: passed.
- Trailing whitespace scan on the two touched TASK_353B docs
  - Result: no matches.
- Targeted status
  - Result: this planning-first pass changed only TASK_353B plan/developer evidence. The status command also shows pre-existing unrelated backend/frontend/test/release/settings residuals, which remain excluded from TASK_353B.

## External Residuals Excluded

The worktree contains unrelated residuals in release/settings/template/desktop packaging paths, TASK_352 PDF import files, TASK_355 paths, Word/Fee output files, and unrelated backend/frontend tests. These remain outside this planning-first pass and must not be packaged with TASK_353B unless separately approved.

## Next Role

Reviewer implementation gate, QA gate, and Integrator packaging/readiness accepted the TASK_353B package. Remote push is not authorized.

## Blocking Summary

None.

## Developer Fix Pass - Reviewer B1

Date: 2026-07-07

Status: fix pass complete - Reviewer/QA/Integrator accepted

### B1 Root Cause

- `RegisteredLtrWorkbookRowPreviewService.preview(...)` wrapped domain validation errors but did not wrap arbitrary workbook gateway/open/read exceptions.
- A workbook missing/locked/Office/read failure could therefore escape the service and become an unhandled API failure instead of the planned readable `blocked` preview.

### B1 Fix

- Added a non-domain exception catch around the read-only workbook preview path.
- The service now returns:
  - `status = "blocked"`
  - `message/blockers = "Unable to read LTR workbook for preview: <error>"`
  - no row values, no commit fields, no backup/save/write fields.
- Added focused regressions for:
  - read-only transaction open failure.
  - workbook row read failure.
  - API response mapping for a workbook read/open failure.

### B1 Files Changed

- `backend/application/registered_ltr_workbook_row_preview_service.py`
- `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
- `tests/integration/test_registered_ltr_workbook_row_preview_api.py`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`

No frontend behavior, Basic Information sync commit behavior, LTR workbook write/commit/backup/save behavior, schema, Matrix, Fee, Folder Actions, Intake, Projects registry, or external residual files were changed by this fix pass.

### B1 Validation

- `py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q`
  - Result: 9 passed.
- `py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q`
  - Result: 42 passed.
- `npm test -- ProjectBasicInformationSummaryCard --run`
  - Result: 10 passed.
- `py -m py_compile backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py`
  - Result: passed.
- `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- `git diff --check -- backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
  - Result: passed.
- Trailing whitespace scan on B1 touched files
  - Result: no matches.

### B1 Next Role

Reviewer re-gate, QA gate, and Integrator packaging/readiness accepted the B1 fix. Remote push is not authorized.
