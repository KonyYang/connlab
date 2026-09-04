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
    "task_id": "TASK_MATRIX_DRAFT_LIFECYCLE_GOVERNANCE",
    "summary": "Govern Matrix draft lifecycle so only one working draft is current, authority-linked lineage is explicit, and stale unreferenced drafts can be cleaned safely.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Define and implement Matrix draft lifecycle transitions and safe cleanup without weakening confirmed Matrix authority or traceability.",
    "scope_paths": [
      "backend/application/matrix_draft_lifecycle_service.py",
      "backend/application/matrix_editor_session_publication.py",
      "backend/application/matrix_editor_session_contracts.py",
      "backend/infrastructure/storage/repositories/project_matrix_draft.py",
      "backend/infrastructure/storage/database_general_migrations.py",
      "backend/infrastructure/storage/database.py",
      "tests/unit/test_matrix_draft_lifecycle_service.py",
      "tests/unit/test_matrix_editor_session_service.py",
      "tests/unit/test_project_matrix_draft_repository.py",
      "tests/unit/test_database.py"
    ],
    "risk_reasons": [
      "database lifecycle migration",
      "destructive cleanup of unreferenced drafts",
      "confirmed Matrix authority lineage"
    ],
    "activation_head": "cd85caadf45e16a39332f93b986dfd70562799d8",
    "started_at": "2026-09-04T00:09:51.155757Z",
    "updated_at": "2026-09-04T00:09:51.155757Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_DRAFT_DUPLICATE_ROW_IDENTITY",
    "tier": "standard",
    "subject": "6747cfffa797890373414e89220ba0aed3e707f7",
    "summary": "Prevent Matrix Editor session restoration from duplicating repeated test rows and step sequences.",
    "disposition": "completed",
    "decision_ref": "User explicitly closed the duplicate-row task and requested a separate Matrix draft lifecycle governance task.",
    "closed_at": "2026-09-04T00:09:51.155757Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
