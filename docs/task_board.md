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
    "task_id": "TASK_BROWSER_RELEASE_LLCR_GATE_AND_RUNTIME_SMOKE",
    "summary": "Make the browser release gate current LLCR/CR workbook behavior and make the browser smoke check start and verify the packaged local server.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Update the browser release build and smoke scripts with regression coverage, then build and validate a current portable browser release for today's sharing.",
    "scope_paths": [
      "scripts/build_windows_browser_release.ps1",
      "scripts/smoke_windows_browser_release.ps1",
      "tests/unit/test_desktop_release_scripts.py"
    ],
    "risk_reasons": [],
    "activation_head": "2a0ba538118307f4ab9681bc0e8eaa8fa064d411",
    "started_at": "2026-08-23T23:30:43.072947Z",
    "updated_at": "2026-08-23T23:30:43.072947Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_LLCR_REFERENCE_COLUMN_WIDTHS",
    "tier": "micro",
    "subject": "dec3314d645c9cae98b1da55dad192164af545f8",
    "summary": "Align generated LLCR workbook default column widths with the supplied approved LLCR Record workbook.",
    "disposition": "completed",
    "decision_ref": "User explicitly replied 关闭 on 2026-08-24",
    "closed_at": "2026-08-23T23:15:45.928418Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
