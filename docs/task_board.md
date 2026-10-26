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
    "task_id": "TASK_LLCR_RESULT_SEMANTICS_20261023",
    "tier": "standard",
    "subject": "1c5c8a07701860d827ac0b0032e1040bf6b76a16",
    "summary": "Correct LLCR absolute resistance versus delta semantics without changing real reports",
    "disposition": "completed",
    "decision_ref": "User explicitly confirmed final Close after 261-test LLCR acceptance",
    "closed_at": "2026-10-22T23:55:52.392518Z"
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
  ],
  "tasks": {
    "TASK_REPORT_CAPABILITIES_3_7_20261026": {
      "slot": "main",
      "state": "running",
      "worktree": "D:\\PythonProject\\connlab-report-capabilities-20261026",
      "branch": "codex/report-capabilities-20261026",
      "resources": [],
      "integrated_head": "dc58b3d49cdbdce6f4420cf5e5f216cf1a3bd600",
      "task": {
        "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
        "summary": "Report Workspace: persistent provenance, temperature/CR, mechanical appendices, photo slots and checked customer copies",
        "tier": "high_risk",
        "route": "full_chain",
        "scope": "One main task, five milestones 3-7. Preserve existing LLCR and local-update protections. Isolated databases and file copies only; real reports/templates/project files read-only; no automatic official publication or force push. Missing decisions stay pending. Include latest 032 review regressions.",
        "scope_paths": [
          "backend/application/report_authoring",
          "backend/domain/report_authoring.py",
          "backend/infrastructure/office/report_authoring",
          "backend/infrastructure/files/report_authoring_assets.py",
          "backend/infrastructure/storage/models_report_authoring.py",
          "backend/infrastructure/storage/repositories/report_authoring.py",
          "backend/infrastructure/storage/report_authoring_schema.py",
          "backend/infrastructure/storage/database.py",
          "backend/api/routes_report_authoring.py",
          "backend/api/report_authoring_schemas.py",
          "backend/api/dependencies.py",
          "backend/api/main.py",
          "backend/api/routes_report_workspace.py",
          "backend/application/report_section_update_service.py",
          "backend/infrastructure/files/report_draft_workspace.py",
          "backend/infrastructure/office/test_report_document_gateway.py",
          "backend/infrastructure/office/customer_report_document_gateway.py",
          "backend/application/customer_report_projection_service.py",
          "backend/application/project_customer_report_job_service.py",
          "backend/api/project_customer_report_runner.py",
          "frontend/src/features/report-workspace",
          "frontend/src/api/reportAuthoring.ts",
          "frontend/src/api/reportAuthoring.test.ts",
          "frontend/src/styles.css",
          "tests/unit/report_authoring",
          "tests/integration/test_report_authoring_api.py",
          "tests/unit/test_report_authoring_schema.py",
          "tests/unit/test_report_draft_workspace.py",
          "tests/unit/test_customer_report_document_gateway.py",
          "tests/unit/test_test_report_document_gateway.py",
          "tests/unit/test_customer_report_projection_service.py",
          "tests/unit/test_project_customer_report_job_service.py",
          "tests/integration/test_project_customer_report_runner.py",
          "tests/integration/test_report_section_draft_api.py",
          "tests/fixtures/report_authoring",
          "docs/architecture/report_authoring.md"
        ],
        "risk_reasons": [
          "Additive report provenance persistence schema",
          "Report data semantics and confidential customer-copy verification"
        ],
        "activation_head": "cd6250e189e5ad67f4c005a3f32c3cfc92945884",
        "started_at": "2026-10-26T00:05:01.578908Z",
        "updated_at": "2026-10-26T14:57:09.728438Z",
        "checkpoint": {
          "schema": "connlab.sol-task-checkpoint",
          "version": 1,
          "task_id": "TASK_REPORT_CAPABILITIES_3_7_20261026",
          "stage": "revision",
          "status": "running",
          "summary": "User approved next improvement: visible report preparation entry, source/update/customer-review navigation and truthful status guidance; preserve existing business logic and file protection.",
          "requires_user": false
        },
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
