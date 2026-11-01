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
      "integrated_head": "d8c923c54c8ddb521e31df30476c3e939b8a1f1e",
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
        "updated_at": "2026-11-01T00:58:44.270025Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "stage": "implementation",
          "requires_user": false,
          "status": "running",
          "summary": "Sixth slice: imported projects without real draft steps no longer display the default Visual Examination example; empty saved drafts are handled, actual saved draft steps remain, readonly guidance does not suggest edits. Browse Files uses standard secondary style and review copy explicitly adds managed Projects. Portable new working-copy destination uses validated full LTR including suffix, not transport folder basename; 5 targeted restore/replacement/history tests passed. Frontend related 137 passed and final typecheck/build passed after optional legacy draft fields were handled. Local commit saved. Main remaining implementation is existing-local-Project-ID intake as one reviewed confirmation with writer lock, stale-context guards and correct old-root/business path rebinding; detailed recovery plan in managed-import-20261101/EXISTING_ID_INTAKE_NEXT.md. Then exact-diff review, full affected QA and fresh isolated real-sample UI including snapshots, local integration only. No goal-complete claim, real-data writes, push or publication.",
          "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
          "version": 1
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_MANAGED_PROJECT_IMPORT_20261101",
          "subject": "bce16e716a5b0317ce46ee59aa0958012dfce0f5",
          "summary": "Confirmed intake establishes a managed Project with standard catalog/workbench actions, truthful missing-information state and LTR-preserving directory reception. Known local identities reuse their data under writer/stale-review protection. Portable recovery and conflict/Recycle protections retained. Isolated acceptance complete; no real-data migration, push, publication or automatic Close.",
          "scope_ok": true,
          "changed_paths": [
            "backend/api/dependencies.py",
            "backend/api/routes_confirmed_fee_version.py",
            "backend/api/routes_project.py",
            "backend/application/project_identity.py",
            "backend/application/project_library/service.py",
            "backend/application/project_registry_management_service.py",
            "backend/application/project_registry_summary_service.py",
            "backend/infrastructure/project_library/files.py",
            "backend/infrastructure/project_library/intake_layout.py",
            "backend/infrastructure/project_library/restore_conflicts.py",
            "backend/infrastructure/storage/repositories/project_library.py",
            "docs/architecture/project_library.md",
            "frontend/src/App.test.tsx",
            "frontend/src/App.tsx",
            "frontend/src/api/client.ts",
            "frontend/src/features/project-library/ProjectImportResults.tsx",
            "frontend/src/features/project-library/ProjectImportReviewList.tsx",
            "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
            "frontend/src/features/project-library/ProjectLibraryImport.tsx",
            "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
            "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
            "frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx",
            "frontend/src/pages/ProjectListPage.test.tsx",
            "frontend/src/pages/ProjectListPage.tsx",
            "frontend/src/pages/ProjectWorkbenchPage.test.tsx",
            "frontend/src/pages/ProjectWorkbenchPage.tsx",
            "tests/integration/test_confirmed_fee_version_api.py",
            "tests/integration/test_project_library_api.py",
            "tests/integration/test_project_library_portability.py",
            "tests/integration/test_project_registry_management_api.py",
            "tests/unit/test_project_registry_summary_service.py"
          ],
          "validation": [
            {
              "name": "Managed intake and recovery matrix",
              "status": "passed",
              "result": "177 passed in 274.04s: complete affected library API/portability, registry API/summary/management/generation lock and library unit suites.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\managed-import-20261101\\final-python-qa.log"
            },
            {
              "name": "Final bounded QA finding and fees regression",
              "status": "passed",
              "result": "Final exact patch catches only missing-Matrix read exception as 404. RED reproduced 500; 46 fee API/service/lineage/automatic-build tests passed. Actual isolated manual and unnumbered status 404, restored status 200. Existing confirmation path unchanged. Earlier 177 unrelated checks remain applicable.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\managed-import-20261101\\fee-not-ready-green.log"
            },
            {
              "name": "Complete affected frontend matrix",
              "status": "passed",
              "result": "31 files /371 tests passed; TypeScript tsc -b and Vite build passed sequentially. No frontend edits after this run.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\managed-import-20261101\\final-frontend-qa.log"
            },
            {
              "name": "Isolated actual UI and data integrity",
              "status": "passed",
              "result": "Real historical force-test directory copy, EK200 portable snapshot and unnumbered fixture imported through one final confirmation. Normal workspace/list actions, files/back/search and Recycle/restore verified. No-Matrix placeholder absent. Snapshot 64 tables/326 rows and 4 asset hashes match; 54 source files and 54 previous-copy files unchanged. Duplicate already_added; changed same-LTR source review without overwrite. No invented manual LTR or confirmed Matrix.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\managed-import-20261101\\final-ui\\integrity.json"
            },
            {
              "name": "Exact standards and requirements review",
              "status": "passed",
              "result": "Distinct review passes by current agent on complete task diff and final bounded fee patch: dependency boundaries, source preservation, identity, retry/writer context, conflict and authority checks reviewed. QA log finding fixed and verified. No outstanding actionable finding. Not an independent-agent review.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\managed-import-20261101\\final-review.json"
            },
            {
              "name": "Local integration preflight",
              "status": "passed",
              "result": "Task and primary clean; primary changes since base board-only. Developer 8000 dedicated console inventory verified and normally stopped via Ctrl+C without force; not restarted. No release service changed.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\managed-import-20261101\\normal-stop.json"
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "context": "Current Astra agent; coherent TDD slices, local commits, targeted feedback."
            },
            "reviewer": {
              "status": "passed",
              "context": "Distinct focused standards/spec review pass by same agent, not independent."
            },
            "qa": {
              "status": "passed",
              "context": "Current agent final risk-proportionate 177 backend/371 frontend matrix/build and real isolated UI; bounded 46 fee tests and actual readiness after QA finding. No duplicate full suite claimed."
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "bce16e716a5b0317ce46ee59aa0958012dfce0f5",
            "primary_before": "8552dd1ae871c64d73a864c01a868c09e27485d9",
            "integrated_head": "d8c923c54c8ddb521e31df30476c3e939b8a1f1e",
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
