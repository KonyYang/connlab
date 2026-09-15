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
    "task_id": "TASK_PROJECT_CUSTOMER_REPORT_PROGRESS",
    "summary": "Project customer report background generation with real progress and recoverable results",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Implement the authorized customer report background lifecycle, progress, recovery and downloads, preserving official publication authority and Tools compatibility.",
    "scope_paths": [
      "backend/application/project_customer_report_job_service.py",
      "backend/application/customer_report_projection_service.py",
      "backend/api/routes_report_workspace.py",
      "backend/api/dependencies.py",
      "backend/api/project_customer_report_runner.py",
      "backend/infrastructure/office/customer_report_subprocess_runner.py",
      "backend/infrastructure/files/report_publication_gateway.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/useCustomerReportJob.ts",
      "frontend/src/features/report-workspace/useCustomerReportJob.test.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "frontend/src/components/common/CustomerReportProgress.tsx",
      "frontend/src/components/common/customer-report-progress.css",
      "frontend/src/pages/ToolsPage.tsx",
      "frontend/src/tools.css",
      "tests/unit/test_project_customer_report_job_service.py",
      "tests/unit/test_customer_report_projection_service.py",
      "tests/unit/test_customer_report_subprocess_runner.py",
      "tests/integration/test_project_customer_report_job_api.py",
      "tests/integration/test_project_customer_report_runner.py",
      "docs/project_customer_report_progress.md"
    ],
    "risk_reasons": [
      "Move authoritative external report publication into a background task while preserving conflict and archive guarantees"
    ],
    "activation_head": "4d73358271b4a99e82dcef3293e783bfe96e1f73",
    "started_at": "2026-09-14T23:54:54.505598Z",
    "updated_at": "2026-09-15T00:30:27.103829Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_CUSTOMER_REPORT_PROGRESS",
      "stage": "scope_approval",
      "status": "blocked",
      "summary": "Current-scope implementation/review complete: backend QA89, frontend QA39 and production build passed. Main-agent isolated browser smoke verified real stage/elapsed, refresh recovery, managed downloads and official archives; controlled writer, no business reports or release EXE used. Awaiting explicit approval to extend gateway+child+tests for task-owned Word PID/creation-identity timeout cleanup. Current timeout kills Python child but cannot prove separate Word COM process release. Not ready_for_close. Planner/QA and Reviewer/Integrator contexts reused due four-agent host limit, not five independent contexts.",
      "requires_user": true
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_DEVELOPMENT_LOG_PERSISTENCE",
    "tier": "micro",
    "subject": "1a0f99c025b108b7507744d1fa23946fe6872b0c",
    "summary": "Persist development runtime logs and export them through existing diagnostics",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closure in this conversation.",
    "closed_at": "2026-09-14T23:52:39.624411Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
