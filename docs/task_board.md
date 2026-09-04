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
    "task_id": "TASK_ASTRA_USAGE_GUIDE",
    "summary": "Create a Chinese GPT-6 Astra usage guide and align active documentation.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Documentation-only Astra usage and proportional execution guidance.",
    "scope_paths": [
      "AGENTS.md",
      "docs/INDEX.md",
      "docs/project_management/SOL_NATIVE_WORKFLOW.md",
      "docs/project_management/GPT6_ASTRA_USAGE_GUIDE.md"
    ],
    "risk_reasons": [],
    "activation_head": "9dc15b1ddf22dbdcb3a50a7cde3878de5a154cc0",
    "started_at": "2026-09-04T23:17:00.410896Z",
    "updated_at": "2026-09-04T23:17:00.410896Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_REPOSITORY_TEST_BASELINE_REPAIR",
    "tier": "standard",
    "subject": "7d246edbde386f32581a449a77c969a56debd164",
    "summary": "Repair the repository test baseline by resolving Draft Measurement Plan Excel gateway import errors and the Product Spec Matrix Group P label contract mismatch.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-09-04T16:25:20.954405Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
