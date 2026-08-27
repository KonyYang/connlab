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
    "task_id": "REPORT-001",
    "summary": "Generate a downloadable non-overwriting E-3707_H initialization report draft from confirmed project authority in Project Workbench.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Read E-3707_H from Settings Template folder; use current confirmed Basic Information and Active Confirmed Matrix; generate only into the controlled draft area; add the Project Workbench Test Report action; exclude result imports, formal project-folder writes, overwrite/archive flows, customer reports, and ongoing synchronization.",
    "scope_paths": [
      "backend/application/test_report_template_resource.py",
      "backend/application/test_report_draft_service.py",
      "backend/infrastructure/office/test_report_document_gateway.py",
      "backend/api/routes_test_report_draft.py",
      "backend/api/dependencies.py",
      "backend/api/main.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/TestReportDraftButton.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "tests/unit/test_test_report_template_resource.py",
      "tests/unit/test_test_report_draft_service.py",
      "tests/unit/test_test_report_document_gateway.py",
      "tests/integration/test_test_report_draft_api.py",
      "frontend/src/features/project-workbench/TestReportDraftButton.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "docs/report_generation_architecture.md",
      "tmp/report-001/artifact.md"
    ],
    "risk_reasons": [],
    "activation_head": "f43b054f32a70faf0705a04ac1173a9dca923d92",
    "started_at": "2026-08-27T16:01:45.547819Z",
    "updated_at": "2026-08-27T16:01:45.547819Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_BASIC_INFORMATION_APPLICATION_DEFAULTS",
    "tier": "standard",
    "subject": "7d71196ced448737828df3e7889c5133e1269272",
    "summary": "Populate Basic Information requested completion date and sample deposition defaults from the selected application form.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭 on 2026-08-27.",
    "closed_at": "2026-08-27T13:25:47.066964Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
