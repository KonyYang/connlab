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
    "updated_at": "2026-10-03T02:47:00.335067Z",
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
      "subject": "5805d8af1dbf158ee0f535ca79357cd8df14d3cc",
      "summary": "Initialize and explicitly archive/rebuild Internal Reports solely from approved template and latest confirmed Basic Information/Matrix. Full current path once, always Generate, official Open folder, managed download compatibility. Stage validation, fresh reads, preview replay/source guards, project lock, ownership-aware rollback and atomic metadata. No automatic LLCR/equipment integration. Approved feedback: header Open project folder immediately left of Back to Workspace; independent local-folder availability, actionable disabled hover reasons and stale-response safety; no report-generation changes.",
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
          "result": "Independent QA: 181 passed, 0 skipped, one existing Starlette/httpx deprecation warning; 65.38s. Reused for frontend-only revision5805d8af: backend and Python test bytes unchanged from206edd1b."
        },
        {
          "command": "In-app Browser: isolated live API/SQLite/files + real document gateway; initial/cancel/archive regenerate",
          "status": "passed",
          "result": "Root actual browser: one current report; Cancel preserved manual SHA with no History and revision1; approved regeneration archived exact old bytes and fresh report excluded manual marker. Production project preview+Cancel only, SHA 692bb15247634efca3d1b02a0d50f6f3b5506242648049413d7edfa57fff83a7 unchanged. Both browser error logs empty. QA independently audited screenshots/DOCX/SQLite. Contract test template used; no release package or COM rendering verification."
        },
        {
          "command": "npm run test -- --run src/features/report-workspace/ReportWorkspace.test.tsx src/features/report-workspace/reportWorkspaceModel.test.ts",
          "status": "passed",
          "result": "Developer TDD header/no-report real RED then GREEN; final 43 passed (34 UI,9 model)."
        },
        {
          "command": "In-app Browser: actual report-workspace641px header feedback on5805d8af",
          "status": "passed",
          "result": "Root reloaded a7a5... actual user project, viewed screenshot tmp/internal-report-header-feedback-20261003.png: header Open project folder then Back to Workspace adjacent on wrapped row, card only Generate; folder enabled, logs empty. Did not launch Explorer or regenerate business files. Production report SHA unchanged692bb15247634efca3d1b02a0d50f6f3b5506242648049413d7edfa57fff83a7. Disabled reason/open trustedID public-contract component tests; no actual Explorer opening claim."
        },
        {
          "command": "npm test (cwd frontend; exact5805d8af)",
          "status": "passed",
          "result": "Independent QA:89 files /771 tests passed,1 opt-in MatrixEditorWorkspace.profile file/test skipped because VITE_MATRIX_PROFILE unset,22.20s; existing Error: boom error-path tests passed."
        },
        {
          "command": "npm run build (cwd frontend; sequential after npm test; exact5805d8af)",
          "status": "passed",
          "result": "Independent QA: tsc -b and Vite passed,157modules, no build warnings,command4.98s; Vite948ms."
        },
        {
          "command": "git diff --check e3052c65..5805d8af; git status --porcelain=v1",
          "status": "passed",
          "result": "Clean exact candidate and approved4 feedback files; cumulative19 businesspaths verified byIntegrator."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "subject": "36f1510d28034c9befd7d1048b61ae264f3850ec",
          "result": "Independent internal_report_planner code-grounded plan; approved 19-file scope and public-seam safety tests; no unresolved product choice. Independent Planner confirmed bounded header-feedback seam, loading/failure isolation, stale project guards, same approved scope."
        },
        "developer": {
          "status": "passed",
          "subject": "5805d8af1dbf158ee0f535ca79357cd8df14d3cc",
          "result": "Independent internal_report_developer implemented bounded4-file feedback with TDD RED/GREEN,43targetedpassed, scoped commit and clean tree; no backend edits."
        },
        "reviewer": {
          "status": "passed",
          "subject": "5805d8af1dbf158ee0f535ca79357cd8df14d3cc",
          "result": "Independent internal_report_reviewer reviewed e3052c65..5805d8af exact feedback standards/spec,0findings, clean and scope passed; approvedQA."
        },
        "qa": {
          "status": "passed",
          "subject": "5805d8af1dbf158ee0f535ca79357cd8df14d3cc",
          "result": "Independent internal_report_qa final all-frontend matrix and sequential production build passed; independently viewed641px browser screenshot; backend/Python bytes unchanged retains prior181passed. No findings; actual Explorer opening/native disabled tooltip visual not tested."
        },
        "integrator": {
          "status": "passed",
          "subject": "5805d8af1dbf158ee0f535ca79357cd8df14d3cc",
          "result": "Independent internal_report_integrator verified exact candidate ancestry, clean tree, approved4 feedback paths and cumulative19 product paths, diff-check, Reviewer/QA evidence,641px screenshot. Backend/Python bytes unchanged; prior181passed retained. No findings."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "5805d8af1dbf158ee0f535ca79357cd8df14d3cc",
        "result": "All independent contexts passed on exact5805d8af; header feedback scoped and non-mutating. No business report overwritten; original SHA unchanged. Explorer launch/native tooltip visual, release package and Word COM rendering not verified. Await final User close/publication gate."
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
