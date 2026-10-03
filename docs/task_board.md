# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_INTERNAL_REPORT_INITIALIZE_REGENERATE_20261003",
    "summary": "Internal Report 初始化与安全重新生成",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Simplify Internal Report card: display report full path once, concise nonpersistent success, always-present Generate Internal Report, official Open folder vs managed download. Initialize or explicitly confirm archive/rebuild from approved template + latest confirmed Basic Information and Matrix only; retain old manual content solely in History/Report, preserve old file on failures, revalidate source/target/authority, serialize project writes. Preserve partial LLCR/equipment updates, existing managed publication and legacy interfaces. No automatic LLCR/equipment/photo import and no generic task platform; isolated tests only, no existing business-report mutation.",
    "scope_paths": [
      "backend/application/internal_report_generation_service.py",
      "backend/api/dependencies.py",
      "backend/api/routes_report_workspace.py",
      "backend/infrastructure/files/report_publication_gateway.py",
      "backend/application/test_report_draft_service.py",
      "backend/application/report_workspace_service.py",
      "tests/unit/test_internal_report_generation_service.py",
      "tests/unit/test_report_publication_gateway.py",
      "tests/unit/test_test_report_draft_service.py",
      "tests/unit/test_report_workspace_service.py",
      "tests/integration/test_report_workspace_api.py",
      "tests/integration/test_internal_report_generation_api.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/reportWorkspaceModel.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "frontend/src/features/report-workspace/reportWorkspaceModel.test.ts",
      "frontend/src/workbench.css",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [
      "Authoritative external Word report archive and replacement; must preserve existing report on generation, publication, or persistence failure."
    ],
    "activation_head": "59eaa8b2b4882478ceea5368bbcfcfe07eb89923",
    "started_at": "2026-10-03T00:49:35.493203Z",
    "updated_at": "2026-10-03T00:49:35.493203Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_REPORT_WORKSPACE_HIDE_AUTHORITY_VERSIONS_20261003",
    "tier": "micro",
    "subject": "9ad084e7de66903f099f48c35d6471ce4d5c330b",
    "summary": "Remove permanent Report Workspace authority version strip",
    "disposition": "completed",
    "decision_ref": "User explicitly closes completed small task and opens Internal Report initialization/safe-regeneration on 2026-10-03; local rollover only, no publication.",
    "closed_at": "2026-10-03T00:49:35.493203Z"
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
    }
  ]
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
