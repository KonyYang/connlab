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
    "task_id": "TASK_PUBLIC_PROJECT_PATHS_20261102",
    "tier": "high_risk",
    "subject": "2732e17a4a683d9332c6156ed13bfae99d95c105",
    "summary": "Correct public project folder names",
    "disposition": "completed",
    "decision_ref": "User authorized local close only; no push or publication.",
    "closed_at": "2026-11-02T23:01:39.946185Z"
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
    },
    {
      "task_id": "TASK_EQUIPMENT_TABLE_FONT_20261030",
      "tier": "standard",
      "subject": "d1ee9f3c58be943f5ec4e7e6536e2e7020e93b7c",
      "summary": "Preserve equipment table typography after clearing and refilling cells",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current equipment-table font repair task after 127 affected tests, 164 release checks, and successful new-EXE validation of three real document scenarios.",
      "closed_at": "2026-10-30T05:59:50.377281Z"
    },
    {
      "task_id": "TASK_TOOLS_FOLDER_ENCRYPTION_20261030",
      "tier": "standard",
      "subject": "60b5f073724cd0d78e2168a1d1ad518d4e21eebf",
      "summary": "Batch encrypted Word/Excel copies from a selected folder without modifying originals",
      "disposition": "completed",
      "decision_ref": "User explicitly requested final task close after the Tools layout, encryption and copy refinements; final UI matrix 33 passed, production build and isolated browser checks completed.",
      "closed_at": "2026-10-31T08:53:23.134515Z"
    },
    {
      "task_id": "TASK_IMPORT_FLOW_COMPACT_20261030",
      "tier": "micro",
      "subject": "35c18660c16871513836c7fab9da4fdd50f6e726",
      "summary": "Simplify import controls and confirmation; return to full Projects",
      "disposition": "completed",
      "decision_ref": "User explicitly approved local close of prior task and start of full managed project import implementation; retain all commits and evidence; no push or publication.",
      "closed_at": "2026-10-31T21:21:46.655993Z"
    },
    {
      "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
      "tier": "standard",
      "subject": "4f9fe9fb08fb793000f7272a1f7508b662e1d5b4",
      "summary": "Imported projects use the standard project catalog and workbench with truthful completeness",
      "disposition": "completed",
      "decision_ref": "User explicitly confirmed task Close. Preserve local commits, isolated copies and acceptance records. Existing no-push/no-publication restriction remains in force; local close only, --publish-close omitted.",
      "closed_at": "2026-11-01T10:42:49.086984Z"
    },
    {
      "task_id": "TASK_BASIC_INFO_RESULT_DEFAULT_20261101",
      "tier": "micro",
      "subject": "23df9f3ae2701d83eca8db11d97c880109486892",
      "summary": "Default Basic Information Test Result to In progress",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current Basic Information field refinements task. Preserve local commits and acceptance records; existing no-push/no-publication restriction remains. Local close only; --publish-close omitted.",
      "closed_at": "2026-11-01T11:30:40.142659Z"
    },
    {
      "task_id": "TASK_GROUP_COMPLETION_DESCRIPTION_20261101",
      "tier": "high_risk",
      "subject": "bca6b7ebe4994480d6127976e81b84d31e42e6ee",
      "summary": "Compact group completion controls with saved descriptions",
      "disposition": "completed",
      "decision_ref": "User explicitly requested closing the current group completion description task. Preserve local commits, consistent development database backups and acceptance records. Existing no-push/no-publication restriction persists. Local close only; --publish-close omitted. Leave authorized running development backend unchanged.",
      "closed_at": "2026-11-01T14:02:54.674013Z"
    },
    {
      "task_id": "TASK_PROJECTS_DEFAULT_ONGOING_20261101",
      "tier": "micro",
      "subject": "3b473cc2cd203ebb2165eedd25fb7ae6789dfb19",
      "summary": "Default Projects view to On-going",
      "disposition": "completed",
      "decision_ref": "User explicitly authorized local closing of accepted Projects default On-going micro task to release App.test.tsx scope for the single-project import task. Retain commits and evidence; no push/publication; --publish-close omitted.",
      "closed_at": "2026-11-02T00:20:02.997114Z"
    },
    {
      "task_id": "TASK_SINGLE_PROJECT_IMPORT_20261102",
      "tier": "standard",
      "subject": "e02b11e8b06d58c6cbcdb0ddc729abc708d0f187",
      "summary": "Make Import Projects default to one complete project folder",
      "disposition": "completed",
      "decision_ref": "用户明确要求仅本地关闭单项目导入任务，不推送、不发布",
      "closed_at": "2026-11-02T10:21:08.363527Z"
    },
    {
      "task_id": "TASK_LTR_REMARKS_DEFAULT_20261102",
      "tier": "high_risk",
      "subject": "dba951276d3da39cdda78039804087bb95e53c3d",
      "summary": "Correct Remarks PO defaults for Basic Information and LTR registration",
      "disposition": "completed",
      "decision_ref": "用户明确要求仅本地关闭，不推送、不发布",
      "closed_at": "2026-11-02T10:32:44.622761Z"
    }
  ],
  "tasks": {
    "TASK_SAMPLE_DEPOSITION_20261102": {
      "slot": "micro",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\sample-deposition\\connlab",
      "branch": "codex/sample-deposition-20261102",
      "resources": [],
      "integrated_head": "fa948595b5afa2da7c88df4c9690790389d94091",
      "task": {
        "task_id": "TASK_SAMPLE_DEPOSITION_20261102",
        "summary": "Shorten automatic sample deposition",
        "tier": "micro",
        "route": "sol_direct",
        "scope": "Map Send Back to Requestor to Send Back when automatically filling Sample deposition, preserve manual values",
        "scope_paths": [
          "frontend/src/features/project-basic-information/basicInformationFieldConfig.ts",
          "frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts",
          "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx"
        ],
        "risk_reasons": [],
        "activation_head": "c286b21c9b1533855cf8d9d3900978fb565f32eb",
        "started_at": "2026-11-02T10:35:42.908317Z",
        "updated_at": "2026-11-02T10:37:26.048834Z",
        "checkpoint": null,
        "report": {
          "scope_ok": true,
          "summary": "Automatically shorten Send Back to Requestor to Send Back while retaining manual values",
          "task_id": "TASK_SAMPLE_DEPOSITION_20261102",
          "changed_paths": [
            "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
            "frontend/src/features/project-basic-information/basicInformationFieldConfig.ts",
            "frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts"
          ],
          "validation": [
            {
              "status": "passed",
              "name": "TDD and frontend regression",
              "result": "RED reproduced old value; 45 Basic Information tests passed after fix"
            }
          ],
          "schema": "connlab.sol-task-report",
          "subject": "8fabcd24c0aadae48e40de816a67723e7141f00f",
          "roles": {
            "developer": {
              "status": "passed",
              "method": "same-agent implementation and exact diff review"
            }
          },
          "version": 1,
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "8fabcd24c0aadae48e40de816a67723e7141f00f",
            "primary_before": "67615450e198ef6ff2db137785e7f9f208938f26",
            "integrated_head": "fa948595b5afa2da7c88df4c9690790389d94091",
            "recovered": false
          }
        }
      }
    },
    "TASK_PUBLIC_PARTIAL_SYNC_20261103": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\public-partial-sync\\connlab",
      "branch": "codex/public-partial-sync-20261103",
      "resources": [
        "public-folder"
      ],
      "integrated_head": "3621c75fbf72ae60b605a3ebb24db4558081b780",
      "task": {
        "task_id": "TASK_PUBLIC_PARTIAL_SYNC_20261103",
        "summary": "Safely synchronize non-conflicting project files",
        "tier": "high_risk",
        "route": "full_chain",
        "scope": "Partial public Open projects synchronization with conflict skipping, explicit existing-folder confirmation, accurate results and preserved submit/pull protections",
        "scope_paths": [
          "backend/application/public_folder_workflow_service.py",
          "backend/infrastructure/files/public_folder_workflow_gateway.py",
          "backend/api/routes_public_folder_workflow.py",
          "frontend/src/api/client.ts",
          "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
          "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx",
          "frontend/src/features/project-workbench/projectFolderTaskSelectors.ts",
          "frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts",
          "frontend/src/features/project-workbench/ProjectFolderTaskList.tsx",
          "frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx",
          "tests/unit/test_public_folder_workflow_service.py",
          "tests/unit/test_public_folder_workflow_gateway.py",
          "tests/integration/test_public_folder_workflow_api.py"
        ],
        "risk_reasons": [
          "Public-drive writes, concurrent file changes and ownership confirmation"
        ],
        "activation_head": "15fe1349b836f21d76e3f6e6d1cffdb62d8d5eb8",
        "started_at": "2026-11-02T23:02:48.168269Z",
        "updated_at": "2026-11-02T23:24:51.418738Z",
        "checkpoint": null,
        "report": {
          "task_id": "TASK_PUBLIC_PARTIAL_SYNC_20261103",
          "version": 1,
          "changed_paths": [
            "backend/api/routes_public_folder_workflow.py",
            "backend/application/public_folder_workflow_service.py",
            "backend/infrastructure/files/public_folder_workflow_gateway.py",
            "frontend/src/api/client.ts",
            "frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx",
            "frontend/src/features/project-workbench/ProjectFolderTaskList.tsx",
            "frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts",
            "frontend/src/features/project-workbench/projectFolderTaskSelectors.ts",
            "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx",
            "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
            "tests/integration/test_public_folder_workflow_api.py",
            "tests/unit/test_public_folder_workflow_gateway.py",
            "tests/unit/test_public_folder_workflow_service.py"
          ],
          "summary": "Safely upload nonconflicting files with explicit existing-folder confirmation and partial results; skip existing file updates as user chose",
          "validation": [
            {
              "status": "passed",
              "name": "Developer TDD",
              "result": "Reproduced original all-or-nothing failure; backend 35 and frontend 35 targeted tests passed"
            },
            {
              "status": "passed",
              "name": "Independent review",
              "result": "Independent Reviewer standards 0 and spec 0 blockers; residual platform race and SMB directory identity limitation disclosed"
            },
            {
              "status": "passed",
              "name": "Independent QA",
              "result": "57 backend tests, 115 frontend tests and production build passed; browser UI checked in isolated Vite fixture with mock data, not end-to-end; no real public drive used"
            }
          ],
          "schema": "connlab.sol-task-report",
          "subject": "0429140e295d23a064249c9ee58c1d1d05f752b8",
          "roles": {
            "integrator": {
              "method": "independent integrator",
              "status": "passed"
            },
            "qa": {
              "method": "independent QA",
              "status": "passed"
            },
            "reviewer": {
              "method": "independent reviewer",
              "status": "passed"
            },
            "planner": {
              "method": "independent planner",
              "status": "passed"
            },
            "developer": {
              "method": "independent developer",
              "status": "passed"
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "0429140e295d23a064249c9ee58c1d1d05f752b8",
            "primary_before": "e0879357c2d1f1a2f27bae28bb0faba531a7b18a",
            "integrated_head": "3621c75fbf72ae60b605a3ebb24db4558081b780",
            "recovered": false
          },
          "scope_ok": true
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
