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
    "task_id": "TASK_MECHANICAL_SUMMARY_TOOL_20261028",
    "tier": "standard",
    "subject": "b74f4d0847ed5be7cc42cba57b4438518d2ca4cf",
    "summary": "Standalone mechanical test summary tool",
    "disposition": "completed",
    "decision_ref": "用户确认关闭 Tools 独立机械 Summary 第一部分",
    "closed_at": "2026-10-28T14:02:09.933828Z"
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
    }
  ],
  "tasks": {
    "TASK_PROJECT_IMPORT_ENTRY_20261028": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\unified-project-library-ui\\connlab",
      "branch": "codex/project-import-entry-20261028",
      "resources": [],
      "integrated_head": "88b946a4cd47936101dd1cff4071bd74d1cbf174",
      "task": {
        "task_id": "TASK_PROJECT_IMPORT_ENTRY_20261028",
        "summary": "Consolidate project import entry under Projects",
        "tier": "standard",
        "route": "sol_build_review_qa",
        "scope": "Projects is the project intake entry: Import Projects on active and legacy lists, no import cards in Tools, existing library/portable receiving and in-place linking preserved. Import returns to Projects and legacy preview returns to the common import flow. Preserve existing data, URLs and project navigation. Frontend only; no database/schema/data migration, no push/publication, no automatic Close.",
        "scope_paths": [
          "backend/api/project_library_schemas.py",
          "backend/application/project_library/service.py",
          "docs/architecture/project_library.md",
          "frontend/src/App.temperatureNavigation.test.tsx",
          "frontend/src/App.test.tsx",
          "frontend/src/App.tsx",
          "frontend/src/api/projectLibrary.ts",
          "frontend/src/features/legacy-projects/LegacyProjectBrowser.tsx",
          "frontend/src/features/legacy-projects/LegacyProjectList.test.tsx",
          "frontend/src/features/legacy-projects/LegacyProjectList.tsx",
          "frontend/src/features/legacy-projects/LegacyProjectPreview.test.tsx",
          "frontend/src/features/legacy-projects/LegacyProjectPreview.tsx",
          "frontend/src/features/project-library/ProjectImportResults.test.tsx",
          "frontend/src/features/project-library/ProjectImportResults.tsx",
          "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
          "frontend/src/features/project-library/ProjectLibraryImport.tsx",
          "frontend/src/features/project-library/ProjectLibraryList.test.tsx",
          "frontend/src/features/project-library/ProjectLibraryList.tsx",
          "frontend/src/features/project-library/ProjectLibraryMember.tsx",
          "frontend/src/features/project-library/project-library.css",
          "frontend/src/features/projects-registry/ProjectFolderRow.tsx",
          "frontend/src/features/projects-registry/ProjectRegistryManagementDialog.test.tsx",
          "frontend/src/features/projects-registry/ProjectRegistryManagementDialog.tsx",
          "frontend/src/features/projects-registry/ProjectRegistryManagementPanel.test.tsx",
          "frontend/src/features/projects-registry/ProjectRegistryManagementPanel.tsx",
          "frontend/src/features/projects-registry/projectCatalog.test.ts",
          "frontend/src/features/projects-registry/projectCatalog.ts",
          "frontend/src/pages/ProjectListPage.test.tsx",
          "frontend/src/pages/ProjectListPage.tsx",
          "frontend/src/pages/ToolsPage.test.tsx",
          "frontend/src/pages/ToolsPage.tsx",
          "frontend/src/project-dashboard.css",
          "tests/integration/test_project_library_api.py"
        ],
        "risk_reasons": [],
        "activation_head": "265625bc429234bc9e90ca09a7d705d0fc00cca4",
        "started_at": "2026-10-28T14:26:30.121108Z",
        "updated_at": "2026-10-29T00:09:11.557324Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_PROJECT_IMPORT_ENTRY_20261028",
          "stage": "revision",
          "status": "running",
          "summary": "User annotation requests removing Import Projects from the Recycle view only. Preserve the sole import action in normal Projects and show it again after Back to Projects. Local frontend visibility change only; no real data writes, push/publication or automatic Close.",
          "requires_user": false
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_PROJECT_IMPORT_ENTRY_20261028",
          "subject": "a7a547ecde2b7b76247ee25c4c57a803b84300f3",
          "summary": "Latest annotation: replace Import Projects position with Back to Projects within Recycle. Keep the sole import entry on normal Projects and restore it on return. Two frontend files only; no real business/source mutation, push/publication or automatic Close.",
          "scope_ok": true,
          "changed_paths": [
            "frontend/src/pages/ProjectListPage.test.tsx",
            "frontend/src/pages/ProjectListPage.tsx"
          ],
          "validation": [
            {
              "name": "Public visibility regression RED/GREEN and build",
              "status": "passed",
              "result": "Expanded existing regression failed before change because Import remained in Recycle. Final19 homepage regressions passed, tsc -b and Vite build passed.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\project-entry-20261028\\hide-recycle-import-validation.log"
            },
            {
              "name": "Standards/Spec and isolated actual UI",
              "status": "passed",
              "result": "Current agent sequential self-review, no open findings. Private DB actual612x804 header confirms Back to Projects first and no import within Recycle, and import returns after Back. All4 source files unchanged; browser/service cleaned.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\project-entry-20261028\\hide-recycle-import-review-ui.json"
            },
            {
              "name": "Local integration safety",
              "status": "passed",
              "result": "Exact2 frontend files, primary clean, no backend/Python changes; real services not signalled and isolated18745 stopped."
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "context": "Current agent bounded annotation correction, existing public regression RED/GREEN."
            },
            "reviewer": {
              "status": "passed",
              "context": "Current agent Standards and Spec sequential self-review."
            },
            "qa": {
              "status": "passed",
              "context": "Current agent targeted test/typecheck/build and isolated actual UI; no independent review claimed."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "a7a547ecde2b7b76247ee25c4c57a803b84300f3",
            "primary_before": "9a6cd2a13453fd9f92db6e7330adfbd1fcb3f7fc",
            "integrated_head": "88b946a4cd47936101dd1cff4071bd74d1cbf174",
            "recovered": false
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
