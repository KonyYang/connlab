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
    "task_id": "TASK_RELEASE_PUBLICATION_DIAGNOSTICS",
    "summary": "Add correlated, privacy-bounded diagnostics for Fee Form publication and project folder generation, including Office child failures and a verified browser release.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Observability only: preserve publication/conflict/recovery semantics; add operation IDs, stages/timings, safe Windows/COM exceptions and file metadata, readable UI references and support bundle retention. Validate injected failures and build portable release.",
    "scope_paths": [
      "backend/shared",
      "backend/application/fee_form_publication_service.py",
      "backend/application/project_folder_generation_service.py",
      "backend/application/confirmed_matrix_fee_evaluation_export_timeout_service.py",
      "backend/application/support_diagnostic_bundle_service.py",
      "backend/infrastructure/office",
      "backend/infrastructure/files",
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "tests",
      "docs/packaging_notes.md",
      "packaging/README_FOR_BROWSER_OPERATOR.md"
    ],
    "risk_reasons": [],
    "activation_head": "cb181d1125108f0869e163e58dc598276560bfda",
    "started_at": "2026-09-11T13:15:18.994287Z",
    "updated_at": "2026-09-11T13:15:18.994287Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_RELEASE_FEE_PUBLICATION_AND_WORKSPACE_RECOVERY",
    "tier": "high_risk",
    "subject": "0fcc9780c2b1938d8a97d05663a69339e9f7b032",
    "summary": "Repair Fee Form publication staging, pricing autosave races, and recoverable project folder failures reported on another workstation.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭.",
    "closed_at": "2026-09-11T08:09:37.417962Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
