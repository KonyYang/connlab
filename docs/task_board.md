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
    "task_id": "TASK_REPORT_REMOVE_DUPLICATE_HEADING_20261003",
    "summary": "移除报告卡片重复标题",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove only the visible Internal Report heading and its empty heading wrapper from first report card; retain accessible region label, current path, generation action and all workflow behavior. Validate existing related UI tests and actual browser.",
    "scope_paths": [
      "frontend/src/features/report-workspace/ReportWorkspace.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "56db8460c4fb7846160724dc757ff899bfc6e870",
    "started_at": "2026-10-03T03:18:48.225658Z",
    "updated_at": "2026-10-03T03:29:29.197725Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_REPORT_REMOVE_DUPLICATE_HEADING_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_REPORT_REMOVE_DUPLICATE_HEADING_20261003",
      "subject": "a6d4b4a00c45eb58a3ced61868b0baac10e6da21",
      "summary": "Removed repeated card heading. Generate is left-aligned above filename only; filename green,13px,normal400 weight. No report generation/archive/file behaviors changed.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/workbench.css",
        "docs/PROJECT_CONTEXT.md"
      ],
      "validation": [
        {
          "command": "npm run test -- --run src/features/report-workspace/ReportWorkspace.test.tsx src/features/report-workspace/reportWorkspaceModel.test.ts",
          "status": "passed",
          "result": "Final exact bytes43passed,0skips. TDD filename-only test RED on prior path display thenGREEN; filename order and existing cancel/retry/managed publication flows covered."
        },
        {
          "command": "npm run build",
          "status": "passed",
          "result": "Final exact bytes tsc-b/Vite passed157modules, no warnings."
        },
        {
          "command": "In-app browser actual report workspace738px screenshot inspection; git diff --check",
          "status": "passed",
          "result": "Filename only under left Generate,green normal text; no repeated heading/path. Viewed tmp/report-filename-normal-20261003.png; logs empty. No external report writes. diff clean."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "subject": "a6d4b4a00c45eb58a3ced61868b0baac10e6da21",
          "result": "Single-agent micro implementation plus code-review self-review: Standards0findings,Spec0findings; TDD public UI boundary; no independent agents claimed."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "a6d4b4a00c45eb58a3ced61868b0baac10e6da21",
        "result": "Clean local master,4product paths coherent in-scope feedback; doc updated. Await User close; no push."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_INTERNAL_REPORT_INITIALIZE_REGENERATE_20261003",
    "tier": "high_risk",
    "subject": "5805d8af1dbf158ee0f535ca79357cd8df14d3cc",
    "summary": "Internal Report 初始化与安全重新生成",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭",
    "closed_at": "2026-10-03T03:16:59.746854Z"
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
