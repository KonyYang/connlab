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
    "updated_at": "2026-09-20T14:43:31.369750Z",
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
      "subject": "41cf0282728569f496160d11bee11f5a8e99f8d2",
      "summary": "Shortened generated report filenames and reduced the default official project-folder segment limit so report generation stays within traditional Windows/Word path budgets without requiring administrator long-path settings. A new Windows browser release package was built and smoke-checked.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/official_project_workspace_naming.py",
        "backend/application/test_report_draft_service.py",
        "docs/report_generation_architecture.md",
        "tests/unit/test_official_project_workspace_naming.py",
        "tests/unit/test_test_report_draft_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "details": "RED/GREEN focused report naming and folder naming tests: 12 passed."
        },
        {
          "status": "passed",
          "details": "Affected report generation, customer projection, publication, and API suite: 54 passed."
        },
        {
          "status": "passed",
          "details": "Complete backend non-Office gate: 2956 passed, 7 skipped, 19 deselected."
        },
        {
          "status": "passed",
          "details": "Complete frontend suite: 645 passed, 1 skipped; production build passed."
        },
        {
          "status": "passed",
          "details": "Windows browser release package built and smoke-checked on isolated port 8766: ConnLab_Web_202609202239_v0.1.0."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "details": "Reproduced long report names, then applied the minimum filename and folder-budget changes with regression coverage."
        },
        "reviewer": {
          "status": "passed",
          "details": "Sequential standards and specification review found no actionable defects; documentation was aligned with the new filename contract."
        },
        "qa": {
          "status": "passed",
          "details": "Focused report suite, complete backend non-Office gate, complete frontend suite, production build, and packaged smoke check passed."
        }
      },
      "integration": {
        "status": "passed",
        "details": "Exact task diff is committed; the new portable browser release package was generated from it."
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
