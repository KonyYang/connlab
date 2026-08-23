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
    "task_id": "TASK_SOL_WORKFLOW_REVISE",
    "summary": "Allow in-scope feedback to return a completed task from ready_for_close to running without closing or creating a new task.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Add a guarded revise transition, expose it through the public task entry, protect it with workflow tests, and document automatic continuation semantics.",
    "scope_paths": [
      "scripts/connlab_sol_task.py",
      "scripts/run_task.ps1",
      "tests/unit/test_connlab_sol_native_workflow.py",
      "docs/project_management/SOL_NATIVE_WORKFLOW.md",
      "AGENTS.md"
    ],
    "risk_reasons": [],
    "activation_head": "a3872582456aafc736cf3cc0c6b29ab8f1d5c30c",
    "started_at": "2026-08-23T07:07:34.037938Z",
    "updated_at": "2026-08-23T07:07:34.037938Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_LLCR_CR_ONE_CLICK_DOWNLOAD",
    "tier": "standard",
    "subject": "b5e0150f44fb11c97320f238a2d219f57107aabc",
    "summary": "Simplify the Matrix Editor LLCR and CR record controls to one-click generate-and-download actions matching the Test Record interaction.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-23T06:53:24.502481Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
