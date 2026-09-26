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
    "task_id": "TASK_MATRIX_METHOD_VERSION_COMPACT_UI",
    "summary": "Move Matrix Method version sync into a compact table-toolbar entry with an on-demand review dialog, preserving preview, selection, and apply behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Matrix Editor frontend layout and interaction only; preserve existing backend draft and confirmation semantics.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixMethodVersionSyncPanel.tsx",
      "frontend/src/features/matrix-editor/MatrixMethodVersionSyncPanel.test.tsx",
      "frontend/src/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "a8621582e1faa4411561948e26286629345ddb9a",
    "started_at": "2026-09-26T04:21:39.101968Z",
    "updated_at": "2026-09-26T04:42:42.482710Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_METHOD_VERSION_COMPACT_UI",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "scope_ok": true,
      "integration": {
        "status": "passed",
        "detail": "Committed exact six frontend paths on master; clean tree"
      },
      "task_id": "TASK_MATRIX_METHOD_VERSION_COMPACT_UI",
      "summary": "Matrix Method version sync now opens from the table toolbar in an on-demand review dialog; preview, selected apply, saved-draft checks, and Matrix confirmation remain intact.",
      "roles": {
        "developer": {
          "status": "passed",
          "detail": "Implemented and ran targeted tests"
        },
        "qa": {
          "status": "passed",
          "detail": "Sequential same-agent full frontend test/build and UI smoke"
        },
        "reviewer": {
          "status": "passed",
          "detail": "Sequential same-agent standards and spec review; no findings"
        }
      },
      "subject": "90005c3dfe91662ea2f7479a4a8adc4c7f4b028b",
      "validation": [
        {
          "check": "TDD red/green targeted Method review tests",
          "status": "passed"
        },
        {
          "check": "Frontend full Vitest: 670 passed, 1 skipped",
          "status": "passed"
        },
        {
          "check": "TypeScript and Vite production build",
          "status": "passed"
        },
        {
          "check": "In-app browser narrow viewport, dialog and Escape/focus verification",
          "status": "passed"
        },
        {
          "check": "git diff --check",
          "status": "passed"
        }
      ],
      "schema": "connlab.sol-task-report",
      "changed_paths": [
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixMethodVersionSyncPanel.test.tsx",
        "frontend/src/features/matrix-editor/MatrixMethodVersionSyncPanel.tsx",
        "frontend/src/workbench.css"
      ],
      "version": 1
    }
  },
  "last_closed": {
    "task_id": "TASK_BASIC_INFORMATION_CANCEL_RELOAD_AUTHORITY",
    "tier": "standard",
    "subject": "9600f2ed7e18c5ba80d9401a2cabfd61f5417627",
    "summary": "After Cancel exits Project Basic Information, the next explicit entry from the Project Workbench should load the authoritative Basic Information version; leaving and returning through sidebar navigation should continue restoring the existing draft behavior.",
    "disposition": "completed",
    "decision_ref": "User requested close of current task on 2026-09-26.",
    "closed_at": "2026-09-26T03:28:34.583873Z"
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
