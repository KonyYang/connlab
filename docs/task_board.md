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
    "task_id": "TASK_PROJECT_IMPORT_ENTRY_20261028",
    "tier": "standard",
    "subject": "a7a547ecde2b7b76247ee25c4c57a803b84300f3",
    "summary": "Consolidate project import entry under Projects",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closing this task, retaining local commits, with no push or publication. Local close only; --publish-close intentionally omitted.",
    "closed_at": "2026-10-29T00:11:03.627184Z"
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
    }
  ],
  "tasks": {
    "TASK_IMPORT_PROJECTS_UX_20261029": {
      "slot": "main",
      "state": "ready_for_close",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\unified-project-library-ui\\connlab",
      "branch": "codex/project-import-entry-20261028",
      "resources": [],
      "integrated_head": "d330b993ba4076e6deaefce95fb3c1929736e7b7",
      "task": {
        "task_id": "TASK_IMPORT_PROJECTS_UX_20261029",
        "summary": "Simplify Import Projects selection, preview, results and restore entry",
        "tier": "standard",
        "route": "sol_build_review_qa",
        "scope": "Frontend-only minimal UX: clear project-folder choice and copy guidance, consistent import wording, hide unnecessary single-project bulk controls and one-page pagination, one-level Restore Project Data entry under other methods, focused fresh-success results. Preserve final confirmations, boundaries, duplicate/conflict guards, retry identities and snapshot restoration. Isolated test DB/files only; no real data/source mutations, no push/publication or automatic close.",
        "scope_paths": [
          "backend/infrastructure/project_library/portability.py",
          "backend/infrastructure/storage/repositories/project_matrix_draft.py",
          "docs/architecture/project_library.md",
          "frontend/src/App.test.tsx",
          "frontend/src/features/project-library/PortableRestore.tsx",
          "frontend/src/features/project-library/ProjectImportResults.test.tsx",
          "frontend/src/features/project-library/ProjectImportResults.tsx",
          "frontend/src/features/project-library/ProjectLibraryImport.test.tsx",
          "frontend/src/features/project-library/ProjectLibraryImport.tsx",
          "frontend/src/features/project-library/ProjectLibraryMember.test.tsx",
          "frontend/src/features/project-library/project-library.css",
          "tests/integration/test_project_library_portability.py",
          "tests/unit/test_project_matrix_draft_repository.py"
        ],
        "risk_reasons": [],
        "activation_head": "2e90a3d636e9d613b61f721139d2995351650078",
        "started_at": "2026-10-29T10:47:06.903822Z",
        "updated_at": "2026-10-29T14:59:26.319001Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_IMPORT_PROJECTS_UX_20261029",
          "stage": "revision",
          "status": "running",
          "summary": "User authorizes next step: reproduce and minimally fix restored Matrix page autosave failure using preserved isolated inputs; preserve FK/rollback protection and confirmed/test history, no real data changes, no push/publication.",
          "requires_user": false
        },
        "report": {
          "schema": "connlab.sol-task-report",
          "version": 1,
          "task_id": "TASK_IMPORT_PROJECTS_UX_20261029",
          "subject": "449011b88f9206886b149f176bdf6fe682e13540",
          "summary": "Fix restored-project Matrix autosave with foreign-key-safe parent/child flush ordering; same transaction and integrity guards retained. Private continuous two-snapshot restore/UI save/reopen passes; original confirmed authority, result datasets, histories, and sample sources preserved. No real data mutation, push, publication, or automatic Close.",
          "scope_ok": true,
          "changed_paths": [
            "backend/infrastructure/storage/repositories/project_matrix_draft.py",
            "tests/unit/test_project_matrix_draft_repository.py"
          ],
          "validation": [
            {
              "name": "affected_python",
              "status": "passed",
              "result": "189 passed, 1 existing Starlette/httpx deprecation warning in 689.61s",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\matrix-restore-autosave-fix-20261029\\affected-python-tests.txt"
            },
            {
              "name": "tdd_fk_and_rollback",
              "status": "passed",
              "result": "Before fix 2 failed/1 passed; after fix all 12 repository tests pass. FK-on create/replace, invalid child rejection, rollback preservation, no FK violations.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\matrix-restore-autosave-fix-20261029\\pytest-red.txt"
            },
            {
              "name": "actual_ui_continuous_restore_autosave",
              "status": "passed",
              "result": "Restore two copied real-derived snapshots without restarting service; edit actual Matrix page, reopen with persisted requirement, edit again, Confirm enabled after save; six exact-body replays HTTP 200.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\matrix-restore-autosave-fix-20261029\\replay-green.json"
            },
            {
              "name": "history_and_original_source_integrity",
              "status": "passed",
              "result": "All 2978 original restored rows preserved except expected registry revision advance; 6 result datasets remain readable; only new non-authority draft and derived fee rebase added. 111 originals plus 111 copied inputs keep names, bytes, mtime and hashes.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\matrix-restore-autosave-fix-20261029\\green-history-and-source-verification.json"
            },
            {
              "name": "review_and_diff_check",
              "status": "passed",
              "result": "Exact two-file diff reviewed; Standards 0 findings, Spec 0 findings; git diff --check clean. Sequential self-review, not independent agents.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\matrix-restore-autosave-fix-20261029\\review.md"
            },
            {
              "name": "runtime_isolation",
              "status": "passed",
              "result": "Original-source open/listdir/scandir denied in private UI harness; only startup selftest denied. Owned UI server stopped; authorized normal developer stop confirmed; 8765 release PID unchanged. Test fallback DB newly created in private worktree and empty of projects/members.",
              "evidence": "C:\\Users\\White\\.codex\\visualizations\\2026\\10\\16\\01a14537-004d-7463-950c-c066b79be2b2\\matrix-restore-autosave-fix-20261029\\normal-stop.json"
            }
          ],
          "roles": {
            "developer": {
              "status": "passed",
              "method": "same-agent implementation and TDD"
            },
            "reviewer": {
              "status": "passed",
              "method": "same-agent sequential Standards/Spec review; no independent reviewer",
              "findings": 0
            },
            "qa": {
              "status": "passed",
              "method": "same-agent execution of 189-test gate and isolated actual UI acceptance"
            }
          },
          "integration": {
            "status": "passed",
            "mode": "serial_local_merge",
            "subject": "449011b88f9206886b149f176bdf6fe682e13540",
            "primary_before": "5983ae4172d6c5503be444cd71e88f7314e2079d",
            "integrated_head": "d330b993ba4076e6deaefce95fb3c1929736e7b7",
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
