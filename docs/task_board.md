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
    "task_id": "TASK_EQUIPMENT_UPDATE_PERFORMANCE_FEEDBACK_20261003",
    "summary": "优化设备清单更新耗时并仅展示异常待确认项",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "测量设备清单更新性能，优化只读台账查询与重复解析；保留来源哈希校验、报告保护、更新和History归档协议；正常完成不弹窗，仅异常或待确认项显示；实际页面验证",
    "scope_paths": [
      "backend/application/external_excel_read_service.py",
      "backend/infrastructure/office",
      "tests/unit",
      "tests/integration/test_report_workspace_api.py",
      "frontend/src/features/report-workspace",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "342058fb2393886dedef4a3e6fac493b11d28186",
    "started_at": "2026-10-03T11:48:39.580110Z",
    "updated_at": "2026-10-03T12:33:32.327207Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_EQUIPMENT_UPDATE_PERFORMANCE_FEEDBACK_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "subject": "3a64ef833561e84a072d511500d695b6402a8a59",
      "scope_ok": true,
      "task_id": "TASK_EQUIPMENT_UPDATE_PERFORMANCE_FEEDBACK_20261003",
      "version": 1,
      "integration": {
        "status": "passed",
        "result": "Exact final validated local subject committed; clean; no remote publication",
        "branch": "master"
      },
      "schema": "connlab.sol-task-report",
      "summary": "保留设备台账提速及安全来源/History机制；异常窗口紧凑可滚动，成功或无需更新用按钮旁普通绿色文字反馈，重试和项目切换清除旧提示。",
      "roles": {
        "developer": {
          "status": "passed",
          "context": "current agent",
          "result": "2 meaningful RED feedback tests then GREEN; 10 targeted equipment checks and cleanup protections"
        },
        "reviewer": {
          "status": "passed",
          "context": "same agent focused sequential review, not independent",
          "result": "Corrected CSS name collision; standards and spec each 0 outstanding findings"
        },
        "qa": {
          "status": "passed",
          "context": "same agent final affected matrix and browser",
          "result": "86 frontend / build / actual narrow viewport; no backend changes requiring repeated backend matrix"
        }
      },
      "changed_paths": [
        "backend/application/external_excel_read_service.py",
        "backend/infrastructure/office/excel_com_readonly_tabular_gateway.py",
        "backend/infrastructure/office/office_facade.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "frontend/src/workbench.css",
        "tests/unit/test_equipment_report_update_service.py",
        "tests/unit/test_excel_com_readonly_tabular_gateway.py",
        "tests/unit/test_external_excel_read_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "frontend final Report suite",
          "result": "86 passed, no act warnings"
        },
        {
          "status": "passed",
          "name": "TypeScript and Vite build",
          "result": "passed after final source/test edits"
        },
        {
          "status": "passed",
          "name": "actual browser smoke",
          "result": "543px viewport: review dialog 440x161px, 18px heading; completed no-op status green regular weight400 border0 below button; Close restores button focus"
        },
        {
          "status": "passed",
          "name": "unchanged backend retained validation",
          "result": "117 passed on b5e30447; backend bytes unchanged in this revision; earlier actual 373-row catalog/9-project-row parity and 2.5-6.9s smoke retained"
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_GROUP_BASE_DEFAULTS_20261003",
    "tier": "standard",
    "subject": "84ffa8fbc887be6bb8695f86fd6e66186d6b0b05",
    "summary": "按 Matrix 组数设置默认基本费并显示参考条件悬浮提示",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭任务",
    "closed_at": "2026-10-03T11:40:52.575104Z"
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
