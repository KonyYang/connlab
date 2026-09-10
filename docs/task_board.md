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
    "task_id": "TASK_PROJECT_FOLDER_LOCK_RESILIENT_UPDATE",
    "summary": "Make Update project folder safe and recoverable when the existing official workspace contains files held open by Windows processes.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Diagnose and replace the fragile whole-directory rename path with a data-safe publication/recovery strategy, provide recovery from non-restartable step-0 checkpoints, preserve authoritative project files, and add focused regression coverage. Do not adopt lossy skip-and-delete behavior or junction migration without evidence.",
    "scope_paths": [
      "backend/api/routes_project_folder_generation.py",
      "backend/application/official_project_workspace_service.py",
      "backend/application/project_folder_generation_service.py",
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "docs/PROJECT_CONTEXT.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/workbench.css",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/unit/test_generation_workspace_recovery.py",
      "tests/unit/test_official_project_workspace_service.py",
      "tests/unit/test_project_folder_generation_service.py"
    ],
    "risk_reasons": [
      "authoritative external project-folder mutation",
      "Windows file-lock and crash-recovery behavior",
      "checkpoint lifecycle and API/UI recovery semantics"
    ],
    "activation_head": "365a9d0cb9136e298b54e651dcead038bc472b22",
    "started_at": "2026-09-10T09:53:57.576209Z",
    "updated_at": "2026-09-10T11:33:34.478786Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_LOCK_RESILIENT_UPDATE",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_LOCK_RESILIENT_UPDATE",
      "subject": "f810b9562a3b1ec7ecde9f151a3114619ea3ee86",
      "summary": "Project-folder updates now offer a non-destructive continue-existing strategy and recover safely from an initial Windows folder-lock failure.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_project_folder_generation.py",
        "backend/application/official_project_workspace_service.py",
        "backend/application/project_folder_generation_service.py",
        "backend/infrastructure/files/recoverable_workspace_publisher.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "frontend/src/workbench.css",
        "tests/integration/test_project_folder_generation_api.py",
        "tests/unit/test_generation_workspace_recovery.py",
        "tests/unit/test_official_project_workspace_service.py",
        "tests/unit/test_project_folder_generation_service.py"
      ],
      "validation": [
        {
          "name": "affected backend pytest matrix",
          "status": "passed",
          "summary": "65 passed in 32.65s"
        },
        {
          "name": "affected frontend Vitest matrix",
          "status": "passed",
          "summary": "72 passed"
        },
        {
          "name": "Vite production build",
          "status": "passed",
          "summary": "156 modules transformed"
        },
        {
          "name": "Python compile check",
          "status": "passed"
        },
        {
          "name": "exact diff review",
          "status": "passed",
          "summary": "No blocking requirement-fit, safety, or regression findings remained."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "summary": "A sequential planning pass constrained the fix to recoverable, non-destructive project-folder behavior; no independent agent was used."
        },
        "developer": {
          "status": "passed",
          "summary": "Implemented the typed lock failure, missing-only merge strategy, UI action, recovery state, and tests."
        },
        "reviewer": {
          "status": "passed",
          "summary": "A focused sequential review corrected generic PermissionError classification and operation-owned stage cleanup; no independent agent was used."
        },
        "qa": {
          "status": "passed",
          "summary": "A sequential final-state QA pass completed the affected backend, frontend, build, and compile matrix; no independent agent was used."
        },
        "integrator": {
          "status": "passed",
          "summary": "Verified the committed change and integration boundaries locally; no external project folders were mutated."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "verified_local",
        "summary": "Committed source state was validated locally; release packaging was intentionally not run."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FEEDBACK_PATH_AND_CONFIRMED_WORKSPACE_NAME",
    "tier": "high_risk",
    "subject": "365a9d0cb9136e298b54e651dcead038bc472b22",
    "summary": "Fix Customer Feedback Windows long staging paths and official folder names not following confirmed Basic Information.",
    "disposition": "cancelled",
    "decision_ref": "user: close the pending existing-folder rename task and solve the attached project-folder update failure",
    "closed_at": "2026-09-10T09:53:57.576209Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
