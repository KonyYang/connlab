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
    "task_id": "TASK_PROJECTS_DEFAULT_ONGOING_20261101",
    "tier": "micro",
    "subject": "3b473cc2cd203ebb2165eedd25fb7ae6789dfb19",
    "summary": "Default Projects view to On-going",
    "disposition": "completed",
    "decision_ref": "User explicitly authorized local closing of accepted Projects default On-going micro task to release App.test.tsx scope for the single-project import task. Retain commits and evidence; no push/publication; --publish-close omitted.",
    "closed_at": "2026-11-02T00:20:02.997114Z"
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
    }
  ],
  "tasks": {
    "TASK_SINGLE_PROJECT_IMPORT_20261102": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "D:\\PythonProject\\connlab\\tmp\\basic-info-result-default-20261101",
      "branch": "codex/single-project-import-20261102",
      "resources": [],
      "integrated_head": "8067c3a1c67776a814b955123f4cc5ff60f37bcc",
      "task": {
        "task_id": "TASK_SINGLE_PROJECT_IMPORT_20261102",
        "summary": "Make Import Projects default to one complete project folder",
        "tier": "standard",
        "route": "sol_build_review_qa",
        "scope": "Single-project default chooser and manual path; check exact selected boundary without recursive expansion; contextual invalid-folder and missing-LTR handling. Preserve backend batch API, final reviewed confirmation, duplicate/conflict decisions, snapshot recovery protections and existing Open Project navigation. Use isolated DBs and temporary sources only; no real business DB/source mutations, push or publication.",
        "scope_paths": [
          "backend/api/project_library_schemas.py",
          "backend/api/routes_project_library.py",
          "backend/application/project_library/service.py",
          "backend/infrastructure/project_library/files.py",
          "backend/infrastructure/project_library/intake_layout.py",
          "docs/architecture/project_library.md",
          "frontend/src/App.test.tsx",
          "frontend/src/api/projectLibrary.ts",
          "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
          "frontend/src/features/project-library/ProjectLibraryImport.tsx",
          "frontend/src/features/project-library/ProjectLibrarySingleImport.test.tsx",
          "tests/integration/test_project_library_api.py"
        ],
        "risk_reasons": [],
        "activation_head": "5284b620e4ddcd641b43db54c4f33ca398bba411",
        "started_at": "2026-11-01T23:56:22.459419Z",
        "updated_at": "2026-11-02T00:22:20.354666Z",
        "checkpoint": null,
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_SINGLE_PROJECT_IMPORT_20261102",
          "subject": "e02b11e8b06d58c6cbcdb0ddc729abc708d0f187",
          "summary": "Default import now checks one complete project folder without recursive batch expansion, replacing rather than appending selections. Conditional parent/partial guidance, metadata-first LTR identification and bounded manual LTR input preserve identity, duplicate/conflict and snapshot guards. One final Confirm Import; eligible success enters verified workspace. Settings destination and backend batch compatibility retained. Validated only isolated intake data; no push/publication.",
          "scope_ok": true,
          "changed_paths": [
            "backend/api/project_library_schemas.py",
            "backend/api/routes_project_library.py",
            "backend/application/project_library/service.py",
            "backend/infrastructure/project_library/files.py",
            "backend/infrastructure/project_library/intake_layout.py",
            "docs/architecture/project_library.md",
            "frontend/src/App.test.tsx",
            "frontend/src/api/projectLibrary.ts",
            "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
            "frontend/src/features/project-library/ProjectLibraryImport.tsx",
            "frontend/src/features/project-library/ProjectLibrarySingleImport.test.tsx",
            "tests/integration/test_project_library_api.py"
          ],
          "validation": [
            {
              "name": "TDD and bounded development feedback",
              "status": "passed",
              "result": "RED/GREEN at scan API, missing-LTR/identity API and visible single-project UI seams; final targeted61tests passed. Tests for cancelled/mismatched/late/retry/recovery behavior retained; obsolete batch-entry UI cases removed because the product flow is now single-project.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\qa.json"
            },
            {
              "name": "Sequential Standards and Spec review",
              "status": "passed",
              "result": "Root separate sequential passes: Standards0/Spec0; not an independent agent review. Exact12file source/test/doc diff, boundaries, compatibility and safety checked.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\review.json"
            },
            {
              "name": "Final related backend QA",
              "status": "passed",
              "result": "159passed; API, portability including batch compatibility and isolated transfer/unit guards. Existing TestClient deprecation warning only.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\backend-qa.log"
            },
            {
              "name": "Final complete frontend QA",
              "status": "passed",
              "result": "1183passed,1skipped on reviewed exact subject. Existing unrelated test diagnostic/React act output retained in full log.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\frontend-qa.log"
            },
            {
              "name": "Final typecheck and production build",
              "status": "passed",
              "result": "tsc-b and Vite production build passed sequentially after frontend tests.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\build-qa.log"
            },
            {
              "name": "Isolated browser intake smoke",
              "status": "passed",
              "result": "706px viewport,691px document, zero preview checkboxes and one final confirmation. Parent blocked, actual copy then verified workspace, repeated import opens existing; missing-LTR same-number conflict stays blocked until explicit decision. Source hashes equal, copy count1, confirmation count1, SQLite integrityok. Actual native chooser window was not retested; its API unchanged and selection/cancel covered by component tests.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\smoke-result.json"
            },
            {
              "name": "Isolated browser write audit and normal cleanup",
              "status": "passed",
              "result": "Only owned temporary databases/directories connected/written;18882normalshutdown, own browser tab closed and viewport reset.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\audit.json"
            },
            {
              "name": "Safe local integration preflight",
              "status": "passed",
              "result": "Development8000dedicated console normally stopped with noforce; consistent readonly three-database backups and two full new-code startup rehearsals on copy preserved all original rows/schema. No real schema migration.",
              "evidence": "D:\\PythonProject\\connlab\\tmp\\single-project-import-20261102\\runtime-baseline.json"
            }
          ],
          "roles": {
            "planner": {
              "status": "passed",
              "context": "Root planning pass: inspect actual entry/scanner/state flows; smallest standard change, no schema migration/new dependency."
            },
            "developer": {
              "status": "passed",
              "context": "Root implementation with recorded RED/GREEN and bounded targeted feedback."
            },
            "reviewer": {
              "status": "passed",
              "context": "Root focused sequential Standards/Spec review, not independent agent."
            },
            "qa": {
              "status": "passed",
              "context": "Root subsequent complete selected QA/build and actual isolated browser pass on frozen subject, not independent agent."
            },
            "integrator": {
              "status": "passed",
              "context": "Root preflight verifies scope release/subject/tree/cleanliness and startup-copy equality; actual local serial merge and post-merge checks follow via sole writer."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "e02b11e8b06d58c6cbcdb0ddc729abc708d0f187",
            "primary_before": "cca1099dd8821c569e47ef3678fd02cd5a00a8e7",
            "integrated_head": "8067c3a1c67776a814b955123f4cc5ff60f37bcc",
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
