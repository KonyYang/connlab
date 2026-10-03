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
  "state": "ready_for_close",
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
    "updated_at": "2026-10-03T01:52:58.733394Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_INTERNAL_REPORT_INITIALIZE_REGENERATE_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_INTERNAL_REPORT_INITIALIZE_REGENERATE_20261003",
      "subject": "206edd1b5acd06acf4fd2a0368031a59565f0283",
      "summary": "Initialize and explicitly archive/rebuild Internal Reports solely from approved template and latest confirmed Basic Information/Matrix. Full current path once, always Generate, official Open folder, managed download compatibility. Stage validation, fresh reads, preview replay/source guards, project lock, ownership-aware rollback and atomic metadata. No automatic LLCR/equipment integration.",
      "scope_ok": true,
      "changed_paths": [
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
      "validation": [
        {
          "command": "C:/PythonEnvs/connlab/.venv/Scripts/python.exe -m pytest -q tests/unit/test_internal_report_generation_service.py tests/integration/test_internal_report_generation_api.py tests/unit/test_report_publication_gateway.py tests/unit/test_test_report_draft_service.py tests/integration/test_test_report_draft_api.py tests/unit/test_test_report_document_gateway.py tests/unit/test_report_workspace_service.py tests/integration/test_report_workspace_api.py tests/unit/test_current_report_update_service.py tests/unit/test_equipment_report_update_service.py tests/unit/test_customer_report_projection_service.py tests/unit/test_project_customer_report_job_service.py tests/unit/test_customer_report_document_gateway.py tests/unit/test_customer_report_subprocess_runner.py tests/integration/test_project_customer_report_job_api.py tests/integration/test_project_customer_report_runner.py tests/unit/test_tools_customer_report_job_service.py tests/integration/test_tools_customer_report_job_api.py tests/integration/test_project_registry_generation_lock.py tests/integration/test_project_registry_management_api.py",
          "status": "passed",
          "result": "Independent QA: 181 passed, 0 skipped, one existing Starlette/httpx deprecation warning; 65.38s."
        },
        {
          "command": "npm test (cwd frontend)",
          "status": "passed",
          "result": "Independent QA: 89 files / 765 tests passed; one opt-in MatrixEditorWorkspace.profile test skipped because VITE_MATRIX_PROFILE unset; 37.33s. Existing expected error-path stderr tests passed."
        },
        {
          "command": "npm run build (cwd frontend; after npm test)",
          "status": "passed",
          "result": "Independent QA: tsc -b and Vite passed; 157 modules, no build warnings."
        },
        {
          "command": "In-app Browser: isolated live API/SQLite/files + real document gateway; initial/cancel/archive regenerate",
          "status": "passed",
          "result": "Root actual browser: one current report; Cancel preserved manual SHA with no History and revision1; approved regeneration archived exact old bytes and fresh report excluded manual marker. Production project preview+Cancel only, SHA 692bb15247634efca3d1b02a0d50f6f3b5506242648049413d7edfa57fff83a7 unchanged. Both browser error logs empty. QA independently audited screenshots/DOCX/SQLite. Contract test template used; no release package or COM rendering verification."
        },
        {
          "command": "git diff --check 36f1510d28034c9befd7d1048b61ae264f3850ec..206edd1b5acd06acf4fd2a0368031a59565f0283; git status --porcelain=v1",
          "status": "passed",
          "result": "Reviewer/Integrator/QA confirmed exact 19 approved files, clean master and pinned candidate. Temporary browser artifacts ignored; owned servers/tab stopped, original user tab retained."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "subject": "36f1510d28034c9befd7d1048b61ae264f3850ec",
          "result": "Independent internal_report_planner code-grounded plan; approved 19-file scope and public-seam safety tests; no unresolved product choice."
        },
        "developer": {
          "status": "passed",
          "subject": "206edd1b5acd06acf4fd2a0368031a59565f0283",
          "result": "Independent internal_report_developer implemented with public behavior TDD RED/GREEN: missing service/seams/full path; real SQLite Decimal; foreign replacement/recovery archive safety. Final 69 targeted Python and 37 UI passed before immutable commit."
        },
        "reviewer": {
          "status": "passed",
          "subject": "206edd1b5acd06acf4fd2a0368031a59565f0283",
          "result": "Independent internal_report_reviewer read-only exact base-to-candidate standards/spec review; 0 findings; approved pinned candidate."
        },
        "qa": {
          "status": "passed",
          "subject": "206edd1b5acd06acf4fd2a0368031a59565f0283",
          "result": "Independent internal_report_qa ran complete 20-suite relevant Python matrix, all frontend tests and sequential production build; independently audited persisted browser artifacts; no findings."
        },
        "integrator": {
          "status": "passed",
          "subject": "206edd1b5acd06acf4fd2a0368031a59565f0283",
          "result": "Independent internal_report_integrator verified parent registration/activation ancestry, clean tree, exact approved 19 paths, no artifact/dependency/schema/packaging expansion, and passing Reviewer/QA evidence. Approved ready_for_close."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "206edd1b5acd06acf4fd2a0368031a59565f0283",
        "result": "All independent contexts passed on exact candidate; no business report overwritten. No release package/COM render claim; filesystem lacking stable identity/hardlink fails closed, foreign recovery edits retained for manual review. Local candidate only; await final User close/publication gate."
      }
    }
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
