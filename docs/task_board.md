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
    "task_id": "TASK_FRONTEND_RELEASE_BUILD_REPAIR",
    "summary": "Repair the browser release frontend build by removing the stale Fee header destructuring and excluding test files from production TypeScript compilation.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Frontend-only release-build repair; preserve Vitest test execution and existing Fee export behavior.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
      "frontend/tsconfig.json"
    ],
    "risk_reasons": [],
    "activation_head": "b337ac2daec945691882680668e4efc424befd71",
    "started_at": "2026-09-20T12:30:53.160623Z",
    "updated_at": "2026-09-20T12:39:35.637303Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FRONTEND_RELEASE_BUILD_REPAIR",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_FRONTEND_RELEASE_BUILD_REPAIR",
      "subject": "01a09b3dc0406dddefffb17b3e062c7a30de3a7c",
      "summary": "Restored the browser release frontend build by removing the stale Fee header destructuring and excluding Vitest files from production TypeScript compilation.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
        "frontend/tsconfig.json"
      ],
      "validation": [
        {
          "status": "passed",
          "details": "Release-equivalent npm run build (tsc -b and vite build) passed."
        },
        {
          "status": "passed",
          "details": "Focused Fee component and fee-summary contract suite: 11 tests passed."
        },
        {
          "status": "passed",
          "details": "Complete frontend Vitest suite: 645 tests passed and 1 test skipped."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "details": "Removed the stale destructuring and scoped production TypeScript to application sources while preserving Vitest tests."
        },
        "reviewer": {
          "status": "passed",
          "details": "Sequential standards and specification review found no actionable issues."
        },
        "qa": {
          "status": "passed",
          "details": "Production build, focused regressions, and the complete frontend suite passed."
        }
      },
      "integration": {
        "status": "passed",
        "details": "Exact task diff is committed; working tree is clean."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_BASIC_INFORMATION_TOPBAR_LTR",
    "tier": "standard",
    "subject": "519f4f2e764dc161c5f38acbc36b7c9a686a4438",
    "summary": "Move the Basic Information LTR identity into the fixed top bar beside the page title.",
    "disposition": "completed",
    "decision_ref": "User requested: 关闭",
    "closed_at": "2026-09-20T12:20:29.828929Z"
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
