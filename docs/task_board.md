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
    "task_id": "TASK_REPORT_COMBINED_GENERATION_SOURCE_PICKER_20261003",
    "summary": "合并报告生成区并支持内部报告缺失时选择已有 DOCX 生成客户报告下载副本",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "前端合并生成区；复用现有 Tools 异步转换 API，不变更项目正式发布逻辑；保留进度和错误恢复",
    "scope_paths": [
      "frontend/src/features/report-workspace",
      "frontend/src/workbench.css",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "d2b6b2b82ee016b2f9fb994dee81806c0482e94e",
    "started_at": "2026-10-03T03:43:49.089751Z",
    "updated_at": "2026-10-03T04:26:58.106908Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_REPORT_COMBINED_GENERATION_SOURCE_PICKER_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_REPORT_COMBINED_GENERATION_SOURCE_PICKER_20261003",
      "subject": "b826bf1ce2f17de02378f83016fd13459e3d036a",
      "summary": "验收反馈已处理：客户报告完成后的进度、耗时卡片和重复下载完成提示不再常驻；绿色文件名保留，排队/运行中的进度、失败和重试继续可见。项目发布与选文件生成逻辑不变。",
      "scope_ok": true,
      "changed_paths": [
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/CustomerReportSourceDialog.tsx",
        "frontend/src/features/report-workspace/useUploadedCustomerReportJob.ts",
        "frontend/src/features/report-workspace/useUploadedCustomerReportJob.test.tsx",
        "frontend/src/workbench.css"
      ],
      "validation": [
        {
          "command": "npm test -- src/features/report-workspace/ReportWorkspace.test.tsx src/features/report-workspace/useCustomerReportJob.test.tsx src/features/report-workspace/useUploadedCustomerReportJob.test.tsx",
          "status": "passed",
          "result": "58 related tests passed on final bytes. Meaningful RED: two completed-state UI assertions failed before fix; GREEN covers official/managed/uploaded completion plus running progress and publication failure."
        },
        {
          "command": "npm run build",
          "status": "passed",
          "result": "Final TypeScript and Vite production build passed sequentially after tests."
        },
        {
          "command": "In-app browser smoke",
          "status": "passed",
          "result": "a7a5a11d report workspace now shows both green filenames without completed/elapsed card; no browser errors and no report generation triggered. Visual evidence tmp/report-completed-status-removed-20261003.png."
        },
        {
          "command": "git diff --check",
          "status": "passed",
          "result": "Exact revision limited to UI rendering guards and regression assertions, plus board; clean scoped commit."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "subject": "b826bf1ce2f17de02378f83016fd13459e3d036a",
          "result": "TDD UI-seam RED/GREEN; no hook, backend, filesystem or authority changes in this revision."
        },
        "reviewer": {
          "status": "passed",
          "subject": "b826bf1ce2f17de02378f83016fd13459e3d036a",
          "result": "Focused same-agent Standards and Spec review of exact revision: zero findings; completed state removed in both workflows, running progress and errors retained."
        },
        "qa": {
          "status": "passed",
          "subject": "b826bf1ce2f17de02378f83016fd13459e3d036a",
          "result": "Risk-proportionate final QA: all 58 report-area tests, production build and actual completed-project browser view passed. Unaffected full frontend suite and Office engine not rerun or claimed as current executions."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "b826bf1ce2f17de02378f83016fd13459e3d036a",
        "result": "Scoped local master commit, clean tree, no unrelated changes or remote publication."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_REPORT_REMOVE_DUPLICATE_HEADING_20261003",
    "tier": "micro",
    "subject": "a6d4b4a00c45eb58a3ced61868b0baac10e6da21",
    "summary": "移除报告卡片重复标题",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭",
    "closed_at": "2026-10-03T03:30:30.636966Z"
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
