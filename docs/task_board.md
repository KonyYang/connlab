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
    "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
    "tier": "standard",
    "subject": "4f9fe9fb08fb793000f7272a1f7508b662e1d5b4",
    "summary": "Imported projects use the standard project catalog and workbench with truthful completeness",
    "disposition": "completed",
    "decision_ref": "User explicitly confirmed task Close. Preserve local commits, isolated copies and acceptance records. Existing no-push/no-publication restriction remains in force; local close only, --publish-close omitted.",
    "closed_at": "2026-11-01T10:42:49.086984Z"
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
    }
  ],
  "tasks": {
    "TASK_PROJECTS_DEFAULT_ONGOING_20261101": {
      "slot": "micro",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\unified-project-library-ui\\connlab",
      "branch": "codex/project-import-entry-20261028",
      "resources": [],
      "integrated_head": "2b3ad410dd7dceccfa1fc28e40d90e51c97158ce",
      "task": {
        "task_id": "TASK_PROJECTS_DEFAULT_ONGOING_20261101",
        "summary": "Default Projects view to On-going",
        "tier": "micro",
        "route": "sol_direct",
        "scope": "Change only the fresh or invalid saved Projects filter default to On-going; preserve explicit saved user choices and other filters. Targeted frontend verification only; no real business data changes, push or publication.",
        "scope_paths": [
          "frontend/src/App.test.tsx",
          "frontend/src/pages/ProjectListPage.test.tsx",
          "frontend/src/pages/ProjectListPage.tsx"
        ],
        "risk_reasons": [],
        "activation_head": "5f3514effa800d93578b48fdfeedc9fbddaaba77",
        "started_at": "2026-11-01T10:44:18.897851Z",
        "updated_at": "2026-11-01T10:47:17.055877Z",
        "checkpoint": null,
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_PROJECTS_DEFAULT_ONGOING_20261101",
          "subject": "3b473cc2cd203ebb2165eedd25fb7ae6789dfb19",
          "summary": "Projects defaults to On-going when no valid saved view exists. Preserve explicit saved view choices and all other filters. Regression tests explicitly choose All Projects when testing files-only/all-catalog behavior. No business data mutation, push/publication or automatic Close.",
          "scope_ok": true,
          "changed_paths": [
            "frontend/src/App.test.tsx",
            "frontend/src/pages/ProjectListPage.test.tsx",
            "frontend/src/pages/ProjectListPage.tsx"
          ],
          "validation": [
            {
              "name": "Projects and App targeted tests",
              "status": "passed",
              "result": "33 tests passed across 2 files; new default regression first failed against old All Projects default, then passed. Search, view switching, pagination, saved return context and route behavior retained.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\projects-default-ongoing-20261101\\final-tests.log"
            },
            {
              "name": "TypeScript",
              "status": "passed",
              "result": "npx tsc -b completed successfully on final code.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\projects-default-ongoing-20261101\\typecheck.log"
            },
            {
              "name": "Micro self-review",
              "status": "passed",
              "result": "Only runtime change is fallback selectedView all to ongoing; saved valid choices retain precedence. Test-only adaptations preserve existing assertions. Exact diff reviewed, git diff --check clean. No backend, data or filesystem behavior changes.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\projects-default-ongoing-20261101\\subject.json"
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "context": "Current agent implementation, self-review and targeted tests; no independent-agent review claimed."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "3b473cc2cd203ebb2165eedd25fb7ae6789dfb19",
            "primary_before": "c17353e4f57090d077ccad67e21e86502461b150",
            "integrated_head": "2b3ad410dd7dceccfa1fc28e40d90e51c97158ce",
            "recovered": false
          }
        }
      }
    },
    "TASK_BASIC_INFO_RESULT_DEFAULT_20261101": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "D:\\PythonProject\\connlab\\tmp\\basic-info-result-default-20261101",
      "branch": "codex/basic-info-result-default-20261101",
      "resources": [],
      "integrated_head": "5bafe5379b2c1b42897fec741f05f3c7aa383705",
      "task": {
        "task_id": "TASK_BASIC_INFO_RESULT_DEFAULT_20261101",
        "summary": "Default Basic Information Test Result to In progress",
        "tier": "micro",
        "route": "sol_direct",
        "scope": "Change Test Result UI fallback from OK to In progress, preserving valid saved and authoritative values. Targeted mock API tests only; no real business data writes, push or publication.",
        "scope_paths": [
          "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
          "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx",
          "frontend/src/features/project-basic-information/basicInformationFieldConfig.ts"
        ],
        "risk_reasons": [],
        "activation_head": "a96b15ef819a6915e5c08a0b7d371029def89fc3",
        "started_at": "2026-11-01T10:49:56.769932Z",
        "updated_at": "2026-11-01T11:06:58.816693Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_BASIC_INFO_RESULT_DEFAULT_20261101",
          "stage": "revision",
          "status": "running",
          "summary": "User in-scope Basic Information feedback: default missing/blank Remarks (PO) to actual editable NA, preserve existing notes, preserve CNY placeholder and Test Result defaults. No writes to real business data, push or publication.",
          "requires_user": false
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_BASIC_INFO_RESULT_DEFAULT_20261101",
          "subject": "23df9f3ae2701d83eca8db11d97c880109486892",
          "summary": "Basic Information field refinements: unset Test Result defaults to In progress, Test Fee uses a CNY placeholder only, and missing/blank Remarks PO defaults to actual editable NA. Nonblank remarks and valid saved results remain unchanged. Defaults participate in existing save/confirm flow; opening alone does not save. No real-data modification, push/publication or automatic Close.",
          "scope_ok": true,
          "changed_paths": [
            "frontend/src/features/project-basic-information/basicInformationFieldConfig.ts",
            "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx"
          ],
          "validation": [
            {
              "name": "Basic Information and App tests",
              "status": "passed",
              "result": "66 tests passed across 3 files. Missing/empty/whitespace remarks show NA; existing PO-123 retained. Existing complete autosave and confirmation payload assertions now explicitly include remarks_po NA. Existing Test Result and CNY placeholder protections remain covered.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\basic-info-remarks-default-20261101\\final-tests.log"
            },
            {
              "name": "TypeScript",
              "status": "passed",
              "result": "npx tsc -b completed successfully on final state.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\basic-info-remarks-default-20261101\\typecheck.log"
            },
            {
              "name": "Micro self-review",
              "status": "passed",
              "result": "Exact diff reviewed; text defaults apply only to text/textarea fields with explicitly configured defaults and blank values. Only Remarks config adds such a default. No API, backend, business DB or source-directory changes. git diff --check passed. RED captured 3 failing defaults and 1 preserved-note pass before implementation.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\basic-info-remarks-default-20261101\\default-red.log"
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "context": "Current agent implementation, self-review and mock API regression tests. No independent review claimed."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "23df9f3ae2701d83eca8db11d97c880109486892",
            "primary_before": "09d388ca25bcad8b4e4690ee56580816631c997f",
            "integrated_head": "5bafe5379b2c1b42897fec741f05f3c7aa383705",
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
