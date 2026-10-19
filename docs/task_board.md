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
    "task_id": "TASK_INTERNAL_REPORT_DRAFT_FALLBACK_20261019",
    "summary": "Download a non-overwriting Internal Report draft when the official project folder is unavailable",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Preserve existing validated official report publication and explicit conflict protection; add isolated draft download for absent official folders without changing original reports or real project data; validate with isolated regression tests",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/routes_report_workspace.py",
      "backend/application/internal_report_generation_service.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "tests/unit/test_internal_report_generation_service.py",
      "tests/integration/test_internal_report_generation_api.py",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [],
    "activation_head": "8c284a85a5fbe9aefc835d6825e60ff96ed0e7f3",
    "started_at": "2026-10-19T10:29:12.104235Z",
    "updated_at": "2026-10-19T10:45:13.443067Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_INTERNAL_REPORT_DRAFT_FALLBACK_20261019",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_INTERNAL_REPORT_DRAFT_FALLBACK_20261019",
      "subject": "72e10deb8ffbd2b68e3b492da3259830bbf60b15",
      "summary": "Internal Report uses validated official publication when available; absent folder/manifest downloads a preview-bound _Draft copy in isolated staging without publishing, archiving, overwriting, or registering a new current report. Existing managed APIs remain compatible. No real project reports were modified.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/routes_report_workspace.py",
        "backend/application/internal_report_generation_service.py",
        "docs/report_generation_architecture.md",
        "frontend/src/api/client.ts",
        "frontend/src/api/internalReportGeneration.test.ts",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "tests/integration/test_internal_report_generation_api.py"
      ],
      "validation": [
        {
          "name": "Related isolated backend matrix, 7 files",
          "status": "passed",
          "result": "86 passed; 1 existing Starlette deprecation warning"
        },
        {
          "name": "Report workspace and download client Vitest matrix, 5 files",
          "status": "passed",
          "result": "94 passed"
        },
        {
          "name": "TypeScript and Vite production build",
          "status": "passed",
          "result": "195 modules; passed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "method": "same agent, isolated red-green API and component tests; regressions for absent folders, repeated downloads, same-name and controlled drafts, stale folder/template, failed generation cleanup and late responses"
        },
        "reviewer": {
          "status": "passed",
          "method": "same agent, sequential Standards and Spec passes of exact 2a729a71..72e10deb diff; 0 unresolved findings on each axis"
        },
        "qa": {
          "status": "passed",
          "method": "same agent, complete affected matrix once on clean exact commit; mocked Word boundary with real temporary filesystem/database/API, no real Office generation or real project writes"
        }
      },
      "integration": {
        "status": "passed",
        "method": "local master commit with clean tree; no push or publication"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_REPORT_READ_ERRORS_20261019",
    "tier": "standard",
    "subject": "9774e0be539ae516563cdc91a1bd54cf56badfb3",
    "summary": "Read protected customer reports safely and isolate page load errors",
    "disposition": "completed",
    "decision_ref": "User closes the prior task and requests Internal Report draft-download fallback; no publication requested.",
    "closed_at": "2026-10-19T10:29:12.104235Z"
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
