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
    "task_id": "TASK_BASIC_INFORMATION_LEGACY_CLEANUP",
    "summary": "Remove verified dead Basic Information schedule UI configuration and unused application-form date projections without changing legacy compatibility behavior.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Basic Information empty schedule UI configuration and unused application form identity projections only.",
    "scope_paths": [
      "frontend/src/features/project-basic-information/basicInformationFieldConfig.ts",
      "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx",
      "backend/application/project_basic_information_output_identity.py",
      "tests/unit/test_project_basic_information_output_identity.py"
    ],
    "risk_reasons": [],
    "activation_head": "5760e0050b9a8987c94615d5f2a105218e6f3b7e",
    "started_at": "2026-09-09T10:56:31.963765Z",
    "updated_at": "2026-09-09T10:56:31.963765Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_SCHEDULE_PREFLIGHT",
    "tier": "standard",
    "subject": "1ae9f3dd5924cf56f1284f51f8f918eb6e5fa6d1",
    "summary": "Validate confirmed Project Schedule before Project Folder generation starts so the workflow never reaches Customer Feedback with a missing date authority.",
    "disposition": "completed",
    "decision_ref": "用户明确同意先关闭当前任务，并实施已核对的小范围清理。",
    "closed_at": "2026-09-09T10:56:31.963765Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
