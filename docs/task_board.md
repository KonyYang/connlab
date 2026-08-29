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
    "task_id": "REPORT-001D",
    "summary": "Carry confirmed application-form Test Sample Information through structured persistence and Basic Information authority into the E-3707_H SAMPLE DESCRIPTION table.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Only REPORT-001D sample-information authority, legacy compatibility, report projection, and proportional regression/visual validation.",
    "scope_paths": [
      "backend/domain/models.py",
      "backend/application/intake_mappers.py",
      "backend/application/intake_confirmation_service.py",
      "backend/application/project_basic_information_service.py",
      "backend/application/project_basic_information_output.py",
      "backend/application/test_report_draft_service.py",
      "backend/infrastructure/storage/models.py",
      "backend/infrastructure/storage/repositories/intake.py",
      "backend/infrastructure/storage/repositories/project_basic_information.py",
      "backend/infrastructure/storage/database_general_migrations.py",
      "backend/infrastructure/storage/database.py",
      "backend/infrastructure/office/test_report_document_gateway.py",
      "backend/api/routes_project_basic_information.py",
      "backend/api/routes_test_report_draft.py",
      "backend/api/dependencies.py",
      "tests/unit/test_intake_mappers.py",
      "tests/unit/test_intake_confirmation_service.py",
      "tests/unit/test_project_basic_information_service.py",
      "tests/unit/test_project_basic_information_repository.py",
      "tests/unit/test_project_basic_information_output_identity.py",
      "tests/unit/test_test_report_draft_service.py",
      "tests/unit/test_test_report_document_gateway.py",
      "tests/integration/test_repositories.py",
      "tests/integration/test_manual_intake_api.py",
      "tests/integration/test_msg_package_intake_api.py",
      "tests/integration/test_project_basic_information_api.py",
      "tests/integration/test_test_report_draft_api.py"
    ],
    "risk_reasons": [
      "SQLite schema migration for sample information and Basic Information authority snapshots."
    ],
    "activation_head": "d7cc39d6e9ea5f09556ff9aeebae2646b4921d64",
    "started_at": "2026-08-29T01:06:18.024318Z",
    "updated_at": "2026-08-29T01:06:18.024318Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-001C",
    "tier": "standard",
    "subject": "edbc41a6d6238c996c3ee42e17ed91d4bfcd350e",
    "summary": "Populate the E-3707_H first-page test date range from confirmed Basic Information Start Test Date and Finish Test Date using the golden-report date format joined by to.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭.",
    "closed_at": "2026-08-29T00:42:33.426618Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
