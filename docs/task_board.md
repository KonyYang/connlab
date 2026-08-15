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
    "task_id": "TASK_LTR_WORKBOOK_PASSWORD_ADMIN_CONFIG_ONLY",
    "summary": "Remove the LTR workbook password editor and secret-returning/update flow from the Settings UI/API so the effective password is loaded only from the administrator-managed ConnLab local configuration or environment override, preserving the existing packaged %LOCALAPPDATA% configuration contract and workbook behavior.",
    "kind": "planned",
    "classification": "complex",
    "phase": "planning",
    "scope_contract": null,
    "plan_ref": null,
    "approval_ref": null,
    "activation_parent_sha": "521b9ed54dd01a7fab7ccac7e8d662de953c3bd6",
    "activated_at": "2026-08-15T14:04:08Z",
    "updated_at": "2026-08-15T14:04:08Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": null,
      "task_worktree": null,
      "base_sha": "521b9ed54dd01a7fab7ccac7e8d662de953c3bd6",
      "head_sha": "521b9ed54dd01a7fab7ccac7e8d662de953c3bd6",
      "integration_target": "master",
      "worktree_lifecycle": "absent",
      "current_role": "Planner",
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "458e8cb081db716a16adc9550a1514ab5fcfd69f0d1026983781b776b1bd3a49",
          "role": "Planner",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/ltr_password_admin_planner",
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-15T14:07:23.8391181Z"
        }
      ],
      "host_thread_id": null,
      "host_id": null,
      "approved_code_paths": [
        "frontend/src/pages/SettingsPage.tsx",
        "frontend/src/features/settings/SettingsExternalResourcesPanel.tsx",
        "frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx",
        "frontend/src/api/client.ts",
        "backend/api/routes_settings.py",
        "backend/application/ltr_workbook_password_settings_service.py",
        "backend/shared/config.py",
        "tests/unit/test_ltr_workbook_password_settings_service.py",
        "tests/unit/test_config.py",
        "tests/integration/test_settings_admin_config_only.py",
        "tests/unit/test_frontend_shell_files.py",
        "docs/packaging_notes.md",
        "connlab.local.example.toml",
        "tasks/TASK_LTR_WORKBOOK_PASSWORD_ADMIN_CONFIG_ONLY.md",
        "docs/task_ltr_workbook_password_admin_config_only_plan.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PASSWORD_ADMIN_CONFIG_ONLY_planner.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PASSWORD_ADMIN_CONFIG_ONLY_developer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PASSWORD_ADMIN_CONFIG_ONLY_reviewer.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PASSWORD_ADMIN_CONFIG_ONLY_qa.md",
        "docs/lane_evidence/TASK_LTR_WORKBOOK_PASSWORD_ADMIN_CONFIG_ONLY_integrator.md",
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
      "evidence_refs": [],
      "blocker_history": [],
      "pending_callback": {
        "state": "callback_pending",
        "action_id": "458e8cb081db716a16adc9550a1514ab5fcfd69f0d1026983781b776b1bd3a49",
        "role": "Planner",
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
    "task_id": "TASK_PROJECT_REGISTRY_DEFAULT_RECENT_FIRST_SORT",
    "disposition": "closed after human review",
    "decision_ref": "User decision in current message: 关闭 TASK_PROJECT_REGISTRY_DEFAULT_RECENT_FIRST_SORT",
    "closed_at": "2026-08-15T13:03:55Z"
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
