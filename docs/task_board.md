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
    "task_id": "TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY",
    "summary": "Make Matrix Editor Import Matrix open at the project Submitted Material folder after project-folder creation, otherwise at the stored intake-attachment directory, with safe desktop and browser fallback behavior.",
    "kind": "planned",
    "classification": "complex",
    "phase": "development",
    "scope_contract": {
      "may_touch": [
        "backend/application/project_test_plan_source_candidate_service.py",
        "backend/api/routes_project_test_plan_source_candidates.py",
        "backend/api/dependencies.py",
        "backend/desktop/path_picker_api.py",
        "backend/desktop/shell.py",
        "frontend/src/api/client.ts",
        "frontend/src/desktop/pathPickerBridge.ts",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
        "tests/unit/test_matrix_source_candidate_service.py",
        "tests/integration/test_project_test_plan_source_candidates_api.py",
        "tests/unit/test_desktop_path_picker_api.py",
        "tests/unit/test_frontend_shell_files.py",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
        "docs/task_board.md"
      ],
      "expected_file_count": 16,
      "classification_reason": "Complex cross-frontend/backend desktop UX change with an existing API response extension and mandatory independent Reviewer, QA, and Integrator gates; no database, schema, persistence, Matrix authority, public-drive, or business-rule change.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/unit/test_desktop_path_picker_api.py tests/unit/test_frontend_shell_files.py -q",
        "py -m pytest tests/integration/test_project_test_plan_source_candidates_api.py -q",
        "npm test -- --run frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "npm run build",
        "py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py backend/desktop/path_picker_api.py backend/desktop/shell.py",
        "git diff --check",
        "desktop smoke: project without workspace opens at stored attachment directory; project with workspace opens at Submitted Material; browser-only fallback remains usable"
      ],
      "forbidden_categories": {
        "api_contract": true,
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
    "plan_ref": "docs/task_matrix_import_default_source_directory_plan.md@63e3036815e4273f0d76086accab67d320bcff8e#415869f59a108ecf5365a564aa11f809478a55dff0e1bad666d3d2f29248d49e",
    "approval_ref": "User approved the above exact Plan ref and approved-request SHA-256 in this conversation on 2026-08-13.",
    "activation_parent_sha": "57a735199927387e0978a92165fd858fce435972",
    "activated_at": "2026-08-13T12:35:47Z",
    "updated_at": "2026-08-13T12:56:39Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": null,
      "task_worktree": null,
      "base_sha": "57a735199927387e0978a92165fd858fce435972",
      "head_sha": "57a735199927387e0978a92165fd858fce435972",
      "integration_target": "master",
      "worktree_lifecycle": "absent",
      "current_role": null,
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "52ed7cfd1c6a00acd853e4ee75534c147b28f7e3920980d6e223c1480b5b2098",
          "role": "Planner",
          "attempt": 1,
          "thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
          "agent_id": null,
          "host_id": null,
          "status": "completed",
          "recorded_at": "2026-08-13T12:42:04Z"
        }
      ],
      "host_thread_id": null,
      "host_id": null,
      "approved_code_paths": [
        "backend/application/project_test_plan_source_candidate_service.py",
        "backend/api/routes_project_test_plan_source_candidates.py",
        "backend/api/dependencies.py",
        "backend/desktop/path_picker_api.py",
        "backend/desktop/shell.py",
        "frontend/src/api/client.ts",
        "frontend/src/desktop/pathPickerBridge.ts",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
        "tests/unit/test_matrix_source_candidate_service.py",
        "tests/integration/test_project_test_plan_source_candidates_api.py",
        "tests/unit/test_desktop_path_picker_api.py",
        "tests/unit/test_frontend_shell_files.py",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
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
        "docs/lane_evidence/TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY_planner.md@63e3036815e4273f0d76086accab67d320bcff8e#4d3c85b15d52762e6f16efb92cae147ef95b5ade88a267b555a4a9952796864e"
      ],
      "pending_callback": null,
      "closeout_disposition": null,
      "retained_resource_refs": [],
      "close_decision_ref": null
    }
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_NEW_PROJECT_APPLY_LTR_BACKEND_BLOCKER_NOTICE",
    "disposition": "closed after human review",
    "decision_ref": "User confirmed the pywin32 configuration issue is resolved and explicitly requested close.",
    "closed_at": "2026-08-13T12:22:06Z"
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
