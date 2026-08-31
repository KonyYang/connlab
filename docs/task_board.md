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
    "task_id": "TASK_PROJECT_FILE_ENCRYPTION",
    "summary": "Add previewed one-click nonrecursive Office file encryption for trusted official project workspaces.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Only the user-approved project file encryption behavior in Folder Actions, with trusted backend path resolution and recoverable file mutation.",
    "scope_paths": [
      "docs/task_board.md",
      "backend/application/project_file_encryption_service.py",
      "backend/infrastructure/files/project_file_encryption_gateway.py",
      "backend/infrastructure/office/office_file_password_gateway.py",
      "backend/api/routes_project_file_encryption.py",
      "backend/api/dependencies.py",
      "backend/api/main.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/ProjectFileEncryptionAction.tsx",
      "frontend/src/features/project-workbench/ProjectFileEncryptionAction.test.tsx",
      "frontend/src/features/project-workbench/ProjectFolderTaskList.tsx",
      "frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx",
      "frontend/src/workbench.css",
      "tests/unit/test_project_file_encryption_service.py",
      "tests/unit/test_project_file_encryption_gateway.py",
      "tests/unit/test_office_file_password_gateway.py",
      "tests/integration/test_project_file_encryption_api.py"
    ],
    "risk_reasons": [
      "Encrypts and replaces authoritative external Office files.",
      "Moves unencrypted Test results files into project History.",
      "Uses Word, Excel, and PowerPoint COM automation."
    ],
    "activation_head": "fe06b6a9724ea1b56ce46fe5d40e9993f4af6fcc",
    "started_at": "2026-08-31T00:03:20.570346Z",
    "updated_at": "2026-08-31T00:03:20.570346Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-003B",
    "tier": "high_risk",
    "subject": "41c7f325d55942f0c74e0f07ca49b489f670083a",
    "summary": "Implement Equipment List source inspection, preview, and controlled report-region update from EquipmentID.docx and the configured calibration workbook.",
    "disposition": "completed",
    "decision_ref": "用户明确回复：关闭",
    "closed_at": "2026-08-30T23:22:04.869054Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
