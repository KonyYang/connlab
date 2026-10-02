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
    "task_id": "TASK_REPORT_WORKSPACE_HIDE_AUTHORITY_VERSIONS_20261003",
    "summary": "Remove permanent Report Workspace authority version strip",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove the always-visible Basic Information/Matrix version strip and unused CSS. Preserve all authority/readiness validation and contextual blockers. Update affected public UI assertions and product facts; no backend or business-file mutations.",
    "scope_paths": [
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "frontend/src/workbench.css",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "1f6ffd0a10da13830763a4e0890785dcf77d9607",
    "started_at": "2026-10-02T23:34:20.905824Z",
    "updated_at": "2026-10-02T23:40:37.501745Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_REPORT_WORKSPACE_HIDE_AUTHORITY_VERSIONS_20261003",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "task_id": "TASK_REPORT_WORKSPACE_HIDE_AUTHORITY_VERSIONS_20261003",
      "integration": {
        "subject": "9ad084e7de66903f099f48c35d6471ce4d5c330b",
        "result": "Scoped local commit; clean working tree. No backend, report publication, or external authoritative file mutations.",
        "status": "passed"
      },
      "scope_ok": true,
      "subject": "9ad084e7de66903f099f48c35d6471ce4d5c330b",
      "schema": "connlab.sol-task-report",
      "version": 1,
      "validation": [
        {
          "command": "npm test -- src/features/report-workspace/ReportWorkspace.test.tsx src/features/report-workspace/reportWorkspaceModel.test.ts src/features/report-workspace/useCustomerReportJob.test.tsx",
          "result": "41 tests passed across 3 files on final source bytes. Targeted RED first failed because the version strip was still visible.",
          "status": "passed"
        },
        {
          "command": "npm run build",
          "result": "TypeScript and Vite production build passed on final source bytes.",
          "status": "passed"
        },
        {
          "command": "In-app browser Report Workspace read-only smoke",
          "result": "Version strip absent; all 3 report regions remain; missing Internal Report blockers retained; no console errors. Screenshot tmp/report-workspace-no-authority-strip-20261003.png. No business report writes.",
          "status": "passed"
        },
        {
          "command": "git diff --check",
          "result": "No whitespace errors.",
          "status": "passed"
        }
      ],
      "roles": {
        "developer": {
          "subject": "9ad084e7de66903f099f48c35d6471ce4d5c330b",
          "result": "Micro task implemented and exact diff self-reviewed by root. No independent reviewer claimed. Existing backend and readiness logic unchanged.",
          "status": "passed"
        }
      },
      "changed_paths": [
        "frontend/src/features/report-workspace/ReportWorkspace.tsx",
        "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
        "frontend/src/workbench.css",
        "docs/PROJECT_CONTEXT.md"
      ],
      "summary": "Remove permanent authority version strip; retain contextual blockers and all report authority checks."
    }
  },
  "last_closed": {
    "task_id": "TASK_REPORT_WORKSPACE_COMPACT_LAYOUT_20261002",
    "tier": "standard",
    "subject": "1d82ecbc050308f4a87ec3fd4dea5227139c16ae",
    "summary": "Unify Report Workspace top bar and three compact business sections",
    "disposition": "completed",
    "decision_ref": "User final Close on 2026-10-03 after ready_for_close delivery; preserve disclosed release-package and live Office verification limitations.",
    "closed_at": "2026-10-02T23:31:31.508883Z"
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
