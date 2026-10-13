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
    "task_id": "TASK_TEMPERATURE_REVIEW_SIMPLIFICATION_20261014",
    "summary": "Simplify temperature warning review and remove redundant row controls",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove Keep Flagged Rows, Select Unpowered Rows and Restore All Rows; explicit Confirm Data accepts nonblocking warnings, preserving highlights, warning text, error blocking, top row edit actions and stale-response guards",
    "scope_paths": [
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/features/temperature/DataPreview.tsx",
      "frontend/src/features/temperature/useDataGridEditing.ts",
      "frontend/src/features/temperature/useTemperatureTool.ts",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "adaa8440a6105ac92028757e1f7e283b4d3dc7d6",
    "started_at": "2026-10-13T23:14:27.942753Z",
    "updated_at": "2026-10-13T23:19:29.211813Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_REVIEW_SIMPLIFICATION_20261014",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "changed_paths": [
        "docs/temperature_rise_tool.md",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/useDataGridEditing.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx"
      ],
      "integration": {
        "status": "passed",
        "detail": "Clean local master exact subject, no remote publication; awaiting explicit user Close"
      },
      "subject": "ac6da92dbc79c1b357dd029b5208bf3913d14a31",
      "roles": {
        "developer": {
          "status": "passed",
          "detail": "Sequential same-agent Standards and Spec exact-diff reviews found zero outstanding issues. Existing request/check/error lifecycle retained, obsolete acknowledgement and footer-only restore-all state removed, no new dependency or authority mutation. No independent agent review claimed."
        }
      },
      "version": 1,
      "validation": [
        {
          "status": "passed",
          "detail": "RED: two targeted page regressions failed for existing checkbox and acknowledge_warnings=false. Final GREEN: 91 frontend page/grid/scan formatter/API tests passed; top selection, exclude/restore, reconfirm/export, invalid-data blockers and stale operations covered."
        },
        {
          "status": "passed",
          "detail": "65 backend preparation/API tests passed on final state (one existing Starlette/httpx deprecation warning); existing acknowledge_warnings contract retains errors and original source/numerical semantics. No backend implementation changes."
        },
        {
          "status": "passed",
          "detail": "Sequential npm run build (TypeScript/Vite) and git diff --check passed."
        },
        {
          "status": "passed",
          "detail": "Real localhost UI smoke via isolated headless Edge and synthetic zero-current CSV: three controls absent, warning text/highlight retained, top exclusion/restoration invalidates results, reconfirmation generates both charts, real XLSX download succeeds, no page errors. In-app Browser import restricted by EPERM; bundled Playwright fallback used without touching user session or business files."
        }
      ],
      "scope_ok": true,
      "task_id": "TASK_TEMPERATURE_REVIEW_SIMPLIFICATION_20261014",
      "schema": "connlab.sol-task-report",
      "summary": "Removed redundant warning acknowledgement and footer row actions; explicit Confirm Data accepts warnings via existing API, retains row highlight/review text and top editing controls, while backend errors remain blocking"
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_COMPACT_MANUAL_INFO_20261013",
    "tier": "micro",
    "subject": "81ee97b33b8398e4cadfd3d0973038df2cbdee17",
    "summary": "Simplify temperature Test Info to compact manual entry without project association",
    "disposition": "completed",
    "decision_ref": "User accepted the completed temperature report and export refinements and requested close on 2026-10-14",
    "closed_at": "2026-10-13T22:55:52.331395Z"
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
