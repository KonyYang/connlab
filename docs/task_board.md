# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_XLSX_DATE_READING_CALIBRATION_20261019",
    "summary": "Fix styled XLSX dates and epoch handling; verify calibration report in a separate copy",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Style-aware XLSX tabular date reading using 1900/1904 epoch; preserve text, ordinary numeric fields and existing read contracts; generate a separately verified report copy from supplied attachments without replacing any original.",
    "scope_paths": [
      "backend/infrastructure/office/excel_workbook_gateway.py",
      "tests/unit/test_excel_structure_probe.py",
      "tests/unit/test_external_excel_read_service.py",
      "tests/unit/test_tools_equipment_report_service.py",
      "tests/unit/test_ltr_workbook_snapshot_gateway.py",
      "tests/unit/test_excel_standard_record_layout_xlsx.py",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [
      "Shared XLSX external-authority date interpretation feeds reports and other consumers; protect source files and downstream correctness."
    ],
    "activation_head": "5429a8b4a95d377060c5b032298d20ce6ab5fee6",
    "started_at": "2026-10-19T12:10:58.287465Z",
    "updated_at": "2026-10-19T12:10:58.287465Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_CUSTOMER_REPORT_DOWNLOAD_SOURCE_20261019",
    "tier": "standard",
    "subject": "6f283c720789a3604e63f2cfac4084a15a1c7e88",
    "summary": "Use the latest matching downloaded Internal Report draft for Customer Report download fallback",
    "disposition": "completed",
    "decision_ref": "User explicitly closes the other completed task and requests continuation of XLSX date repair with a non-overwriting attachment verification copy.",
    "closed_at": "2026-10-19T12:10:58.287465Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_361A_FEE_SUMMARY_ACCEPTANCE_CONTRACT",
      "tier": "standard",
      "closed_at": "2026-09-18T03:01:50.000000Z"
    },
    {
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS_COMPLETE",
      "tier": "high_risk",
      "closed_at": "2026-09-17T11:59:24.022479Z"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.

## Pending engineering-debt tasks ( backlog / not active )

These items are not in-flight; they are recorded here for prioritization. They do not
change the `active` field above.

### TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT

**Tier:** micro
**Revised from:** the stale broad test-environment proposal discovered during TASK_361A
**Goal:** Keep the supported test entry point on the same Python runtime as ConnLab development.

The original diagnosis was rechecked before implementation:

- `C:/PythonEnvs/connlab/.venv` is Python 3.11.9 and imports Tkinter 8.6 successfully; no
  dependency installation is needed.
- Office-dependent integration tests already use the `office_integration` marker. The normal gate
  excludes them and `-Suite Office` remains the explicit installed-Office check.
- WorkBuddy or Codex temporary-directory and safe-delete restrictions are host permissions, not
  ConnLab product behavior. They must be handled by the runner environment or an explicitly
  permitted pytest temp location, not by weakening repository cleanup or test semantics.

The remaining defect was limited to `scripts/run_tests.ps1`: it invoked the ambient `py` launcher,
which selected Python 3.13.3 instead of the Python 3.11.9 environment used by ConnLab. The revised
runner defaults to `C:/PythonEnvs/connlab/.venv/Scripts/python.exe`, supports an explicit
`-PythonExe` override, fails clearly when that interpreter is missing, and preserves the existing
normal/Office split.

**Validation:** the focused runner contract passes, and the complete non-Office Python gate passes
with 2954 tests, 7 skips, and 19 Office tests deselected on Python 3.11.9. No product code,
dependencies, Office implementation, or host safety policy changed.
