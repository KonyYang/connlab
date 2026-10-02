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
    "task_id": "TASK_CREATE_FOLDER_ARCHIVE_ONLY_20261002",
    "summary": "Unify Create folder as reviewed whole-folder archive and fresh authority generation",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Create a missing official folder; existing verified sole owned folder requires whole-folder archive confirmation and fresh generation from templates and latest confirmed authorities. Remove content-based update/rename/rebind choices from the Create folder entry. Preserve legacy persisted-operation recovery, ownership/path/concurrency/lock safeguards and unrelated User work.",
    "scope_paths": [
      "docs/PROJECT_CONTEXT.md",
      "docs/plans/REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md",
      "docs/plans/REPORT_AUTOMATION_VBA_REFERENCE_MAP.md",
      "docs/plans/REPORT_RESULT_PHOTO_AUTOMATION_DESIGN.md",
      "docs/project_folder_generation_recovery.md",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts"
    ],
    "risk_reasons": [
      "Changes initiation of authoritative external folder archival and replacement"
    ],
    "activation_head": "3f8aac97e5c12b528ad5b5cdc88ed533aa4b5d32",
    "started_at": "2026-10-02T12:05:08.026304Z",
    "updated_at": "2026-10-02T12:59:23.536535Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CREATE_FOLDER_ARCHIVE_ONLY_20261002",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_CREATE_FOLDER_ARCHIVE_ONLY_20261002",
      "subject": "0ed750d81cfc37de9e836058457660b879bc02e6",
      "summary": "Create folder now creates a missing folder or requires explicit whole-folder Backup and Rebuild for a verified existing folder. Old files stay in timestamped History; fresh outputs and folder name use templates and latest confirmed authorities. Removed granular in-place/rename/rebind entry choices and content-based update-mode selection, while retaining safety checks and historical recovery. Six-file product commit818de002. Separate commitba5a7d77 moved three design docs outside repository; User approved only board manifest correction recording those existing deletions. No document restoration or new document commit. Isolated browser acceptance passed; installed Office COM and packaged release not exercised.",
      "scope_ok": true,
      "changed_paths": [
        "docs/PROJECT_CONTEXT.md",
        "docs/plans/REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md",
        "docs/plans/REPORT_AUTOMATION_VBA_REFERENCE_MAP.md",
        "docs/plans/REPORT_RESULT_PHOTO_AUTOMATION_DESIGN.md",
        "docs/project_folder_generation_recovery.md",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
        "frontend/src/features/project-workbench/useProjectFolderGeneration.ts"
      ],
      "validation": [
        {
          "status": "passed",
          "command": "Selected project-folder generation service/API/write-guard/recovery/process-recovery/complete-chain pytest suites",
          "result": "Independent QA:110 passed, one existing Starlette/httpx warning. Backend unchanged during frontend correction; no redundant rerun."
        },
        {
          "status": "passed",
          "command": "npm test -- src/features/project-workbench",
          "result": "Independent QA final reviewed frontend state:18 files/219 tests passed; hook43 and Layout77 included."
        },
        {
          "status": "passed",
          "command": "npm run build",
          "result": "Independent QA production build passed sequentially after final frontend test run."
        },
        {
          "status": "passed",
          "command": "In-app browser isolated copied-template/SQLite fixture at127.0.0.1:8095/projects/P1",
          "result": "Root actual clicks, independent QA screenshot/filesystem verification:missing-folder Create; existing-folder Cancel preserves directory/file identities, hashes,mtime; latest Basic v3 changes description and completes spec/date; explicit Backup and Rebuild archives exact original IR workbook plus operator file added AFTER preview, without copying it into fresh folder; fresh name/header latestdescription, measured cellsblank, LTR root/SourceBookretained; unchanged-input Create still shows backupconfirmation, Cancel writesnothing. Only owned server24666 stopped. Real IR XLSX/openpyxl, fake otherOffice adapters; no business-project writes, installedCOM or packagedrelease."
        },
        {
          "status": "passed",
          "command": "git diff --check and frozen six product blobs",
          "result": "Reviewed, tested six product paths exactly unchanged after final tests/build/browser. Only board-only commits since product818de002. External relocated design SHA B27165CBEF9272CBBDE498BDB5BC06910A213E6E5455F7D96EC09DB8D43464A7 unchanged."
        },
        {
          "status": "passed",
          "command": "connlab_sol_task.py amend-scope",
          "result": "ALLOW_AMEND_SCOPE after User explicit approval on2026-10-02. Nine-path manifest includes six product paths plus three externally committed document deletions solely for cumulative Git-diff accounting. No changes to deleted/external documents."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "context": "Independent archive_rebuild_planner",
          "result": "Planned unified reviewed whole-folder archive/fresh generation entry, existing backend seam reuse, explicit ownership/source/concurrency safeguards and legacy recovery. No business-content comparison or old-file copyback."
        },
        "developer": {
          "status": "passed",
          "context": "Independent archive_only_developer plus root scoped documentation",
          "result": "Implemented six approved paths only. Meaningful RED/GREEN covers defaultexistingbackup, no granular choices, pendingoriginalResume, reviewtoken/intentrace, safelyrestartablefreshcreation, unverifiedlegacyconflictblocking, realmissingfolderpreviewshape and specificfresh blockers. Final targeted120pass(43hook+77Layout)."
        },
        "reviewer": {
          "status": "passed",
          "context": "Independent archive_only_reviewer",
          "result": "Final exact six-file review:Standards0/Spec0 unresolved. Initial focused findings aboutfreshrestart, unprovenlegacybackupoptions, actualmissingfolderpreview and specificerrorguidance resolved and reviewed on final frozenstate."
        },
        "qa": {
          "status": "passed",
          "context": "Independent create_folder_ir_dwv_qa",
          "result": "Final110Python/219frontend/sequentialbuildpassed. Root actual browser operations independently verified through screenshots and filesystem identities/hashes/mtime/workbook contents, including after-preview operatorfilearchival and no copyback. No businesswrites or installedOffice/package claim."
        },
        "integrator": {
          "status": "passed",
          "context": "Independent create_folder_ir_dwv_integrator",
          "result": "Final independent integration passed at0ed750d81cfc37de9e836058457660b879bc02e6:cleanworktree, expectedancestry, nine-path approvedmanifestexactactivationdiff(excludingboard), onlyboardchangesafter818de002, sixfrozenproductblobsandexternaldesignSHAunchanged. ExplicitUsercorrectionresolvesadministrativeblocker. No duplicateQA or writes."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "0ed750d81cfc37de9e836058457660b879bc02e6",
        "result": "Direct local six-file product commit818de002 and subsequent board-only recovery/correction independentlyverified at0ed750d8. User-approved cumulative manifest records externalba5a7d77 three-documentrelocation without product/documentedits. No merge or push claimed."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_CREATE_FOLDER_IR_DWV_RECORDS_20261002",
    "tier": "high_risk",
    "subject": "0b1f58320e01be1cbaa32da1a8491e4d7bc152fa",
    "summary": "Generate IR/DWV blank records in the Create folder workflow and disclose generated files",
    "disposition": "completed",
    "decision_ref": "User final Close 2026-10-02 after generated-file list removal delivery; retain disclosed business-folder occupancy/retry limitation and preserve unrelated design document.",
    "closed_at": "2026-10-02T11:08:38.105836Z"
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
