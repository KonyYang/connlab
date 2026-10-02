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
    "task_id": "TASK_CREATE_FOLDER_IR_DWV_RECORDS_20261002",
    "summary": "Generate IR/DWV blank records in the Create folder workflow and disclose generated files",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Extend existing confirmed-Matrix contact-record Create folder preflight and recoverable generation to IR/DWV; show generated-file readiness/skip/archive information in creation UI. Preserve existing LLCR/CR, names, authority and measured files; isolated validation only; no measurement-result import or report/photo automation.",
    "scope_paths": [
      "backend/api/project_folder_preflight.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/application/project_folder_generation_service.py",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "tests/unit/test_project_folder_generation_service.py",
      "docs/PROJECT_CONTEXT.md",
      "docs/project_folder_generation_recovery.md"
    ],
    "risk_reasons": [
      "authoritative external mutation"
    ],
    "activation_head": "d3aef5c9d2c01803f18d4dfdc0ea53e550377ad2",
    "started_at": "2026-10-02T08:47:00.592399Z",
    "updated_at": "2026-10-02T11:06:54.232070Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CREATE_FOLDER_IR_DWV_RECORDS_20261002",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_CREATE_FOLDER_IR_DWV_RECORDS_20261002",
      "subject": "0b1f58320e01be1cbaa32da1a8491e4d7bc152fa",
      "summary": "Create folder generates confirmed-Matrix IR&DWV blank records through the existing safe publisher. User revisions clarify folder-in-use guidance and hide informational file lists while retaining failures, diagnostics, preflight and confirmation. Isolated create/reload/rebuild/skip and current business-page display checks passed. Residual limitation retained in this closure record: existing business-folder WinError 5 requires closing Explorer/documents; archive retry after release was not exercised. Installed COM and packaged release were not exercised.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/project_folder_generation_composition.py",
        "backend/api/project_folder_preflight.py",
        "backend/application/project_folder_generation_service.py",
        "docs/PROJECT_CONTEXT.md",
        "docs/project_folder_generation_recovery.md",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "tests/integration/test_generation_workspace_process_recovery.py",
        "tests/integration/test_project_folder_generation_complete_chain.py",
        "tests/integration/test_project_folder_generation_recovery.py",
        "tests/unit/test_project_folder_generation_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "command": "C:/PythonEnvs/connlab/.venv/Scripts/python.exe -m pytest -q --tb=short tests/unit/test_project_folder_generation_service.py tests/integration/test_project_folder_generation_api.py tests/integration/test_project_folder_generation_write_guard.py tests/integration/test_project_folder_generation_complete_chain.py tests/integration/test_project_folder_generation_recovery.py tests/integration/test_generation_workspace_process_recovery.py tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py tests/unit/test_ir_dwv_record_projection.py tests/unit/test_ir_dwv_record_workbook_gateway.py tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py",
          "result": "Initial feature commit 4497df98 independent QA: 247 passed in 156.95s on generation/write-guard/recovery and IR/DWV/LLCR/CR selected suites. Subsequent backend edit was error copy only; complete affected service suite rerun 20 passed. Backend feature/safety paths otherwise unchanged."
        },
        {
          "status": "passed",
          "command": "npm test -- src/features/project-workbench",
          "result": "Initial feature commit 4497df98 independent QA: 18 files /202 tests passed. Subsequent UI revisions final complete affected Layout suite:81 passed; other frontend paths unchanged. Meaningful revision RED/GREEN recorded."
        },
        {
          "status": "passed",
          "command": "npm run build",
          "result": "Independent QA final revision state: production build passed sequentially after Layout Vitest."
        },
        {
          "status": "passed",
          "command": "In-app browser smoke against isolated copied-template/SQLite fixture projects",
          "result": "Actual fresh create and IR workbook content/blank results; reload exact hash and mtime unchanged; reviewed Backup and Rebuild archives measured workbook exact bytes and creates new blank; missing pairs shows skipped instruction and completed warning with no IR workbook. No business-project mutation. Actual IR XLSX, fake other Office adapters; installed COM and packaged release not exercised. Later final-revision business-page display: root refreshed requested URL, outputs=[],alerts=[],matrix=true; independent QA screenshot review confirmed no informational list. This did not execute archive/rebuild and is not proof that the existing business-folder lock has cleared."
        },
        {
          "status": "passed",
          "command": "git diff --check, exact commit scope and frozen revision file hashes",
          "result": "Independent Reviewer, QA and Integrator: exact 11 approved task paths over activation baseline; frozen final affected bytes unchanged, clean task index, unrelated protected document excluded."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "context": "Independent create_folder_ir_dwv_planner",
          "result": "Approved existing publisher seam, confirmed authority, missing-pairs-only skip, fingerprints, legacy journal compatibility, owned resources and recovery coverage."
        },
        "developer": {
          "status": "passed",
          "context": "Independent create_folder_ir_dwv_developer",
          "result": "Implemented 11 scoped files. Meaningful RED/GREEN: preflight/version 6 failures to 11 passes; real complete chain missing IR to generated/archived XLSX; disclosure 2 failures to passes; Reviewer P2 followup 3 failures to 3 passes, final Layout 73 passes. User revisions: archive warning copy/diagnostic folding RED5 failing UI cases and2 backend cases; targeted7UI/5backend GREEN. File-list removal RED5 failures/2 passes to targeted12 passes, failure alerts unchanged."
        },
        "reviewer": {
          "status": "passed",
          "context": "Independent create_folder_ir_dwv_reviewer",
          "result": "Independent reviews of feature and each revision: Standards0/Spec0 unresolved, approved scope. Final file-list removal preserves errors/progress/archive confirmation and backend safeguards."
        },
        "qa": {
          "status": "passed",
          "context": "Independent create_folder_ir_dwv_qa",
          "result": "Independent initial isolated feature suites247Python/202frontend and real isolated browser passed. Final affected backend-copy service20 passed; latest Layout81 and sequentialbuild passed. Current business-page list removal executed by root with independent QA screenshot review. Original business archive retry remains not exercised; no passing result claimed for it."
        },
        "integrator": {
          "status": "passed",
          "context": "Independent create_folder_ir_dwv_integrator",
          "result": "Independent immutable commit verification:4497df98 feature,2625bfb9 warningrevision,0b1f5832 listremoval. Exact approved paths/parents/index and protected doc blob unchanged. Actual local direct integration, not a merge. Original business-folder occupancy limitation retained."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "0b1f58320e01be1cbaa32da1a8491e4d7bc152fa",
        "result": "Direct feature and bounded revision commits integrated locally and independently verified. User final Close requests closure with explicitly reported business-folder occupancy/retry limitation, not a claim that Windows access was repaired."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_REPORT_AUTOMATION_DOC_BASELINE_20261002",
    "tier": "micro",
    "subject": "2106e342e65b7c1d625aecfca6f8833247a0c355",
    "summary": "Reconcile three report automation documents with current ConnLab implementation",
    "disposition": "completed",
    "decision_ref": "User final Close 2026-10-02: three report automation documents reconciled, validated and committed.",
    "closed_at": "2026-10-02T08:35:36.218394Z"
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
