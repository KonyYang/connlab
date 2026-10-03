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
    "task_id": "TASK_EQUIPMENT_LIST_ONE_CLICK_UPDATE_20261003",
    "summary": "设备清单一键更新、缺失编号补录与完成统计",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "已讨论的Equipment List一键更新：纯LTR来源缺失补录无覆盖保存、来源编号去重、台账首条匹配、缺失留空、过期到期日标红、完成统计、报告归档及并发保护",
    "scope_paths": [
      "backend/application/equipment_report_update_service.py",
      "backend/application/current_report_update_service.py",
      "backend/infrastructure/office/equipment_id_document_reader.py",
      "backend/infrastructure/office/test_report_document_gateway.py",
      "backend/api/routes_report_workspace.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/reportWorkspaceModel.ts",
      "frontend/src/features/report-workspace/reportWorkspaceModel.test.ts",
      "tests/unit/test_equipment_report_update_service.py",
      "tests/unit/test_equipment_id_document_reader.py",
      "tests/unit/test_current_report_update_service.py",
      "tests/unit/test_test_report_document_gateway.py",
      "tests/integration/test_report_workspace_api.py",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [
      "authoritative report mutation and creation of external EquipmentID.docx; protect History and competing edits"
    ],
    "activation_head": "d86c443a772e596d20245d6d484ddf7708a527d5",
    "started_at": "2026-10-03T07:19:28.897091Z",
    "updated_at": "2026-10-03T08:35:34.534143Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_EQUIPMENT_LIST_ONE_CLICK_UPDATE_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_EQUIPMENT_LIST_ONE_CLICK_UPDATE_20261003",
      "subject": "27ee40b816f9894adcbaf08fecebfad5fa988051",
      "summary": "Equipment List one-click update complete; user feedback removed redundant heading and Section 7 note, retaining button and all business behavior.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_report_workspace.py",
        "backend/application/current_report_update_service.py",
        "backend/application/equipment_report_update_service.py",
        "backend/infrastructure/office/equipment_id_document_reader.py",
        "backend/infrastructure/office/test_report_document_gateway.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "frontend/src/features/report-workspace/reportWorkspaceModel.test.ts",
        "frontend/src/features/report-workspace/reportWorkspaceModel.ts",
        "tests/integration/test_report_workspace_api.py",
        "tests/unit/test_current_report_update_service.py",
        "tests/unit/test_equipment_id_document_reader.py",
        "tests/unit/test_equipment_report_update_service.py",
        "tests/unit/test_test_report_document_gateway.py"
      ],
      "validation": [
        {
          "summary": "Independent QA final revision: ReportWorkspace.test.tsx 51 passed in 6.71s; only 4 JSX lines removed.",
          "status": "passed",
          "kind": "frontend"
        },
        {
          "summary": "Independent Reviewer Standards0 Spec0; Integrator clean master and exact task scope16 verified; diff check passed.",
          "status": "passed",
          "kind": "diff"
        },
        {
          "summary": "Earlier independent QA 122 Python passed; backend unchanged. Model8 tests, build and isolated browser previously passed; not rerun for literal deletion and not claimed as new final UI checks.",
          "status": "passed",
          "kind": "retained_unchanged_backend"
        }
      ],
      "roles": {
        "reviewer": {
          "summary": "Independent revision review Standards0 Spec0; original untouched-file review retained.",
          "status": "passed",
          "context": "/root/equipment_reviewer"
        },
        "planner": {
          "summary": "只读代码数据流与精确16路径/风险验收规划",
          "status": "passed",
          "context": "/root/equipment_planner"
        },
        "integrator": {
          "summary": "Independent clean master,subject,parent and total16 scope verified; current revision evidence passed.",
          "status": "passed",
          "context": "/root/equipment_integrator"
        },
        "qa": {
          "summary": "Independent final revision QA 51 frontend tests passed6.71s; proportional omission of repeated build/backend/browser.",
          "status": "passed",
          "context": "/root/equipment_qa"
        },
        "developer": {
          "summary": "Independent developer removed four display JSX lines and self-reviewed diff; no button or behavior changes; original substantive TDD evidence retained.",
          "status": "passed",
          "context": "/root/equipment_developer"
        }
      },
      "integration": {
        "summary": "Local revision committed; no push. Original residual risks unchanged: no real-project write E2E or manual Word visual check.",
        "branch": "master",
        "status": "passed",
        "subject": "27ee40b816f9894adcbaf08fecebfad5fa988051",
        "parent": "d86c443a772e596d20245d6d484ddf7708a527d5"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_CUSTOMER_REPORT_SAFE_REGENERATION_DRAFT_20261003",
    "tier": "high_risk",
    "subject": "43521f7027c29f2e48130db90c8302adaaddec37",
    "summary": "Customer Report 安全重新生成与 Draft 下载",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭",
    "closed_at": "2026-10-03T07:12:48.178636Z"
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
