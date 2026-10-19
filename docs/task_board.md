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
  "state": "ready_for_close",
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
    "updated_at": "2026-10-19T15:00:24.579488Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_XLSX_DATE_READING_CALIBRATION_20261019",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_XLSX_DATE_READING_CALIBRATION_20261019",
      "subject": "e8018c96ca0ef5c5de3872c2c51da6e495e5dc7d",
      "summary": "Decode styled XLSX calendar values using the workbook epoch; verify the supplied seven-device report in a separate non-overwriting copy.",
      "scope_ok": true,
      "changed_paths": [
        "backend/infrastructure/office/excel_workbook_gateway.py",
        "docs/PROJECT_CONTEXT.md",
        "tests/unit/test_excel_structure_probe.py",
        "tests/unit/test_external_excel_read_service.py",
        "tests/unit/test_tools_equipment_report_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Developer regression feedback",
          "summary": "Meaningful RED: raw 46020 versus expected 2025-12-29. Localized-format repair RED 11 failed / 83 passed; final three affected modules 94 passed in 3.40s. Existing text/numeric/time/duration/cached-formula and 1900/1904 boundaries protected."
        },
        {
          "status": "passed",
          "name": "Independent final QA",
          "summary": "Final reviewed bytes: 12 affected Python unit/integration modules, 191 passed in 18.38s; one existing Starlette/httpx deprecation warning. Diff check passed. No frontend/API contract change."
        },
        {
          "status": "passed",
          "name": "Actual attachment conversion",
          "summary": "Real ToolsEquipmentReportService -> ExternalExcelReadService -> TestReportDocumentGateway. Seven exact date/text pairs passed, filled=7, unmatched/incomplete/expired=0. IDs derived from supplied erroneous report, not another project's EquipmentID. Four original SHA256 values unchanged.",
          "output": "D:/PythonProject/connlab/tmp/equipment_datefix_qa_e8a94ca7ea064379b069076fc2f990ed/DL-2026-09-082 EK550 Connector T-rise and LLCR Testing Report _Rev_A_EquipmentDatesCorrected.docx",
          "sha256": "a2926118801e65cb46e2e8623ffe367906c5bdb130b65d3f52c1cd396df279cc"
        },
        {
          "status": "passed",
          "name": "Document preservation and rendering",
          "summary": "Canonical renderer attempted but bundled soffice unavailable; owned hidden Word read-only export and bundled Poppler rendered ten pages. QA and root opened all ten PNGs; equipment dates complete. Output hash unchanged by rendering. Outside-equipment text unchanged; existing writer adds 37 explicit font sizes, otherwise equivalent body semantics; images/OLE bytes and effective content types preserved."
        },
        {
          "status": "passed",
          "name": "Integration and residual delivery boundary",
          "summary": "Clean local master exact subject/parent/tree and five-path approved-scope subset verified independently. No new dependencies, original mutations, push or release rebuild. Existing portable release still needs rebuilding before use on another PC."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "context": "/root/equipment_planner",
          "summary": "Independent high-risk plan: seven-path scope, read-only adapter repair, preservation matrix and attachment copy."
        },
        "developer": {
          "status": "passed",
          "context": "/root/xlsx_date_developer",
          "summary": "Independent implementation and actual RED/GREEN; final three modules 94 passed. Earlier interrupted developer did not supply completion evidence."
        },
        "reviewer": {
          "status": "passed",
          "context": "/root/xlsx_date_reviewer",
          "summary": "Independent exact-diff review and bounded re-review. Localized implied-format P2 fixed; final Standards=0, Spec=0."
        },
        "qa": {
          "status": "passed",
          "context": "/root/equipment_qa",
          "summary": "Independent final 191-test matrix, actual attachment copy/date assertions, unchanged originals and ten-page rendering verification. Permission waits were not counted as test failures."
        },
        "integrator": {
          "status": "passed",
          "context": "/root/xlsx_date_integrator",
          "summary": "Independent read-only exact subject/parent/tree/scope/cleanliness check; recalculated output and all original hashes. No duplicate matrix."
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "subject": "e8018c96ca0ef5c5de3872c2c51da6e495e5dc7d",
        "parent": "ca92d6646f57ffd77aac6a2bcedc96a49635adf1",
        "tree": "ed70eee6beb407323d1a5c04448a6e5a48008f66",
        "summary": "Direct local integration; exact five-path cumulative product diff within seven approved paths. Clean subject verified. No remote publication."
      }
    }
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
