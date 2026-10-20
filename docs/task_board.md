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
    "task_id": "TASK_REPORT_DUAL_MODE_UPDATES_20261019",
    "summary": "Update Internal Report sections through official archive updates or chained draft downloads",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Preserve existing official report archive updates. Without a ready official report, resolve a validated current-project draft, update a new owned copy and offer retryable Draft download. Chain LLCR, Equipment List and Customer Report against the latest successful draft; preserve source files and manual content, guard changed authorities, retain required input validation and manual selection. Isolated regressions and actual Word generation/download smoke; no real project writes.",
    "scope_paths": [
      "backend/application",
      "backend/api",
      "backend/infrastructure/files",
      "frontend/src/features/report-workspace",
      "frontend/src/api",
      "tests/unit",
      "tests/integration",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [],
    "activation_head": "61a289a98a270784bebd1b65dde280f5693e7755",
    "started_at": "2026-10-19T15:08:32.753322Z",
    "updated_at": "2026-10-20T04:53:58.284768Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_REPORT_DUAL_MODE_UPDATES_20261019",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_REPORT_DUAL_MODE_UPDATES_20261019",
      "subject": "1aab9baadb65c0179e35a3d707bc149d17c1049d",
      "summary": "Implemented official archive updates or immutable chained draft downloads for LLCR and Equipment List; Customer Report consumes the latest successful draft. Original reports, templates, calibration resources and real projects were not changed by validation.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/project_customer_report_runner.py",
        "backend/api/routes_report_section_updates.py",
        "backend/api/routes_report_workspace.py",
        "backend/application/current_report_update_service.py",
        "backend/application/customer_report_source_resolver.py",
        "backend/application/report_section_update_service.py",
        "backend/infrastructure/files/downloaded_internal_report_source.py",
        "backend/infrastructure/files/report_draft_workspace.py",
        "docs/report_generation_architecture.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "frontend/src/features/report-workspace/useReportDraftUpdates.test.tsx",
        "frontend/src/features/report-workspace/useReportDraftUpdates.ts",
        "tests/integration/test_report_section_draft_api.py",
        "tests/unit/test_report_draft_workspace.py"
      ],
      "validation": [
        {
          "status": "passed",
          "check": "Affected backend matrix",
          "result": "229 passed; one pre-existing Starlette deprecation warning."
        },
        {
          "status": "passed",
          "check": "Report Workspace frontend and API tests",
          "result": "102 passed."
        },
        {
          "status": "passed",
          "check": "TypeScript and Vite production build",
          "result": "npm run build passed after frontend tests."
        },
        {
          "status": "passed",
          "check": "Native Word and HTTP download smoke",
          "result": "Isolated LLCR -> Equipment -> actual Word Customer projection; three HTTP 200 Draft DOCX downloads; original source, template, catalog and retained sentinel unchanged; no official folder/history/report registration created. Evidence: tmp/dual-report-smoke-puethi1v/evidence.json."
        },
        {
          "status": "passed",
          "check": "Native Word visual verification",
          "result": "Inspected all four Internal and three Customer pages exported by Microsoft Word and rasterized with bundled Poppler; no clipping or overlap. Standard render_docx could not run because LibreOffice is absent; native Word was the verified fallback. Existing approved-template pagination retained."
        },
        {
          "status": "passed",
          "check": "Isolated actual browser",
          "result": "Port 18766 temporary project: LLCR and Equipment actions downloaded Draft files; downloaded Word retains both result and equipment data. Source dialog opens, Escape cancels, screenshot inspected. Test browser closed; real user page untouched. Evidence retained under ignored tmp/report-dual-mode-browser-20261020."
        },
        {
          "status": "passed",
          "check": "TDD evidence",
          "result": "Public API missing-route/disabled-button REDs preceded implementation; no-op changed flag and reload error tests failed before bounded fixes, then passed."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "execution": "Current Astra agent; public API/hook behavior slices and targeted RED/GREEN checks."
        },
        "reviewer": {
          "status": "passed",
          "execution": "Distinct sequential self-review by the current agent, not an independent agent. Standards: existing adapters/authority boundaries retained; source/copy/cache responsibilities explicit. Spec: formal compatibility, draft fallback/chaining, failed download retention, source validation and non-overwrite rules satisfied. No unresolved material findings."
        },
        "qa": {
          "status": "passed",
          "execution": "Same agent final QA on clean 1aab9baa: affected backend/frontend matrix, sequential build, native Word/HTTP/browser checks. Only isolated fixture corrections were needed during native smoke; product commit unchanged."
        }
      },
      "integration": {
        "status": "passed",
        "method": "Local master implementation commit; exact reviewed product diff and clean tree verified. No remote publication or final Close performed."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_XLSX_DATE_READING_CALIBRATION_20261019",
    "tier": "high_risk",
    "subject": "e8018c96ca0ef5c5de3872c2c51da6e495e5dc7d",
    "summary": "Fix styled XLSX dates and epoch handling; verify calibration report in a separate copy",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closing the completed task.",
    "closed_at": "2026-10-19T15:06:07.683419Z"
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
