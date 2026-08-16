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
    "task_id": "TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN",
    "summary": "Complete the same LTR workbook administrator runtime configuration goal through a corrected production-parser-readable Plan and a fresh normal V2 role/evidence chain while non-destructively reusing the retained clean implementation subject ff01fb1d725c98fb58a3e343cf241076853e8cfa.",
    "kind": "planned",
    "classification": "needs_discovery",
    "phase": "integration",
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
        "frontend/src/api/client.ts",
        "frontend/src/features/settings/SettingsExternalResourcesPanel.tsx",
        "frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx",
        "frontend/src/pages/SettingsPage.test.tsx",
        "frontend/src/pages/SettingsPage.tsx",
        "frontend/src/settings.css",
        "packaging/README_FOR_BROWSER_OPERATOR.md",
        "packaging/README_FOR_OPERATOR.md",
        "scripts/build_windows_browser_release.ps1",
        "scripts/build_windows_desktop_release.ps1",
        "tests/integration/test_ltr_workbook_admin_runtime_config_api.py",
        "tests/unit/test_config.py",
        "tests/unit/test_desktop_packaged_runtime_paths.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tests/unit/test_ltr_workbook_password_settings_service.py",
        "tests/unit/test_packaging_notes.py",
        "tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN.md",
        "docs/task_ltr_workbook_admin_runtime_config_corrected_plan_plan.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_planner.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_developer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_reviewer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_qa.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_integrator.md",
        "docs/task_board.md"
      ],
      "expected_file_count": 33,
      "classification_reason": "Planned/complex authority recovery because the task must bind a corrected committed Plan, safely reuse a retained divergent implementation branch/worktree, freshly validate an API/persistence/administrator-authority and cross-frontend/backend subject, reconstruct exact V2 evidence topology, and integrate only after independent Reviewer, QA, and Integrator gates.",
      "targeted_validation": [
        "Verify the retained registered branch/worktree is clean at ff01fb1d725c98fb58a3e343cf241076853e8cfa with base 4540da65516b4c0fd2a0e7442f05ada8bfc8f917 and exact ancestry.",
        "Verify the retained base-to-subject diff contains exactly the approved 25 product/test paths, passes git diff --check, and has no tracked or untracked drift.",
        "Run the approved backend and packaging pytest matrix; expected retained baseline is 62 passed.",
        "Run the two focused Settings Vitest files; expected retained baseline is 2 files and 4 tests passed.",
        "Run the production frontend build and compile all eight surviving touched Python files.",
        "Verify deleted password UI/client/API/write-service references remain absent, the removed API path remains only in negative tests, connlab.admin.toml is ignored and untracked, and tracked TOML password assignments contain only the blank administrator placeholder.",
        "Run QA browser smoke with disposable state at desktop and 514px, proving Settings loads without password request/UI/console error and existing resource controls remain usable.",
        "Verify no real password, ProgramData file, deployment config, workbook, installed release, public-drive resource, or user data is read, printed, created, changed, copied, or deleted.",
        "Verify fresh corrected-task Planner/Developer/Reviewer/QA/Integrator evidence identity, raw SHA-256, exact route, ordered primary ancestry, and unchanged subject.",
        "At integration, verify exact non-conflicting merge parents/tree, clean states, accepted evidence refs, and absence of forbidden Git or lifecycle operations."
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
    "plan_ref": "docs/task_ltr_workbook_admin_runtime_config_corrected_plan_plan.md@dac9f6c6bfe203e8d4e5b6e57a01645ee8b85dcf#7126c7a948a86dd9676be4550b0d7506648fb257f1fb2c834a3b28a7509a1f55",
    "approval_ref": "我批准 TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN。 Plan ref: docs/task_ltr_workbook_admin_runtime_config_corrected_plan_plan.md@dac9f6c6bfe203e8d4e5b6e57a01645ee8b85dcf#7126c7a948a86dd9676be4550b0d7506648fb257f1fb2c834a3b28a7509a1f55 Approved-request SHA-256: 44508f43b8c604b6c59cf913aa341922fa34919740dc8ea455f5b8e8166d4a30",
    "activation_parent_sha": "ad42ae649b9ebda488ffb75088db2cf04bc5857d",
    "activated_at": "2026-08-15T23:53:15Z",
    "updated_at": "2026-08-16T00:13:49Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-ltr-workbook-admin-runtime-config",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-ltr-workbook-admin-runtime-config",
      "base_sha": "4540da65516b4c0fd2a0e7442f05ada8bfc8f917",
      "head_sha": "ff01fb1d725c98fb58a3e343cf241076853e8cfa",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": "Integrator",
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "edcecab846dd9467263a996ae88931b33e9b033a37119337263ba567dbc91a97",
          "role": "Planner",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_admin_runtime_config_planner",
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-15T23:55:50.6350656Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "6632b406c9f4713a65c004f6eebfcde6e8cb63ff60fbedd227a3285ce2d004ad",
          "role": "Developer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_admin_runtime_config_host/developer",
          "host_id": "/root/ltr_admin_runtime_config_host",
          "status": "started",
          "recorded_at": "2026-08-16T00:16:51.4291354Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "6dbaa2c226d74f7f575a21a52385166f968ea479f4407e8e4ccee9647cec2f89",
          "role": "Reviewer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_admin_runtime_config_planner",
          "host_id": "/root/ltr_admin_runtime_config_host",
          "status": "started",
          "recorded_at": "2026-08-16T00:23:49Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "9447fa264b07b29ed15f809650bba1c2f9524ad7a57d601f0c99e849953d7e71",
          "role": "QA",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_admin_runtime_config_host",
          "host_id": "/root/ltr_admin_runtime_config_host",
          "status": "started",
          "recorded_at": "2026-08-16T00:29:43Z"
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
        "frontend/src/api/client.ts",
        "frontend/src/features/settings/SettingsExternalResourcesPanel.tsx",
        "frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx",
        "frontend/src/pages/SettingsPage.test.tsx",
        "frontend/src/pages/SettingsPage.tsx",
        "frontend/src/settings.css",
        "packaging/README_FOR_BROWSER_OPERATOR.md",
        "packaging/README_FOR_OPERATOR.md",
        "scripts/build_windows_browser_release.ps1",
        "scripts/build_windows_desktop_release.ps1",
        "tests/integration/test_ltr_workbook_admin_runtime_config_api.py",
        "tests/unit/test_config.py",
        "tests/unit/test_desktop_packaged_runtime_paths.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tests/unit/test_ltr_workbook_password_settings_service.py",
        "tests/unit/test_packaging_notes.py",
        "tasks/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN.md",
        "docs/task_ltr_workbook_admin_runtime_config_corrected_plan_plan.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_planner.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_developer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_reviewer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_qa.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_integrator.md",
        "docs/task_board.md"
      ],
      "required_gates": [
        "Reviewer",
        "QA",
        "Integrator"
      ],
      "developer_subject_commit": "ff01fb1d725c98fb58a3e343cf241076853e8cfa",
      "reviewer_subject_commit": "ff01fb1d725c98fb58a3e343cf241076853e8cfa",
      "qa_subject_commit": "ff01fb1d725c98fb58a3e343cf241076853e8cfa",
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_planner.md@dac9f6c6bfe203e8d4e5b6e57a01645ee8b85dcf#3af1bdc08bcb6971e11f34422c9f64839e980f4414ea911b5cef0788d9e78271",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_developer.md@bfe77740bff6866401fcbd0d52c20df281d1513b#f52e044fec29732011c40506d0b9a4806398d1f796d3fff3666ea2428d2a7d42",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_reviewer.md@205b52726d07e800f0e0e4fac961fcd876fc0bf2#d7a14d4684183b7b7d04f273c34170ca367ed1fc3958cd5bf17a329085b12910",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_qa.md@25bdaa83bf4089780256af8b4fa2a556c28e2854#c3a8913d388d97758ea173d8aac1ca1e2253c5f682eb159e744240960defcb07"
      ],
      "blocker_history": [],
      "pending_callback": {
        "state": "dispatch_pending",
        "action_id": "cfb30e9c06fc0b41d76da7d1e0c8023a03f323b249aa16d5a1815f67015c7b44",
        "role": "Integrator",
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
    "task_id": "TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG",
    "disposition": "User terminated the current task after a production callback route-parser mismatch; preserve the clean task branch/worktree at ff01fb1d725c98fb58a3e343cf241076853e8cfa and all committed planning/developer evidence; no cleanup, deletion, push, or integration; resubmit the same goal as a corrected-Plan task.",
    "decision_ref": "保留当前 branch/worktree/evidence，使用 production cancel 终止本次任务，然后重新提交同目标 corrected-Plan 任务。",
    "closed_at": "2026-08-15T23:50:22Z"
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
