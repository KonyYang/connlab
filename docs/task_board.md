# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> WIP=1. GPT-5.6 Sol routes work as micro, standard, or high risk and runs routine stages
> automatically until the User's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_CANONICAL_OFFICIAL_FOLDER_LIFECYCLE",
    "summary": "Keep one active LTR-named official project folder, reconcile confirmed Basic Information names, and archive reviewed rebuild versions safely.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Only the approved official project-folder naming, same-project rename/manual relink, History folder archive, path-reference recovery, and foreign-identity guard. No mutation of existing business folders during implementation.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/api/routes_official_project_workspace.py",
      "backend/api/routes_project_folder_generation.py",
      "backend/application/official_folder_relocation_service.py",
      "backend/application/official_project_workspace_service.py",
      "backend/application/project_folder_generation_service.py",
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "backend/infrastructure/official_workspace_manifest.py",
      "backend/infrastructure/storage/repositories/official_workspace.py",
      "backend/infrastructure/storage/repositories/project_output_record.py",
      "docs/PROJECT_CONTEXT.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "tests/integration/test_official_project_workspace_api.py",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/unit/test_generation_workspace_recovery.py",
      "tests/unit/test_official_project_workspace_service.py",
      "tests/unit/test_project_folder_generation_service.py"
    ],
    "risk_reasons": [
      "Authoritative external project-folder moves and path-reference migration require recoverable, identity-checked publication."
    ],
    "activation_head": "932fc1f8aa7efd3bae2e5b460497295e6a053f19",
    "started_at": "2026-09-24T15:28:17.482354Z",
    "updated_at": "2026-09-24T23:06:35.021016Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CANONICAL_OFFICIAL_FOLDER_LIFECYCLE",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "summary": "Implemented identity-checked official folder naming, relocation/relink, History/Folders rebuild archive, in-place update, and fail-closed safeguards without touching business folders.",
      "scope_ok": true,
      "task_id": "TASK_CANONICAL_OFFICIAL_FOLDER_LIFECYCLE",
      "integration": {
        "status": "passed",
        "detail": "Implementation 7fda10a3 and approved scope correction c469def1 are local commits; no push, release, close, or real business-folder mutation."
      },
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/project_folder_generation_composition.py",
        "backend/api/routes_official_project_workspace.py",
        "backend/api/routes_project_folder_generation.py",
        "backend/application/official_folder_relocation_service.py",
        "backend/application/official_project_workspace_service.py",
        "backend/application/project_folder_generation_service.py",
        "backend/infrastructure/files/recoverable_workspace_publisher.py",
        "backend/infrastructure/official_workspace_manifest.py",
        "backend/infrastructure/storage/repositories/official_workspace.py",
        "backend/infrastructure/storage/repositories/project_output_record.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
        "tests/integration/test_generation_workspace_process_recovery.py",
        "tests/integration/test_official_project_workspace_api.py",
        "tests/integration/test_project_folder_generation_api.py",
        "tests/integration/test_project_folder_generation_complete_chain.py",
        "tests/integration/test_project_folder_generation_recovery.py",
        "tests/unit/test_generation_workspace_recovery.py",
        "tests/unit/test_official_project_workspace_service.py",
        "tests/unit/test_project_folder_generation_service.py"
      ],
      "schema": "connlab.sol-task-report",
      "version": 1,
      "subject": "c469def1731e75eaa20ceb7f66c1619033b404bf",
      "roles": {
        "qa": {
          "status": "passed",
          "detail": "Independent complete affected matrix passed."
        },
        "developer": {
          "status": "passed",
          "detail": "RED/GREEN focused tests and implementation completed."
        },
        "integrator": {
          "status": "passed",
          "detail": "Verified clean master, parent chain, exact approved scope, route alignment, and test evidence."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Independent production review and follow-up review passed."
        },
        "planner": {
          "status": "passed",
          "detail": "Independent high-risk planning completed."
        }
      },
      "validation": [
        {
          "status": "passed",
          "name": "Python non-Office suite",
          "detail": "3046 passed, 8 skipped, 19 deselected, 2 warnings on final state."
        },
        {
          "status": "passed",
          "name": "Frontend tests and production build",
          "detail": "661 passed, 1 skipped; TypeScript and Vite production build passed on unchanged frontend."
        },
        {
          "status": "passed",
          "name": "Git diff whitespace check",
          "detail": "git diff --check passed on final committed diff."
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_ASSOCIATED_LTR_INTAKE_REGISTRATION",
    "tier": "high_risk",
    "subject": "84240104066101e4d4d931615873b36922b286d8",
    "summary": "Allow Intake to create a new associated LTR number after comparing the existing base row with the proposed new registration row.",
    "disposition": "completed",
    "decision_ref": "user-close-2026-09-24",
    "closed_at": "2026-09-24T15:05:36.658246Z"
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
