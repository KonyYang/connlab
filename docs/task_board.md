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
    "updated_at": "2026-10-03T04:19:53.301716Z",
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
      "subject": "f205d8048c850968b20e706a86447bf1c7a9249b",
      "summary": "已修正验收反馈：报告文件名样式不再仅匹配左侧容器；两侧共享绿色、13px、400 字重。原报告生成区和已有 DOCX 来源选择功能保持不变。",
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
          "command": "npm run build",
          "status": "passed",
          "result": "TypeScript and Vite production build passed on final CSS revision."
        },
        {
          "command": "In-app browser visual acceptance",
          "status": "passed",
          "result": "Both actual report filenames present in a7a5a11d report workspace; screenshot visually confirms identical green normal-weight typography. No report generation triggered. Evidence tmp/report-matching-filenames-verified-20261003.png."
        },
        {
          "command": "git diff --check",
          "status": "passed",
          "result": "Exact revision is one scoped filename-selector change plus board; no whitespace errors; clean committed worktree."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "subject": "f205d8048c850968b20e706a86447bf1c7a9249b",
          "result": "CSS-only feedback fix; no source-selection, API, report-generation or test changes since prior 785-pass frontend gate. No new implementation-mirroring CSS tests."
        },
        "reviewer": {
          "status": "passed",
          "subject": "f205d8048c850968b20e706a86447bf1c7a9249b",
          "result": "Focused same-agent exact revision review: Standards and Spec zero findings; shared namespaced selector covers both elements, no business changes."
        },
        "qa": {
          "status": "passed",
          "subject": "f205d8048c850968b20e706a86447bf1c7a9249b",
          "result": "Risk-proportionate CSS QA: final production build and actual browser visual check passed. Prior functional suite was 785 passed/1 opt-in skipped, not rerun or claimed as executed on this CSS revision. No Office conversion revalidation."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "f205d8048c850968b20e706a86447bf1c7a9249b",
        "result": "Scoped revision committed locally on master; clean tree and no remote publication."
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
