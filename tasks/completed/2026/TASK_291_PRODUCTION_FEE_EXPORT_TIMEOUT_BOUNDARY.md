# TASK_291_PRODUCTION_FEE_EXPORT_TIMEOUT_BOUNDARY

## Status

Complete on 2026-06-06.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Add a production timeout boundary around the existing Confirmed Matrix Fee
Evaluation Excel export path so a real user export request cannot hang the
backend indefinitely inside Excel COM automation.

TASK_290A proved the real template smoke path can be controlled safely in a
subprocess. TASK_291 applies the same architectural idea to the production
Fee Evaluation export route while preserving the existing TASK_288/TASK_290
export semantics.

## Current Problem

`POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export`
currently calls the export application service in-process. The service builds
the fee draft or Matrix basic-fill workbook and then calls the Office workbook
gateway. If Excel COM hangs during `Workbooks.Open`, row insertion, `SaveAs`, or
close/quit, the API request can hang with the backend process.

## Scope

### In Scope

1. Add a production export runner that executes the existing
   `ConfirmedMatrixFeeEvaluationExportService.export(...)` in a subprocess.
2. Apply a hard timeout to the production route path. V1 default is 90 seconds.
3. Preserve the existing API endpoint and request/response shape.
4. Preserve both export modes:
   - `fill_mode="fee_draft"`;
   - `fill_mode="matrix_basic"`.
5. Preserve existing business behavior:
   - no-overwrite guard;
   - `allow_review_required`;
   - `Prepared by` / `Approved by`;
   - output record registration;
   - line-level traceability;
   - `.xls` / `.xlsx` COM SaveAs behavior.
6. Return an actionable timeout failure instead of hanging indefinitely.
7. Capture child stdout, stderr, exit code, elapsed time, timeout status, and
   structured error details where available.
8. Make the child process own its database transaction boundary:
   - open the session with the normal session factory;
   - commit after `service.export(command)` succeeds;
   - rollback before emitting any known or unknown error result.
9. Keep cleanup conservative:
   - do not broad-kill Excel;
   - do not delete user-requested output directories;
   - report manual cleanup warning when timeout leaves Excel state uncertain.
10. Keep a direct in-process service path available for unit tests and internal
   use where explicitly injected.
11. Add automated tests for command serialization, child-result parsing,
    timeout mapping, API timeout response, and preservation of successful
    export responses.

### Out Of Scope

1. No frontend export button or UI copy changes.
2. No fee calculation changes.
3. No Matrix basic-fill row-selection changes.
4. No workbook template mutation.
5. No new workbook-writer dependency.
6. No background job queue, polling endpoint, or async task management.
7. No broad Excel process kill.
8. No StepInstance, execution persistence, report generation, AI, permissions,
   or multi-user scope.

## Required Behavior

1. The production API dependency should use the timeout-aware export service by
   default.
2. The subprocess child should construct and call the existing
   `ConfirmedMatrixFeeEvaluationExportService` with normal repositories,
   settings, and `FeeEvaluationWorkbookGateway`.
3. The child should emit exactly one final JSON object to stdout. Any non-JSON
   stdout is treated as execution failure by the parent.
4. On success, the API response remains compatible with TASK_288/TASK_290
   response fields.
5. On timeout, the API returns an actionable `503` response whose
   `HTTPException.detail` is a stable object:
   `{message, elapsed_seconds, manual_cleanup_warning}`.
6. On child-reported business errors, the API should preserve existing status
   mapping as closely as possible:
   - validation / not-ready / overwrite conflicts -> `400`;
   - missing template/output/authority -> `404`;
   - Excel COM unavailable or timeout -> `503`;
   - malformed request path values -> `422`.
7. If timeout occurs after partial output creation, V1 does not guess whether the
   file is valid. The response must warn the user to inspect or remove the
   partial output manually.

## Acceptance Criteria

1. The existing Fee Evaluation export API returns the same successful response
   shape when the subprocess export succeeds.
2. The API maps a simulated subprocess timeout to `503` instead of hanging.
3. Timeout responses include `detail.message`, `detail.elapsed_seconds`, and
   `detail.manual_cleanup_warning`.
4. Child business errors map to the existing route status categories.
5. Parent result parsing rejects non-JSON stdout as execution failure.
6. Successful subprocess results preserve output path, output record id, warnings,
   and line traceability.
7. Successful child execution commits output record registration before the
   parent returns success.
8. Child known/unknown errors rollback before emitting the final error JSON.
9. Existing TASK_288/TASK_290 service tests continue to pass.
10. TASK_290A smoke harness tests continue to pass.
11. Scope boundary is held: no UI, no fee calculation change, no template change,
   no broad Excel kill, and no background job system.

## Implementation Notes

- The child process should run the full export service, not only the Office
  gateway. This is intentional because TASK_291 protects the real production
  path, including output record registration.
- The parent process should not register output records after the child returns;
  registration remains inside the existing export service running in the child.
- The timeout-aware service should expose the same `export(command)` method as
  `ConfirmedMatrixFeeEvaluationExportService` so the API route can remain thin.
- The in-process service should remain injectable for existing unit/integration
  tests and for future non-COM test seams.

## Completion Notes

- Added a production timeout-aware export service wrapper with the same
  `export(command)` contract as the direct TASK_288/TASK_290 service.
- Added a parent subprocess runner that serializes export commands, launches a
  child process, enforces a 90-second default timeout, rejects non-JSON stdout,
  and returns timeout results with manual cleanup guidance.
- Added a child entry point that reconstructs the direct export service, runs
  the full production export path, commits output-record registration after
  success, and rolls back on known/unknown errors before emitting final JSON.
- Updated the production API dependency to use the timeout-aware wrapper by
  default while keeping fake/direct service injection compatible.
- Updated the API route to use an export-service protocol and return structured
  timeout `503` detail with `message`, `elapsed_seconds`, and
  `manual_cleanup_warning`.
- Scope boundary held: no frontend export button, no fee calculation change, no
  Matrix basic-fill row-selection change, no workbook template mutation, no new
  workbook-writer dependency, no background job queue, and no broad Excel kill.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded backend
process-boundary change with clear existing service contracts, deterministic
timeout behavior, and strong tests available from TASK_288/TASK_290/TASK_290A.
The main risk is preserving error mapping and database/output-record behavior
across the subprocess boundary; the executable plan must therefore implement
typed serialization and focused integration tests before changing the default
dependency.
