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
    "task_id": "TASK_LOCAL_REGISTRATION_TEMPERATURE_SAMPLES_20261014",
    "summary": "Local offline account registration remembered login and adjustable temperature sample grouping",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Local username display-name password registration with automatic remembered login, opaque revocable expiring sessions and logout, dynamic identity defaults preserving manual/historical data; numbered temperature groups first otherwise default3 editable sample count with nondivisible confirmation blocked; preserve existing column identities exclusion restoration movement and exports; no cloud RBAC or global business API authorization cutover",
    "scope_paths": [
      "backend/domain/local_identity.py",
      "backend/application/local_identity_service.py",
      "backend/infrastructure/storage/local_identity_store.py",
      "backend/api/routes_local_identity.py",
      "backend/api/main.py",
      "frontend/src/api/localIdentity.ts",
      "frontend/src/currentUser.ts",
      "frontend/src/components/layout/Sidebar.tsx",
      "frontend/src/features/local-identity/AccountDialog.tsx",
      "frontend/src/features/local-identity/localIdentity.css",
      "frontend/src/features/temperature/useTemperatureReportInfo.ts",
      "frontend/src/features/project-basic-information/currentUserDisplay.ts",
      "backend/domain/temperature_data.py",
      "backend/application/temperature_channel_layout.py",
      "backend/application/temperature_data_preparation.py",
      "backend/api/temperature_schemas.py",
      "frontend/src/api/temperature.ts",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/features/temperature/useTemperatureTool.ts",
      "frontend/src/features/temperature/sampleGroups.ts",
      "frontend/src/features/temperature/sourceColumns.ts",
      "frontend/src/features/temperature/useDataGridEditing.ts",
      "frontend/src/features/temperature/DataPreview.tsx",
      "frontend/src/features/temperature/temperature.css",
      "tests/unit/test_local_identity_service.py",
      "tests/unit/test_local_identity_store.py",
      "tests/integration/test_local_identity_api.py",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/integration/test_tools_temperature_api.py",
      "frontend/src/currentUser.test.ts",
      "frontend/src/api/localIdentity.test.ts",
      "frontend/src/features/local-identity/AccountDialog.test.tsx",
      "frontend/src/components/layout/Sidebar.test.tsx",
      "frontend/src/features/temperature/sampleGroups.test.ts",
      "frontend/src/features/temperature/useTemperatureReportInfo.test.tsx",
      "frontend/src/features/temperature/DataPreview.test.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/features/project-basic-information/currentUserDisplay.test.ts",
      "docs/local_identity.md",
      "docs/temperature_rise_tool.md",
      "frontend/src/App.tsx"
    ],
    "risk_reasons": [
      "Password authentication and persistent session security",
      "New additive local identity database schema independent of project authority"
    ],
    "activation_head": "a1357cbcc7dd8013e9a80f79f087959ccdd86121",
    "started_at": "2026-10-14T10:12:27.939232Z",
    "updated_at": "2026-10-14T10:58:39.812615Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_LOCAL_REGISTRATION_TEMPERATURE_SAMPLES_20261014",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_LOCAL_REGISTRATION_TEMPERATURE_SAMPLES_20261014",
      "subject": "2a7fca8b8017c608d304bb97301f66c22b58d6cd",
      "summary": "Local offline registration auto-login with remembered revocable sessions, dynamic identity defaults preserving report edits, and numbered-first/default-three adjustable authoritative sample grouping; browser-discovered sync-failure, focus and checkbox presentation refinements verified",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/main.py",
        "backend/api/routes_local_identity.py",
        "backend/api/temperature_schemas.py",
        "backend/application/local_identity_service.py",
        "backend/application/temperature_channel_layout.py",
        "backend/application/temperature_data_preparation.py",
        "backend/domain/local_identity.py",
        "backend/domain/temperature_data.py",
        "backend/infrastructure/storage/local_identity_store.py",
        "docs/local_identity.md",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/localIdentity.test.ts",
        "frontend/src/api/localIdentity.ts",
        "frontend/src/api/temperature.ts",
        "frontend/src/components/layout/Sidebar.test.tsx",
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/currentUser.test.ts",
        "frontend/src/currentUser.ts",
        "frontend/src/features/local-identity/AccountDialog.test.tsx",
        "frontend/src/features/local-identity/AccountDialog.tsx",
        "frontend/src/features/local-identity/localIdentity.css",
        "frontend/src/features/project-basic-information/currentUserDisplay.ts",
        "frontend/src/features/temperature/DataPreview.test.tsx",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/sampleGroups.test.ts",
        "frontend/src/features/temperature/sampleGroups.ts",
        "frontend/src/features/temperature/sourceColumns.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useDataGridEditing.ts",
        "frontend/src/features/temperature/useTemperatureReportInfo.test.tsx",
        "frontend/src/features/temperature/useTemperatureReportInfo.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_local_identity_api.py",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_local_identity_service.py",
        "tests/unit/test_local_identity_store.py",
        "tests/unit/test_temperature_data_preparation.py"
      ],
      "validation": [
        {
          "status": "passed",
          "detail": "Independent QA: 151 backend identity service/store/API and temperature preparation/calculation/workbook/HTTP tests passed on f8bca517; exact final Python/backend test bytes unchanged, independently verified. One existing Starlette/httpx deprecation warning. Backend results retained without unnecessary duplicate matrix."
        },
        {
          "status": "passed",
          "detail": "Independent QA on exact final subject 2a7fca8b: 162 frontend tests in 13 affected files passed, covering identity API/store/dialog/sidebar, App, Basic Information and temperature editing/grouping/report metadata; sequential npm run build TypeScript/Vite passed. Earlier QA sync-error/focus findings fixed with RED/GREEN regressions and rerun affected frontend checks."
        },
        {
          "status": "passed",
          "detail": "Isolated real Edge: registration automatically signs in with remember checked; refresh and complete owned-browser restart restore session; logout/switch/invalid and valid passwords, modal keyboard/focus, 530/1280 visual checks passed. Numbered1/3/5 groups; unnamed6 -> 3x2, unnamed20 -> incomplete3 then adjusted5x4 keeping all IDs; column exclusion/move/undo and row restore passed. No browser exceptions/server errors; root inspected final narrow screenshots."
        },
        {
          "status": "passed",
          "detail": "Actual XLSX download plus isolated read-only Excel CalculateFullRebuild: 5 groups x4 probes, manual tester/date retained, final Max13.9 and average maxima13.1, no formula errors. Owned temporary databases/browser profiles/screenshots/downloads cleaned, owned Edge/server/Excel closed; production identities/projects/source files untouched. Current localhost Vite proxy HEAD confirmed identity GET route loaded (405 Allow GET), no account/session read or mutation."
        },
        {
          "status": "passed",
          "detail": "git diff --check clean; exact final master subject clean; 39 observed product/test/doc paths inside approved41. Independent Integrator verified linear parents and unchanged backend bytes. No remote publication."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Independent Planner identity_samples_planner inspected real storage/config/API/sidebar/report/grouping seams and approved exact manifest, isolated identity database, PBKDF2 600k/revocable sessions/origin safeguards, optional sample_count legacy compatibility, exclusion/role restoration and desired-count validation; no material decision outstanding."
        },
        "developer": {
          "status": "passed",
          "detail": "Independent Developer identity_samples_developer TDD RED missingauthmodule and authoritative sample_count; finalauth24GREEN; sampleoverride4GREEN; focusedUI11GREEN; tsc-b passed. QA-sync failure RED then4targetedGREEN includingpriorBasicInfoWorkspace mount,30skipped; onlycurrentUser.ts/test changed, no backendchange, no unrelatedfixture edits. Writesstopped beforeimmutablecommits. Separate focus RED BODY-to-trigger and7 targeted GREEN; CSS-only visual correction uses app tokens."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Independent Reviewer PASS initial f8bca517 vs a1357cbc 39files Standards0/Spec0, ownedDB/getcookie/explicitcount fixesverified. FocusedPASS7061b40d syncadapterguard regression Standards0Spec0; finalfocusedPASS2a7fca8b stableafter-closekeyboardfocus+compacttokenCSS Standards0Spec0; priorreviewsretained, no backendbytechange andno fullmatrixduplicate."
        },
        "qa": {
          "status": "passed",
          "detail": "Independent context identity_samples_qa completed final affected matrix, sequential production build, real isolated Edge and native Excel/download verification; found sync-adapter/focus defects, fixes rechecked on final subject; clean owned-resource teardown verified."
        },
        "integrator": {
          "status": "passed",
          "detail": "Independent identity_samples_integrator accepted final QA and verified exact clean master 2a7fca8b, linear chain to a1357cbc, board-only CloseAndSubmit rollover, 39/41 allowed paths and unchanged backend files. No mutations/test reruns/remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Exact final subject already integrated in legacy local master; clean tree, scoped linear commits and independent integrator attestation. No fetch/push; waiting user acceptance and explicit final Close."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_MULTI_CURRENT_EXPORT_20261014",
    "tier": "standard",
    "subject": "ca8c56d437cd43a2b825fc00bb659c66b2f2eaae",
    "summary": "Export stable auxiliary current rows above the selected main current in T-riseChart",
    "disposition": "completed",
    "decision_ref": "User explicitly closes preceding export task and starts local registration login and sample grouping on 2026-10-14",
    "closed_at": "2026-10-14T10:12:27.939232Z"
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
