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
    "task_id": "TASK_REPORT_READ_ERRORS_20261019",
    "summary": "Read protected customer reports safely and isolate page load errors",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fix read-only report lineage inspection and actionable page errors using isolated tests; no real report writes or unrelated fixes",
    "scope_paths": [
      "backend/infrastructure/office/customer_report_document_gateway.py",
      "backend/application/customer_report_projection_service.py",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "tests/unit/test_customer_report_document_gateway.py",
      "tests/unit/test_customer_report_projection_service.py",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "eefbd0a4554a2af204a22c1ebd664749acc75310",
    "started_at": "2026-10-19T00:13:54.221852Z",
    "updated_at": "2026-10-19T00:19:00.432499Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_REPORT_READ_ERRORS_20261019",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "summary": "Protected customer lineage uses read-only decrypted copy; unreadable reports return actionable blocked state; customer query failures preserve Internal Report UI with read-only retry. Originals untouched.",
      "changed_paths": [
        "backend/application/customer_report_projection_service.py",
        "backend/infrastructure/office/customer_report_document_gateway.py",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "tests/integration/test_report_workspace_api.py",
        "tests/unit/test_customer_report_document_gateway.py",
        "tests/unit/test_customer_report_projection_service.py"
      ],
      "version": 1,
      "scope_ok": true,
      "integration": {
        "status": "passed",
        "method": "local master commit, clean tree; no push"
      },
      "schema": "connlab.sol-task-report",
      "subject": "9774e0be539ae516563cdc91a1bd54cf56badfb3",
      "validation": [
        {
          "result": "60 passed; one Starlette deprecation warning",
          "name": "Relevant isolated backend suite",
          "status": "passed"
        },
        {
          "result": "88 passed",
          "name": "Report workspace Vitest suite",
          "status": "passed"
        },
        {
          "result": "passed",
          "name": "TypeScript and Vite production build",
          "status": "passed"
        }
      ],
      "task_id": "TASK_REPORT_READ_ERRORS_20261019",
      "roles": {
        "developer": {
          "status": "passed",
          "method": "isolated red-green regression tests"
        },
        "qa": {
          "status": "passed",
          "method": "same agent; final affected matrix on clean exact subject"
        },
        "reviewer": {
          "status": "passed",
          "method": "same-agent separate standards and request-fit passes; no outstanding findings"
        }
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_LEGACY_PROJECT_REGISTRATION_20261019",
    "tier": "high_risk",
    "subject": "683ce90fe6b7dfa0e14f638f7b2ba3522d2b214a",
    "summary": "Register selected legacy project folders for search and browse in place",
    "disposition": "completed",
    "decision_ref": "User explicitly closes this task locally, retains all local commits and documented acceptance exceptions, and forbids push or publication.",
    "closed_at": "2026-10-19T00:11:36.348190Z"
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
