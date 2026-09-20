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
    "task_id": "TASK_WORKBENCH_FOLDER_ACTION_MIGRATION",
    "summary": "Move project folder create and update control from the Workbench top bar into Folder Actions with correct labels, primary weight, lifecycle reachability, and narrow-width coverage.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Frontend Workbench folder action placement and its public behavior tests; preserve existing folder generation authority and backend contracts.",
    "scope_paths": [
      "frontend/src/features/project-workbench",
      "frontend/src/workbench.css",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "6649350ccd38e71135b4260378b4742a0b9ba509",
    "started_at": "2026-09-19T14:33:41.881450Z",
    "updated_at": "2026-09-20T00:29:23.559381Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_WORKBENCH_FOLDER_ACTION_MIGRATION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_WORKBENCH_FOLDER_ACTION_MIGRATION",
      "subject": "eb48ff598fabe73f85d70d4bdeb4d46824319772",
      "summary": "Moved the existing project-folder command into the Folder Actions header as a fixed Create folder button, removed the extra task-row implementation, and preserved the established generation workflow.",
      "scope_ok": true,
      "changed_paths": [
        "docs/workbench_topbar_actions_and_folder_create_migration_plan.md",
        "frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx",
        "frontend/src/features/project-workbench/ProjectFolderTaskList.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
        "frontend/src/workbench.css"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "targeted frontend tests",
          "summary": "98 tests passed across Folder Actions, layout, selectors, and folder-generation workflow."
        },
        {
          "status": "passed",
          "name": "Vite production build",
          "summary": "163 modules transformed and production assets built successfully."
        },
        {
          "status": "passed",
          "name": "browser smoke",
          "summary": "Desktop and 393px checks confirmed header placement, four operation rows, and no horizontal overflow."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented the revision with a public-seam RED/GREEN cycle."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Sequential primary-agent standards and specification reviews found no remaining issue."
        },
        "qa": {
          "status": "passed",
          "summary": "Affected suite, production build, and responsive browser smoke passed; the unrelated ReportWorkspace timer test remains outside this task."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "The fixed header action reuses the original handler, disabled reasons, and conflict-confirmation flow without backend or authority changes."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT",
    "tier": "micro",
    "subject": "ad0cbb757b4fa5f5549dcfb6746d7f20ed6528f3",
    "summary": "Align the supported test runner with the ConnLab Python virtual environment and retire stale broad environment-debt assumptions.",
    "disposition": "completed",
    "decision_ref": "User requested closure after accepting the completed TASK_361B result.",
    "closed_at": "2026-09-18T22:04:32.468267Z"
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
