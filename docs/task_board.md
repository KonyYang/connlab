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
    "task_id": "TASK_CUSTOMER_REPORT_DOWNLOAD_SOURCE_20261019",
    "summary": "Use the latest matching downloaded Internal Report draft for Customer Report download fallback",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Keep official Customer Report publication unchanged; when no official Internal Report is available, read only the current project's validated latest Internal Report draft in the OS Downloads folder and generate an independent Customer draft download through existing jobs. Preserve sources, manual picker and race protection; isolated regression tests only.",
    "scope_paths": [
      "backend/application/customer_report_source_resolver.py",
      "backend/infrastructure/files/downloaded_internal_report_source.py",
      "backend/api/dependencies.py",
      "backend/api/project_customer_report_runner.py",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "tests/unit/test_downloaded_internal_report_source.py",
      "tests/unit/test_customer_report_source_resolver.py",
      "tests/integration/test_customer_report_download_source_api.py",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [],
    "activation_head": "51475da8d78dc4f1310e1765e2f1856dcef49d38",
    "started_at": "2026-10-19T11:54:13.469037Z",
    "updated_at": "2026-10-19T12:07:41.551991Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CUSTOMER_REPORT_DOWNLOAD_SOURCE_20261019",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_CUSTOMER_REPORT_DOWNLOAD_SOURCE_20261019",
      "subject": "6f283c720789a3604e63f2cfac4084a15a1c7e88",
      "summary": "Customer Report keeps official-source priority. Without a ready official report it resolves the latest exact-project Internal Report draft in the OS Downloads folder, validates header DL and E-3707 footer, then uses the existing async job to download a non-publishing Draft customer copy. Sources and existing project/report files remain unchanged. Unavailable or invalid downloads fail closed with the existing missing-source manual picker; managed-source compatibility is retained when no download matches. Custom browser download locations still require manual selection.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/project_customer_report_runner.py",
        "backend/application/customer_report_source_resolver.py",
        "backend/infrastructure/files/downloaded_internal_report_source.py",
        "docs/report_generation_architecture.md",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "tests/integration/test_customer_report_download_source_api.py",
        "tests/integration/test_internal_report_generation_api.py",
        "tests/unit/test_customer_report_source_resolver.py",
        "tests/unit/test_downloaded_internal_report_source.py"
      ],
      "validation": [
        {
          "name": "Affected backend matrix, 10 files",
          "status": "passed",
          "result": "102 passed; one existing Starlette deprecation warning. Tested final backend bytes at c069f985; subsequent commit changes only frontend picker guard, so backend results remain applicable."
        },
        {
          "name": "Final report-workspace and download client Vitest matrix",
          "status": "passed",
          "result": "95 passed across 5 files at 6f283c72. First complete pass exposed 3 manual-picker regressions; narrowed automatic path to managed_download mode and all passed after fix."
        },
        {
          "name": "TypeScript and Vite production build",
          "status": "passed",
          "result": "195 modules, passed at 6f283c72."
        },
        {
          "name": "Actual Microsoft Word and HTTP draft download smoke",
          "status": "passed",
          "result": "Production CustomerReport subprocess writer, approved E-4515 template copied read-only into an isolated project with missing official folder. HTTP 200; generated DL-2026-05-001-CR Latest Connector Qualification Testing Report_Rev_A_Draft.docx, 244098 bytes. Protected DOCX inspected successfully; E-4515 footer and project content verified. Original internal source, template and retained sentinel hashes unchanged; no folder recreation, History or report registration. Evidence: tmp/customer-download-word-smoke-rrcfs83m/evidence.json. HTTP route exercised by TestClient, not the live user browser."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "method": "same agent, public adapter/resolver/API/component seams; initial missing adapter and picker failures before implementation; corrupt-DOCX and similar-form identity RED then GREEN. All writes isolated to test-owned data."
        },
        "reviewer": {
          "status": "passed",
          "method": "same agent, separate Standards and Spec passes of exact 25ad0f4c..6f283c72 change set, including new files and subsequent picker fix. Standards: 0 unresolved findings. Spec: 0 unresolved findings. Checked infrastructure/application direction, no authority registration, non-overwrite, exact-project/type selection, source races and formal/managed compatibility."
        },
        "qa": {
          "status": "passed",
          "method": "same agent, affected final matrix on clean reviewed commits, sequential Vitest/build and isolated actual Word smoke. Frontend-only compatibility finding fixed and complete frontend matrix rerun; unchanged backend/native results retained without duplicate full run."
        }
      },
      "integration": {
        "status": "passed",
        "method": "Local master commits c069f985 and 6f283c72 on activation 25ad0f4c, clean tree and exact 11-path product diff; no remote publication."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_INTERNAL_REPORT_DRAFT_FALLBACK_20261019",
    "tier": "standard",
    "subject": "72e10deb8ffbd2b68e3b492da3259830bbf60b15",
    "summary": "Download a non-overwriting Internal Report draft when the official project folder is unavailable",
    "disposition": "completed",
    "decision_ref": "User accepts ordinary browser download handling and explicitly closes the completed Internal Report draft fallback task.",
    "closed_at": "2026-10-19T10:48:13.514898Z"
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
