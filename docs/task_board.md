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
    "task_id": "TASK_EQUIPMENT_TABLE_FONT_20261030",
    "tier": "standard",
    "subject": "d1ee9f3c58be943f5ec4e7e6536e2e7020e93b7c",
    "summary": "Preserve equipment table typography after clearing and refilling cells",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closing the current equipment-table font repair task after 127 affected tests, 164 release checks, and successful new-EXE validation of three real document scenarios.",
    "closed_at": "2026-10-30T05:59:50.377281Z"
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
    },
    {
      "task_id": "TASK_GROUP_COMPLETION_20261028",
      "tier": "high_risk",
      "subject": "5ad3ba35ac03251caf39e83396b18c3b7da09d78",
      "summary": "Group completion tracking and project registry summary",
      "disposition": "completed",
      "decision_ref": "用户确认关闭组别完成统计任务",
      "closed_at": "2026-10-27T23:53:40.876783Z"
    },
    {
      "task_id": "TASK_MECHANICAL_SUMMARY_TOOL_20261028",
      "tier": "standard",
      "subject": "b74f4d0847ed5be7cc42cba57b4438518d2ca4cf",
      "summary": "Standalone mechanical test summary tool",
      "disposition": "completed",
      "decision_ref": "用户确认关闭 Tools 独立机械 Summary 第一部分",
      "closed_at": "2026-10-28T14:02:09.933828Z"
    },
    {
      "task_id": "TASK_PROJECT_IMPORT_ENTRY_20261028",
      "tier": "standard",
      "subject": "a7a547ecde2b7b76247ee25c4c57a803b84300f3",
      "summary": "Consolidate project import entry under Projects",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing this task, retaining local commits, with no push or publication. Local close only; --publish-close intentionally omitted.",
      "closed_at": "2026-10-29T00:11:03.627184Z"
    },
    {
      "task_id": "TASK_IMPORT_PROJECTS_UX_20261029",
      "tier": "standard",
      "subject": "6f2b6f8ee517bd47df32b9daf06a09f1cc9ab373",
      "summary": "Simplify Import Projects selection, preview, results and restore entry",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing this completed task; preserve local commits. Existing no-push/no-publication instruction remains in force. Local close only; --publish-close omitted.",
      "closed_at": "2026-10-29T22:42:59.921841Z"
    },
    {
      "task_id": "TASK_EQUIPMENT_MERGED_TABLE_20261030",
      "tier": "standard",
      "subject": "33f26b1814b4ecca95614ea3d4f0fdfe755d1766",
      "summary": "Recognize horizontally merged equipment tables and explain reports without equipment tables",
      "disposition": "completed",
      "decision_ref": "User explicitly requested final Close of the completed equipment-table source-code repair after 123 passing tests and successful browser upload/download validation on 2026-10-30.",
      "closed_at": "2026-10-30T00:00:01.969757Z"
    }
  ],
  "tasks": {
    "TASK_IMPORT_FLOW_COMPACT_20261030": {
      "slot": "micro",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\unified-project-library-ui\\connlab",
      "branch": "codex/project-import-entry-20261028",
      "resources": [],
      "integrated_head": "8fef12518136e1a6bfcf0c4c944f4d5b5886da0d",
      "task": {
        "task_id": "TASK_IMPORT_FLOW_COMPACT_20261030",
        "summary": "Simplify import controls and confirmation; return to full Projects",
        "tier": "micro",
        "route": "sol_direct",
        "scope": "Localized frontend import presentation and navigation only; retain backend conflict, snapshot, destination and retry protections. Isolated validation only; no real data changes, push or publication.",
        "scope_paths": [
          "frontend/src/App.test.tsx",
          "frontend/src/App.tsx",
          "frontend/src/features/project-library/ProjectImportDestination.test.tsx",
          "frontend/src/features/project-library/ProjectImportDestination.tsx",
          "frontend/src/features/project-library/ProjectImportResults.test.tsx",
          "frontend/src/features/project-library/ProjectImportResults.tsx",
          "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
          "frontend/src/features/project-library/ProjectLibraryImport.tsx",
          "frontend/src/features/project-library/project-library.css"
        ],
        "risk_reasons": [],
        "activation_head": "58acc1cf38e50703749e448138824bfdbd8f3415",
        "started_at": "2026-10-30T00:00:32.976018Z",
        "updated_at": "2026-10-30T00:21:27.442454Z",
        "checkpoint": null,
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_IMPORT_FLOW_COMPACT_20261030",
          "subject": "963b31d00f452951dc3434f438dd633bc132edf9",
          "summary": "Import page uses Settings destination only, one selection checkbox per project and one final confirmation. Preserve conflict/restore protections and return all import exits to full Projects; isolated UI, files and snapshot verified. No real-data changes, push or publication.",
          "scope_ok": true,
          "changed_paths": [
            "frontend/src/App.test.tsx",
            "frontend/src/App.tsx",
            "frontend/src/features/project-library/ProjectImportDestination.test.tsx",
            "frontend/src/features/project-library/ProjectImportDestination.tsx",
            "frontend/src/features/project-library/ProjectImportResults.test.tsx",
            "frontend/src/features/project-library/ProjectImportResults.tsx",
            "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
            "frontend/src/features/project-library/ProjectLibraryImport.tsx",
            "frontend/src/features/project-library/project-library.css"
          ],
          "validation": [
            {
              "name": "Frontend related regression",
              "status": "passed",
              "detail": "99 library/catalog/list + 20 App navigation; affected 44 rerun after final result-heading edit."
            },
            {
              "name": "Python isolation",
              "status": "passed",
              "detail": "116 API/portability/runtime tests; private DB/temp/cache only."
            },
            {
              "name": "Typecheck and build",
              "status": "passed"
            },
            {
              "name": "Isolated UI and integrity",
              "status": "passed",
              "detail": "2 imported, conflict skipped, previous project retained; 64 snapshot tables/326 rows/4 assets equal; 107 source-copy files unchanged."
            },
            {
              "name": "Diff review",
              "status": "passed",
              "detail": "Sequential current-agent requirements and standards passes; git diff --check clean."
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "method": "TDD, implementation, sequential self-review and isolated validation by current agent; no independent review claimed"
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "963b31d00f452951dc3434f438dd633bc132edf9",
            "primary_before": "2c3fcaf516432a97b14ecf164f80a8fd696128d4",
            "integrated_head": "8fef12518136e1a6bfcf0c4c944f4d5b5886da0d",
            "recovered": false
          }
        }
      }
    },
    "TASK_TOOLS_FOLDER_ENCRYPTION_20261030": {
      "slot": "main",
      "state": "running",
      "worktree": "D:\\PythonProject\\connlab\\tmp\\worktrees\\tools-folder-encryption-20261030",
      "branch": "codex/tools-folder-encryption-20261030",
      "resources": [],
      "integrated_head": null,
      "task": {
        "task_id": "TASK_TOOLS_FOLDER_ENCRYPTION_20261030",
        "summary": "Batch encrypted Word/Excel copies from a selected folder without modifying originals",
        "tier": "standard",
        "route": "sol_build_review_qa",
        "scope": "Add a recursive browser folder picker alongside single-file encryption. Reuse unchanged Office encryption/password policy; stage uploaded copies, preserve relative paths in a downloadable ZIP, report individual failures without including plaintext originals, validate upload paths and limits, prevent duplicate/stale UI operations, and verify isolated native Office/browser behavior. No changes to cipher, passwords, project authority or original files.",
        "scope_paths": [
          "backend/application/tools_folder_encryption_service.py",
          "backend/infrastructure/files/tools_folder_archive_gateway.py",
          "backend/api/routes_tools_folder_encryption.py",
          "backend/api/routes_tools.py",
          "frontend/src/features/tools/EncryptionTool.tsx",
          "frontend/src/features/tools/EncryptionTool.test.tsx",
          "frontend/src/pages/ToolsPage.tsx",
          "frontend/src/pages/ToolsPage.test.tsx",
          "frontend/src/api/client.ts",
          "frontend/src/api/toolsEncryption.test.ts",
          "frontend/src/tools.css",
          "tests/unit/test_tools_folder_encryption_service.py",
          "tests/integration/test_tools_folder_encryption_api.py",
          "docs/PROJECT_CONTEXT.md"
        ],
        "risk_reasons": [],
        "activation_head": "94bda8831421a86a6aae37dcc3855f022b8d30bf",
        "started_at": "2026-10-30T14:46:47.475269Z",
        "updated_at": "2026-10-30T14:46:47.475269Z",
        "checkpoint": null,
        "report": null
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
