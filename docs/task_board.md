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
    "task_id": "TASK_INTAKE_LTR_ROW_COMPARISON_LAYOUT",
    "summary": "Show existing and proposed LTR workbook row values side by side in a single field-aligned English comparison table.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Intake specified-LTR preview dialog presentation, accessibility, responsive styling and focused frontend regression only. Preserve preview acknowledgement and workbook write behavior.",
    "scope_paths": [
      "frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx",
      "frontend/src/intake-inbox.css",
      "frontend/src/components/workflow/new-project-workflow.css",
      "frontend/src/pages/IntakeInboxPage.test.tsx",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "8b1db641c73427a8dfa82c745637d251a80ef87b",
    "started_at": "2026-09-26T07:22:25.478363Z",
    "updated_at": "2026-09-26T07:55:03.534095Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_INTAKE_LTR_ROW_COMPARISON_LAYOUT",
      "stage": "revision",
      "status": "running",
      "summary": "User requested the existing LTR Preview changed-row background, no Changed label, and denser type so all rows fit vertically when possible.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_METHOD_VERSION_COMPACT_UI",
    "tier": "standard",
    "subject": "0038c7dab04525f94b8e97876b04a68d2f9391fa",
    "summary": "Move Matrix Method version sync into a compact table-toolbar entry with an on-demand review dialog, preserving preview, selection, and apply behavior.",
    "disposition": "completed",
    "decision_ref": "User requested final close after completed one-click Method version update.",
    "closed_at": "2026-09-26T06:23:16.758591Z"
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
