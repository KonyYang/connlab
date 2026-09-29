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
    "task_id": "TASK_FEE_CONFIRM_STATE_AND_FOLDER_HINT",
    "summary": "Fix Fee confirmation re-entry state and explain unavailable project folder on Fee Form action",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Make Fee content comparison insensitive to row ordering, reflect confirmed unchanged state on re-entry, and provide an actionable hover reason when the official project folder cannot be used.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation",
      "backend/application/fee_form_publication_service.py",
      "backend/application/fee_evaluation_pricing_draft_serialization.py",
      "tests/unit/test_fee_form_publication_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "ad5993d56fc080ca7c737160e999d41b96239e12",
    "started_at": "2026-09-29T00:07:48.538762Z",
    "updated_at": "2026-09-29T00:27:09.479222Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_CONFIRM_STATE_AND_FOLDER_HINT",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "scope_ok": true,
      "task_id": "TASK_FEE_CONFIRM_STATE_AND_FOLDER_HINT",
      "schema": "connlab.sol-task-report",
      "summary": "Fee confirmation recognizes equal reordered values; unchanged Confirm is disabled; unavailable official folder explains draft-download action.",
      "validation": [
        {
          "name": "Python Fee Form service and API",
          "status": "passed",
          "result": "31 passed"
        },
        {
          "name": "Frontend Fee Evaluation",
          "status": "passed",
          "result": "86 passed"
        },
        {
          "name": "Frontend production build",
          "status": "passed",
          "result": "tsc and vite build passed"
        },
        {
          "name": "Read-only browser smoke",
          "status": "passed",
          "result": "Current project shows official form action and disabled unchanged Confirm"
        }
      ],
      "version": 1,
      "integration": {
        "summary": "Scoped commit at clean master HEAD, exact task diff verified",
        "status": "passed"
      },
      "changed_paths": [
        "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
        "backend/application/fee_form_publication_service.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts",
        "tests/integration/test_confirmed_matrix_fee_file_download_api.py",
        "tests/unit/test_fee_form_publication_service.py"
      ],
      "roles": {
        "qa": {
          "summary": "Backend, frontend, build and read-only browser matrix passed",
          "status": "passed"
        },
        "developer": {
          "summary": "Regression RED/GREEN and implementation complete",
          "status": "passed"
        },
        "reviewer": {
          "summary": "Same-agent standards and requirement diff review; no material findings",
          "status": "passed"
        }
      },
      "subject": "c6940c6bd4218ab1f801c0057872e2f8e96b4ecb"
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_TEST_DAYS_TYPOGRAPHY",
    "tier": "micro",
    "subject": "97e1bdb2f86b9361bccd5048f732362ae559c5ab",
    "summary": "Increase the Matrix Editor Test Days summary-row text to match surrounding editor typography.",
    "disposition": "completed",
    "decision_ref": "User explicit close request.",
    "closed_at": "2026-09-28T23:59:22.744523Z"
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
