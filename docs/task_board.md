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
    "updated_at": "2026-08-27T13:20:04.724441Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_BASIC_INFORMATION_APPLICATION_DEFAULTS",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "subject": "7d71196ced448737828df3e7889c5133e1269272",
      "changed_paths": [
        "backend/application/project_basic_information_source.py",
        "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
        "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx",
        "tests/unit/test_project_basic_information_service.py"
      ],
      "roles": {
        "qa": {
          "status": "passed"
        },
        "developer": {
          "status": "passed"
        },
        "reviewer": {
          "status": "passed",
          "details": "Standards and request review found no actionable findings"
        }
      },
      "scope_ok": true,
      "integration": {
        "status": "passed",
        "details": "Committed on master and exact diff matches task scope"
      },
      "task_id": "TASK_BASIC_INFORMATION_APPLICATION_DEFAULTS",
      "version": 1,
      "schema": "connlab.sol-task-report",
      "validation": [
        {
          "status": "passed",
          "details": "31 pytest tests passed",
          "name": "backend_basic_information_suite"
        },
        {
          "status": "passed",
          "details": "31 Vitest tests passed",
          "name": "frontend_basic_information_suite"
        },
        {
          "status": "passed",
          "details": "TypeScript and Vite build passed",
          "name": "frontend_production_build"
        },
        {
          "status": "passed",
          "details": "Requested date 2023-06-19 and both disposition fields displayed; no console warnings/errors",
          "name": "browser_project_verification"
        }
      ],
      "summary": "Basic Information now receives the selected application form completion date and post-testing disposition; US-style dates display correctly and Sample deposition uses the existing mirror default."
    }
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
