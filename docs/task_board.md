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
    "task_id": "TASK_RELEASE_FEE_PUBLICATION_AND_WORKSPACE_RECOVERY",
    "summary": "Repair Fee Form publication staging, pricing autosave races, and recoverable project folder failures reported on another workstation.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Reproduce the reported errors; fix operation staging and draft save serialization; allow safe recovery of unchanged/unpublished workspace operations without bypassing conflict checks; verify and produce a corrected portable browser release.",
    "scope_paths": [
      "backend/application/fee_form_publication_service.py",
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "backend/application/project_folder_generation_service.py",
      "backend/api/project_folder_generation_composition.py",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx",
      "tests/unit/test_fee_form_publication_service.py",
      "tests/unit/test_generation_workspace_recovery.py",
      "tests/unit/test_project_folder_generation_service.py",
      "tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "docs/project_folder_generation_recovery.md",
      "docs/packaging_notes.md"
    ],
    "risk_reasons": [
      "Changes recovery for publishing into existing operator project folders; preserve explicit conflict authority and file ownership."
    ],
    "activation_head": "67aa363e9f4cd53495dc214fda5e4e455c40e476",
    "started_at": "2026-09-11T04:39:52.435610Z",
    "updated_at": "2026-09-11T04:39:52.435610Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_REGISTRY_ACTION_ICON_BUTTONS",
    "tier": "micro",
    "subject": "4e81a97759ea6f5d83ed55bee9a512a24c1dce99",
    "summary": "Project registry actions are compact icon buttons placed directly beside Open Workbench.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭.",
    "closed_at": "2026-09-11T04:34:26.592539Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
