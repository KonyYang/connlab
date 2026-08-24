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
    "task_id": "TASK_PROJECT_PACKAGE_DRAFT_PREVIEW",
    "summary": "Allow Project Package preview to remain usable from a Matrix draft; only formal actions require confirmed Matrix authority.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Project Package preview must render a non-authoritative Matrix draft state without requiring Matrix confirmation; confirmed authority remains required for formal actions.",
    "scope_paths": [
      "backend/application/project_package_preview_service.py",
      "backend/application/confirmed_fee_version_service.py",
      "backend/api/routes_project_package_preview.py",
      "tests/unit/test_project_package_preview_service.py",
      "tests/integration/test_project_package_preview_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "62887b9ef6d6f2aca242314c04566b7e06f6c9c4",
    "started_at": "2026-08-23T23:54:46.584360Z",
    "updated_at": "2026-08-23T23:54:46.584360Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_BROWSER_RELEASE_LLCR_GATE_AND_RUNTIME_SMOKE",
    "tier": "standard",
    "subject": "1966e98bc782d824abb83197ad72cb61bbb65868",
    "summary": "Make the browser release gate current LLCR/CR workbook behavior and make the browser smoke check start and verify the packaged local server.",
    "disposition": "completed",
    "decision_ref": "user-message-2026-08-24-close",
    "closed_at": "2026-08-23T23:46:37.671259Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
