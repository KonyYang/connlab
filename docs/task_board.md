# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_MATRIX_SCHEDULE_INLINE_FIELDS",
    "summary": "Align Matrix Schedule labels beside their narrowed editing controls.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "In the Matrix Editor Schedule card, simplify the visible post-test label to “Post-test”, place each of the four field labels immediately left of its existing editor, enlarge labels modestly, and narrow editors so label and control fit on one line when space allows. Preserve accessible names, input values, validation, calculations, and responsive readability.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx",
      "frontend/src/workbench.css",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "b70520e63a663f2679dabbd87aa3696bd01fd470",
    "started_at": "2026-09-28T22:58:50.126617Z",
    "updated_at": "2026-09-28T23:27:57.663947Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_SCHEDULE_INLINE_FIELDS",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_SCHEDULE_INLINE_FIELDS",
      "subject": "a0d89d69bef6156ac674596728c009ac6ff81f6f",
      "summary": "Changed Schedule fields to compact intrinsic-width groups with wrapping only when needed, allowing all four controls to share one row at workstation widths while preserving narrow-screen wrapping.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx",
        "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx",
        "frontend/src/workbench.css"
      ],
      "validation": [
        {
          "name": "MatrixSchedulePlanningCard focused tests",
          "status": "passed",
          "evidence": "9/9 passed"
        },
        {
          "name": "Frontend production build",
          "status": "passed"
        },
        {
          "name": "In-app browser responsive layout inspection",
          "status": "passed",
          "evidence": "At 601px the fields wrap without overflow; computed natural group widths total about 937px including gaps, which fits in the roughly 1060px field area at the 1366px workstation breakpoint."
        },
        {
          "name": "git diff --check",
          "status": "passed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed"
        }
      },
      "integration": {
        "status": "passed",
        "evidence": "Revision committed on master as a0d89d69; working tree clean before task-board finish."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_DELTA_R_HEADER_LAYOUT",
    "tier": "micro",
    "subject": "ffe04d0ea0c4d6f9d79570a55d75559d83bc0a84",
    "summary": "Move the Matrix editor ΔR toggle into the LLCR/CR project-points header row.",
    "disposition": "completed",
    "decision_ref": "User requested CloseAndSubmit: 关闭并开始 Schedule 调整 (2026-09-29)",
    "closed_at": "2026-09-28T22:58:50.126617Z"
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
