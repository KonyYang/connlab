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
    "task_id": "TASK_BASIC_INFORMATION_CANCEL_RELOAD_AUTHORITY",
    "summary": "After Cancel exits Project Basic Information, the next explicit entry from the Project Workbench should load the authoritative Basic Information version; leaving and returning through sidebar navigation should continue restoring the existing draft behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Keep Cancel distinct from ordinary route/sidebar navigation. A Cancel-return followed by clicking Basic Information should initialize the editor from the latest confirmed Basic Information authority, falling back to current upstream field suggestions when no confirmed version exists. Sidebar navigation away from and back to Basic Information must keep the existing draft-first load behavior. Do not delete persisted drafts or change backend authority/write semantics.",
    "scope_paths": [
      "frontend/src/App.tsx",
      "frontend/src/pages/ProjectBasicInformationPage.tsx",
      "frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts",
      "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
      "frontend/src/App.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "562ccc692597695a18b1921875738affa114afdd",
    "started_at": "2026-09-26T03:04:10.401636Z",
    "updated_at": "2026-09-26T03:26:29.806327Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_BASIC_INFORMATION_CANCEL_RELOAD_AUTHORITY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_BASIC_INFORMATION_CANCEL_RELOAD_AUTHORITY",
      "subject": "9600f2ed7e18c5ba80d9401a2cabfd61f5417627",
      "summary": "Cancel exits Basic Information; the next workbench re-entry loads latest confirmed authority (or current source suggestions when none exists), while sidebar navigation preserves draft-first behavior. The one-shot Cancel marker is cleared when navigating away via the sidebar.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/App.test.tsx",
        "frontend/src/App.tsx",
        "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
        "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx",
        "frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts",
        "frontend/src/pages/ProjectBasicInformationPage.tsx"
      ],
      "validation": [
        {
          "name": "Focused route and workspace tests",
          "status": "passed",
          "result": "27 passed"
        },
        {
          "name": "Complete Frontend QA",
          "status": "passed",
          "result": "88 test files passed, 1 skipped; 667 tests passed, 1 skipped; Vite production build passed"
        },
        {
          "name": "Git diff check",
          "status": "passed",
          "result": "No whitespace errors"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented; initial targeted RED reproduced the sidebar-marker leak; fixed it and reran focused tests."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Primary agent performed separate Standards and Spec passes; found and fixed one route-boundary issue, then re-reviewed. Not an independent-agent review."
        },
        "qa": {
          "status": "passed",
          "summary": "Primary agent ran the complete frontend suite and production build on the reviewed state."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "direct_primary",
        "summary": "Integrated as 9600f2ed7e18c5ba80d9401a2cabfd61f5417627 on master; clean after commit."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_ARCHIVE_RECREATE_SIMPLIFICATION",
    "tier": "high_risk",
    "subject": "555cec43847e13918e495c5ae15a73ca8874f352",
    "summary": "Create folder archives the sole verified active LTR business folder to timestamped History and regenerates a fresh folder from template and latest confirmed information without old-file content checks.",
    "disposition": "completed",
    "decision_ref": "User requested final close on 2026-09-26.",
    "closed_at": "2026-09-26T02:40:03.174297Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_361A_FEE_SUMMARY_ACCEPTANCE_CONTRACT",
      "tier": "standard",
      "closed_at": "2026-09-18T03:01:50.000000Z"
    },
    {
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS_COMPLETE",
      "tier": "high_risk",
      "closed_at": "2026-09-17T11:59:24.022479Z"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.

## Pending engineering-debt tasks ( backlog / not active )

These items are not in-flight; they are recorded here for prioritization. They do not
change the `active` field above.

### TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT

**Tier:** micro
**Revised from:** the stale broad test-environment proposal discovered during TASK_361A
**Goal:** Keep the supported test entry point on the same Python runtime as ConnLab development.

The original diagnosis was rechecked before implementation:

- `C:/PythonEnvs/connlab/.venv` is Python 3.11.9 and imports Tkinter 8.6 successfully; no
  dependency installation is needed.
- Office-dependent integration tests already use the `office_integration` marker. The normal gate
  excludes them and `-Suite Office` remains the explicit installed-Office check.
- WorkBuddy or Codex temporary-directory and safe-delete restrictions are host permissions, not
  ConnLab product behavior. They must be handled by the runner environment or an explicitly
  permitted pytest temp location, not by weakening repository cleanup or test semantics.

The remaining defect was limited to `scripts/run_tests.ps1`: it invoked the ambient `py` launcher,
which selected Python 3.13.3 instead of the Python 3.11.9 environment used by ConnLab. The revised
runner defaults to `C:/PythonEnvs/connlab/.venv/Scripts/python.exe`, supports an explicit
`-PythonExe` override, fails clearly when that interpreter is missing, and preserves the existing
normal/Office split.

**Validation:** the focused runner contract passes, and the complete non-Office Python gate passes
with 2954 tests, 7 skips, and 19 Office tests deselected on Python 3.11.9. No product code,
dependencies, Office implementation, or host safety policy changed.
