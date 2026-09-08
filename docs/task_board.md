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
    "task_id": "TASK_PROJECT_FOLDER_BASIC_INFORMATION_PREFLIGHT",
    "summary": "Prevent Project Folder generation from starting before Basic Information is confirmed and provide precise actionable guidance for incomplete versus unconfirmed information.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Add backend-owned Basic Information preflight to Project Folder generation, distinguish incomplete data from completed-but-unconfirmed data in user-facing messages, and make recovery UI guide stale blocked operations to refresh and restart safely.",
    "scope_paths": [
      "backend/api/project_folder_generation_composition.py",
      "backend/application/project_folder_generation_service.py",
      "backend/application/project_basic_information_service.py",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "86917453e61dc7a86f91cc744b82693ce42c3ee9",
    "started_at": "2026-09-08T12:04:58.541204Z",
    "updated_at": "2026-09-08T13:29:59.411664Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_BASIC_INFORMATION_PREFLIGHT",
      "stage": "revision",
      "status": "running",
      "summary": "User smoke feedback: generation now reaches Application Form but Word open returns None; diagnose and fix continuation.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_SAMPLE_SIZE_CASE_COMPATIBILITY",
    "tier": "micro",
    "subject": "6908dc52695bc64ae081a50d564fa6e1316ada8c",
    "summary": "Accept a legacy ConnLab Matrix XLSX footer labeled Sample Size without weakening the controlled footer structure.",
    "disposition": "completed",
    "decision_ref": "user:close current task and start Project Folder Basic Information preflight repair",
    "closed_at": "2026-09-08T12:04:58.541204Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
