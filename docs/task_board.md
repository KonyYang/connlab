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
    "task_id": "TASK_PROJECT_FOLDER_ARCHIVE_RECREATE_SIMPLIFICATION",
    "summary": "Create folder archives the sole verified active LTR business folder to timestamped History and regenerates a fresh folder from template and latest confirmed information without old-file content checks.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Only the confirmed project-folder archive-and-recreate workflow, safe retirement of an unexecuted relocation checkpoint, user confirmation, focused tests and current product context. Never mutate the real operator project during validation.",
    "scope_paths": [
      "backend/api/project_folder_generation_composition.py",
      "backend/application/official_folder_relocation_service.py",
      "backend/application/official_project_workspace_service.py",
      "backend/application/project_folder_generation_service.py",
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "docs/PROJECT_CONTEXT.md",
      "docs/project_folder_generation_recovery.md",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/unit/test_official_project_workspace_service.py"
    ],
    "risk_reasons": [
      "Moves an authoritative external business folder into History before rebuilding.",
      "Changes interruption recovery and publication safeguards."
    ],
    "activation_head": "6dc76802e937ad6094a46f99782685729bc7b004",
    "started_at": "2026-09-25T13:14:31.988339Z",
    "updated_at": "2026-09-26T02:37:46.063968Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_ARCHIVE_RECREATE_SIMPLIFICATION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "roles": {
        "integrator": {
          "status": "passed",
          "summary": "Exact diff, scope, clean HEAD and board gate verified"
        },
        "planner": {
          "status": "passed",
          "summary": "Independent recovery-plan and identity-only archive rule check"
        },
        "qa": {
          "status": "passed",
          "summary": "Independent full Python and frontend suites plus production build passed"
        },
        "reviewer": {
          "status": "passed",
          "summary": "Independent final two-axis review passed"
        },
        "developer": {
          "status": "passed",
          "summary": "Approved regression test corrected; targeted tests passed"
        }
      },
      "validation": [
        {
          "status": "passed",
          "summary": "Python full suite: 3068 passed, 8 skipped, 19 Office deselected"
        },
        {
          "status": "passed",
          "summary": "Frontend full Vitest rerun: 662 passed, 1 skipped"
        },
        {
          "status": "passed",
          "summary": "Frontend production build: tsc and Vite passed"
        },
        {
          "status": "passed",
          "summary": "Approved recovery test file: 14 passed; exact diff check passed"
        },
        {
          "status": "passed",
          "summary": "Isolated real project retry previously completed; no live project mutation in final QA"
        }
      ],
      "changed_paths": [
        "backend/api/project_folder_generation_composition.py",
        "backend/application/official_folder_relocation_service.py",
        "backend/application/official_project_workspace_service.py",
        "backend/application/project_folder_generation_service.py",
        "backend/infrastructure/files/recoverable_workspace_publisher.py",
        "docs/PROJECT_CONTEXT.md",
        "docs/project_folder_generation_recovery.md",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "tests/integration/test_generation_workspace_process_recovery.py",
        "tests/integration/test_project_folder_generation_api.py",
        "tests/integration/test_project_folder_generation_recovery.py",
        "tests/unit/test_official_project_workspace_service.py"
      ],
      "schema": "connlab.sol-task-report",
      "integration": {
        "status": "passed",
        "summary": "Approved test and board-only scope amendment committed; clean worktree; no release package run; transient frontend async test passed on rerun"
      },
      "subject": "555cec43847e13918e495c5ae15a73ca8874f352",
      "task_id": "TASK_PROJECT_FOLDER_ARCHIVE_RECREATE_SIMPLIFICATION",
      "version": 1,
      "summary": "Confirmed Create folder archives the sole active LTR business folder into timestamped History, rebuilds from template and latest confirmed information, preserves crash recovery, and updates the approved process-recovery regression.",
      "scope_ok": true
    }
  },
  "last_closed": {
    "task_id": "TASK_CANONICAL_OFFICIAL_FOLDER_LIFECYCLE",
    "tier": "high_risk",
    "subject": "c469def1731e75eaa20ceb7f66c1619033b404bf",
    "summary": "Keep one active LTR-named official project folder, reconcile confirmed Basic Information names, and archive reviewed rebuild versions safely.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested Close on 2026-09-25.",
    "closed_at": "2026-09-24T23:28:26.697642Z"
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
