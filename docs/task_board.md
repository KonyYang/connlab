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
    "task_id": "TASK_CUSTOMER_REPORT_SAFE_REGENERATION_DRAFT_20261003",
    "summary": "Customer Report 安全重新生成与 Draft 下载",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Customer Report 已存在时确认归档重新生成或取消；显式重新生成即使相同内容也归档；缺失项目文件夹走已有下载通道并使用 draft 后缀；保留现有来源、指纹、锁和失败恢复，LLCR及Equipment更新行为不变",
    "scope_paths": [
      "backend/application/customer_report_projection_service.py",
      "backend/infrastructure/files/report_publication_gateway.py",
      "tests/unit/test_customer_report_projection_service.py",
      "tests/unit/test_report_publication_gateway.py",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "frontend/src/features/report-workspace/CustomerReportRegenerationDialog.tsx",
      "frontend/src/features/report-workspace/useUploadedCustomerReportJob.ts",
      "frontend/src/features/report-workspace/useUploadedCustomerReportJob.test.tsx",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [
      "Explicit regeneration archives and replaces an authoritative external customer report"
    ],
    "activation_head": "152ae46d0a8ba3162ac22820664f103dd599428b",
    "started_at": "2026-10-03T06:26:35.015541Z",
    "updated_at": "2026-10-03T07:10:13.885396Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CUSTOMER_REPORT_SAFE_REGENERATION_DRAFT_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "integration": {
        "status": "passed",
        "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
        "result": "Local master commits e003ca98 task rollover, 67140d37 implementation, 43521f70 focus fix; clean reviewed subject. No merge needed in legacy direct workflow; no push."
      },
      "schema": "connlab.sol-task-report",
      "scope_ok": true,
      "summary": "Customer Report 已存在时确认归档后重新生成或取消；显式重新生成包括同字节归档；无项目文件夹下载副本加 draft。浏览器验收发现并补修 Cancel/Esc 焦点恢复；业务报告未替换。",
      "changed_paths": [
        "backend/application/customer_report_projection_service.py",
        "backend/infrastructure/files/report_publication_gateway.py",
        "tests/unit/test_customer_report_projection_service.py",
        "tests/unit/test_report_publication_gateway.py",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/CustomerReportRegenerationDialog.tsx",
        "frontend/src/features/report-workspace/useUploadedCustomerReportJob.ts",
        "frontend/src/features/report-workspace/useUploadedCustomerReportJob.test.tsx",
        "docs/PROJECT_CONTEXT.md"
      ],
      "version": 1,
      "validation": [
        {
          "command": "pytest -p no:cacheprovider tests/unit/test_report_publication_gateway.py tests/unit/test_customer_report_projection_service.py tests/unit/test_current_report_update_service.py tests/unit/test_internal_report_generation_service.py tests/unit/test_project_customer_report_job_service.py tests/unit/test_tools_customer_report_job_service.py tests/integration/test_project_customer_report_job_api.py tests/integration/test_project_customer_report_runner.py tests/integration/test_internal_report_generation_api.py tests/integration/test_tools_customer_report_job_api.py tests/integration/test_report_workspace_api.py -q",
          "status": "passed",
          "result": "90 passed on 67140d37; final focus fix changed frontend only, backend/test bytes unchanged. One Starlette/httpx deprecation warning."
        },
        {
          "command": "npm.cmd test -- src/features/report-workspace",
          "status": "passed",
          "result": "Final subject 43521f70: 78 tests passed, no skipped. Developer meaningful RED/GREEN for same-byte archives, draft naming, confirmation and Cancel/Escape focus restoration."
        },
        {
          "command": "npm.cmd run build",
          "status": "passed",
          "result": "Final subject TypeScript and Vite production build passed sequentially after affected frontend tests."
        },
        {
          "command": "In-app browser smoke and business report fingerprint comparison",
          "status": "passed",
          "result": "Final live existing-report modal: Cancel/Escape no generation, focus returns to trigger, Tab wrapping works. Missing-source picker opens/cancels without upload. Console warnings/errors empty, both business report hashes unchanged. Screenshot tmp/customer-regeneration-qa-final-modal-20261003.png. No live Office conversion or business archive performed. Existing unchanged source-picker Cancel focus-to-body issue is outside scope/non-blocking."
        },
        {
          "command": "git diff --check and exact scope/subject inspection",
          "status": "passed",
          "result": "Final clean master, exact ten approved paths, parent/tree checked independently; no unrelated changes or remote publication."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
          "result": "Independent Planner approved minimal compatible archive_unchanged opt-in, captured hashes and draft-only naming; exact ten-file plan and risk-based matrix."
        },
        "integrator": {
          "status": "passed",
          "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
          "result": "Independent Integrator verified clean master, parent chain, tree 3fcd2902609a380cbee4440c9188c30653b6266b, exact ten-file cumulative scope and accepted final Reviewer/QA. No integration blocker."
        },
        "reviewer": {
          "status": "passed",
          "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
          "result": "Independent Reviewer full initial ten-file change plus focused three-file final fix: Standards0, Spec0; no findings."
        },
        "qa": {
          "status": "passed",
          "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
          "result": "Independent final QA: Python90 unchanged-backend evidence, final report-feature78 tests/build/live browser and unchanged business hashes. Earlier full frontend794 + optional performance skip was pre-fix historical only. Source-picker focus residual and no live Office conversion recorded."
        },
        "developer": {
          "status": "passed",
          "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
          "result": "Independent Developer TDD: initial Python38 and UI57; bounded focus RED2/GREEN47. No generic Tools/API/job contract changes or external report mutation."
        }
      },
      "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
      "task_id": "TASK_CUSTOMER_REPORT_SAFE_REGENERATION_DRAFT_20261003"
    }
  },
  "last_closed": {
    "task_id": "TASK_REPORT_COMBINED_GENERATION_SOURCE_PICKER_20261003",
    "tier": "standard",
    "subject": "b826bf1ce2f17de02378f83016fd13459e3d036a",
    "summary": "合并报告生成区并支持内部报告缺失时选择已有 DOCX 生成客户报告下载副本",
    "disposition": "completed",
    "decision_ref": "User authorizes closing current task and opening Customer Report 安全重新生成与 Draft 下载",
    "closed_at": "2026-10-03T06:26:35.015541Z"
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
