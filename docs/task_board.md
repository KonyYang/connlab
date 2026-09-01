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
    "task_id": "RELEASE-007A",
    "summary": "Bundle the pywin32 win32timezone dependency in portable browser and desktop releases so packaged Excel COM can read the approved legacy equipment calibration workbook.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Change only PyInstaller hidden imports and their regression coverage; build a new browser release and validate the real equipment preview read-only without modifying project reports or external source files.",
    "scope_paths": [
      "packaging/connlab_browser_server.spec",
      "packaging/connlab_desktop.spec",
      "tests/unit/test_desktop_release_scripts.py",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "2c294abcbc4dc6c8c4323cfcc2464ab310375720",
    "started_at": "2026-09-01T16:03:50.328148Z",
    "updated_at": "2026-09-01T16:03:50.328148Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-004C",
    "tier": "high_risk",
    "subject": "03541da992c6890555b25af623314d110fd8185c",
    "summary": "Fix the Report Workspace LLCR update 500 for password-protected Internal Reports by preventing Word link-update prompts, returning actionable Office errors, and aligning the LLCR controlled-region copy with Appendix A ownership.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭 after reviewing the REPORT-004C delivery.",
    "closed_at": "2026-09-01T15:41:17.627238Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
