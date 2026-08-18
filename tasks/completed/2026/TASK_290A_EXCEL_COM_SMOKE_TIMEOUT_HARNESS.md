# TASK_290A_EXCEL_COM_SMOKE_TIMEOUT_HARNESS

## Status

Complete on 2026-06-05.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Create a controlled Excel COM smoke timeout harness for the TASK_290 Matrix
basic-fill Fee Evaluation export path.

TASK_290 closed without repeating real-template Excel COM smoke because the
temporary smoke attempt had no subprocess timeout, step-level logs, or reliable
cleanup boundary. TASK_290A exists only to make that smoke path safe and
diagnosable.

This task does not protect the production export request path from Excel COM
hangs. If user-facing export timeout protection is required, that must be a
separate production-boundary task.

## Scope

### In Scope

1. Add a test/tool-layer harness that runs real Excel COM smoke in an isolated
   subprocess.
2. Use a hard timeout; V1 default is 90 seconds.
3. Emit stable step logs for:
   - start;
   - open template;
   - build request;
   - export;
   - save output;
   - close Excel;
   - verify output.
4. Use a harness-owned temporary output directory under the workspace.
5. Verify successful output:
   - file exists;
   - suffix is `.xls`;
   - size is greater than zero.
6. Capture subprocess stdout, stderr, exit code, elapsed time, and timeout
   status.
7. Classify failure as actionable unavailable / timeout / execution failure.
8. Clean only harness-created temporary files and directories.
9. Attempt Excel cleanup only when the harness can safely identify processes it
   created; otherwise emit a manual cleanup warning.
10. Add automated tests for parent harness behavior without requiring real Excel
    COM.
11. The child smoke path directly calls the Office gateway
    `generate_matrix_basic_fill()` with a minimal Matrix basic-fill workbook.
    It does not exercise the API/export-service/output-record stack; those are
    covered by non-COM TASK_290 tests.

### Out Of Scope

1. No production API changes.
2. No UI changes.
3. No fee calculation changes.
4. No change to TASK_290 Matrix basic-fill behavior.
5. No template mutation or template optimization.
6. No new workbook-writer dependency.
7. No broad process-kill behavior.
8. No StepInstance, execution persistence, report generation, AI, permissions, or
   multi-user scope.

## Required Template

Use the formal TASK_289/TASK_290 template baseline:

```text
D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls
```

The harness must never overwrite this file.

## Acceptance Criteria

1. The smoke runner executes the real Matrix basic-fill export in a subprocess
   when explicitly invoked.
2. A hung smoke run terminates through parent timeout control instead of hanging
   the main process indefinitely.
3. Timeout results include `timed_out=True`, elapsed time, stdout, stderr, and
   collected step logs when available.
4. Successful smoke results include output path, output size, elapsed time, and
   step logs.
5. The harness validates that generated output is `.xls`, exists, and is
   non-empty.
6. Cleanup is limited to harness-owned temporary paths.
7. Excel process cleanup is conservative and never kills broad unrelated Excel
   sessions.
8. Timeout acceptance does not require proving that no Excel process remains; it
   requires proving that unrelated Excel sessions are not killed and that
   uncertain cleanup produces `manual_cleanup_warning`.
9. If Excel COM is unavailable, the result is actionable and does not suggest a
   Python workbook-writer fallback.
10. Existing TASK_290 automated tests remain unchanged in behavior.

## Completion Notes

- Added a parent subprocess harness for manual Excel COM smoke runs.
- Added a child entry point that directly calls
  `FeeEvaluationWorkbookGateway.generate_matrix_basic_fill()` with a minimal
  `MatrixBasicFillWorkbook`.
- Child stdout emits exactly one final JSON object; step logs are emitted inside
  the JSON `steps` array.
- Parent timeout returns `status="timeout"`, preserves stdout/stderr, and emits
  `manual_cleanup_warning` instead of broad-killing Excel.
- Cleanup is constrained to harness-owned run directories.
- Manual host smoke test is skipped unless `CONNLAB_RUN_EXCEL_COM_SMOKE=1`.
- This task does not protect production export requests from Excel COM hangs.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded
test/tooling-infrastructure slice with clear process boundaries, deterministic
timeouts, and no product-behavior design ambiguity. The main risk is Windows COM
process lifecycle handling, which is manageable when isolated behind tests and
explicit cleanup limits.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Also read
`docs/project_management/TASK_EXECUTION_SKILL.md` and run
`docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until this task file and
`docs/task_290a_excel_com_smoke_timeout_harness_plan.md` are reviewed and
explicitly approved by the user.
