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
    "task_id": "TASK_MATRIX_GROUP_IDENTITY_C",
    "summary": "Implement a previewable, fingerprinted, backup-backed, reversible Matrix data-integrity repair and compatible schema migration without changing confirmed authority content or revision counts.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Repair only proven legacy Matrix identity inconsistencies: preview findings, require matching fingerprint for execution, create and verify backup, repair safe superseded-draft orphans transactionally, preserve confirmed history, remove invalid confirmed-to-mutable-draft child foreign keys, enforce same-draft child invariants, and enable SQLite foreign keys per connection only after compatibility migration. Validate on database copies; do not mutate operator databases during development.",
    "scope_paths": [
      "backend/infrastructure/storage/database.py",
      "backend/infrastructure/storage/database_matrix_migrations.py",
      "backend/infrastructure/storage/models_confirmed_matrix_authority.py",
      "backend/infrastructure/storage/models_project_matrix_draft.py",
      "backend/infrastructure/storage/matrix_identity_integrity_audit.py",
      "backend/infrastructure/storage/matrix_identity_integrity_repair.py",
      "scripts/audit_matrix_identity.py",
      "scripts/repair_matrix_identity.py",
      "tests/unit/test_database.py",
      "tests/unit/test_matrix_identity_integrity_audit.py",
      "tests/unit/test_matrix_identity_integrity_repair.py",
      "docs/matrix_group_identity_audit_and_repair_design.md"
    ],
    "risk_reasons": [
      "SQLite schema migration and foreign-key enforcement",
      "Transactional repair can delete proven orphan rows in database copies",
      "Confirmed Matrix authority history and operator recovery must remain intact"
    ],
    "activation_head": "a632812a3c0cf64e51bca52bc6c0ab38dee11b27",
    "started_at": "2026-09-15T23:17:55.590456Z",
    "updated_at": "2026-09-15T23:17:55.590456Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_GROUP_IDENTITY_B",
    "tier": "standard",
    "subject": "0565045f8d20af81d38294f4fb04f85a1061934e",
    "summary": "Audit Matrix draft and confirmed-authority identity integrity against the real local database, then define a previewable and reversible repair workflow plus a simpler retention and UI policy for draft and authority history.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested: 关闭并启动 Matrix 数据完整性修复任务",
    "closed_at": "2026-09-15T23:17:55.590456Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
