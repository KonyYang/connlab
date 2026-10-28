# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 2,
  "mode": "sol_native",
  "wip_limit": 2,
  "last_closed": {
    "task_id": "TASK_GROUP_COMPLETION_20261028",
    "tier": "high_risk",
    "subject": "5ad3ba35ac03251caf39e83396b18c3b7da09d78",
    "summary": "Group completion tracking and project registry summary",
    "disposition": "completed",
    "decision_ref": "用户确认关闭组别完成统计任务",
    "closed_at": "2026-10-27T23:53:40.876783Z"
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
    },
    {
      "task_id": "TASK_LLCR_RESULT_SEMANTICS_20261023",
      "tier": "standard",
      "subject": "1c5c8a07701860d827ac0b0032e1040bf6b76a16",
      "summary": "Correct LLCR absolute resistance versus delta semantics without changing real reports",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed final Close after 261-test LLCR acceptance",
      "closed_at": "2026-10-22T23:55:52.392518Z"
    },
    {
      "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
      "tier": "high_risk",
      "subject": "41e6caed8dc1621d25065e0c54bfe1963922d3bf",
      "summary": "Report Workspace: persistent provenance, temperature/CR, mechanical appendices, photo slots and checked customer copies",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed closing the current Report Workspace capabilities 3-7 task on 2026-10-27.",
      "closed_at": "2026-10-26T23:47:10.164767Z"
    },
    {
      "task_id": "TASK_UNIFIED_PROJECT_LIBRARY_20261027",
      "tier": "high_risk",
      "subject": "f46aa1defba6442bcfe057fd976ef5566e4e577f",
      "summary": "Unified project library: managed batch intake, mutable titles, portable project data and offline takeover",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing this task, retaining local commits, with no push or publication.",
      "closed_at": "2026-10-27T23:03:07.142347Z"
    }
  ],
  "tasks": {
    "TASK_MECHANICAL_SUMMARY_TOOL_20261028": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\mechanical-summary\\connlab",
      "branch": "codex/mechanical-summary-tool",
      "resources": [],
      "integrated_head": "402e8f39778a4a6bbaeb5501e03240bc7930333b",
      "task": {
        "task_id": "TASK_MECHANICAL_SUMMARY_TOOL_20261028",
        "summary": "Standalone mechanical test summary tool",
        "tier": "standard",
        "route": "sol_build_review_qa",
        "scope": "Independent Tools workflow to assemble uploaded mechanical instrument records into editable XLSX, with isolated validation; no project integration or temperature changes",
        "scope_paths": [
          "backend/api",
          "backend/application",
          "backend/infrastructure/files",
          "backend/infrastructure/office",
          "docs/mechanical_summary_tool.md",
          "frontend/src",
          "tests"
        ],
        "risk_reasons": [],
        "activation_head": "9c9c51f30224402222f6b8d58ab41a7189871bfd",
        "started_at": "2026-10-28T10:39:42.160098Z",
        "updated_at": "2026-10-28T11:45:07.057862Z",
        "checkpoint": null,
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "scope_ok": true,
          "subject": "b74f4d0847ed5be7cc42cba57b4438518d2ca4cf",
          "validation": [
            {
              "name": "21 focused Python and Office tests",
              "status": "passed"
            },
            {
              "name": "Frontend 1079 tests, 1 skipped; production build",
              "status": "passed"
            },
            {
              "name": "Isolated browser and Excel output smoke",
              "status": "passed"
            }
          ],
          "changed_paths": [
            "backend/api/main.py",
            "backend/api/routes_tools_mechanical_summary.py",
            "backend/application/mechanical_summary.py",
            "backend/infrastructure/files/mechanical_summary_pdf.py",
            "backend/infrastructure/office/mechanical_summary_excel_copy.py",
            "backend/infrastructure/office/mechanical_summary_workbook.py",
            "frontend/src/api/mechanicalSummary.ts",
            "frontend/src/features/tools/MechanicalSummaryTool.test.tsx",
            "frontend/src/features/tools/MechanicalSummaryTool.tsx",
            "frontend/src/pages/ToolsPage.tsx",
            "frontend/src/tools.css",
            "tests/integration/test_mechanical_summary_excel_copy.py",
            "tests/integration/test_tools_mechanical_summary_api.py",
            "tests/unit/test_mechanical_summary.py"
          ],
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "b74f4d0847ed5be7cc42cba57b4438518d2ca4cf",
            "primary_before": "ef2b67f847582403a1c2827a32a4c76ae1911db3",
            "integrated_head": "402e8f39778a4a6bbaeb5501e03240bc7930333b",
            "recovered": false
          },
          "summary": "Standalone mechanical summary with reviewed PDF and XLS sources",
          "task_id": "TASK_MECHANICAL_SUMMARY_TOOL_20261028",
          "roles": {
            "reviewer": {
              "status": "passed",
              "method": "same agent focused code review"
            },
            "developer": {
              "status": "passed",
              "method": "implementation and targeted tests"
            },
            "qa": {
              "status": "passed",
              "method": "same agent clean-subject targeted backend, full frontend and build"
            }
          }
        }
      }
    }
  }
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
