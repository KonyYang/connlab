# ConnLab Task Board

> Status Authority: Read `state` and `active` in the machine control block below; dynamic task status is not duplicated in human prose.
> Last Updated: 2026-08-14
> Current Source Of Truth: `docs/task_board.md`
> Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
> Execution Rule: WIP=1; occupied submissions wait with zero writes, while idle submissions classify into direct simple work or the automatic approved complex role chain.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.personal-serial-control",
  "version": 2,
  "mode": "personal_serial",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG",
    "summary": "Establish one administrator-managed LTR workbook password runtime configuration contract with a secret-free packaged template, an upgrade-safe mutable ProgramData file, preserved environment override and runtime consumers, and removal of the ordinary Settings UI/API/write-service password chain.",
    "kind": "planned",
    "classification": "needs_discovery",
    "phase": "development",
    "scope_contract": {
      "may_touch": [
        ".gitignore",
        "backend/api/main.py",
        "backend/api/routes_settings.py",
        "backend/application/ltr_workbook_password_settings_service.py",
        "backend/desktop/runtime_paths.py",
        "backend/shared/config.py",
        "connlab.admin.example.toml",
        "connlab.local.example.toml",
        "docs/packaging_notes.md",
        "packaging/README_FOR_BROWSER_OPERATOR.md",
        "packaging/README_FOR_OPERATOR.md",
        "scripts/build_windows_browser_release.ps1",
        "scripts/build_windows_desktop_release.ps1",
        "frontend/src/api/client.ts",
        "frontend/src/pages/SettingsPage.tsx",
        "frontend/src/features/settings/SettingsExternalResourcesPanel.tsx",
        "frontend/src/settings.css",
        "frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx",
        "frontend/src/pages/SettingsPage.test.tsx",
        "tests/unit/test_config.py",
        "tests/unit/test_desktop_packaged_runtime_paths.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tests/unit/test_packaging_notes.py",
        "tests/integration/test_ltr_workbook_admin_runtime_config_api.py",
        "tests/unit/test_ltr_workbook_password_settings_service.py",
        "tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG.md",
        "docs/task_ltr_workbook_admin_runtime_config_plan.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_planner.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_developer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_reviewer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_qa.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_integrator.md",
        "docs/task_board.md"
      ],
      "expected_file_count": 33,
      "classification_reason": "Planned/complex because the change intentionally removes a public API contract, relocates a persisted secret authority from ordinary local configuration to an administrator-managed deployment contract, changes packaged runtime path policy and release assembly, and crosses frontend, backend, packaging, documentation, and test boundaries.",
      "targeted_validation": [
        "Run focused backend configuration, packaged runtime-path, release-script, packaging-note, route-absence, local-config preservation, transaction, read-only-open, and Excel gateway pytest suites.",
        "Run focused Settings panel and Settings page Vitest suites proving no password UI or password request while existing resource behavior remains.",
        "Run the production frontend build.",
        "Run py_compile for every touched surviving Python product and test module.",
        "Verify both release scripts ship only config/connlab.admin.example.toml and never create or overwrite %PROGRAMDATA%/ConnLab/config/connlab.admin.toml.",
        "Verify environment-over-admin-file precedence, explicit blank environment behavior, local-file password rejection, safe-summary redaction, and existing runtime password consumption.",
        "Verify GET and PUT /api/settings/ltr-workbook-password return 404 and are absent from OpenAPI and the typed frontend client.",
        "Verify tracked TOML templates contain only an empty password placeholder, connlab.admin.toml is ignored and untracked, and no real secret appears in source, tests, docs, evidence, or output.",
        "Run QA browser smoke at desktop and 514px with disposable state, confirming Settings loads without password requests/UI/errors and existing resource controls remain usable.",
        "Run git diff --check, exact changed-path whitelist, cached-diff-empty, deleted-import/reference, UTF-8, and no-real-data/config/workbook mutation checks."
      ],
      "forbidden_categories": {
        "api_contract": true,
        "database": false,
        "schema_or_migration": false,
        "persistence": true,
        "authority": true,
        "public_drive_workflow": true,
        "business_rule_semantics": false,
        "destructive_action": true,
        "external_mutation": false
      }
    },
    "plan_ref": "docs/task_ltr_workbook_admin_runtime_config_plan.md@fdaa1feb3781d5704fece77f167cc1f30e893f6b#5d0de22809e9534d39f843d0d1bd09676ca2620f078966f8997cc33c58fd37d5",
    "approval_ref": "批准上述 Plan ref 与 approved-request SHA-256",
    "activation_parent_sha": "a61b7dc559a5122093ebaaa06476c0395e63321a",
    "activated_at": "2026-08-15T14:26:38Z",
    "updated_at": "2026-08-15T23:13:59Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-ltr-workbook-admin-runtime-config",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-ltr-workbook-admin-runtime-config",
      "base_sha": "4540da65516b4c0fd2a0e7442f05ada8bfc8f917",
      "head_sha": "4540da65516b4c0fd2a0e7442f05ada8bfc8f917",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": "Developer",
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "f85e2a37bbb95a6b8a012af1c4cdaeba2667e2757b56ca895023a44fa21dba8c",
          "role": "Planner",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_admin_runtime_config_planner",
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-15T16:29:55Z"
        }
      ],
      "host_thread_id": "/root/ltr_admin_runtime_config_host",
      "host_id": "/root/ltr_admin_runtime_config_host",
      "approved_code_paths": [
        ".gitignore",
        "backend/api/main.py",
        "backend/api/routes_settings.py",
        "backend/application/ltr_workbook_password_settings_service.py",
        "backend/desktop/runtime_paths.py",
        "backend/shared/config.py",
        "connlab.admin.example.toml",
        "connlab.local.example.toml",
        "docs/packaging_notes.md",
        "packaging/README_FOR_BROWSER_OPERATOR.md",
        "packaging/README_FOR_OPERATOR.md",
        "scripts/build_windows_browser_release.ps1",
        "scripts/build_windows_desktop_release.ps1",
        "frontend/src/api/client.ts",
        "frontend/src/pages/SettingsPage.tsx",
        "frontend/src/features/settings/SettingsExternalResourcesPanel.tsx",
        "frontend/src/settings.css",
        "frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx",
        "frontend/src/pages/SettingsPage.test.tsx",
        "tests/unit/test_config.py",
        "tests/unit/test_desktop_packaged_runtime_paths.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tests/unit/test_packaging_notes.py",
        "tests/integration/test_ltr_workbook_admin_runtime_config_api.py",
        "tests/unit/test_ltr_workbook_password_settings_service.py",
        "tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG.md",
        "docs/task_ltr_workbook_admin_runtime_config_plan.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_planner.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_developer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_reviewer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_qa.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_integrator.md",
        "docs/task_board.md"
      ],
      "required_gates": [
        "Reviewer",
        "QA",
        "Integrator"
      ],
      "developer_subject_commit": null,
      "reviewer_subject_commit": null,
      "qa_subject_commit": null,
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_planner.md@fdaa1feb3781d5704fece77f167cc1f30e893f6b#f6c13b8f4c70969c88dbce360dd0417e3fe02d9f2a20953156fe701883d03d5f"
      ],
      "blocker_history": [],
      "pending_callback": {
        "state": "dispatch_pending",
        "action_id": "045bd2dd4567cc617b5250491178abe4bb6f89c25d15336ca871a732999b5695",
        "role": "Developer",
        "attempt": 1
      },
      "closeout_disposition": null,
      "retained_resource_refs": [],
      "close_decision_ref": null
    }
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_SETTINGS_HIDE_LTR_WORKBOOK_PASSWORD_CARD",
    "disposition": "closed after human review",
    "decision_ref": "关闭 TASK_SETTINGS_HIDE_LTR_WORKBOOK_PASSWORD_CARD",
    "closed_at": "2026-08-15T14:25:19Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF",
      "status": "cancelled",
      "owner": "User / manual governance",
      "disposition": "retain clean Task-A lane and all evidence; no automatic adoption, merge, rewrite, deletion, or role dispatch",
      "evidence": "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_reviewer.md@85e71dfa212c57c26527fad42eaf00a83b19c935#f1ca9341149d567958d837c18932e25ddee1ad47189266d0de73a03540e6de3a",
      "branch": "lane/task-governance-active-context-deterministic-transition-and-event-handoff",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-active-context-deterministic-transition-and-event-handoff",
      "head": "85e71dfa212c57c26527fad42eaf00a83b19c935"
    },
    {
      "task_id": "TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH",
      "status": "retained",
      "owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH_integrator.md",
      "branch": "lane/task-governance-wip1-and-proportionate-quick-fix-fast-path",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-wip1-and-proportionate-quick-fix-fast-path",
      "head": "600bbf2d8d6b7884fed6a3af4e46f56cce3fe3a3"
    },
    {
      "task_id": "TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX",
      "status": "retained",
      "owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_integrator.md",
      "branch": "lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix",
      "head": "45f345f49c43eece139245b00048c74e8c83f73b"
    },
    {
      "task_id": "TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY",
      "status": "retained",
      "owner": "permanent Orchestrator governance",
      "disposition": "retain clean integrated lane branch/worktree until separately authorized safe maintenance retirement",
      "evidence": "docs/lane_evidence/TASK_368E_matrix-import-optional-standard-version-fallback-and-copy-clarity_integrator.md",
      "branch": "lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity",
      "head": "c9a61bcb701178c1042d99ca8011d138e0420330"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

## Active Work

- The machine control block is the sole current-status authority. Read its `state` and `active`
  fields before submitting, continuing, reviewing, or closing work.
- This section intentionally contains no dynamic task identity or idle/running claim.

## Queue

- Version-2 queue compatibility fields are inert and have no daily operation entry. Submission
  availability is determined only by the machine control block's `state` and `active` fields.

## Retained History

- Four retained/cancelled lane snapshots remain location-addressable in the machine-control block.
- Task-A remains cancelled. All retained branches, worktrees, and evidence are untouched.
- `TASK_GOVERNANCE_CLASSIC_ROLE_MIGRATION` remains historical planning material only; it is not queued or executable.
- `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING` auxiliary reconciliation/proof resources are retained. After the first subsequent real task completes and the User closes it, report `CLEANUP_READY` and request explicit cleanup authorization.

## Immutable History

- Generation-1 board archive and canonical index remain unchanged under `docs/archive/task_board_history/`.
- Direct generation-1 rollback proof may return `BLOCKED_ROLLBACK_CHAIN` after later legitimate board commits; this is expected protection, not failure.
