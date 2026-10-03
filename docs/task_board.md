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
    "task_id": "TASK_TOOLS_EQUIPMENT_LIST_UPDATE_20261003",
    "summary": "Tools 添加任意内部报告设备清单更新快捷工具",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "上传内部报告与设备来源，复用设备校准匹配，输出下载副本并保留原文件；不修改项目或发布权威文件",
    "scope_paths": [
      "backend/application/equipment_report_update_service.py",
      "backend/application/tools_equipment_report_service.py",
      "backend/api/routes_tools.py",
      "backend/api/dependencies.py",
      "frontend/src/pages/ToolsPage.tsx",
      "frontend/src/pages/ToolsPage.test.tsx",
      "frontend/src/features/tools",
      "frontend/src/api/client.ts",
      "frontend/src/tools.css",
      "tests/unit/test_tools_equipment_report_service.py",
      "tests/integration/test_tools_equipment_report_api.py",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "a0529e90b7952e83d3b06f67d677423e6b2d1bba",
    "started_at": "2026-10-03T12:54:03.891740Z",
    "updated_at": "2026-10-03T13:26:10.784086Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TOOLS_EQUIPMENT_LIST_UPDATE_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "task_id": "TASK_TOOLS_EQUIPMENT_LIST_UPDATE_20261003",
      "version": 1,
      "scope_ok": true,
      "validation": [
        {
          "detail": "109 affected tests passed; one pre-existing Starlette deprecation warning; Office-marked tests excluded",
          "status": "passed",
          "name": "Backend QA"
        },
        {
          "detail": "74 tests passed: ToolsPage, equipment API, ReportWorkspace, App",
          "status": "passed",
          "name": "Frontend QA"
        },
        {
          "detail": "TypeScript and Vite production build passed",
          "status": "passed",
          "name": "Build"
        },
        {
          "detail": "Final code: document mode 1.98s, 12 rows, only DG-Q-0185 unmatched; text mode 1.34s, 1 deduplicated healthy row. Both original hashes and unrelated manual report content unchanged. Requests use running Vite proxy; no project data mutated.",
          "status": "passed",
          "name": "Live API"
        },
        {
          "detail": "Checked missing report, source switching, text entry, and narrow layout. Radios are 16x16. Browser upload automation unavailable; successful file updates/downloads verified at live API plus frontend tests, not claimed as full manual UI upload.",
          "status": "passed",
          "name": "Browser interaction"
        },
        {
          "detail": "Exact changed files reviewed; diff check passed; clean local master",
          "status": "passed",
          "name": "Diff"
        }
      ],
      "summary": "Tools 新增兼容内部报告设备清单快捷更新，下载副本且保留原件和项目权威",
      "roles": {
        "qa": {
          "context": "Same-agent final affected matrix on reviewed final bytes",
          "status": "passed"
        },
        "developer": {
          "context": "Same-agent implementation and TDD RED/GREEN at public service/API/UI boundaries",
          "status": "passed"
        },
        "reviewer": {
          "context": "Separate focused Standards and Spec passes by same agent; zero material remaining findings; no independent-agent claim",
          "status": "passed"
        }
      },
      "schema": "connlab.sol-task-report",
      "integration": {
        "detail": "Exact verified subject committed on clean local master; not published",
        "status": "passed"
      },
      "subject": "757c39d6df9a21cf1d9e430ebe4c3760f108ead7",
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/routes_tools.py",
        "backend/application/equipment_report_update_service.py",
        "backend/application/tools_equipment_report_service.py",
        "backend/infrastructure/office/test_report_document_gateway.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/api/client.ts",
        "frontend/src/api/toolsEquipment.test.ts",
        "frontend/src/features/tools/EquipmentListTool.tsx",
        "frontend/src/pages/ToolsPage.test.tsx",
        "frontend/src/pages/ToolsPage.tsx",
        "frontend/src/tools.css",
        "tests/integration/test_tools_equipment_report_api.py",
        "tests/unit/test_tools_equipment_report_service.py"
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_EQUIPMENT_UPDATE_PERFORMANCE_FEEDBACK_20261003",
    "tier": "standard",
    "subject": "3a64ef833561e84a072d511500d695b6402a8a59",
    "summary": "优化设备清单更新耗时并仅展示异常待确认项",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭",
    "closed_at": "2026-10-03T12:42:13.941073Z"
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
