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
    "task_id": "TASK_IMPORT_FLOW_COMPACT_20261030",
    "tier": "micro",
    "subject": "35c18660c16871513836c7fab9da4fdd50f6e726",
    "summary": "Simplify import controls and confirmation; return to full Projects",
    "disposition": "completed",
    "decision_ref": "User explicitly approved local close of prior task and start of full managed project import implementation; retain all commits and evidence; no push or publication.",
    "closed_at": "2026-10-31T21:21:46.655993Z"
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
    }
  ],
  "tasks": {
    "TASK_MANAGED_PROJECT_IMPORT_20261101": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\unified-project-library-ui\\connlab",
      "branch": "codex/project-import-entry-20261028",
      "resources": [],
      "integrated_head": "4d174c19923d251ba05f51d04a94b35e67e2902f",
      "task": {
        "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
        "summary": "Imported projects use the standard project catalog and workbench with truthful completeness",
        "tier": "standard",
        "route": "sol_build_review_qa",
        "scope": "Implement confirmed import as managed projects, standard LTR directory reception, truthful identity/completeness and unified workbench/recycle actions; preserve conflict and portable restore protections. Isolated data only, no real-data migration, push or publication.",
        "scope_paths": [
          "backend/api/dependencies.py",
          "backend/api/project_library_schemas.py",
          "backend/api/routes_confirmed_fee_version.py",
          "backend/api/routes_project.py",
          "backend/api/routes_project_library.py",
          "backend/application/project_identity.py",
          "backend/application/project_library",
          "backend/application/project_registry_management_service.py",
          "backend/application/project_registry_models.py",
          "backend/application/project_registry_summary_service.py",
          "backend/domain/project_library.py",
          "backend/infrastructure/project_library",
          "backend/infrastructure/storage/repositories/project_library.py",
          "docs/architecture/project_library.md",
          "frontend/src/App.test.tsx",
          "frontend/src/App.tsx",
          "frontend/src/api/client.ts",
          "frontend/src/api/projectLibrary.ts",
          "frontend/src/components/projects",
          "frontend/src/features/project-library",
          "frontend/src/features/project-workbench",
          "frontend/src/features/projects-registry",
          "frontend/src/pages/ProjectListPage.test.tsx",
          "frontend/src/pages/ProjectListPage.tsx",
          "frontend/src/pages/ProjectWorkbenchPage.test.tsx",
          "frontend/src/pages/ProjectWorkbenchPage.tsx",
          "tests/integration/test_confirmed_fee_version_api.py",
          "tests/integration/test_project_library_api.py",
          "tests/integration/test_project_library_portability.py",
          "tests/integration/test_project_registry_management_api.py",
          "tests/unit"
        ],
        "risk_reasons": [],
        "activation_head": "394924ea3d8862e7a1fad5a5a154b1e8181e86d9",
        "started_at": "2026-10-31T21:21:46.877584Z",
        "updated_at": "2026-11-01T07:10:38.786743Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
          "stage": "revision",
          "status": "running",
          "summary": "User in-scope acceptance feedback: reproduce/fix batch replan selection drift and underlying cross-volume rollback, interrupted running recovery, same-name target false success; compact source/path display and useful folded differences. Isolated data only, no push/publication.",
          "requires_user": false
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
          "subject": "4f9fe9fb08fb793000f7272a1f7508b662e1d5b4",
          "summary": "Retain the three-step import design. Fix batch replan choice drift, validate batch-owned copied targets before registration, expose lock-protected Resume for recovered running batches, and make cross-volume switching/rollback recoverable with verified staged copies. Compact source/save-path presentation and show concrete folded differences. Isolated acceptance only; no real business DB/source mutation, push/publication or automatic Close.",
          "scope_ok": true,
          "changed_paths": [
            "backend/api/project_library_schemas.py",
            "backend/application/project_library/service.py",
            "backend/infrastructure/project_library/comparison.py",
            "backend/infrastructure/project_library/files.py",
            "backend/infrastructure/project_library/restore_conflicts.py",
            "docs/architecture/project_library.md",
            "frontend/src/api/projectLibrary.ts",
            "frontend/src/features/project-library/ProjectImportResults.test.tsx",
            "frontend/src/features/project-library/ProjectImportResults.tsx",
            "frontend/src/features/project-library/ProjectImportReviewList.tsx",
            "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
            "frontend/src/features/project-library/ProjectLibraryImport.tsx",
            "frontend/src/features/project-library/project-library.css",
            "frontend/src/features/project-library/projectImportReview.ts",
            "tests/integration/test_project_library_api.py",
            "tests/integration/test_project_library_portability.py",
            "tests/unit/project_library/test_transfer_and_comparison.py"
          ],
          "validation": [
            {
              "name": "Complete affected Python matrix",
              "status": "passed",
              "result": "190 passed in 282.87s, including 300-project batch, project library API/portability, registry summary/management/generation lock and library unit tests. No unresolved failure. One dependency deprecation warning only.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\import-reliability-20261101\\final-python-qa.log"
            },
            {
              "name": "Complete affected frontend matrix",
              "status": "passed",
              "result": "31 files / 382 tests passed on final code, including unchanged/changed batch decisions, explicit running Resume, lost-response/source/destination guards and project workspace/list routing.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\import-reliability-20261101\\final-frontend-qa.log"
            },
            {
              "name": "Final type checking and build",
              "status": "passed",
              "result": "TypeScript tsc -b and Vite production build passed sequentially after frontend tests. No source changes after final QA began.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\import-reliability-20261101\\final-build.log"
            },
            {
              "name": "Actual C/D volume acceptance",
              "status": "passed",
              "result": "Actual source/DB on C:, project storage on D:, recovery packet on C:. Initial restore succeeded. Injected SQL publication failure reached the switch, rollback preserved target files/data, same reviewed request retried, and prior target packet independently restored on a third isolated instance. Source inventory unchanged.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\import-reliability-20261101\\actual-cross-volume.json"
            },
            {
              "name": "Real isolated browser acceptance",
              "status": "passed",
              "result": "Keep another copy for A then Import Files Only for B retained two checked items; actual POST selected both and kept A, both added. One intentional post-copy crash left running; reload exposed Resume Batch, completed once and opened the true workbench with actual missing Basic Info/Matrix. Four source files and existing target unchanged; four members total, no duplicate registration.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\import-reliability-20261101\\ui\\integrity.json"
            },
            {
              "name": "Focused standards and specification review",
              "status": "passed",
              "result": "Distinct same-agent standards/spec passes: zero outstanding findings. Reviewed exact 17-path diff and final source-copy/identity/receipts/fence safety; no independent-agent review claimed.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\import-reliability-20261101\\final-review.json"
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "context": "Current agent; coherent TDD regression slices with captured RED/GREEN evidence and local commit."
            },
            "reviewer": {
              "status": "passed",
              "context": "Sequential standards/spec review passes by current agent, not independent."
            },
            "qa": {
              "status": "passed",
              "context": "Final affected matrix 190 Python /382 frontend, type/build, actual cross-volume failure/rollback and isolated browser request/source-integrity acceptance."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "4f9fe9fb08fb793000f7272a1f7508b662e1d5b4",
            "primary_before": "11cc39619235928d76568267c4aed7f79380a09b",
            "integrated_head": "4d174c19923d251ba05f51d04a94b35e67e2902f",
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
