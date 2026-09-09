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
    "task_id": "TASK_PROJECT_FOLDER_BLOCKER_VISIBILITY",
    "summary": "Keep Project Folder generation blockers visible until the user corrects the input or explicitly starts a new recovery action.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Frontend Project Folder generation error lifetime, recovery presentation, and regression coverage.",
    "scope_paths": [
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "d139cac7dc07ed0d2b6cef1b1f09beafe145f42c",
    "started_at": "2026-09-09T11:08:32.976159Z",
    "updated_at": "2026-09-09T14:25:51.067752Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_BLOCKER_VISIBILITY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_BLOCKER_VISIBILITY",
      "summary": "Project Folder action blockers now remain visible across connection failures and polling of older completed generation records.",
      "integration": {
        "status": "passed",
        "summary": "The committed change is limited to the generation error lifetime model and its regression tests."
      },
      "scope_ok": true,
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Reproduced both overwrite paths and implemented typed error-source priority."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Sequential standards and request review found no actionable finding or scope expansion."
        },
        "qa": {
          "status": "passed",
          "summary": "Focused hook tests, complete frontend suite, production build, and real-browser smoke passed."
        }
      },
      "subject": "0a5b7355291310c390fa022f523c6809cc583164",
      "changed_paths": [
        "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx"
      ],
      "validation": [
        {
          "name": "red_green_regressions",
          "status": "passed",
          "result": "Both reproduced overwrite sequences failed before their fixes and passed after."
        },
        {
          "name": "frontend_full_suite",
          "status": "passed",
          "result": "520 passed, 1 skipped."
        },
        {
          "name": "frontend_production_build",
          "status": "passed",
          "result": "TypeScript and Vite production build passed."
        },
        {
          "name": "real_browser_smoke",
          "status": "passed",
          "result": "Specified project blocker remained visible after 0.7, 5, and 15 seconds."
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_BASIC_INFORMATION_LEGACY_CLEANUP",
    "tier": "micro",
    "subject": "b47d51e412054ef02f8df07afc489e92567c8d4e",
    "summary": "Remove verified dead Basic Information schedule UI configuration and unused application-form date projections without changing legacy compatibility behavior.",
    "disposition": "completed",
    "decision_ref": "用户明确要求关闭当前任务，并修复项目文件夹阻塞提示一闪而过。",
    "closed_at": "2026-09-09T11:08:32.976159Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
