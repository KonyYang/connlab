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
    "task_id": "TASK_TEST_STATUS_WORKBOOK",
    "summary": "Add Matrix Editor Test Status draft download and authoritative Submitted Material workbook generation using shared VBA-compatible projection logic.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Implement the User-requested Test Status workbook draft and authoritative project-folder output without changing Matrix authority semantics.",
    "scope_paths": [
      "backend/application",
      "backend/api",
      "backend/infrastructure/office",
      "backend/domain/enums.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor",
      "tests/unit",
      "tests/integration",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "161d4a027affff0d0c91d6d81ea1260d581c2df0",
    "started_at": "2026-08-26T23:29:40.759240Z",
    "updated_at": "2026-08-27T00:05:39.944244Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEST_STATUS_WORKBOOK",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "roles": {
        "reviewer": {
          "status": "passed",
          "summary": "Standards and specification passes found and corrected the project-reference filename defect and output-kind mapping omission; no remaining findings."
        },
        "qa": {
          "status": "passed",
          "summary": "Backend, frontend, build, browser, local API, compile, and whitespace checks passed on the final implementation."
        },
        "developer": {
          "status": "passed",
          "summary": "Implemented shared draft/authority projection, XLSX writer, API, UI, Required Forms integration, and regression tests using TDD."
        }
      },
      "task_id": "TASK_TEST_STATUS_WORKBOOK",
      "summary": "Matrix Editor now downloads a VBA-compatible Test Status workbook from current draft state, while project-folder creation generates the confirmed authority version under Submitted Material.",
      "integration": {
        "status": "passed",
        "summary": "Committed exact task changes on master with a clean worktree at the reported subject."
      },
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/main.py",
        "backend/api/routes_matrix_editor_test_status_generation.py",
        "backend/application/confirmed_matrix_test_status_workbook_generation_service.py",
        "backend/application/matrix_editor_test_status_workbook_generation_service.py",
        "backend/application/project_folder_required_forms_service.py",
        "backend/application/project_output_record_service.py",
        "backend/application/test_status_workbook_projection.py",
        "backend/domain/enums.py",
        "backend/infrastructure/office/test_status_workbook_gateway.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx",
        "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx",
        "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
        "tests/integration/test_matrix_editor_test_status_generation_api.py",
        "tests/unit/test_project_folder_required_forms_service.py",
        "tests/unit/test_required_forms_staging_generator.py",
        "tests/unit/test_test_status_workbook.py"
      ],
      "schema": "connlab.sol-task-report",
      "scope_ok": true,
      "version": 1,
      "validation": [
        {
          "command": "py -m pytest affected backend matrix",
          "status": "passed",
          "result": "60 passed"
        },
        {
          "command": "npm test affected frontend matrix",
          "status": "passed",
          "result": "41 passed"
        },
        {
          "command": "npm run build",
          "status": "passed",
          "result": "TypeScript and Vite production build passed"
        },
        {
          "command": "in-app browser and localhost API smoke",
          "status": "passed",
          "result": "Test Status download succeeded with DL-2026-08-004 test status.xlsx"
        },
        {
          "command": "py_compile and git diff --check",
          "status": "passed",
          "result": "passed"
        }
      ],
      "subject": "b57ea9e6570d78771691386454e77fc599ae3bb9"
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_OPEN_REFRESH_AFTER_CREATE",
    "tier": "micro",
    "subject": "db40fdb6e3e5d7bce14ae4ce172ebcb35c6f986a",
    "summary": "Refresh Folder Actions immediately after successful project-folder creation so Open is available without a page reload.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested close after completed delivery.",
    "closed_at": "2026-08-26T23:03:46.456853Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
