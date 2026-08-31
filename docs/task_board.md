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
    "task_id": "REPORT-003C",
    "summary": "Implement deterministic E-4515_F customer-report projection from the current internal report, then integrate status, download, and safe publication in Report Workspace.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "REPORT-003C-A projection fidelity followed by REPORT-003C-B current-report UI and publication. Do not modify approved templates, golden reports, source reports, or unrelated files. Real official-file smoke remains separately authorized.",
    "scope_paths": [
      "backend/application/customer_report_projection_service.py",
      "backend/application/current_report_update_service.py",
      "backend/application/report_workspace_service.py",
      "backend/api/dependencies.py",
      "backend/api/routes_report_workspace.py",
      "backend/infrastructure/files/report_publication_gateway.py",
      "backend/infrastructure/office/customer_report_document_gateway.py",
      "docs/report_generation_architecture.md",
      "docs/task_board.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/reportWorkspaceModel.test.ts",
      "frontend/src/features/report-workspace/reportWorkspaceModel.ts",
      "frontend/src/workbench.css",
      "tests/integration/test_report_workspace_api.py",
      "tests/unit/test_customer_report_document_gateway.py",
      "tests/unit/test_customer_report_projection_service.py",
      "tests/unit/test_current_report_update_service.py",
      "tests/unit/test_report_publication_gateway.py",
      "tests/unit/test_report_workspace_service.py"
    ],
    "risk_reasons": [
      "Generates and may replace an official customer report adjacent to the current internal report.",
      "Archives and atomically replaces external Word output with optimistic fingerprint checks.",
      "Uses Microsoft Word automation and approved E-4515_F conversion rules.",
      "Changes Report Workspace UI and download/publication behavior."
    ],
    "activation_head": "c630c918ebe00a87a6557b721c7be3aebba7aaec",
    "started_at": "2026-08-31T05:07:26.390808Z",
    "updated_at": "2026-08-31T05:07:26.390808Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FILE_ENCRYPTION",
    "tier": "high_risk",
    "subject": "2ec0cea0a90fa8b647afba966308165599d6fb92",
    "summary": "Add previewed one-click nonrecursive Office file encryption for trusted official project workspaces.",
    "disposition": "completed",
    "decision_ref": "user:G关闭",
    "closed_at": "2026-08-31T04:36:07.785326Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
