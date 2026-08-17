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
    "phase": "review",
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
    "approval_ref": "User explicitly approved the exact committed Plan, canonical approved-request SHA-256 addc7e5e16a2135702dc84a4c6ee40a1705aa9b36ac1e6696b310125df75f075, validation manifest SHA-256 65f31359d60a0868bef3646b17ffee2a09a53a87b193afd196118126c4a63316, and Planner evidence in the current conversation.",
    "activation_parent_sha": "5c4af0aec50346c940cb486ea2faf975c2838277",
    "activated_at": "2026-08-17T04:42:06Z",
    "updated_at": "2026-08-17T10:22:39Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-matrix-import-source-picker-target-folder-file-list",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-matrix-import-source-picker-target-folder-file-list",
      "base_sha": "900c26a78009264ab0fc06f2c038e50d6d280869",
      "head_sha": "1798d0377347459a78478b9a10e3c2f2a23327e4",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": null,
      "current_attempt": 2,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "cde5e45db502422cbb8f514ef034d3bd1b82d5fb25162cf9a683424cfebb531a",
          "role": "Planner",
          "attempt": 1,
          "thread_id": "/root/matrix_source_picker_reactivation_planner",
          "agent_id": null,
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-17T04:43:27Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "55e6765fe4c91789bb00be68590584eafe18577ce8916283f6746c015683087e",
          "role": "Developer",
          "attempt": 1,
          "thread_id": "/root/matrix_source_picker_fresh_host/developer_reactivation",
          "agent_id": null,
          "host_id": "/root/matrix_source_picker_fresh_host",
          "status": "started",
          "recorded_at": "2026-08-17T05:09:48Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "b78591dd5b391b44079ed32bc4d1515d75f1259647a44b9da92a2faa46be9d86",
          "role": "Reviewer",
          "attempt": 1,
          "thread_id": "/root/matrix_source_picker_fresh_host/reviewer",
          "agent_id": null,
          "host_id": "/root/matrix_source_picker_fresh_host",
          "status": "started",
          "recorded_at": "2026-08-17T10:06:18Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "ca3559014c1c6d37b9df83c3e9131488ecb813cc1d0f8c8845cd3659c5e50a7f",
          "role": "Developer",
          "attempt": 2,
          "thread_id": "/root/matrix_source_picker_fresh_host/developer_attempt2",
          "agent_id": null,
          "host_id": "/root/matrix_source_picker_fresh_host",
          "status": "started",
          "recorded_at": "2026-08-17T10:24:34Z"
        }
      ],
      "host_thread_id": "/root/matrix_source_picker_fresh_host",
      "host_id": "/root/matrix_source_picker_fresh_host",
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
      "developer_subject_commit": "9f5fda4dbae711eb4e0800b35b8bb90cfc5a96d2",
      "reviewer_subject_commit": null,
      "qa_subject_commit": null,
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_planner.md@12d5a28c723eaf1b1afe7f65769aa673c7353ed4#0e18ca744ea11cce2ec2d7b8e1575802a6ae1c20fee810fb369d5d40a7272eef",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md@28b3ab84511747546088f27add07c37d175aded5#593b1c838af2b9564cdc1a2fe5d8adbe646d6f05f3c4a814daf1898710478e0f",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md@5171bdb172dca3e56ae89629283f64967dd148a9#b131e72d3ac3db8e684fb47dfe7257ec64884ca6f3a2591f8df8715d4ad6d093",
        "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md@39c78e01698a232c0e022e8e10240c572462d5fc#4ba664789aad0776fc52bd1a8ba369d8c1eec08e00da5e783e8fde142b9560b9"
      ],
      "blocker_history": [
        {
          "blocker": {
            "schema": "connlab.serial-task-blocker",
            "version": 1,
            "code": "REVIEWER_BLOCKED",
            "stage": "review",
            "reason": "Ordinary-browser candidate loading and request-busy states are unreachable while the source-candidate GET is pending, allowing overlapping Import Matrix requests.",
            "dirty_paths": [],
            "failed_validation": null,
            "subject_commit": "1798d0377347459a78478b9a10e3c2f2a23327e4",
            "evidence_ref": "docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md@5171bdb172dca3e56ae89629283f64967dd148a9#b131e72d3ac3db8e684fb47dfe7257ec64884ca6f3a2591f8df8715d4ad6d093",
            "native_action_id": null,
            "related_ids": [
              "MATRIX_SOURCE_PICKER_LOADING_BUSY"
            ],
            "retryable": true,
            "requires_user": false,
            "resume_phase": "development",
            "recorded_at": "2026-08-17T10:19:57Z"
          },
          "decision_ref": "User explicitly approved the exact committed Plan, canonical approved-request SHA-256 addc7e5e16a2135702dc84a4c6ee40a1705aa9b36ac1e6696b310125df75f075, validation manifest SHA-256 65f31359d60a0868bef3646b17ffee2a09a53a87b193afd196118126c4a63316, and Planner evidence in the current conversation.",
          "resolution": "bounded_fix",
          "resolved_at": "2026-08-17T10:22:39Z"
        }
      ],
      "pending_callback": null,
      "closeout_disposition": null,
      "retained_resource_refs": [],
      "close_decision_ref": null,
      "timing_facts": {
        "host": {
          "started_at": "2026-08-17T05:04:17Z",
          "completed_at": "2026-08-17T05:07:41Z"
        },
        "roles": [
          {
            "role": "Planner",
            "attempt": 1,
            "started_at": "2026-08-17T04:42:53Z",
            "completed_at": null
          },
          {
            "role": "Developer",
            "attempt": 1,
            "started_at": "2026-08-17T05:08:34Z",
            "completed_at": "2026-08-17T18:00:09+08:00"
          },
          {
            "role": "Reviewer",
            "attempt": 1,
            "started_at": "2026-08-17T10:03:53Z",
            "completed_at": "2026-08-17T18:18:50+08:00"
          },
          {
            "role": "Developer",
            "attempt": 2,
            "started_at": "2026-08-17T10:22:23Z",
            "completed_at": "2026-08-17T18:38:26+08:00"
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
    "task_id": "TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION",
    "disposition": "planning artifacts retained; task cancelled so the independently authorized out-of-band emergency governance writer repair can run outside the damaged Personal Serial role chain.",
    "decision_ref": "User decision in current conversation: do not approve the current Plan and production cancel TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION while retaining all planning and product resources.",
    "closed_at": "2026-08-16T23:56:04Z"
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
