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
    "task_id": "REPORT-003E",
    "summary": "Recover safely when a customer report is deleted or moved after page preview by refreshing state and requiring explicit confirmation before generating a new report.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Add a typed missing-after-preview conflict and an explicit regenerate-or-cancel UI without weakening internal-report or external-file concurrency guards.",
    "scope_paths": [
      "backend/application/customer_report_projection_service.py",
      "backend/api/routes_report_workspace.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "tests/unit/test_customer_report_projection_service.py",
      "tests/integration/test_report_workspace_api.py",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [
      "The action publishes a formal customer report into the authoritative external project folder.",
      "Stale browser state must never overwrite a customer report that reappears or use an internal report that changed after confirmation."
    ],
    "activation_head": "3c17d3ce589c7cbdebffc3773a395f5105bba1d6",
    "started_at": "2026-08-31T22:34:32.063356Z",
    "updated_at": "2026-08-31T22:34:32.063356Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-003D",
    "tier": "high_risk",
    "subject": "fb8faf053bec9f8221853ac6cf2d619b08a7636c",
    "summary": "Automatically open DGLAB-protected Word and PowerPoint files across current ConnLab Office workflows while preserving protected report update safety.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭.",
    "closed_at": "2026-08-31T22:25:21.142481Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
