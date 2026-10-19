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
    "task_id": "TASK_CUSTOMER_REPORT_DOWNLOAD_SOURCE_20261019",
    "summary": "Use the latest matching downloaded Internal Report draft for Customer Report download fallback",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Keep official Customer Report publication unchanged; when no official Internal Report is available, read only the current project's validated latest Internal Report draft in the OS Downloads folder and generate an independent Customer draft download through existing jobs. Preserve sources, manual picker and race protection; isolated regression tests only.",
    "scope_paths": [
      "backend/application/customer_report_source_resolver.py",
      "backend/infrastructure/files/downloaded_internal_report_source.py",
      "backend/api/dependencies.py",
      "backend/api/project_customer_report_runner.py",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "tests/unit/test_downloaded_internal_report_source.py",
      "tests/unit/test_customer_report_source_resolver.py",
      "tests/integration/test_customer_report_download_source_api.py",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [],
    "activation_head": "51475da8d78dc4f1310e1765e2f1856dcef49d38",
    "started_at": "2026-10-19T11:54:13.469037Z",
    "updated_at": "2026-10-19T11:54:13.469037Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_INTERNAL_REPORT_DRAFT_FALLBACK_20261019",
    "tier": "standard",
    "subject": "72e10deb8ffbd2b68e3b492da3259830bbf60b15",
    "summary": "Download a non-overwriting Internal Report draft when the official project folder is unavailable",
    "disposition": "completed",
    "decision_ref": "User accepts ordinary browser download handling and explicitly closes the completed Internal Report draft fallback task.",
    "closed_at": "2026-10-19T10:48:13.514898Z"
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
