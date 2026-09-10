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
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "backend/application/project_folder_generation_service.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/api/routes",
      "frontend/src",
      "tests",
      "docs/task_board.md"
    ],
    "risk_reasons": [
      "authoritative external project-folder mutation",
      "Windows file-lock and crash-recovery behavior",
      "checkpoint lifecycle and API/UI recovery semantics"
    ],
    "activation_head": "365a9d0cb9136e298b54e651dcead038bc472b22",
    "started_at": "2026-09-10T09:53:57.576209Z",
    "updated_at": "2026-09-10T10:55:11.451794Z",
    "checkpoint": {
      "requires_user": false,
      "status": "running",
      "stage": "implementation_validation",
      "task_id": "TASK_PROJECT_FOLDER_LOCK_RESILIENT_UPDATE",
      "summary": "Reproduced WinError 5 as whole-directory rename fragility. Added non-destructive continue_existing strategy that adds only missing template content, preserves same-name operator files, avoids reading or moving existing files, and recovers after interruption. A failed first backup rename now removes only its verified owned stage and effect so the operation becomes safely replaceable. Added actionable lock guidance and a recommended Workbench conflict action with restart access. Final affected validation and review remain.",
      "version": 1,
      "schema": "connlab.sol-task-checkpoint"
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
