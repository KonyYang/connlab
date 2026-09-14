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
    "task_id": "TASK_CUSTOMER_REPORT_TIMEOUT_AND_LAYOUT_REPAIR",
    "summary": "Prevent customer-report conversion from stalling on linked content and preserve the approved E-4515 continuation header and page geometry.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Repair the isolated customer-report conversion timeout behavior and Word transformation so external links are not refreshed, the template section boundary and continuation logo are retained, and body tables use the approved continuation-page margins; verify against the supplied internal, generated, and expected reports without modifying them.",
    "scope_paths": [
      "backend/infrastructure/office/customer_report_document_gateway.py",
      "backend/infrastructure/office/customer_report_subprocess_child.py",
      "backend/infrastructure/office/customer_report_subprocess_runner.py",
      "tests/unit/test_customer_report_document_gateway.py",
      "tests/unit/test_customer_report_subprocess_runner.py"
    ],
    "risk_reasons": [],
    "activation_head": "5f4a3f1676e2094caedf627b4e4276a3d6006311",
    "started_at": "2026-09-14T10:46:55.027904Z",
    "updated_at": "2026-09-14T10:46:55.027904Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_WORKBENCH_DETAILS_TOGGLE_STYLE",
    "tier": "micro",
    "subject": "b9f21ad874b3c61a12d79d6d04e02e991719e575",
    "summary": "Move the workbench-details toggle to the left and match the Test Report button style.",
    "disposition": "completed",
    "decision_ref": "User explicitly authorized stashing unrelated work and requested only this task be closed.",
    "closed_at": "2026-09-14T00:08:37.566939Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
