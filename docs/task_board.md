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
    "task_id": "TASK_PROJECT_FOLDER_AVAILABILITY_GUIDANCE",
    "summary": "Make Project Folder actions reflect real folder and template availability, disable false Open/Create affordances, and guide missing-template recovery through Settings.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Expose read-only local folder availability from the public-folder context, use it for Folder Actions, prevent Create when the generation preview is blocked by missing template resources, and provide a direct Settings recovery action without changing external files.",
    "scope_paths": [
      "backend/application/public_folder_workflow_service.py",
      "backend/api/routes_public_folder_workflow.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/projectFolderTaskSelectors.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "tests/unit/test_public_folder_workflow_service.py",
      "tests/integration/test_public_folder_workflow_api.py",
      "frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx"
    ],
    "risk_reasons": [
      "project-folder availability controls an authoritative external-folder workflow",
      "must not weaken template preflight or alter project files",
      "must preserve physically existing legacy folders without requiring a latest generation record"
    ],
    "activation_head": "0063f4ba73a3ea1a6e94ce53d26b9c29a15daf77",
    "started_at": "2026-09-22T12:08:25.034029Z",
    "updated_at": "2026-09-22T13:01:33.053843Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_AVAILABILITY_GUIDANCE",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "subject": "d6a6fcfd54f2c0023f0908cc54baa216973d6754",
      "summary": "Project Folder actions now use live directory availability, template-blocked creation is disabled before write, and Settings provides the recovery path.",
      "changed_paths": [
        "backend/application/public_folder_workflow_service.py",
        "backend/api/routes_public_folder_workflow.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/project-workbench/projectFolderTaskSelectors.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "tests/unit/test_public_folder_workflow_service.py",
        "tests/integration/test_public_folder_workflow_api.py",
        "frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx"
      ],
      "task_id": "TASK_PROJECT_FOLDER_AVAILABILITY_GUIDANCE",
      "roles": {
        "reviewer": {
          "status": "passed",
          "summary": "Independent focused review passed; P3 test gap resolved before QA."
        },
        "integrator": {
          "status": "passed",
          "summary": "Exact subject, scope paths, clean tree, commits, and evidence verified."
        },
        "qa": {
          "status": "passed",
          "summary": "Independent complete normal gate passed once."
        },
        "developer": {
          "status": "passed",
          "summary": "Independent implementation and focused checks completed."
        },
        "planner": {
          "status": "passed",
          "summary": "Independent plan confirmed read-only availability contract and recovery guidance."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "verified_local"
      },
      "version": 1,
      "scope_ok": true,
      "validation": [
        {
          "name": "developer-focused",
          "summary": "Backend 13, selector 8, layout 58 passed with TDD red/green evidence.",
          "status": "passed"
        },
        {
          "name": "independent-review",
          "summary": "No blocking defects; safety invariants and scope passed. Exact template blocker regression added.",
          "status": "passed"
        },
        {
          "name": "independent-qa",
          "summary": "Python 2996 passed/7 skipped/19 deselected; frontend 650 passed/1 skipped; production build passed.",
          "status": "passed"
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_CREATE_REBUILD_ENTRY",
    "tier": "high_risk",
    "subject": "785964d4ef996d75677efc22eda670c733090c2b",
    "summary": "Separate project-folder opening from the Folder Actions header so the row icon remains the only Open action and the header handles Create folder or protected Backup and Rebuild.",
    "disposition": "completed",
    "decision_ref": "user-close-2026-09-22",
    "closed_at": "2026-09-22T11:46:06.011819Z"
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
