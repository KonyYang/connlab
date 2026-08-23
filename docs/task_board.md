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
    "task_id": "TASK_MATRIX_EDITOR_LLCR_CR_DRAFT_DOWNLOAD",
    "summary": "Generate LLCR and CR preview workbooks from the current Matrix Editor draft, matching Test Record behavior and resolving explicit split sample allocations safely.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Add a one-click Matrix Editor draft generation path for LLCR and CR, preserve confirmed-Matrix generation for authoritative downstream use, and add regression coverage for current-draft precedence and explicit 5+5(d) LLCR allocation.",
    "scope_paths": [
      "frontend/src/features/matrix-editor",
      "frontend/src/api/client.ts",
      "backend/api",
      "backend/application",
      "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
      "tests/unit",
      "tests/integration"
    ],
    "risk_reasons": [],
    "activation_head": "cda1548f1e51b78a1e5a586de1bc17b7f6e8d019",
    "started_at": "2026-08-23T07:37:10.394579Z",
    "updated_at": "2026-08-23T07:37:10.394579Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_SOL_WORKFLOW_REVISE",
    "tier": "standard",
    "subject": "233149fcb5eb51f2e3fde4cb6afd40a774b4a71c",
    "summary": "Allow in-scope feedback to return a completed task from ready_for_close to running without closing or creating a new task.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-23T07:16:11.423390Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
