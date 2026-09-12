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
    "task_id": "TASK_PROJECT_FOLDER_SINGLE_ENTRY",
    "summary": "Unify project folder update and recovery entry; retain explicit advanced rebuild confirmation.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Single UI entry and read-only recovery guidance using existing generation safety guards; no engine rewrite or real output operations.",
    "scope_paths": [
      "frontend/src/features/project-workbench",
      "frontend/src/api/client.ts",
      "backend/api/project_folder_generation_composition.py",
      "tests",
      "docs/project_management"
    ],
    "risk_reasons": [],
    "activation_head": "b70a1dea611d83e8f2e9ed8b8e063e5240f63446",
    "started_at": "2026-09-12T01:36:01.264661Z",
    "updated_at": "2026-09-12T01:56:48.367291Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_SINGLE_ENTRY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_SINGLE_ENTRY",
      "subject": "3ad1ffa376ded60cf372ff6ba2e4d460bd370364",
      "summary": "Unified normal folder entry with fresh recovery checks and explicit advanced rebuild review; no real project outputs modified.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/project_folder_generation_composition.py",
        "docs/project_management/PROJECT_FOLDER_SINGLE_ENTRY.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
        "frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts",
        "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
        "tests/integration/test_project_folder_generation_api.py"
      ],
      "validation": [
        {
          "status": "passed",
          "suite": "Full frontend Vitest",
          "result": "545 passed, 1 skipped; 65.55s"
        },
        {
          "status": "passed",
          "suite": "TypeScript and Vite production build",
          "result": "exit 0"
        },
        {
          "status": "passed",
          "suite": "Generation API, generation service and recovery pytest",
          "result": "16 passed; 8.01s; existing Starlette deprecation warning"
        },
        {
          "status": "passed",
          "suite": "Browser smoke",
          "result": "Normal entry visible; advanced rebuild collapsed then expanded and collapsed; no generation executed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "method": "Same agent implementation and regression tests; RED then GREEN"
        },
        "reviewer": {
          "status": "passed",
          "method": "Same agent separate standards/spec exact-diff review, not independent agent; no blocking findings"
        },
        "qa": {
          "status": "passed",
          "method": "Same agent final validation on clean committed subject, not independent agent"
        }
      },
      "integration": {
        "status": "passed",
        "method": "Local commit only; no push",
        "head": "3ad1ffa376ded60cf372ff6ba2e4d460bd370364",
        "parents": [
          "b70a1dea611d83e8f2e9ed8b8e063e5240f63446"
        ],
        "tree": "5905ff18dc3544992a10b9f3ffc5e56804b769ae",
        "clean": true
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_RELEASE_PUBLICATION_DIAGNOSTICS",
    "tier": "standard",
    "subject": "4c2fc3a9056c65b524f71606542555a7abc0d74f",
    "summary": "Add correlated, privacy-bounded diagnostics for Fee Form publication and project folder generation, including Office child failures and a verified browser release.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭.",
    "closed_at": "2026-09-12T00:45:34.911362Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
