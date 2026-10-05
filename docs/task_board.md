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
    "task_id": "TASK_TEMPERATURE_AUTO_DATA_REGION_20261005",
    "summary": "Auto-detect scanner data region and show row settings only for detection exceptions",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Hide header/first/last row inputs on successful scanner-region detection; preserve source and ambiguous/failed imports for manual correction with generation blocked until confirmation; retain channel, ambient/current and anomalous-row review.",
    "scope_paths": [
      "backend/application/temperature_data_preparation.py",
      "backend/application/tools_temperature_service.py",
      "backend/api/routes_tools_temperature.py",
      "frontend/src/api/temperature.ts",
      "frontend/src/features/temperature/useTemperatureTool.ts",
      "frontend/src/features/temperature/temperature.css",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/features/temperature/DataRegionCorrection.tsx",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/integration/test_tools_temperature_api.py",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/api/temperature.test.ts",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "5419b7d3883a6ab3ecfe78c32730e266ebca26c0",
    "started_at": "2026-10-05T14:37:57.566451Z",
    "updated_at": "2026-10-05T23:38:33.736817Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_AUTO_DATA_REGION_20261005",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_AUTO_DATA_REGION_20261005",
      "subject": "1300ea2e237f29166446e523ce6c6073a38e5d86",
      "summary": "Scanner regions auto-detect with exception recovery; current decimals are used directly. The header is Temperature Rise with Tools return; duplicate headings are removed. Load Initial Data replaces the Excel File label and localized chooser, retains filename feedback and safe cancellation/reselection. Data confirmation and anomalous-reading review remain explicit.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_tools_temperature.py",
        "backend/application/temperature_data_preparation.py",
        "backend/application/tools_temperature_service.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/App.tsx",
        "frontend/src/api/temperature.test.ts",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/DataRegionCorrection.tsx",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py"
      ],
      "validation": [
        {
          "status": "passed",
          "check": "Latest Load Initial Data revision: TDD RED on visible Excel File label, GREEN for keyboard activation, import, filename feedback, cancellation and same-file reselection. Final 18 page/API/TopBar tests, TypeScript and Vite build passed sequentially. Exact diff Standards/Spec reviews 0 findings and diff check passed. Browser read-only at 680x804 confirmed named button, native input hidden, label absent, top title retained, no overflow; no user data modified. Native OS chooser not automated; tested at DOM boundary. Backend unchanged, not rerun."
        },
        {
          "status": "passed",
          "check": "Earlier Initial Data heading deletion: 10 temperature-page tests passed on that state. Only the heading was deleted; data import/confirmation and top title/return remained. Exact diff self-reviewed, zero outstanding findings, git diff --check passed. Backend/build/typecheck/browser not rerun for that single literal removal."
        },
        {
          "status": "passed",
          "check": "Earlier 2026-10-06 duplicate-heading removal: 15 page/TopBar tests and tsc -b frontend passed; exact diff self-reviewed and git diff --check passed. Heading wrapper and obsolete styles removed, AppShell top title and return icon retained, standalone return preserved. No data/calculation changes; backend/build/browser checks not rerun for that localized removal."
        },
        {
          "status": "passed",
          "check": "TDD RED/GREEN at preparation, import API and page interaction seams. Review regressions first reproduced false-header error-row skipping and configuration/control preamble misidentification; fixed and included in final QA."
        },
        {
          "status": "passed",
          "check": "Original final backend matrix: 56 passed, one existing Starlette/httpx deprecation warning; backend unchanged in revisions, not rerun. Current-conversion revision frontend matrix: 17 passed, TypeScript tsc -b and Vite production build passed sequentially. Latest literal title revision: 15 page/TopBar tests and tsc -b frontend passed; production build not rerun for the literal title change."
        },
        {
          "status": "passed",
          "check": "2026-10-06 title revision exact diff self-reviewed: App route override is Temperature Rise only on temperatureRise; default Tools title, return icon and content heading unchanged. Standards/Spec zero outstanding findings. git diff --check passed."
        },
        {
          "status": "passed",
          "check": "Revision TDD RED/GREEN: removed conversion control and hint, verified decimal source rows unchanged at prepare/analyze, and identity scaling at prepare/analyze/export even after a legacy non-identity import suggestion. Read-only backend preparation check retained current 17.596362 and ambient 20.625 exactly."
        },
        {
          "status": "passed",
          "check": "Running localhost API: unreadable-region recovery retained source rows, manual correction accepted, tail zero-current warning blocked unacknowledged analysis. Real XLSM auto region 31/32/331 with 300 confirmed records and unchanged MAX/AVG coefficients; source SHA-256 unchanged, no VBA."
        },
        {
          "status": "passed",
          "check": "Live browser 856x804: normal row controls and detection alerts absent, mapping/preview/Confirm Data retained, no horizontal page overflow. Revision read-only check: only ambient/current/TC count mapping fields, conversion control and hint absent; existing imported user draft preserved. Exception interaction verified in React tests and live API rather than OS picker automation."
        },
        {
          "status": "passed",
          "check": "Exact working-tree diff including new correction component reviewed sequentially for Standards and Spec. Both axes zero outstanding findings; git diff --check passed."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "mode": "same-agent standard implementation with evidence-backed TDD slices"
        },
        "reviewer": {
          "status": "passed",
          "mode": "same-agent sequential Standards and Spec review; not independent agents",
          "evidence": "docs/temperature_rise_tool.md"
        },
        "qa": {
          "status": "passed",
          "mode": "same-agent affected matrix, production build, live API and browser checks",
          "limitation": "Exception workflow tested via React and live API; no native OS file-picker or full screen-reader automation."
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "publication": "Local only; final User Close remains required"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_TOOLS_RETURN_ICON_20261005",
    "tier": "micro",
    "subject": "effaf89ade660d3b6524f25f6221a4f4e4ce5b67",
    "summary": "Replace temperature tool text return with Tools title-bar icon",
    "disposition": "completed",
    "decision_ref": "User explicitly requested final closure after accepting the Tools return icon and Workspace Report navigation label refinements.",
    "closed_at": "2026-10-05T14:03:34.747734Z"
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
