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
    "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
    "tier": "high_risk",
    "subject": "41e6caed8dc1621d25065e0c54bfe1963922d3bf",
    "summary": "Report Workspace: persistent provenance, temperature/CR, mechanical appendices, photo slots and checked customer copies",
    "disposition": "completed",
    "decision_ref": "User explicitly confirmed closing the current Report Workspace capabilities 3-7 task on 2026-10-27.",
    "closed_at": "2026-10-26T23:47:10.164767Z"
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
    }
  ],
  "tasks": {
    "TASK_UNIFIED_PROJECT_LIBRARY_20261027": {
      "slot": "main",
      "state": "running",
      "worktree": "C:\\Users\\White\\.codex\\worktrees\\unified-project-library\\connlab",
      "branch": "codex/unified-project-library-20261027",
      "resources": [],
      "integrated_head": null,
      "task": {
        "task_id": "TASK_UNIFIED_PROJECT_LIBRARY_20261027",
        "summary": "Unified project library: managed batch intake, mutable titles, portable project data and offline takeover",
        "tier": "high_risk",
        "route": "full_chain",
        "scope": "Implement Goal A M1-M4 from the 2026-10-27 revised unified-project-library plan and verified M0 data contract. Isolated databases, output roots and source copies only. Preserve full LTR, stable identity, everyday file edits, complete project-relative files and explicitly owned relational/JSON data. Provide UI for 300-project intake, title/reconnect, prepare-to-take, inspect/restore and continuation of existing Matrix/Report workflows. No real migration, source mutation, push, publication or automatic final Close.",
        "scope_paths": [
          "backend/domain/project_library.py",
          "backend/application/project_library",
          "backend/infrastructure/project_library",
          "backend/infrastructure/storage/models_project_library.py",
          "backend/infrastructure/storage/repositories/project_library.py",
          "backend/infrastructure/storage/database.py",
          "backend/shared/config.py",
          "backend/desktop/runtime_paths.py",
          "backend/api/routes_project_library.py",
          "backend/api/project_library_schemas.py",
          "backend/api/main.py",
          "backend/api/dependencies.py",
          "backend/application/legacy_project_preview_service.py",
          "backend/infrastructure/files/legacy_project_preview_gateway.py",
          "backend/infrastructure/storage/repositories/official_workspace.py",
          "backend/infrastructure/official_workspace_manifest.py",
          "backend/application/official_folder_relocation_service.py",
          "frontend/src/api/projectLibrary.ts",
          "frontend/src/features/project-library",
          "frontend/src/App.tsx",
          "frontend/src/App.test.tsx",
          "frontend/src/pages/ToolsPage.tsx",
          "frontend/src/pages/ToolsPage.test.tsx",
          "frontend/src/pages/ProjectListPage.tsx",
          "frontend/src/pages/ProjectListPage.test.tsx",
          "tests/unit/project_library",
          "tests/integration/test_project_library_api.py",
          "tests/integration/test_project_library_portability.py",
          "tests/unit/test_config.py",
          "tests/unit/test_desktop_packaged_runtime_paths.py",
          "tests/unit/test_official_project_workspace_service.py",
          "tests/unit/test_official_project_workspace_naming.py",
          "tests/unit/test_legacy_project_preview.py",
          "tests/fixtures/project_library",
          "docs/plans/UNIFIED_PROJECT_LIBRARY_20261027.md",
          "docs/architecture/project_library.md",
          "docs/PROJECT_CONTEXT.md",
          "docs/packaging_notes.md"
        ],
        "risk_reasons": [
          "Additive durable library, batch and snapshot persistence with multi-table restore",
          "Project/Matrix/result/report identity and implicit JSON relationships",
          "Recoverable file copy and project-relative path rebinding",
          "Runtime root binding separated from real/default databases",
          "Copied project identity, LTR ownership and divergent snapshot conflict handling"
        ],
        "activation_head": "eb9f274a693290f651169631f85aa5ea3b1f4dc2",
        "started_at": "2026-10-26T23:55:01.303717Z",
        "updated_at": "2026-10-26T23:55:01.303717Z",
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
