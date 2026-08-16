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
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN",
    "summary": "Simplify the Matrix Import source chooser to list only selectable .doc, .docx, and .pdf files from the resolved intake-attachment or Submitted Material target folder; show only a concise source-location title and filenames, retain Cancel and Upload other file with standard ConnLab button styling, preserve explicit selection, empty/error states, read-only blocking, desktop behavior, and existing preview authority.",
    "kind": "planned",
    "classification": "complex",
    "phase": "development",
    "scope_contract": {
      "may_touch": [
        "backend/application/project_test_plan_source_candidate_service.py",
        "backend/api/routes_project_test_plan_source_candidates.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/workbench.css",
        "tests/unit/test_matrix_source_candidate_service.py",
        "tests/integration/test_project_test_plan_source_candidates_api.py",
        "tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN.md",
        "docs/task_matrix_import_source_picker_target_folder_file_list_corrected_plan_plan.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_planner.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_developer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_reviewer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_qa.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_integrator.md",
        "docs/task_board.md"
      ],
      "expected_file_count": 20,
      "classification_reason": "Planned/complex because the product change extends the existing project source-candidate API contract while preserving its registered-asset default, crosses backend and frontend, and requires independent review, QA, integration, build and browser verification.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/integration/test_project_test_plan_source_candidates_api.py tests/integration/test_project_test_plan_preview_api.py -q",
        "npm.cmd test -- --run src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx (cwd frontend)",
        "npm.cmd run build (cwd frontend)",
        "py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py",
        "git diff --check",
        "deterministic browser smoke at desktop and 514px for source title, filename-only allowed rows, absent legacy metadata, standard buttons, explicit selection, upload fallback, empty/error, cancel zero mutation, read-only zero calls and unchanged desktop picker",
        "verify exact approved scope, opaque candidate identity, containment, stale/foreign rejection, clean worktrees and no database, persistence, parser, Matrix authority, public-drive, attachment-copy or external-file mutation"
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
    "plan_ref": "docs/task_matrix_import_source_picker_target_folder_file_list_corrected_plan_plan.md@e764e3d913fd83b0e284b67cf31c636113afbcb4#6da61c1eaf90df53537743a1c7fdfbcd556e9299fd531dd29186a448b61c1065",
    "approval_ref": "User explicitly approved the corrected Plan ref and approved-request SHA-256 in the current conversation on 2026-08-16.",
    "activation_parent_sha": "fd228ae0f69be6584c981c3cfe00668865f2004d",
    "activated_at": "2026-08-16T09:41:31Z",
    "updated_at": "2026-08-16T10:22:37Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-matrix-import-source-picker-target-folder-file-list",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-matrix-import-source-picker-target-folder-file-list",
      "base_sha": "900c26a78009264ab0fc06f2c038e50d6d280869",
      "head_sha": "163e31d455eb4af12e606288fa36d387c81f1476",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": null,
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "3e26244f4519e2823e1b716c8e7386defbb7a8ca73a4faf0cb28d03152a6f750",
          "role": "Planner",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/matrix_source_picker_corrected_planner",
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-16T09:43:24Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "6ec15414fc8b96dda1e5481ebc1eaeaaf7b517f030f6ef37145bae8a51ef18ba",
          "role": "Developer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/matrix_source_picker_host/corrected_developer",
          "host_id": "/root/matrix_source_picker_host",
          "status": "started",
          "recorded_at": "2026-08-16T10:02:45Z"
        }
      ],
      "host_thread_id": "/root/matrix_source_picker_host",
      "host_id": "/root/matrix_source_picker_host",
      "approved_code_paths": [
        "backend/application/project_test_plan_source_candidate_service.py",
        "backend/api/routes_project_test_plan_source_candidates.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/workbench.css",
        "tests/unit/test_matrix_source_candidate_service.py",
        "tests/integration/test_project_test_plan_source_candidates_api.py",
        "tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN.md",
        "docs/task_matrix_import_source_picker_target_folder_file_list_corrected_plan_plan.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_planner.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_developer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_reviewer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_qa.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_integrator.md",
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
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_planner.md@e764e3d913fd83b0e284b67cf31c636113afbcb4#9dc10b25932cc6ceda1fbc6d77dd24abcdd19fc9b8f2e78a4a5ee6328d021dc1",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_developer.md@c900c7209b179dda1129c2a75fb7e0241a89a338#68c007bd57968c06bb97ceb2a72c13702333ae2cd8bc85148adb2221a91c2756"
      ],
      "blocker_history": [],
      "pending_callback": null,
      "closeout_disposition": null,
      "retained_resource_refs": [],
      "close_decision_ref": null,
      "timing_facts": {
        "host": {
          "started_at": "2026-08-16T09:59:05Z",
          "completed_at": "2026-08-16T10:00:19Z"
        },
        "roles": [
          {
            "role": "Planner",
            "attempt": 1,
            "started_at": "2026-08-16T09:42:24Z",
            "completed_at": null
          },
          {
            "role": "Developer",
            "attempt": 1,
            "started_at": "2026-08-16T10:01:10Z",
            "completed_at": "2026-08-16T18:08:17+08:00"
          }
        ],
        "integration_completed_at": null
      },
      "execution_routes": {
        "Developer": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:api_contract"
        },
        "Integrator": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:api_contract"
        },
        "QA": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:api_contract"
        },
        "Reviewer": {
          "model": "gpt-5.6-sol",
          "reasoning_effort": "medium",
          "reason": "risk:api_contract"
        }
      },
      "validation_manifest": {
        "schema": "connlab.validation-manifest",
        "version": 1,
        "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN",
        "checks": [
          {
            "id": "source-folder-candidate-contract",
            "kind": "targeted",
            "run_for": [
              "Developer",
              "Reviewer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "py",
              "-m",
              "pytest",
              "tests/unit/test_matrix_source_candidate_service.py",
              "tests/integration/test_project_test_plan_source_candidates_api.py",
              "tests/integration/test_project_test_plan_preview_api.py",
              "-q"
            ],
            "timeout_seconds": 900,
            "permission": "pytest_temp",
            "required": true
          },
          {
            "id": "matrix-source-picker-ui",
            "kind": "targeted",
            "run_for": [
              "Developer",
              "Reviewer",
              "QA"
            ],
            "cwd": "frontend",
            "argv": [
              "npm.cmd",
              "test",
              "--",
              "--run",
              "src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
              "src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
              "src/features/matrix-editor/MatrixEditorWorkspace.test.tsx"
            ],
            "timeout_seconds": 900,
            "permission": "workspace",
            "required": true
          },
          {
            "id": "frontend-production-build",
            "kind": "full",
            "run_for": [
              "Developer",
              "QA"
            ],
            "cwd": "frontend",
            "argv": [
              "npm.cmd",
              "run",
              "build"
            ],
            "timeout_seconds": 900,
            "permission": "workspace",
            "required": true
          },
          {
            "id": "source-candidate-compile",
            "kind": "static",
            "run_for": [
              "Developer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "py",
              "-m",
              "py_compile",
              "backend/application/project_test_plan_source_candidate_service.py",
              "backend/api/routes_project_test_plan_source_candidates.py"
            ],
            "timeout_seconds": 120,
            "permission": "workspace",
            "required": true
          },
          {
            "id": "scope-diff-check",
            "kind": "static",
            "run_for": [
              "Developer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "git",
              "diff",
              "--check"
            ],
            "timeout_seconds": 120,
            "permission": "workspace",
            "required": true
          }
        ]
      }
    }
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST",
    "disposition": "Cancelled only to replace the frozen Windows validation argv npm with npm.cmd; retain clean implementation subject 163e31d455eb4af12e606288fa36d387c81f1476, task branch/worktree, host and committed evidence; no cleanup or implementation rejection.",
    "decision_ref": "User authorized production cancel with retained subject/branch/worktree/evidence and resubmission as a corrected-Plan task on 2026-08-16.",
    "closed_at": "2026-08-16T09:40:14Z"
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
