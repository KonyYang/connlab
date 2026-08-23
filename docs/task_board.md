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
  "state": "ready_for_close",
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
    "updated_at": "2026-08-23T07:14:46.882981Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_SOL_WORKFLOW_REVISE",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "summary": "Added an explicit Revise transition and public entry so in-scope feedback resumes the same completed task automatically without close-and-reopen ceremony.",
      "version": 1,
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented with focused red-green tests and self-review."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards and specification review found no actionable findings."
        },
        "qa": {
          "status": "passed",
          "summary": "Complete workflow test file passed: 24 tests."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Implementation is committed on the primary branch with a clean worktree."
      },
      "changed_paths": [
        "AGENTS.md",
        "docs/project_management/SOL_NATIVE_WORKFLOW.md",
        "scripts/connlab_sol_task.py",
        "scripts/run_task.ps1",
        "tests/unit/test_connlab_sol_native_workflow.py"
      ],
      "schema": "connlab.sol-task-report",
      "scope_ok": true,
      "subject": "233149fcb5eb51f2e3fde4cb6afd40a774b4a71c",
      "task_id": "TASK_SOL_WORKFLOW_REVISE",
      "validation": [
        {
          "status": "passed",
          "summary": "24 workflow unit tests passed on the clean implementation commit."
        }
      ]
    }
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
