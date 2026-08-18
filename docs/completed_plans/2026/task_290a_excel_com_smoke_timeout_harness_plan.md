# TASK_290A Excel COM Smoke Timeout Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans`
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> execution tracking.

**Goal:** Add a safe, isolated, timeout-controlled smoke harness for the real
Excel COM Matrix basic-fill Fee Evaluation export path.

**Architecture:** Keep production Fee Evaluation export behavior unchanged.
Introduce a narrow test/tooling harness with a parent runner that launches a
child process, enforces timeout, captures structured output, and limits cleanup
to harness-owned artifacts. The child process exercises the existing TASK_290
Office gateway `generate_matrix_basic_fill()` path against the formal optimized
`.xls` template.

**Tech Stack:** Python 3.11+, pytest, subprocess, pathlib, json, existing
FastAPI/application/Office gateway code, Windows Excel COM through existing
gateway behavior.

---

## Current Task Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: TASK_290 complete; next recommended controlled task is
  `TASK_290A_EXCEL_COM_SMOKE_TIMEOUT_HARNESS`.
- Why this task is allowed for planning now: user explicitly requested the
  TASK_290A plan to be implemented as task/planning documents.
- Implementation gate: do not write smoke harness code until the user explicitly
  approves this task file and plan.

## Scope Summary

### In Scope

- Test/tool-layer parent runner for subprocess timeout and result capture.
- Child smoke entry point that runs existing Matrix basic-fill export with real
  Excel COM.
- Stable step logs and structured JSON result.
- Harness-owned temp output directory and conservative cleanup.
- Tests for timeout, success parsing, command construction, and cleanup limits.

### Out Of Scope

- No production API change.
- No UI change.
- No changes to Matrix basic-fill row selection or workbook write semantics.
- No production export timeout boundary. This task makes manual/test smoke safe;
  it does not prevent a real user export request from hanging inside Excel COM.
- No broad Excel process killing.
- No template mutation.
- No Python workbook-writer dependency.

## Design Decisions

1. **Subprocess boundary**
   - Parent test/helper launches a Python child process.
   - Parent uses a hard timeout; V1 default is `90` seconds.
   - Parent captures stdout/stderr and elapsed time.

2. **Structured result**
   - Child writes no ordinary step logs to stdout.
   - Child prints exactly one final JSON object to stdout.
   - The final JSON contains a `steps` array.
   - Parent accepts only that valid JSON object for success classification.
   - If stdout contains non-JSON text or the child exits before valid JSON,
     parent returns execution failure with raw stdout/stderr.

3. **Step logs**
   - Child logs these exact step names in order when reached:
     - `start`
     - `open_template`
     - `build_request`
     - `export`
     - `save_output`
     - `close_excel`
     - `verify_output`
   - Logs include timestamp and message text.
   - Logs are accumulated in memory and emitted only inside the final JSON
     `steps` field.

4. **Template and output**
   - Default template:
     `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls`.
   - Output lives under a harness-created temp directory, for example
     `tmp/task_290a_excel_com_smoke/<run_id>/`.
   - Output suffix is `.xls`.
   - The template is opened read-only or copied through the existing export path
     without overwriting the source template.

5. **Cleanup**
   - Parent may remove only the run directory it created.
   - Parent must not delete arbitrary paths passed through output.
   - Excel process cleanup is conservative:
     - if the child process exits normally, rely on existing gateway close/quit;
     - if timeout occurs, terminate the child process;
     - do not broad-kill `EXCEL.EXE`;
     - emit `manual_cleanup_warning` if Excel might remain open.
   - Timeout acceptance does not require proving that Excel has no residual
     process. Acceptance requires avoiding unrelated Excel termination and
     reporting uncertain cleanup.

6. **Smoke target**
   - V1 child smoke directly calls `FeeEvaluationWorkbookGateway.generate_matrix_basic_fill()`.
   - It uses a minimal in-memory `MatrixBasicFillWorkbook`.
   - It does not call the FastAPI route, export service, output-record service,
     or database repositories.
   - Rationale: TASK_290A targets Excel COM/template-write hang diagnostics;
     TASK_290 already covers API/export-service behavior with non-COM tests.

## File-Level Plan

### Create

- `backend/infrastructure/office/excel_com_smoke_harness.py`
  - Parent runner dataclasses and subprocess execution helper.
  - Timeout/result parsing logic.
  - Cleanup helper constrained to harness temp roots.

- `backend/infrastructure/office/excel_com_smoke_child.py`
  - Child process entry point.
  - Builds a minimal `MatrixBasicFillWorkbook`.
  - Calls `FeeEvaluationWorkbookGateway.generate_matrix_basic_fill()`.
  - Emits final JSON result.

- `tests/unit/test_excel_com_smoke_harness.py`
  - No real Excel COM required.
  - Tests parent timeout, result parsing, command construction, and cleanup
    boundaries.

- `tests/integration/test_excel_com_smoke_harness_manual_host.py`
  - Marked/skipped by default unless explicitly enabled with an environment
    variable such as `CONNLAB_RUN_EXCEL_COM_SMOKE=1`.
  - Runs the real optimized-template smoke on a manual Windows host with Excel
    COM installed. This is not a CI integration requirement.

### Modify

- `docs/task_board.md`
  - Update only after implementation and validation pass.

- `tasks/TASK_290A_EXCEL_COM_SMOKE_TIMEOUT_HARNESS.md`
  - Update completion notes only after implementation and validation pass.

## Implementation Tasks

### Task 1: Parent Harness Types And Timeout Tests

**Files:**

- Create: `backend/infrastructure/office/excel_com_smoke_harness.py`
- Create: `tests/unit/test_excel_com_smoke_harness.py`

- [ ] Write a failing test for timeout classification.
  - Test command: `py -m pytest tests/unit/test_excel_com_smoke_harness.py::test_smoke_runner_returns_timeout_result -q`
  - Expected before implementation: import or attribute failure.

- [ ] Implement:
  - `ExcelComSmokeCommand`
  - `ExcelComSmokeResult`
  - `run_excel_com_smoke(command: ExcelComSmokeCommand) -> ExcelComSmokeResult`
  - Default timeout: `90.0`
  - timeout result fields:
    - `timed_out=True`
    - `exit_code=None`
    - `stdout`
    - `stderr`
    - `elapsed_seconds`
    - `manual_cleanup_warning`

- [ ] Re-run the timeout test and confirm it passes.

### Task 2: Child Command Construction And JSON Parsing

**Files:**

- Modify: `backend/infrastructure/office/excel_com_smoke_harness.py`
- Modify: `tests/unit/test_excel_com_smoke_harness.py`

- [ ] Write a failing test that command construction uses absolute paths and
      does not depend on current working directory.
- [ ] Write a failing test that valid child JSON becomes a success result with:
      output path, output size, step logs, elapsed time, and `timed_out=False`.
- [ ] Implement command construction using the current Python executable and
      module invocation for `backend.infrastructure.office.excel_com_smoke_child`.
- [ ] Implement JSON parsing with explicit failure when stdout contains no final
      JSON object.
- [ ] Re-run unit tests for the harness.

### Task 3: Cleanup Boundary

**Files:**

- Modify: `backend/infrastructure/office/excel_com_smoke_harness.py`
- Modify: `tests/unit/test_excel_com_smoke_harness.py`

- [ ] Write a failing test proving cleanup removes a harness-owned run directory.
- [ ] Write a failing test proving cleanup refuses to remove an external path.
- [ ] Implement cleanup by resolving both root and target paths and requiring the
      target to stay inside the harness root.
- [ ] Re-run unit tests.

### Task 4: Child Smoke Entry Point

**Files:**

- Create: `backend/infrastructure/office/excel_com_smoke_child.py`
- Create: `tests/integration/test_excel_com_smoke_harness_manual_host.py`

- [ ] Implement child argument parsing for:
      `--template-path`, `--output-dir`, `--output-name`.
- [ ] Implement step collection helper that stores steps in memory instead of
      printing ordinary logs to stdout.
- [ ] Build a minimal `MatrixBasicFillWorkbook` with two groups and at least one
      Matrix detail row per group.
- [ ] Execute `FeeEvaluationWorkbookGateway.generate_matrix_basic_fill()`.
- [ ] Verify output file exists, suffix is `.xls`, and size is greater than zero.
- [ ] Emit final JSON with:
      `status`, `output_path`, `output_size`, `steps`, `warnings`.
- [ ] On `OfficeAutomationUnavailable`, emit unavailable status and non-zero exit.
- [ ] On unexpected error, emit failure status with exception summary and non-zero
      exit.

### Task 5: Manual COM Smoke Test Gate

**Files:**

- Modify: `tests/integration/test_excel_com_smoke_harness_manual_host.py`

- [ ] Add default skip unless `CONNLAB_RUN_EXCEL_COM_SMOKE=1`.
- [ ] Use skip reason:
      `Manual Windows host Excel COM smoke; skipped in normal CI/test runs.`
- [ ] Use template path:
      `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls`.
- [ ] Use parent runner with timeout `90.0`.
- [ ] Assert success only when env var is enabled and Excel COM is available.
- [ ] Keep normal CI/unit test runs independent from real Excel COM.

### Task 6: Documentation And Board Closure

**Files:**

- Modify: `tasks/TASK_290A_EXCEL_COM_SMOKE_TIMEOUT_HARNESS.md`
- Modify: `docs/task_board.md`

- [ ] After implementation and validation, update task status to complete.
- [ ] Record validation commands and results.
- [ ] Keep next task as awaiting explicit approval; do not auto-open a new task.

## Validation Commands

Run after implementation:

```powershell
py -m pytest tests/unit/test_excel_com_smoke_harness.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_template_basic_fill_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
py -m pytest tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q
py -m pytest tests/integration/test_excel_com_smoke_harness_manual_host.py -q
git diff --check
```

The manual COM smoke test must skip by default unless explicitly enabled:

```powershell
$env:CONNLAB_RUN_EXCEL_COM_SMOKE='1'
py -m pytest tests/integration/test_excel_com_smoke_harness_manual_host.py -q
```

## Risks And Controls

- **Excel hangs:** controlled by parent subprocess timeout.
- **Unrelated Excel sessions:** no broad process kill in V1.
- **Production export hangs:** not addressed by this task; production timeout
  protection requires a separate approved task.
- **Template overwrite:** output path is always harness-owned temp output.
- **False CI failures:** real COM smoke is skipped unless explicitly enabled.
- **Silent failure:** parent captures stdout, stderr, elapsed time, timeout status,
  and child step logs.

## Stop Rule

Stop after writing this task file and plan. Do not implement TASK_290A until the
user explicitly approves implementation.
