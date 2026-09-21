# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> WIP=1. GPT-5.6 Sol routes work as micro, standard, or high risk and runs routine stages
> automatically until the User's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_CUSTOMER_REPORT_LONG_PATH_REPAIR",
    "summary": "Prevent customer-report generation from passing long official project-report paths directly to Microsoft Word by using a short controlled working copy while preserving source-authority checks and publication behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Customer report Word input staging for long official project-folder paths.",
    "scope_paths": [
      "backend/infrastructure/office/customer_report_subprocess_runner.py",
      "tests/unit/test_customer_report_subprocess_runner.py"
    ],
    "risk_reasons": [],
    "activation_head": "f13b5defef95e9eb3e2b559aeeab3a124a6f5331",
    "started_at": "2026-09-20T14:01:56.007171Z",
    "updated_at": "2026-09-21T01:36:50.044058Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CUSTOMER_REPORT_LONG_PATH_REPAIR",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_CUSTOMER_REPORT_LONG_PATH_REPAIR",
      "subject": "25b68d6d363df5b98b7d31946ba4a311810f07ae",
      "summary": "Verified the corrected customer-report flow in the live browser after replacing the stale backend process: the same real report completed twice in 12.06 and 13.33 seconds with full correlated stage logging; no additional product-code change was justified.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/tools_customer_report_job_service.py",
        "backend/infrastructure/office/customer_report_subprocess_child.py",
        "backend/infrastructure/office/customer_report_subprocess_runner.py",
        "backend/infrastructure/office/test_report_document_gateway.py",
        "docs/report_generation_architecture.md",
        "tests/unit/test_customer_report_subprocess_runner.py",
        "tests/unit/test_test_report_document_gateway.py",
        "tests/unit/test_test_report_draft_service.py",
        "tests/unit/test_tools_customer_report_job_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "details": "Live in-app browser smoke: the same real Internal Report generated and downloaded successfully twice."
        },
        {
          "status": "passed",
          "details": "Current-code stage traces completed in 12.06 and 13.33 seconds through Word open, copy, clean, format, save, verify, and protect."
        },
        {
          "status": "passed",
          "details": "Affected suite remains 34 passed and complete Python 3.11 gate remains 2960 passed, 7 skipped, 19 deselected; no source byte changed after those runs."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "details": "Existing repair was loaded into a clean backend process; no further source change was warranted by the live evidence."
        },
        "reviewer": {
          "status": "passed",
          "details": "Reviewed live stage traces and exact diff; deterministic document/path failures were disproved and no scope creep was introduced."
        },
        "qa": {
          "status": "passed",
          "details": "Two consecutive real-browser conversions succeeded with downloads and correlated backend completion logs."
        }
      },
      "integration": {
        "status": "passed",
        "details": "Live frontend on port 5173 and refreshed backend on port 8000 completed the real customer-report workflow twice."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FRONTEND_RELEASE_BUILD_REPAIR",
    "tier": "standard",
    "subject": "01a09b3dc0406dddefffb17b3e062c7a30de3a7c",
    "summary": "Repair the browser release frontend build by removing the stale Fee header destructuring and excluding test files from production TypeScript compilation.",
    "disposition": "completed",
    "decision_ref": "user-explicit-close-2026-09-20",
    "closed_at": "2026-09-20T13:52:47.547132Z"
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
