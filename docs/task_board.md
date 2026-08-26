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
    "task_id": "TASK_SELECTED_APPLICATION_FORM_PROJECT_FOLDER_BINDING_FINALIZE",
    "summary": "Finalize the already-integrated selected application-form project-folder binding fix.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Verify and close the implemented fix that binds project-folder collection and Word write-back to the application form selected by the confirmed intake case.",
    "scope_paths": [
      "backend/application/intake_confirmation_service.py",
      "backend/application/project_application_form_target_selection.py",
      "backend/application/project_request_material_collection_helpers.py",
      "backend/application/project_request_material_collection_service.py",
      "tests/unit/test_intake_confirmation_service.py",
      "tests/unit/test_project_application_form_target_selection.py",
      "tests/unit/test_project_request_material_collection_service.py",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "0b0a9c9e55d36b7e8feafb4c4eb32b364bb07101",
    "started_at": "2026-08-26T12:51:38.758240Z",
    "updated_at": "2026-08-26T12:51:38.758240Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_SELECTED_APPLICATION_FORM_PROJECT_FOLDER_BINDING",
    "tier": "high_risk",
    "subject": "d2eb09d99a31b25cf496c746aa84b2f03eb0fd51",
    "summary": "Bind project-folder application-form generation to the application form selected from a multi-form imported email.",
    "disposition": "cancelled",
    "decision_ref": "user:允许取消错误的任务登记并重新登记同一修复",
    "closed_at": "2026-08-26T12:51:01.694388Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
