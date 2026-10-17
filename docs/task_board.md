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
    "task_id": "TASK_TEMPERATURE_CURRENT_DECIMALS_20261017",
    "summary": "Unified current decimal precision for temperature zero detection calculations charts and Excel export",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Add0to4 integer current decimal spinner after Samples default0; decimal half-up quantization for current zero detection/calculation and consistent current display/export; preserve original imported data and included rows/sample roles; no unrelated identity/project changes or external authoritative file writes.",
    "scope_paths": [
      "backend/domain/temperature_data.py",
      "backend/application/temperature_data_preparation.py",
      "backend/api/temperature_schemas.py",
      "backend/infrastructure/office/temperature_workbook_gateway.py",
      "backend/infrastructure/office/temperature_rise_report_sheet.py",
      "frontend/src/api/temperature.ts",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/features/temperature",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/unit/test_temperature_workbook_gateway.py",
      "tests/integration/test_tools_temperature_api.py",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "4219ddb74e8bb009d370757e415daed45b0f1e85",
    "started_at": "2026-10-17T03:04:29.050372Z",
    "updated_at": "2026-10-17T03:29:04.085412Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_CURRENT_DECIMALS_20261017",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_CURRENT_DECIMALS_20261017",
      "subject": "282a7bb24097118786eaf8e5ff4eba63a5aa05d1",
      "summary": "Added native Current Decimals spinner after Samples, default0 range0to4. Half-up rounded current drives zero detection, preparation, grouping and fits; matching current display precision in charts and exported Excel. Raw imports and manual exclusions preserved; rounded-zero rows remain included. Precision changes invalidate derived results. Local task complete; no publication.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/temperature_schemas.py",
        "backend/application/temperature_channel_layout.py",
        "backend/application/temperature_data_preparation.py",
        "backend/domain/temperature_data.py",
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/TemperatureCharts.tsx",
        "frontend/src/features/temperature/currentPrecision.test.ts",
        "frontend/src/features/temperature/currentPrecision.ts",
        "frontend/src/features/temperature/sourceScan.test.ts",
        "frontend/src/features/temperature/sourceScan.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "validation": [
        {
          "status": "passed",
          "detail": "Backend affected matrix: 102 tests passed across preparation/calculations/workbook units on product550ac08b. Initial API run exposed3 obsolete raw-current expected values; tests-only commit282a7bb updated those references, then all43 affected API tests passed. Total145 passing backend tests on unchanged implementation; existing Starlette/httpx deprecation warning only."
        },
        {
          "status": "passed",
          "detail": "Frontend affected Vitest suite130 passed across9files; sequential npm run build passed TypeScript and Vite. No frontend changes after this validation."
        },
        {
          "status": "passed",
          "detail": "Isolated real Edge browser: native min0 max4 step1 controls and ArrowUp/ArrowDown; default0 and1dp confirm/analyze/Derating/download; current labels and axes reflect precision; changing precision invalidates results/download;6included0excluded zero rows retained. Manual exclusion followed by precision2 preserves5included1excluded and3samples. Browser console0errors0warnings. Visual screenshots inspected1280wide and598wide."
        },
        {
          "status": "passed",
          "detail": "Both actual browser downloads0dp and1dp opened read-only in owned hidden native Excel instance and CalculateFullRebuild passed. Summary caches matched recalculated values; raw .0087 and10.05 unchanged; current stage values0/10/20 versus0.0/10.1/20.1; calculator underlying results43.521951659279786 and43.598054890585004, matching selected display. Current axes native format0/0.0; no cell comments or Initial Data freeze. Owned Excel/browser/server closed without touching user sessions."
        },
        {
          "status": "passed",
          "detail": "git diff --check passed; exact20changed paths reviewed. No identity/project/database/security changes, no external authoritative writes. Test downloads/screenshots retained only under ignored task-owned tmp QA directory."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Main Astra context established standard bounded plan, current precision contract and half-up boundaries before implementation; preserved raw data and explicit exclusion authority."
        },
        "developer": {
          "status": "passed",
          "detail": "Main context implemented cohesive TDD slices. Observed RED then GREEN for missing precision field/helper/control, exported auxiliary caches, .05A auxiliary detection, decimal multiplication tie .15*3, and rounded-off constant auxiliary stealing main-current role."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Sequential same-agent Standards and Spec self-review passes, not independent agents. Resolved one spec regression by distinguishing raw constant current classification from precision-aware powered auxiliary detection. Final Standards0 and Spec0 remaining actionable findings."
        },
        "qa": {
          "status": "passed",
          "detail": "Same main context performed separate final QA pass:145backend130frontend tests, production build, real browser workflow, two actual downloads and native Excel full recalculation. Corrected only3 obsolete API reference assertions after matrix; reran all43 API tests on exact final test state, avoiding duplicate unaffected suites."
        },
        "integrator": {
          "status": "passed",
          "detail": "Local master clean at exact report subject; product and regression tests committed. No remote publication, force/reset/rebase or user data modification. Task board acceptance recorded through sole writer."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Exact20paths integrated locally at282a7bb24097118786eaf8e5ff4eba63a5aa05d1. Standard single-context sequential passes accurately reported. Ready for user close; no remote push."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_LEGACY_PROJECT_READONLY_PREVIEW_20261017",
    "tier": "standard",
    "subject": "49dccfbc781ce2cccf0ea84713225fc8f7d11806",
    "summary": "Tools legacy-project read-only batch preview with project boundaries, duplicate detection and conflict explanations",
    "disposition": "completed",
    "decision_ref": "User explicitly closes the completed task locally, retaining all local commits and forbidding push or publication.",
    "closed_at": "2026-10-17T02:16:20.299223Z"
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
