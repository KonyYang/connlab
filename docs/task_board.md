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
    "task_id": "TASK_BASIC_INFORMATION_APPLICATION_DEFAULTS",
    "summary": "Populate Basic Information requested completion date and sample deposition defaults from the selected application form.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fix the existing Basic Information source mapping and supported application-form date display without changing source authority or persisted user edits.",
    "scope_paths": [
      "backend/application/project_basic_information_source.py",
      "tests/unit/test_project_basic_information_service.py",
      "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx",
      "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "2168fbc260c2101a185a24bcb96677cca4119983",
    "started_at": "2026-08-27T13:06:51.684483Z",
    "updated_at": "2026-08-27T13:06:51.684483Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_CR_OPTIONAL_SELECTION",
    "tier": "standard",
    "subject": "16a6fedb789a6530ae17b05a748c7e1d777706d6",
    "summary": "Allow point profiles to confirm with no CR categories selected.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested close after completed delivery.",
    "closed_at": "2026-08-27T10:55:07.993505Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
