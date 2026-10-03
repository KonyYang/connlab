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
    "task_id": "TASK_TOOLS_CONCISE_UI_20261003",
    "summary": "精简 Tools 页面重复说明和正常状态信息",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "仅精简 Tools 展示层，保留输入、运行状态、绿色结果文件名与异常提示，不改变 API 或文件操作",
    "scope_paths": [
      "frontend/src/pages/ToolsPage.tsx",
      "frontend/src/pages/ToolsPage.test.tsx",
      "frontend/src/features/tools/EquipmentListTool.tsx",
      "frontend/src/tools.css"
    ],
    "risk_reasons": [],
    "activation_head": "8bd16ae9739bfa67c912b51130b25cabaa719ecd",
    "started_at": "2026-10-03T15:49:12.111414Z",
    "updated_at": "2026-10-03T15:55:16.674623Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TOOLS_CONCISE_UI_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "version": 1,
      "changed_paths": [
        "frontend/src/features/tools/EquipmentListTool.tsx",
        "frontend/src/pages/ToolsPage.test.tsx",
        "frontend/src/pages/ToolsPage.tsx",
        "frontend/src/tools.css"
      ],
      "integration": {
        "status": "passed",
        "summary": "Exact subject committed locally to master; clean worktree, no remote publication before User Close."
      },
      "schema": "connlab.sol-task-report",
      "subject": "ca1b1dcb49af57973822820397646c7c98da8607",
      "summary": "Tools 去掉介绍卡和重复状态，三工具仅保留必要输入、运行反馈、绿色下载文件名和实际异常；API及文件处理不变。",
      "task_id": "TASK_TOOLS_CONCISE_UI_20261003",
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Same Astra agent implementation and sequential Standards/Spec self-review; 0 findings on each axis."
        }
      },
      "scope_ok": true,
      "validation": [
        {
          "status": "passed",
          "summary": "TDD: 3 failures before change; ToolsPage 8 passed after change. Final related frontend 74 passed; TypeScript/Vite build passed; diff check passed."
        },
        {
          "status": "passed",
          "summary": "Live in-app browser narrow layout inspected; customer/equipment missing-source errors, equipment text mode and clean reload verified. Successful downloads covered by component tests; no real Office regeneration required."
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_TOOLS_EQUIPMENT_LIST_UPDATE_20261003",
    "tier": "standard",
    "subject": "757c39d6df9a21cf1d9e430ebe4c3760f108ead7",
    "summary": "Tools 添加任意内部报告设备清单更新快捷工具",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭",
    "closed_at": "2026-10-03T15:42:55.599957Z"
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
