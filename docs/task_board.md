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
    "task_id": "TASK_FEEDBACK_PATH_AND_CONFIRMED_WORKSPACE_NAME",
    "summary": "Fix Customer Feedback Windows long staging paths and official folder names not following confirmed Basic Information.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Use attached reports as evidence, reproduce both defects and implement safe path handling plus confirmed Basic naming. Preserve operator data and prior generation recovery; existing folder rename policy awaits explicit user choice. Do not execute report SQL, registry changes or manual moves.",
    "scope_paths": [
      "backend/infrastructure/office/customer_feedback_workbook_gateway.py",
      "backend/application/customer_feedback_form_generation_service.py",
      "backend/api/dependencies.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/application/official_project_workspace_service.py",
      "backend/application/official_project_workspace_naming.py",
      "backend/application/project_identity.py",
      "backend/application/project_folder_generation_service.py",
      "backend/infrastructure/official_workspace_manifest.py",
      "backend/api/routes_official_project_workspace.py",
      "backend/api/routes_project_folder_generation.py",
      "tests/unit/test_customer_feedback_workbook_gateway.py",
      "tests/unit/test_customer_feedback_form_generation_service.py",
      "tests/integration/test_customer_feedback_form_generation_api.py",
      "tests/unit/test_official_project_workspace_service.py",
      "tests/unit/test_official_project_workspace_naming.py",
      "tests/integration/test_official_project_workspace_api.py",
      "tests/unit/test_project_folder_generation_service.py",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/unit/test_required_forms_staging_generator.py",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [
      "Official folder name changes affect filesystem ownership and persisted paths; preserve existing data and recovery lineage."
    ],
    "activation_head": "4b9e0ce54288672f3d46f0e9e9ad6c7bc74a0d84",
    "started_at": "2026-09-10T05:07:13.004725Z",
    "updated_at": "2026-09-10T05:07:13.004725Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_SCHEDULE_CONFIRM_INDEPENDENCE",
    "tier": "high_risk",
    "subject": "4b9e0ce54288672f3d46f0e9e9ad6c7bc74a0d84",
    "summary": "Fix Matrix confirmation and deleted-row restoration; confirm Project Schedule independently and keep outputs usable.",
    "disposition": "cancelled",
    "decision_ref": "user-close-prior-and-fix-two-reports-20260910",
    "closed_at": "2026-09-10T05:07:13.004725Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
