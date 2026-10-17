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
    "task_id": "TASK_LEGACY_PROJECT_READONLY_PREVIEW_20261017",
    "summary": "Tools legacy-project read-only batch preview with project boundaries, duplicate detection and conflict explanations",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Tools entry and focused read-only preview page; bounded selected-directory inspection with optional legacy metadata; deduplicate overlapping roots, group workspace/inner folders, expose conflicting identities; support batch selection, cancellation/retry, verify existing samples without source or database writes. No formal import, schema/data mutation, registry management, push or publication.",
    "scope_paths": [
      "backend/api/main.py",
      "backend/api/routes_tools_legacy_projects.py",
      "backend/application/legacy_project_preview_service.py",
      "backend/infrastructure/files/legacy_project_preview_gateway.py",
      "backend/infrastructure/files/windows_path_picker.py",
      "frontend/src/api/legacyProjects.ts",
      "frontend/src/features/legacy-projects/LegacyProjectPreview.tsx",
      "frontend/src/features/legacy-projects/LegacyProjectPreview.test.tsx",
      "frontend/src/features/legacy-projects/legacy-project-preview.css",
      "frontend/src/pages/ToolsPage.tsx",
      "frontend/src/pages/ToolsPage.test.tsx",
      "frontend/src/App.tsx",
      "frontend/src/App.test.tsx",
      "tests/unit/test_legacy_project_preview.py",
      "tests/integration/test_tools_legacy_projects_api.py",
      "docs/plans/LEGACY_PROJECT_PREVIEW_20261017.md"
    ],
    "risk_reasons": [],
    "activation_head": "246b589fe8f0999c7df53a32df8c78e2749e7030",
    "started_at": "2026-10-17T00:43:09.694160Z",
    "updated_at": "2026-10-17T01:26:22.903705Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_LEGACY_PROJECT_READONLY_PREVIEW_20261017",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_LEGACY_PROJECT_READONLY_PREVIEW_20261017",
      "subject": "fa4cba9a400fb02da82c8bafb3fbe0fb50b8836b",
      "summary": "Read-only preview complete, including scoped Tools English copy and native button hover guidance. Same-agent review and targeted follow-up QA; no business/source writes or publication.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/main.py",
        "backend/api/routes_tools_legacy_projects.py",
        "backend/application/legacy_project_preview_service.py",
        "backend/infrastructure/files/legacy_project_preview_gateway.py",
        "backend/infrastructure/files/windows_path_picker.py",
        "docs/plans/LEGACY_PROJECT_PREVIEW_20261017.md",
        "frontend/src/App.test.tsx",
        "frontend/src/App.tsx",
        "frontend/src/api/legacyProjects.ts",
        "frontend/src/features/legacy-projects/LegacyProjectPreview.test.tsx",
        "frontend/src/features/legacy-projects/LegacyProjectPreview.tsx",
        "frontend/src/features/legacy-projects/legacy-project-preview.css",
        "frontend/src/pages/ToolsPage.test.tsx",
        "frontend/src/pages/ToolsPage.tsx",
        "tests/integration/test_tools_legacy_projects_api.py",
        "tests/unit/test_legacy_project_preview.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Affected Python",
          "result": "Prior acceptance before copy-only follow-up: 25 passed; final backend/test inputs unchanged from ab9983b3; one existing Starlette deprecation; no unrelated Python or Office rerun."
        },
        {
          "status": "passed",
          "name": "Complete final frontend",
          "result": "Prior acceptance before copy-only follow-up: 961 passed / 1 existing profiling skip; default workers; 41.39s; tsc -b and Vite 187 modules / 1.18s passed sequentially."
        },
        {
          "status": "passed",
          "name": "Read-only real samples and batch scale",
          "result": "Prior acceptance before copy-only follow-up: 36 real project rows, 30 ready / 6 review, overlapping root collapsed, no ancestor/descendant duplicates; 320 disposable-project test. Source 2747 metadata entries and read identity-file hashes unchanged."
        },
        {
          "status": "passed",
          "name": "Final isolated UI",
          "result": "Prior acceptance before copy-only follow-up: Tools/deep-link/back; selection 30->0->30->31; conflict notes; deliberate 503 failure + real retry; atomic delayed-request stop; 514px and desktop no document overflow. Native dialog HTTP boundary mocked; manual input end-to-end. Browser and backend stopped, port 18766 closed."
        },
        {
          "status": "passed",
          "name": "Scope and evidence integrity",
          "result": "Prior acceptance before copy-only follow-up: Exact 16 authorized non-board paths; unchanged executable inputs after final subject; retained QA artifact hashes match; clean local linear history."
        },
        {
          "status": "passed",
          "name": "Final Tools copy follow-up",
          "result": "22 tests across ToolsPage and App passed after final code/test bytes; git diff --check passed. Scoped same-agent review. Prior full matrix not repeated; native title browser rendering not separately automated."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "agent": "/root",
          "independent": false,
          "method": "separate same-agent pass"
        },
        "reviewer": {
          "status": "passed",
          "agent": "/root",
          "independent": false,
          "method": "separate same-agent pass",
          "standards_findings": 0,
          "spec_findings": 0
        },
        "qa": {
          "status": "passed",
          "agent": "/root",
          "independent": false,
          "method": "separate same-agent pass"
        }
      },
      "integration": {
        "status": "passed",
        "result": "Local linear commit fa4cba9a; exact authorized task scope, clean worktree; no push/publication."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_WITHDRAW_EXISTING_PROJECT_INTAKE_20261017",
    "tier": "high_risk",
    "subject": "154a0f394a53d500ea512bd21b56dd09387411e0",
    "summary": "Withdraw rejected existing-project intake increment and preserve original registry operations",
    "disposition": "completed",
    "decision_ref": "User explicitly approved local-only close of the verified withdrawal and start of this read-only preview implementation; no push or publication.",
    "closed_at": "2026-10-17T00:43:09.694160Z"
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
