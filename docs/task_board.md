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
  "state": "implemented_pending_human_review",
  "active": {
    "task_id": "TASK_PROJECT_BASIC_INFORMATION_INITIAL_SAMPLE_DEPOSITION_DEFAULT",
    "summary": "Populate empty Sample deposition from Post-Testing Sample Disposition on first Basic Information load while preserving manual Sample deposition overrides and existing explicit LTR preview/commit behavior.",
    "kind": "simple",
    "classification": "simple",
    "phase": "human_review",
    "scope_contract": {
      "schema": "connlab.serial-task-request",
      "version": 1,
      "task_id": "TASK_PROJECT_BASIC_INFORMATION_INITIAL_SAMPLE_DEPOSITION_DEFAULT",
      "summary": "Populate empty Sample deposition from Post-Testing Sample Disposition on first Basic Information load while preserving manual Sample deposition overrides and existing explicit LTR preview/commit behavior.",
      "root_cause_clear": true,
      "expected_result_clear": true,
      "may_touch": [
        "frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts",
        "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
        "docs/task_board.md"
      ],
      "targeted_validation": [
        "npm test -- --run frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
        "npm run build",
        "browser smoke: initial Basic Information load mirrors empty Sample deposition without manual select interaction",
        "git diff --check"
      ],
      "requires_independent_review": false,
      "forbidden_categories": {
        "api_contract": false,
        "database": false,
        "schema_or_migration": false,
        "persistence": false,
        "authority": false,
        "public_drive_workflow": false,
        "business_rule_semantics": false,
        "destructive_action": false,
        "external_mutation": false,
        "push_or_release": false
      }
    },
    "plan_ref": null,
    "approval_ref": null,
    "activation_parent_sha": "fab0d86bd9f37de918899f8e107bdab5ed1e0213",
    "activated_at": "2026-08-13T11:24:42Z",
    "updated_at": "2026-08-13T11:28:16Z",
    "blocker": null,
    "validation": {
      "schema": "connlab.personal-task-validation",
      "version": 1,
      "status": "passed",
      "checks": [
        {
          "command": "npm test -- --run src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
          "exit_code": 0,
          "summary": "20 passed"
        },
        {
          "command": "npm run build",
          "exit_code": 0,
          "summary": "TypeScript and Vite production build passed"
        },
        {
          "command": "git diff --check",
          "exit_code": 0,
          "summary": "passed"
        }
      ],
      "observed_paths": [],
      "manual_checks": [
        "Fresh browser reload without field interaction: API post_testing_disposition=Send Back to Requestor and sample_deposition=null; UI rendered Sample deposition=Send Back to Requestor on initial load.",
        "No product-code change: current source and existing regression already implement the requested initial-load default."
      ],
      "recorded_at": "2026-08-13T11:28:15.9489699Z"
    },
    "complex_context": null
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_MATRIX_EDITOR_REMOVE_REFERENCE_LIBRARY_PLACEHOLDER",
    "disposition": "closed after human review",
    "decision_ref": "User explicitly closed TASK_MATRIX_EDITOR_REMOVE_REFERENCE_LIBRARY_PLACEHOLDER after inspecting the Matrix Editor placeholder removal; implementation and validation accepted; no push or cleanup.",
    "closed_at": "2026-08-13T11:07:47Z"
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
