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
    "updated_at": "2026-08-23T23:39:36.602907Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_BROWSER_RELEASE_LLCR_GATE_AND_RUNTIME_SMOKE",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_BROWSER_RELEASE_LLCR_GATE_AND_RUNTIME_SMOKE",
      "subject": "1966e98bc782d824abb83197ad72cb61bbb65868",
      "summary": "Browser release builds now retain LLCR/CR record regression coverage, exclude an unrelated live Word COM preview test, and smoke-check the packaged server at runtime.",
      "scope_ok": true,
      "changed_paths": [
        "scripts/build_windows_browser_release.ps1",
        "scripts/smoke_windows_browser_release.ps1",
        "tests/unit/test_desktop_release_scripts.py"
      ],
      "validation": [
        {
          "name": "release script regression",
          "status": "passed",
          "detail": "10 passed in 0.28s"
        },
        {
          "name": "focused browser release gate",
          "status": "passed",
          "detail": "39 passed in 3.98s during the formal build"
        },
        {
          "name": "frontend production build",
          "status": "passed",
          "detail": "tsc -b && vite build completed"
        },
        {
          "name": "formal browser release package",
          "status": "passed",
          "detail": "dist_release/ConnLab_Web_202608240737_v0.1.0 created"
        },
        {
          "name": "packaged runtime smoke",
          "status": "passed",
          "detail": "Packaged server started on 127.0.0.1:8765; /health and / responded; temporary server stopped"
        },
        {
          "name": "diff check",
          "status": "passed",
          "detail": "git diff --check passed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Added release coverage and live packaged-server smoke behavior with regression tests."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Reviewed the exact implementation diff; no standards or specification findings."
        },
        "qa": {
          "status": "passed",
          "summary": "Validated the freshly produced package through a real local server lifecycle."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Formal local-browser release is available at dist_release/ConnLab_Web_202608240737_v0.1.0."
      }
    }
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
