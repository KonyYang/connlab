# TASK_291 Production Fee Export Timeout Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for execution tracking.

**Goal:** Protect the production Confirmed Matrix Fee Evaluation export route
from indefinite Excel COM hangs by running the existing export service in a
timeout-controlled subprocess.

**Architecture:** Keep the existing TASK_288/TASK_290 export service as the
single business implementation. Add a timeout-aware application wrapper whose
infrastructure runner launches a child process. The child reconstructs the
normal export service with repositories and `FeeEvaluationWorkbookGateway`,
executes `service.export(command)`, and emits one structured JSON result.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy session factory, subprocess,
json, pathlib, pytest, existing Office gateway / Fee Evaluation export services.

---

## Current Task Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state before this plan: TASK_290A complete; no active task.
- Current active task for this plan: `TASK_291_PRODUCTION_FEE_EXPORT_TIMEOUT_BOUNDARY`.
- Why this task is allowed now: user explicitly requested production export
  timeout boundary after TASK_290A manual smoke passed.
- Implementation gate: do not write production code until the user explicitly
  approves this TASK_291 task file and plan.

## Scope Summary

### In Scope

- Production timeout boundary for
  `POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export`.
- Subprocess execution of the existing full export application service.
- Same endpoint, same request body, same success response shape.
- Preservation of `fee_draft` and `matrix_basic` modes.
- Timeout and child-failure mapping to actionable API errors.
- Tests for command/result serialization, timeout handling, API mapping, and
  existing export behavior regression.

### Out Of Scope

- No frontend export button or Workbench UI.
- No fee calculation, Matrix selection, or workbook layout changes.
- No template mutation.
- No new workbook writer dependency.
- No async job queue, polling, cancellation endpoint, or progress UI.
- No broad Excel process kill.

## Existing Code Facts

- API route:
  `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
- Direct export service:
  `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
- Dependency wiring:
  `backend/api/dependencies.py`
- TASK_290A smoke subprocess parent/child:
  - `backend/infrastructure/office/excel_com_smoke_harness.py`
  - `backend/infrastructure/office/excel_com_smoke_child.py`

The current production API route depends on
`get_confirmed_matrix_fee_evaluation_export_service()` and then calls
`service.export(...)` in-process. This means Excel COM can still block the API
request if the workbook gateway hangs.

## Design Decisions

1. **Protect the full production path**
   - The child process calls `ConfirmedMatrixFeeEvaluationExportService.export`.
   - It does not call only `FeeEvaluationWorkbookGateway`.
   - Output record registration stays inside the existing service in the child.
   - The child owns the database transaction because it does not run inside
     FastAPI's `get_session()` dependency generator.
   - The child commits after successful `service.export(command)` and rolls back
     before emitting any known or unknown error JSON.

2. **Keep the API route thin**
   - The route continues to call `service.export(command)`.
   - The default dependency returns a timeout-aware service.
   - Tests can still override the dependency with fake direct services.

3. **Use a protocol-compatible wrapper**
   - Add a wrapper with the same `export(command)` method.
   - The wrapper delegates to a subprocess runner.
   - On success, it returns `ExportConfirmedMatrixFeeEvaluationResult`.
   - On timeout/failure, it raises existing or new export exceptions that the
     API route maps cleanly.
   - The API route dependency type should be relaxed to an export protocol or
     type alias with `export(command)` instead of the concrete direct service
     class.

4. **Final JSON only**
   - Child stdout must contain exactly one JSON object.
   - The JSON encodes either:
     - `status="success"` plus serialized result; or
     - `status="business_error" | "not_found" | "unavailable" | "value_error" |
       "execution_failure"` plus error details.
   - Parent treats non-JSON stdout as execution failure.

5. **Conservative cleanup**
   - Parent terminates the child through `subprocess.run(..., timeout=...)`.
   - Parent does not broad-kill Excel.
   - Timeout result includes `manual_cleanup_warning`.
   - Parent does not delete user-requested output paths because those are
     business artifacts, not harness-owned temp files.

6. **V1 timeout**
   - Default timeout: 90 seconds.
   - Keep it as a constant or settings-backed constructor value.
   - No UI configuration in this task.

## Proposed File Responsibilities

- Create `backend/application/confirmed_matrix_fee_evaluation_export_timeout_service.py`
  - Defines the timeout-aware service wrapper.
  - Defines runner protocol.
  - Maps runner results to existing export result / exceptions.

- Create `backend/infrastructure/office/fee_evaluation_export_subprocess_runner.py`
  - Parent-side subprocess runner.
  - Serializes `ExportConfirmedMatrixFeeEvaluationCommand`.
  - Launches child with timeout.
  - Parses final JSON.
  - Returns a typed runner result.

- Create `backend/infrastructure/office/fee_evaluation_export_child.py`
  - Child entry point.
  - Parses command JSON path or inline JSON argument.
  - Builds database session and production export service using existing
    repositories and `FeeEvaluationWorkbookGateway`.
  - Executes the existing service.
  - Commits on successful export and rolls back before emitting known/unknown
    error JSON.
  - Emits exactly one JSON object to stdout.

- Modify `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
  - Add `ConfirmedMatrixFeeEvaluationExportTimeoutError` if a distinct timeout
    exception is preferred over reusing unavailable error.
  - Add small result/command serialization helpers only if they belong next to
    the existing DTOs and do not bloat the service.

- Modify `backend/api/dependencies.py`
  - Default `get_confirmed_matrix_fee_evaluation_export_service()` returns the
    timeout-aware wrapper.
  - Add a private helper for building the direct in-process service for child
    process and tests.

- Modify `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
  - Map timeout errors to `503`.
  - Keep the success response DTO unchanged.
  - For timeout only, return `HTTPException.detail` as a stable object with
    `message`, `elapsed_seconds`, and `manual_cleanup_warning`.
  - Change the route service parameter annotation from the concrete direct
    service to a protocol/type alias that only requires `export(command)`.

- Test `tests/unit/test_fee_evaluation_export_subprocess_runner.py`
  - Parent runner command construction, timeout handling, JSON parsing, and
    non-JSON failure.

- Test `tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py`
  - Wrapper converts runner success to existing result and maps timeout /
    status categories to exceptions.

- Modify `tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py`
  - Add timeout mapping test through dependency override.
  - Keep existing success and status tests passing.

- Optional test `tests/integration/test_fee_evaluation_export_child.py`
  - Exercise child entry point with fake service seam only if implementation can
    do this without real Excel COM.

## Data Contracts

### Serialized Command

The parent sends the existing command fields:

```json
{
  "project_id": "P1",
  "template_path": "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls",
  "output_dir": "D:/some/output",
  "output_file_name": "fee.xls",
  "overwrite": false,
  "allow_review_required": true,
  "prepared_by": "Operator",
  "approved_by": null,
  "connlab_user": null,
  "fill_mode": "matrix_basic"
}
```

### Child Success JSON

```json
{
  "status": "success",
  "result": {
    "project_id": "P1",
    "output_path": "D:/some/output/fee.xls",
    "output_format": "xls",
    "status": "generated",
    "confirmed_matrix_id": "cmv-1",
    "confirmed_revision": 1,
    "pricing_rule_version_id": "fee_rules_v2026_06_03",
    "pricing_effective_from": "2026-06-03",
    "prepared_by": "Operator",
    "approved_by": null,
    "output_record_id": "por-1",
    "line_traceability": [],
    "warnings": ["Matrix basic fill only."]
  },
  "stderr": ""
}
```

### Child Error JSON

```json
{
  "status": "not_found",
  "error_type": "ConfirmedMatrixFeeEvaluationExportNotFoundError",
  "error_message": "Template does not exist: D:/missing.xls"
}
```

Timeout is parent-produced, not child-produced:

```json
{
  "status": "timeout",
  "timed_out": true,
  "elapsed_seconds": 90.0,
  "manual_cleanup_warning": "Fee Evaluation export timed out. Excel cleanup is uncertain; inspect Excel and the output file manually."
}
```

### Timeout HTTP Detail

V1 keeps the successful response model unchanged. Timeout failures use a stable
object in `HTTPException.detail`:

```json
{
  "message": "Fee Evaluation export timed out after 90.0 seconds.",
  "elapsed_seconds": 90.0,
  "manual_cleanup_warning": "Fee Evaluation export timed out. Excel cleanup is uncertain; inspect Excel and the output file manually."
}
```

API tests must assert this object shape for timeout responses.

## Error Mapping

Parent/wrapper maps statuses as follows:

- `success` -> return `ExportConfirmedMatrixFeeEvaluationResult`.
- `business_error` -> raise `ConfirmedMatrixFeeEvaluationExportError`.
- `not_found` -> raise `ConfirmedMatrixFeeEvaluationExportNotFoundError`.
- `unavailable` -> raise `ConfirmedMatrixFeeEvaluationExportUnavailableError`.
- `value_error` -> raise `ValueError`.
- `timeout` -> raise `ConfirmedMatrixFeeEvaluationExportTimeoutError` or
  `ConfirmedMatrixFeeEvaluationExportUnavailableError` with timeout details.
- `execution_failure` / non-JSON stdout -> raise
  `ConfirmedMatrixFeeEvaluationExportUnavailableError`.

The API maps timeout/unavailable to `503`.

## Implementation Tasks

### Task 1: Add Timeout Exception And Serialization Helpers

**Files:**
- Modify: `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
- Test: `tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py`

- [ ] Add `ConfirmedMatrixFeeEvaluationExportTimeoutError(RuntimeError)`.
- [ ] Add private serialization helpers if needed:
  - command to JSON-safe dict;
  - result from JSON-safe dict;
  - line traceability from JSON-safe dict.
- [ ] Write tests that reconstruct an `ExportConfirmedMatrixFeeEvaluationResult`
  from a payload with one line trace and one warning.

Expected focused test command:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py -q
```

### Task 2: Add Parent Subprocess Runner

**Files:**
- Create: `backend/infrastructure/office/fee_evaluation_export_subprocess_runner.py`
- Test: `tests/unit/test_fee_evaluation_export_subprocess_runner.py`

- [ ] Define `DEFAULT_FEE_EXPORT_TIMEOUT_SECONDS = 90.0`.
- [ ] Define `FeeEvaluationExportSubprocessResult` dataclass with:
  - `status`;
  - `timed_out`;
  - `exit_code`;
  - `elapsed_seconds`;
  - `stdout`;
  - `stderr`;
  - `payload`;
  - `error_message`;
  - `manual_cleanup_warning`.
- [ ] Implement command serialization using an absolute temporary command JSON
  file under workspace `tmp/fee_evaluation_export_subprocess/`.
- [ ] Implement child command:
  `sys.executable -m backend.infrastructure.office.fee_evaluation_export_child --command-json <path>`.
- [ ] Use `subprocess.run(..., timeout=timeout_seconds, capture_output=True,
  text=True, check=False)`.
- [ ] On timeout, return `status="timeout"`, `timed_out=True`, raw stdout/stderr,
  elapsed seconds, and manual cleanup warning.
- [ ] Parse exactly one JSON object from stdout on normal exit.
- [ ] Reject invalid/non-JSON stdout as `execution_failure`.
- [ ] Clean only the parent-created command JSON file/run directory.

Focused tests:

```powershell
py -m pytest tests/unit/test_fee_evaluation_export_subprocess_runner.py -q
```

### Task 3: Add Timeout-Aware Application Wrapper

**Files:**
- Create: `backend/application/confirmed_matrix_fee_evaluation_export_timeout_service.py`
- Test: `tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py`

- [ ] Define a runner protocol with `run(command)`.
- [ ] Implement `ConfirmedMatrixFeeEvaluationExportTimeoutService.export(command)`.
- [ ] Convert runner `success` payload into
  `ExportConfirmedMatrixFeeEvaluationResult`.
- [ ] Map timeout to timeout/unavailable exception with manual cleanup guidance.
- [ ] Map business/not-found/unavailable/value errors to existing exception
  categories.
- [ ] Preserve `line_traceability` and warnings on success.

Focused tests:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py -q
```

### Task 4: Add Production Child Entry Point

**Files:**
- Create: `backend/infrastructure/office/fee_evaluation_export_child.py`
- Modify: `backend/api/dependencies.py`
- Test: `tests/unit/test_fee_evaluation_export_subprocess_runner.py`
- Test: `tests/integration/test_fee_evaluation_export_child_transaction.py`

- [ ] Child parses `--command-json`.
- [ ] Child loads the command payload and creates
  `ExportConfirmedMatrixFeeEvaluationCommand`.
- [ ] Child opens a database session through the existing storage/session
  infrastructure using `with session_factory() as session`.
- [ ] Child builds the direct `ConfirmedMatrixFeeEvaluationExportService` with:
  - `ConfirmedMatrixFeeDraftService`;
  - `ConfirmedMatrixAuthorityRepository`;
  - `ProjectOutputRecordService`;
  - `FeeEvaluationWorkbookGateway`.
- [ ] Child calls `service.export(command)`.
- [ ] Child calls `session.commit()` after `service.export(command)` succeeds
  and before emitting success JSON.
- [ ] Child calls `session.rollback()` before emitting known business error JSON.
- [ ] Child calls `session.rollback()` before emitting unknown execution failure
  JSON.
- [ ] Child emits exactly one JSON object to stdout.
- [ ] Child catches known business exceptions and emits mapped status JSON.
- [ ] Child catches unexpected exceptions and emits `execution_failure`.
- [ ] Add a transaction-focused test with a fake session object proving success
  commits and known/unknown errors rollback. If the child construction is not
  directly injectable, add a small internal helper so the test can exercise the
  transaction boundary without real Excel COM.

Implementation note:

- If `backend/api/dependencies.py` already has all direct construction logic,
  extract a small private helper such as
  `_build_direct_confirmed_matrix_fee_evaluation_export_service(session)`.
  The public dependency should remain the production timeout wrapper after
  Task 5.

### Task 5: Wire Default API Dependency To Timeout Wrapper

**Files:**
- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
- Test: `tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py`

- [ ] Change `get_confirmed_matrix_fee_evaluation_export_service()` to return
  `ConfirmedMatrixFeeEvaluationExportTimeoutService` by default.
- [ ] Configure it with `FeeEvaluationExportSubprocessRunner`.
- [ ] Keep test dependency overrides working because the route only needs an
  object with `export(command)`.
- [ ] Map `ConfirmedMatrixFeeEvaluationExportTimeoutError` to HTTP `503`.
- [ ] Add API test for simulated timeout response and assert:
  - `response.status_code == 503`;
  - `response.json()["detail"]["message"]` contains timed out text;
  - `response.json()["detail"]["elapsed_seconds"]` is numeric;
  - `response.json()["detail"]["manual_cleanup_warning"]` contains manual
    cleanup guidance.
- [ ] Relax the route service annotation to a protocol or alias such as
  `FeeEvaluationExportServicePort` so the default timeout wrapper and existing
  test fakes match the route contract.
- [ ] Confirm existing API tests still pass.

Focused tests:

```powershell
py -m pytest tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q
```

### Task 6: Regression And Manual Verification

**Files:**
- Modify: `docs/task_board.md`
- Optional update after implementation: `tasks/TASK_291_PRODUCTION_FEE_EXPORT_TIMEOUT_BOUNDARY.md`

- [ ] Run unit tests:

```powershell
py -m pytest tests/unit/test_fee_evaluation_export_subprocess_runner.py tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py -q
```

- [ ] Run export API regression:

```powershell
py -m pytest tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q
```

- [ ] Run TASK_288/TASK_290 service regression:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_confirmed_matrix_fee_template_basic_fill_service.py -q
```

- [ ] Run TASK_290A harness regression:

```powershell
py -m pytest tests/unit/test_excel_com_smoke_harness.py tests/integration/test_excel_com_smoke_harness_manual_host.py -q
```

The manual host smoke remains skipped unless `CONNLAB_RUN_EXCEL_COM_SMOKE=1`.

- [ ] Run formatting check:

```powershell
git diff --check
```

- [ ] Update task board only after implementation and validation:
  - mark TASK_291 complete;
  - record validation commands and results;
  - name the next recommended task.

## Risks And Controls

- **Risk: child cannot access the same database/settings.**
  Control: child uses the existing settings/session construction path; tests
  should cover command construction and API timeout behavior without requiring
  real Excel.

- **Risk: successful child output record exists but parent result parsing fails.**
  Control: final JSON only, typed parser tests, and execution-failure message
  that tells the user to inspect output records/output file manually.

- **Risk: timeout leaves Excel or partial output behind.**
  Control: no broad kill; return `503` with manual cleanup warning and partial
  output inspection guidance.

- **Risk: API dependency tests become brittle.**
  Control: route continues depending on an object with `export(command)`, so
  existing fake services remain usable.

## Self-Review Checklist For Plan Approval

- Scope matches user request: production export timeout boundary, not UI.
- Full production export service is protected, not only workbook gateway smoke.
- API response shape is preserved on success.
- Timeout maps to actionable `503`.
- No broad Excel kill is introduced.
- No fee calculation, workbook layout, or template behavior changes are included.
- Tests cover timeout behavior without requiring real Excel COM in CI.
