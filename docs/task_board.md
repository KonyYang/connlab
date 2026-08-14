# ConnLab Task Board

> Status: Personal serial workflow v2 is active; no task is currently active.
> Last Updated: 2026-08-07
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: `none`
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
    "task_id": "TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER",
    "summary": "In browser Matrix Editor, show current project intake source candidates before file upload, preview only after explicit selection, preserve Upload other file, desktop picker, empty state, cancel and read-only behavior.",
    "kind": "planned",
    "classification": "complex",
    "phase": "qa",
    "scope_contract": {
      "may_touch": [
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/workbench.css",
        "docs/task_board.md"
      ],
      "expected_file_count": 8,
      "classification_reason": "Bounded browser Matrix source-selection UI using existing candidate list and preview APIs, with independent review and QA; no backend, API, database, schema, persistence, parser, attachment-storage, Matrix-authority, public-drive, or business-rule change.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_matrix_source_candidate_service.py -q",
        "npm test -- --run frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "npm run build",
        "git diff --check",
        "deterministic browser smoke: API-ranked candidate list and recommendation; explicit candidate preview; upload fallback; empty/error state; cancel zero mutation; read-only zero calls; desktop native picker unchanged"
      ],
      "forbidden_categories": {
        "api_contract": false,
        "database": false,
        "schema_or_migration": false,
        "persistence": false,
        "authority": false,
        "public_drive_workflow": false,
        "business_rule_semantics": false,
        "destructive_action": false,
        "external_mutation": false
      }
    },
    "plan_ref": "docs/task_matrix_import_browser_project_source_picker_plan.md@74eb8850c332afebad37536fdf1e60624613e202#e3192530a4ee0e5c1aac20b57213a09a778ec720e0b29039b3e5be48de7ecc80",
    "approval_ref": "User approved the exact committed Plan and approved-request in this task on 2026-08-14.",
    "activation_parent_sha": "c87fa35bcb9336aa6dda8e40520f08f2624b0729",
    "activated_at": "2026-08-13T23:45:39Z",
    "updated_at": "2026-08-13T23:58:40Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-matrix-import-browser-project-source-picker",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-matrix-import-browser-project-source-picker",
      "base_sha": "d767547084fce64e4d4373818c3131cbde574d29",
      "head_sha": "d767547084fce64e4d4373818c3131cbde574d29",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": "QA",
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "5960a14479c4f0e8d6dc63de4d4644319438c16cefec01cd5f6f7f18ac6cf633",
          "role": "Planner",
          "attempt": 1,
          "thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
          "agent_id": null,
          "host_id": null,
          "status": "completed",
          "recorded_at": "2026-08-13T23:47:17.757282Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "0934ab0dc57fdec600ee8f4782df21c9cadfa87e5917fe7b66fda45bce3a8375",
          "role": "Developer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/browser_source_picker_developer",
          "host_id": "host-task-matrix-import-browser-project-source-picker",
          "status": "started",
          "recorded_at": "2026-08-14T00:02:13.877397Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "962042cf69836ff7172ec8a44fc0baf4007575dc5500dc8f9407c6591d90dc32",
          "role": "Reviewer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/browser_source_picker_reviewer",
          "host_id": "host-task-matrix-import-browser-project-source-picker",
          "status": "started",
          "recorded_at": "2026-08-14T04:42:02.799113Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "a1e73c2fcc90ff575edc0432e75a813c3f01045bcdffeb270415444938fdcd44",
          "role": "QA",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/browser_source_picker_qa",
          "host_id": "host-task-matrix-import-browser-project-source-picker",
          "status": "started",
          "recorded_at": "2026-08-14T04:50:34.180014Z"
        }
      ],
      "host_thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
      "host_id": "host-task-matrix-import-browser-project-source-picker",
      "approved_code_paths": [
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/workbench.css",
        "docs/task_board.md"
      ],
      "required_gates": [
        "Reviewer",
        "QA",
        "Integrator"
      ],
      "developer_subject_commit": "05be2d9ad8ebab387f1c8414805a55f14ac9cff8",
      "reviewer_subject_commit": "05be2d9ad8ebab387f1c8414805a55f14ac9cff8",
      "qa_subject_commit": null,
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER_planner.md@74eb8850c332afebad37536fdf1e60624613e202#e33e19803414adb65502794005404032e60c2741880afe73160a50c665fbd247",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER_developer.md@ba76dd8d9c5e66e60ad8d269f665dbd447c625ec#e66d9d71565ae3a0e89206eef242101c3ecf38e0c74afa3c62ea7c875d13bf7d",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER_reviewer.md@42d620bd0575a6d9ca47504eb26d283befb442d7#31b612f984ea8c8aab7bc8822c5332cc4dac29a94441ae5131731c06c4b449e7"
      ],
      "pending_callback": {
        "state": "callback_pending",
        "action_id": "a1e73c2fcc90ff575edc0432e75a813c3f01045bcdffeb270415444938fdcd44",
        "role": "QA",
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
    "task_id": "TASK_GOVERNANCE_ATOMIC_COMPLEX_CLOSE",
    "disposition": "closed after human review",
    "decision_ref": "User decision in current thread: 关闭",
    "closed_at": "2026-08-13T23:43:21Z"
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

- No active task.
- `TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION` was atomically closed by the cutover that
  activated the version-2 personal serial workflow and released the active slot.
- The prior lifecycle-probe evidence and all retained resources remain unchanged and
  location-addressable; they do not occupy WIP.

## Queue

- Idle; ready to accept a newly submitted task. Version-2 queue compatibility fields are inert and empty.

## Retained History

- Four retained/cancelled lane snapshots remain location-addressable in the machine-control block.
- Task-A remains cancelled. All retained branches, worktrees, and evidence are untouched.
- `TASK_GOVERNANCE_CLASSIC_ROLE_MIGRATION` remains historical planning material only; it is not queued or executable.
- `TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING` auxiliary reconciliation/proof resources are retained. After the first subsequent real task completes and the User closes it, report `CLEANUP_READY` and request explicit cleanup authorization.

## Immutable History

- Generation-1 board archive and canonical index remain unchanged under `docs/archive/task_board_history/`.
- Direct generation-1 rollback proof may return `BLOCKED_ROLLBACK_CHAIN` after later legitimate board commits; this is expected protection, not failure.
