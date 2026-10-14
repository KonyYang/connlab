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
      "backend/api/main.py",
      "backend/api/routes_local_identity.py",
      "backend/api/temperature_schemas.py",
      "backend/application/intake_case_review_service.py",
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
      "frontend/src/pages/IntakeInboxPage.test.tsx",
      "frontend/src/pages/IntakeInboxPage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "tests/integration/test_local_identity_api.py",
      "tests/integration/test_tools_temperature_api.py",
      "tests/unit/test_intake_case_review_service.py",
      "tests/unit/test_local_identity_service.py",
      "tests/unit/test_local_identity_store.py",
      "tests/unit/test_temperature_data_preparation.py"
    ],
    "risk_reasons": [
      "Password authentication and persistent session security",
      "New additive local identity database schema independent of project authority"
    ],
    "activation_head": "a1357cbcc7dd8013e9a80f79f087959ccdd86121",
    "started_at": "2026-10-14T10:12:27.939232Z",
    "updated_at": "2026-10-14T12:38:54.936953Z",
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
      "subject": "e94f1d72e0fd49554d12caf794568065debf2412",
      "summary": "Login-free persistent local Project Leader Name via avatar; new project/report defaults preserve existing manual blank frozen values and original accounts; retain reviewed adjustable temperature sample grouping.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/main.py",
        "backend/api/routes_local_identity.py",
        "backend/api/temperature_schemas.py",
        "backend/application/intake_case_review_service.py",
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
        "frontend/src/pages/IntakeInboxPage.test.tsx",
        "frontend/src/pages/IntakeInboxPage.tsx",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_local_identity_api.py",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_intake_case_review_service.py",
        "tests/unit/test_local_identity_service.py",
        "tests/unit/test_local_identity_store.py",
        "tests/unit/test_temperature_data_preparation.py"
      ],
      "validation": [
        {
          "status": "passed",
          "detail": "Final exact e94f1d72:83 backend tests across identity service/store/API and intake review/manual intake/new-project completion boundaries; existing Starlette/httpx deprecation warning only."
        },
        {
          "status": "passed",
          "detail": "Final exact e94f1d72:176 frontend tests across14 affected files, followed sequentially by npm run build; TypeScript and Vite production build passed."
        },
        {
          "status": "passed",
          "detail": "Owned isolated Edge: avatar single-name editor/no authentication UI, clear validation and Cancel/Escape focus, cookie clearing plus full browser/server restart retains saved profile; real new-project/report initial defaults snapshot with existing/manual/blank preservation, fresh defaults, no browser exceptions or old auth calls."
        },
        {
          "status": "passed",
          "detail": "Profile API tests prove original registered database byte preservation. Actual browser-downloaded XLSX read-only native Excel full recalculation:5samplesx4points ManualTester/date preserved, Max13.9 average13.1, zeroformulaerrors;530/1280 screenshots independently inspected."
        },
        {
          "status": "passed",
          "detail": "Prior accepted pure backend sample recognition/numerical/workbook matrix reused because those files are unchanged by login-free revision; not reported as a new run. Owned QA server/browser/Excel closed and exact temporary artifacts deleted; no production/userdata touched."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Independent Planner verified permanent separate profile store/API and snapshot defaults, including four Intake paths required for explicit blank persistence, missing-key eligibility, frozen and required validation unchanged; no database migration/external writes."
        },
        "developer": {
          "status": "passed",
          "detail": "Independent Developer implemented login-free profile, TDD RED missing service/new leader default/lost cleared leader then GREEN26 focused frontend12profilebackend11intakeservice; TypeScript compile and diff check passed. Product24 changed paths; no sample logic changes from previously accepted feature; all writes stopped before e94f1d72 pin."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Independent exact e94f1d72 Standards0 material findings; Spec0 remaining findings; exact43 manifest matches; separate profile data/file boundary and original credentials preservation, no expiry/authUI, late read generation and per-context default/explicitblank/frozen provenance, samples unchanged. Diff check passed without repeating QA matrix."
        },
        "qa": {
          "status": "passed",
          "detail": "Independent QA reviewed e94f1d72:83backendtests6files176frontendtests14files and sequential production build PASS; isolated owned Edge direct avatar/single name/inline validation and stable Cancel Escape focus, profile persisted after clearing cookies and full browser/server restart, new-project/report snapshots manual and blank preservation, fresh defaults, no auth calls/legacyDB creation/browserexceptions; seeded account DBbytepreservationAPI; actual downloadedxlsx nativeExcel5x4ManualTester/date13.9Max13.1Avg0formulaerrors. Root530/1280visualPASS. Prior unchanged numerical/samplebackend evidence reused explicitly. QA cleanup confirmed owned resources removed."
        },
        "integrator": {
          "status": "passed",
          "detail": "Independent Integrator PASS exact e94f1d72 clean local master linear board-only parent over ecef3900; activation43paths exact43manifest noextra/missing diffcheckclean; approved profile/defaults/preservation and unchanged samples, independentReviewQA evidence accepted, no writes/reruns/remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Clean local master exact e94f1d72; scope manifest equals43 observed activation-range paths. Original account data and public external-file authority preserved. No remote publication; awaiting final User Close. Historical missing leader keys cannot recover prior clear intent, documented."
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
