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
    "updated_at": "2026-10-03T12:09:24.128134Z",
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
      "integration": {
        "result": "Local exact validated subject committed, clean working tree; not pushed",
        "branch": "master",
        "status": "passed"
      },
      "summary": "设备台账离线优先读取，保留只读Excel回退及完整来源/History保护；正常完成不弹窗，仅实际设备问题显示处理提示。",
      "subject": "b5e3044770019e9d39927fcd243f5c0dbc24650b",
      "task_id": "TASK_EQUIPMENT_UPDATE_PERFORMANCE_FEEDBACK_20261003",
      "schema": "connlab.sol-task-report",
      "changed_paths": [
        "backend/application/external_excel_read_service.py",
        "backend/infrastructure/office/excel_com_readonly_tabular_gateway.py",
        "backend/infrastructure/office/office_facade.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "tests/unit/test_equipment_report_update_service.py",
        "tests/unit/test_excel_com_readonly_tabular_gateway.py",
        "tests/unit/test_external_excel_read_service.py"
      ],
      "scope_ok": true,
      "validation": [
        {
          "name": "backend affected matrix",
          "result": "117 passed; existing Starlette/httpx deprecation warning",
          "status": "passed"
        },
        {
          "name": "Report frontend suite",
          "result": "85 passed",
          "status": "passed"
        },
        {
          "name": "TypeScript and Vite build",
          "result": "passed",
          "status": "passed"
        },
        {
          "name": "real catalog differential",
          "result": "373 rows; only optional UTC offset representation differs; 9 project rows, warnings and blockers identical",
          "status": "passed"
        },
        {
          "name": "actual browser smoke",
          "result": "Repeated click-to-completion 2472ms and 6926ms; no healthy dialog; report SHA256 and History file count unchanged",
          "status": "passed"
        }
      ],
      "roles": {
        "qa": {
          "context": "same agent final affected matrix and actual browser",
          "result": "117 backend / 85 frontend / production build / real Office differential",
          "status": "passed"
        },
        "reviewer": {
          "context": "same agent focused sequential review, not independent",
          "standards_findings": 0,
          "status": "passed",
          "spec_findings": 0
        },
        "developer": {
          "context": "current agent",
          "result": "Meaningful backend/frontend RED then targeted GREEN; no authority/publication protocol changes",
          "status": "passed"
        }
      },
      "version": 1
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
