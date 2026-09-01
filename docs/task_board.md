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
    "updated_at": "2026-09-01T16:16:12.453028Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "RELEASE-007A",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "RELEASE-007A",
      "subject": "6b5052114ef11271ed31171fbebad4897e5036cf",
      "summary": "Bundled win32timezone in both PyInstaller release variants and produced a traceable browser release that reads the real legacy equipment calibration workbook through Excel COM.",
      "scope_ok": true,
      "changed_paths": [
        "packaging/connlab_browser_server.spec",
        "packaging/connlab_desktop.spec",
        "tests/unit/test_desktop_release_scripts.py"
      ],
      "validation": [
        {
          "name": "packaging regression",
          "status": "passed",
          "detail": "10 release script tests passed after a red-green cycle"
        },
        {
          "name": "browser release build",
          "status": "passed",
          "detail": "72 focused tests, TypeScript build, Vite build, and PyInstaller completed"
        },
        {
          "name": "archive inspection",
          "status": "passed",
          "detail": "win32timezone is present and release manifest matches commit 6b505211"
        },
        {
          "name": "real packaged equipment preview",
          "status": "passed",
          "detail": "14 rows projected, 13 matched, and no calibration workbook unavailable blocker"
        },
        {
          "name": "settings revalidation",
          "status": "passed",
          "detail": "equipment calibration Excel status is valid"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed"
        },
        "reviewer": {
          "status": "passed"
        },
        "qa": {
          "status": "passed"
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Final ConnLab_Web_202609020012_v0.1.0 was verified on port 8766 against the current project and real .xls source without updating the report or external files."
      }
    }
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
