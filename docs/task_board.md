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
  "state": "running",
  "active": {
    "task_id": "TASK_ASSOCIATED_LTR_INTAKE_REGISTRATION",
    "summary": "Allow Intake to create a new associated LTR number after comparing the existing base row with the proposed new registration row.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Extend the specified-LTR Intake workflow so a missing associated DL suffix whose base exists can be reviewed as a separate new workbook row using current Intake/project mappings, then explicitly confirmed and appended without changing the base row. Preserve the exact-existing-number reuse flow; block missing bases and exact suffix duplicates; revalidate preview state and target absence at commit. Do not redesign other LTR registration modes.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/routes_new_project_completion.py",
      "backend/application/intake_confirmation_service.py",
      "backend/application/ltr_authority.py",
      "backend/application/ltr_excel_authority_adapter.py",
      "backend/application/ltr_workbook_write_commit_service.py",
      "backend/application/ltr_workbook_write_preview_service.py",
      "backend/application/new_project_completion_service.py",
      "backend/application/specified_ltr_workbook_authority_preview_service.py",
      "docs/PROJECT_CONTEXT.md",
      "frontend/src/api/client.ts",
      "frontend/src/components/workflow/new-project-workflow.css",
      "frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx",
      "frontend/src/features/new-project/useNewProjectCompletion.ts",
      "frontend/src/pages/IntakeInboxPage.test.tsx",
      "tests/integration/test_new_project_completion_api.py",
      "tests/unit/test_ltr_workbook_write_commit_service.py",
      "tests/unit/test_specified_ltr_workbook_authority_preview_service.py"
    ],
    "risk_reasons": [
      "authoritative public LTR workbook row creation",
      "duplicate and stale-preview race protection across external workbook writes"
    ],
    "activation_head": "a7c28aae0bf6b58397f02dab1be3e16cb406e812",
    "started_at": "2026-09-24T04:46:32.259629Z",
    "updated_at": "2026-09-24T14:57:30.337041Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_ASSOCIATED_LTR_INTAKE_REGISTRATION",
      "stage": "revision",
      "status": "running",
      "summary": "Correct integration report implementation commit SHA to the actual Git object ID before final delivery.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_LEGACY_RECOVERY_REVIEW",
    "tier": "high_risk",
    "subject": "71ba57e9522627e0742826b9c7778c1ee9969647",
    "summary": "Repair project folder generation review, stale legacy path recovery, template guidance, and safely blocked checkpoints without overwriting operator files.",
    "disposition": "completed",
    "decision_ref": "user-close-and-submit-2026-09-24-associated-ltr",
    "closed_at": "2026-09-24T04:46:32.259629Z"
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
