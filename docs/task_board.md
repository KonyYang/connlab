# ConnLab Task Board

> Status: Personal serial workflow migration is approved and active.
> Last Updated: 2026-08-06
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: `TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION`
> Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
> Execution Rule: One active task, durable FIFO queue, direct primary-worktree implementation, local commits only.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.personal-serial-control",
  "version": 1,
  "mode": "personal_serial",
  "wip_limit": 1,
  "state": "implemented_pending_human_review",
  "active": {
    "task_id": "TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION",
    "summary": "Simplify ConnLab task execution to personal single-active FIFO mode.",
    "kind": "planned",
    "phase": "human_review",
    "scope_contract": {
      "may_touch": [
        "AGENTS.md",
        "docs/task_board.md",
        "docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md",
        "docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md",
        "docs/project_management/TASK_EXECUTION_SKILL.md",
        "docs/project_management/TASK_REVIEW_CHECKLIST.md",
        "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
        "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
        "docs/project_management/ROLE_THREAD_REGISTRY.md",
        "docs/project_management/PARALLEL_EXECUTION_MODEL.md",
        "docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        ".agents/skills/connlab-planner/SKILL.md",
        "scripts/connlab_personal_task.py",
        "scripts/run_task.ps1",
        "scripts/connlab_execution_gate.ps1",
        "tests/unit/test_connlab_personal_serial_workflow.py",
        "tests/unit/test_connlab_execution_gate_script.py",
        "tests/integration/test_connlab_execution_gate_recovery.py",
        "tests/unit/test_execution_wip_and_quick_fix_governance.py",
        "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
        "tests/unit/test_connlab_lane_worktree_script.py",
        "tests/unit/test_connlab_active_context_governance.py",
        "tasks/TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION.md",
        "docs/task_governance_personal_serial_workflow_simplification_plan.md",
        "scripts/connlab_active_context.py"
      ],
      "expected_file_count": 26,
      "classification_reason": "User-approved narrow scope correction for read-only personal-schema inspect compatibility; archive, maintenance, rollback, and mixed-EOL behavior remain frozen.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q",
        "py -m pytest tests/unit/test_connlab_execution_gate_script.py -q",
        "py -m pytest tests/integration/test_connlab_execution_gate_recovery.py -q",
        "py -m pytest tests/unit/test_execution_wip_and_quick_fix_governance.py -q",
        "py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q",
        "py -m pytest tests/unit/test_connlab_lane_worktree_script.py -q",
        "py -m pytest tests/unit/test_connlab_active_context_governance.py -q",
        "py -m pytest tests/unit/test_connlab_active_context.py -q",
        "PowerShell parser checks for scripts/connlab_execution_gate.ps1 and scripts/run_task.ps1",
        "py scripts/connlab_active_context.py inspect --repo-root D:/PythonProject/connlab",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/connlab_execution_gate.ps1 -Intent Inspect -RepositoryRoot D:/PythonProject/connlab -Json",
        "git diff --check",
        "git status --short"
      ],
      "forbidden_categories": {
        "api_contract": false,
        "database": false,
        "schema_or_migration": true,
        "persistence": true,
        "authority": true,
        "public_drive_workflow": false,
        "business_rule_semantics": false,
        "destructive_action": false,
        "external_mutation": false
      }
    },
    "plan_ref": "docs/task_governance_personal_serial_workflow_simplification_plan.md@b66b5eee4610f38d2a81b3fe4b7dbf795b44380a#16a8571d34f0a51be81d9e657bad78e28a63643fdf9202ddd9d30f2a29ea37dd",
    "approval_ref": "User explicitly approved adding scripts/connlab_active_context.py for read-only inspect compatibility in the current side conversation on 2026-08-06.",
    "activation_parent_sha": "a796d574bf6747ee091adbf4881aa8cb623a7a36",
    "activated_at": "2026-08-06T01:14:27+08:00",
    "updated_at": "2026-08-05T23:09:40Z",
    "blocker": null,
    "validation": {
      "schema": "connlab.personal-task-validation",
      "version": 1,
      "status": "passed",
      "checks": [
        {
          "command": "py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_execution_gate_script.py tests/integration/test_connlab_execution_gate_recovery.py tests/unit/test_execution_wip_and_quick_fix_governance.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py tests/unit/test_connlab_active_context_governance.py tests/unit/test_connlab_active_context.py -q",
          "exit_code": 0,
          "summary": "56 passed in 67.39s"
        },
        {
          "command": "PowerShell parser checks for scripts/connlab_execution_gate.ps1 and scripts/run_task.ps1",
          "exit_code": 0,
          "summary": "Both scripts parsed with zero errors."
        },
        {
          "command": "py scripts/connlab_active_context.py inspect --repo-root . --json",
          "exit_code": 0,
          "summary": "ALLOW_INSPECT for connlab.personal-serial-control."
        },
        {
          "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/connlab_execution_gate.ps1 -Intent Inspect -RepositoryRoot D:/PythonProject/connlab -Json",
          "exit_code": 0,
          "summary": "ALLOW_INSPECT through the personal gate adapter."
        },
        {
          "command": "git diff --check",
          "exit_code": 0,
          "summary": "No whitespace errors."
        }
      ],
      "observed_paths": [
        "AGENTS.md",
        "docs/task_board.md",
        "docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md",
        "docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md",
        "docs/project_management/TASK_EXECUTION_SKILL.md",
        "docs/project_management/TASK_REVIEW_CHECKLIST.md",
        "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
        "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
        "docs/project_management/ROLE_THREAD_REGISTRY.md",
        "docs/project_management/PARALLEL_EXECUTION_MODEL.md",
        "docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        ".agents/skills/connlab-planner/SKILL.md",
        "scripts/connlab_personal_task.py",
        "scripts/run_task.ps1",
        "scripts/connlab_execution_gate.ps1",
        "tests/unit/test_connlab_personal_serial_workflow.py",
        "tests/unit/test_connlab_execution_gate_script.py",
        "tests/integration/test_connlab_execution_gate_recovery.py",
        "tests/unit/test_execution_wip_and_quick_fix_governance.py",
        "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
        "tests/unit/test_connlab_lane_worktree_script.py",
        "tests/unit/test_connlab_active_context_governance.py",
        "tasks/TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION.md",
        "docs/task_governance_personal_serial_workflow_simplification_plan.md",
        "scripts/connlab_active_context.py"
      ],
      "manual_checks": [
        "Observed paths equal all 26 approved paths with no outside or missing path.",
        "Generation-1 archive remains 798128 bytes with the frozen SHA-256 and Git blob.",
        "Canonical index remains 6787 bytes with the frozen SHA-256 and Git blob.",
        "Task-A lane remains clean at 85e71dfa212c57c26527fad42eaf00a83b19c935.",
        "External governance-migration repository remains clean and was not modified."
      ],
      "recorded_at": "2026-08-05T23:09:40Z"
    }
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": null,
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

- `TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION`: approved and active in implementation.
- Work is limited to the exact allowlist stored in the machine-control block.
- No role dispatch, lane/worktree creation, Task-A restoration, push, or external governance work is authorized.

## Queue

- Empty. New tasks must be submitted to the durable FIFO queue while this task remains active.

## Retained History

- Four retained/cancelled lane snapshots remain location-addressable in the machine-control block.
- Task-A remains cancelled. All retained branches, worktrees, and evidence are untouched.
- `TASK_GOVERNANCE_CLASSIC_ROLE_MIGRATION` remains historical planning material only; it is not queued or executable.

## Immutable History

- Generation-1 board archive and canonical index remain unchanged under `docs/archive/task_board_history/`.
- Direct generation-1 rollback proof may return `BLOCKED_ROLLBACK_CHAIN` after later legitimate board commits; this is expected protection, not failure.
