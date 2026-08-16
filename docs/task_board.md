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
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH",
    "summary": "In the ordinary-browser Matrix Editor, list only direct .doc, .docx and .pdf files from the resolved email-attachment or Submitted Material project folder, show a concise source title and filename-only choices, preserve explicit selection, Cancel, Upload other file, empty/error/read-only states and desktop picker behavior, reuse retained clean implementation as the starting point, diagnose the failed source-folder candidate contract, and reject stale in-place same-name replacements without adding endpoints, persistence or path exposure.",
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
        "tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH.md",
        "docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_planner.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_qa.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_integrator.md",
        "docs/task_board.md"
      ],
      "expected_file_count": 20,
      "classification_reason": "Planned/complex because this is a retained cross-backend/frontend API-contract task with a known authoritative backend/API validation failure, a missing stale in-place replacement identity guarantee, a complete frozen build/browser validation matrix, and mandatory independent Reviewer, QA and Integrator gates.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/integration/test_project_test_plan_source_candidates_api.py tests/integration/test_project_test_plan_preview_api.py -q",
        "py -m pytest tests/unit/test_matrix_source_candidate_service.py::test_resolved_directory_listing_and_selection_do_not_mutate_source_file -q",
        "npm.cmd test -- --run src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx (cwd frontend)",
        "npm.cmd run build (cwd frontend)",
        "py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py",
        "git diff --check 900c26a78009264ab0fc06f2c038e50d6d280869..HEAD",
        "verify the base-to-HEAD product diff is exactly the frozen 12 product implementation/test paths",
        "verify retained subject 163e31d455eb4af12e606288fa36d387c81f1476 remains an ancestor, its sole parent is 900c26a78009264ab0fc06f2c038e50d6d280869, the retained branch identity is unchanged, and primary/task worktrees are clean",
        "node scripts/connlab_ui_smoke.mjs --config tmp/matrix-source-picker-ui-smoke.json at desktop 1280x800 and narrow 514x831",
        "verify read-only source bytes/metadata, path-free opaque IDs, no external-file mutation, no new endpoint, database/schema/persistence, attachment copy, recursion, parser/conversion, Matrix authority, desktop bridge, public-drive or governance-runtime change"
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
    "plan_ref": "docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md@4249a74f9c672f070112226a6c37bbc705dc8f1c#bd33c088519c1f4c694469f95e2b2436f12e2e7d6105124a1fc2d374d56d514c",
    "approval_ref": "User approved Plan ref and approved-request SHA-256 in the current conversation.",
    "activation_parent_sha": "1f0cc2c579bcd4ac1b638b53b8e7cb34b0ac6ec0",
    "activated_at": "2026-08-16T13:16:43Z",
    "updated_at": "2026-08-16T14:33:14Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": null,
      "task_worktree": null,
      "base_sha": "1f0cc2c579bcd4ac1b638b53b8e7cb34b0ac6ec0",
      "head_sha": "1f0cc2c579bcd4ac1b638b53b8e7cb34b0ac6ec0",
      "integration_target": "master",
      "worktree_lifecycle": "absent",
      "current_role": null,
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "8c02f7360e455dd03bd695b6185df799e16be8be3f8d319cb7e073333359e879",
          "role": "Planner",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/matrix_source_picker_fresh_planner",
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-16T13:24:46Z"
        }
      ],
      "host_thread_id": null,
      "host_id": null,
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
        "tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH.md",
        "docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_planner.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_qa.md",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_integrator.md",
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
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_planner.md@4249a74f9c672f070112226a6c37bbc705dc8f1c#6edaae2e9dedcc4a421f926392b36dd7d979bd2763bd5ae7e3ca4eb722b57937"
      ],
      "blocker_history": [],
      "pending_callback": null,
      "closeout_disposition": null,
      "retained_resource_refs": [],
      "close_decision_ref": null,
      "timing_facts": {
        "host": null,
        "roles": [
          {
            "role": "Planner",
            "attempt": 1,
            "started_at": "2026-08-16T13:20:01Z",
            "completed_at": null
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
        "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH",
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
            "id": "source-folder-read-only-contract",
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
              "tests/unit/test_matrix_source_candidate_service.py::test_resolved_directory_listing_and_selection_do_not_mutate_source_file",
              "-q"
            ],
            "timeout_seconds": 300,
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
              "--check",
              "900c26a78009264ab0fc06f2c038e50d6d280869..HEAD"
            ],
            "timeout_seconds": 120,
            "permission": "workspace",
            "required": true
          },
          {
            "id": "approved-product-scope",
            "kind": "static",
            "run_for": [
              "Developer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "py",
              "-c",
              "from subprocess import check_output; base='900c26a78009264ab0fc06f2c038e50d6d280869'; expected=['backend/application/project_test_plan_source_candidate_service.py','backend/api/routes_project_test_plan_source_candidates.py','frontend/src/api/client.ts','frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx','frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx','frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts','frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx','frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx','frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx','frontend/src/workbench.css','tests/unit/test_matrix_source_candidate_service.py','tests/integration/test_project_test_plan_source_candidates_api.py']; actual=check_output(['git','diff','--name-only',base+'..HEAD'],text=True,encoding='utf-8').splitlines(); print({'expected':expected,'actual':actual}); raise SystemExit(0 if len(actual)==len(expected) and set(actual)==set(expected) else 1)"
            ],
            "timeout_seconds": 120,
            "permission": "workspace",
            "required": true
          },
          {
            "id": "retained-subject-clean-state",
            "kind": "static",
            "run_for": [
              "Developer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "py",
              "-c",
              "import subprocess; q=lambda *a: subprocess.check_output(['git',*a],text=True,encoding='utf-8').strip(); start='163e31d455eb4af12e606288fa36d387c81f1476'; base='900c26a78009264ab0fc06f2c038e50d6d280869'; branch=q('branch','--show-current'); parent_line=q('rev-list','--parents','-n','1',start); head=q('rev-parse','HEAD'); task_clean=not q('status','--porcelain=v1','--untracked-files=all'); primary='D:/PythonProject/connlab'; primary_clean=not subprocess.check_output(['git','-C',primary,'status','--porcelain=v1','--untracked-files=all'],text=True,encoding='utf-8').strip(); ancestor=subprocess.run(['git','merge-base','--is-ancestor',start,'HEAD'],check=False).returncode==0; print({'branch':branch,'head':head,'parent_line':parent_line,'ancestor':ancestor,'task_clean':task_clean,'primary_clean':primary_clean}); raise SystemExit(0 if branch=='codex/task-matrix-import-source-picker-target-folder-file-list' and parent_line==start+' '+base and ancestor and task_clean and primary_clean else 1)"
            ],
            "timeout_seconds": 120,
            "permission": "workspace",
            "required": true
          },
          {
            "id": "matrix-source-picker-browser-smoke",
            "kind": "ui",
            "run_for": [
              "Developer",
              "Reviewer",
              "QA"
            ],
            "cwd": ".",
            "argv": [
              "node",
              "scripts/connlab_ui_smoke.mjs",
              "--config",
              "tmp/matrix-source-picker-ui-smoke.json"
            ],
            "timeout_seconds": 180,
            "permission": "browser",
            "required": true
          }
        ]
      }
    }
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN",
    "disposition": "Cancelled at User direction; retained clean subject 163e31d455eb4af12e606288fa36d387c81f1476, task branch/worktree, Task/Plan/Planner evidence, Developer evidence, governance recovery planning bundle and all history; no cleanup or push; fresh same-goal product task will be submitted with a complete initial validation manifest.",
    "decision_ref": "User rejected adding scripts/connlab_personal_task.py and explicitly authorized production cancel with all retained resources preserved on 2026-08-16.",
    "closed_at": "2026-08-16T13:14:27Z"
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
