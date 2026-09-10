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
  "state": "running",
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
    "updated_at": "2026-09-10T11:32:37.541507Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_LOCK_RESILIENT_UPDATE",
      "stage": "scope_manifest_correction",
      "status": "running",
      "summary": "User requested closing the prior task and implementing the attached source-level project-folder lock fix; these are the exact committed implementation and regression paths.",
      "requires_user": false
    },
    "report": null
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
