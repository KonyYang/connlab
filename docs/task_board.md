# ConnLab Task Board

> Status: Pre-cutover implementation checkpoint validated; active task is blocked because probe closeout/cleanup is not authorized.
> Last Updated: 2026-08-06
> Current Source Of Truth: `docs/task_board.md`
> Current Active Task: `TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION`
> Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
> Execution Rule: One active task, durable FIFO queue, direct primary-worktree implementation, local commits only.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.personal-serial-control",
  "version": 1,
  "mode": "personal_serial",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION",
    "summary": "Implement and verify dormant serial complex role-chain support without cutover.",
    "kind": "planned",
    "phase": "blocked",
    "scope_contract": {
      "may_touch": [
        "tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md",
        "docs/task_governance_serial_complex_role_chain_automation_plan.md",
        "docs/task_board.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_capability_probe.md",
        "docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_cutover_manifest.json",
        "scripts/connlab_personal_task.py",
        "scripts/connlab_serial_board.py",
        "scripts/connlab_serial_complex.py",
        "scripts/connlab_serial_worktree.ps1",
        "tests/unit/test_connlab_personal_serial_workflow.py",
        "tests/unit/test_connlab_serial_classifier.py",
        "tests/unit/test_connlab_serial_complex_state.py",
        "tests/unit/test_connlab_serial_complex_worktree.py",
        "tests/unit/test_connlab_serial_complex_orchestrator_contract.py",
        "tests/unit/test_connlab_execution_gate_script.py",
        "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
        "tests/integration/test_connlab_serial_complex_recovery.py"
      ],
      "expected_file_count": 18,
      "classification_reason": "This planned governance change adds dormant CLI/schema/state-machine support, persistent board migration logic, authority rules and a native Codex capability probe; the first approval excludes every cutover-only path and keeps v1 authoritative.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_classifier.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_worktree.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_connlab_execution_gate_script.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/integration/test_connlab_serial_complex_recovery.py -q",
        "py scripts/connlab_personal_task.py inspect --repo-root D:\\PythonProject\\connlab --json",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/connlab_execution_gate.ps1 -RepositoryRoot D:\\PythonProject\\connlab -Intent Inspect -Json",
        "git diff --check",
        "Verify git diff <approval-commit>..<implementation-head> --name-only is a subset of the 18 approved paths.",
        "Verify generation-1 archive, canonical history index, Task-A and retained evidence hashes are unchanged.",
        "Execute the bounded native capability probe and commit its evidence; do not cut over."
      ],
      "forbidden_categories": {
        "api_contract": true,
        "database": false,
        "schema_or_migration": true,
        "persistence": true,
        "authority": true,
        "public_drive_workflow": false,
        "business_rule_semantics": false,
        "destructive_action": false,
        "external_mutation": true
      }
    },
    "plan_ref": "docs/task_governance_serial_complex_role_chain_automation_plan.md@d9923605a9f9e24a8aadadc5516f512fd971420f#3de6416dc8633b3e91faccaf5352ca9354440d5542e7c35bc4e24824ee1eacb2",
    "approval_ref": "Controller task 019fc491-21b0-77b0-bf18-53f53a366a7c exact User approval on 2026-08-06: 批准 Revision 5 首次实施。仅授权首次审批 JSON 中的 18 个 implementation-before-cutover 路径和 pre-cutover 实施；不授权 cutover、第二次审批、实际权限授予、runtime message、pilot、push 或清理。",
    "activation_parent_sha": "17207db931cbe75d31c05fa1ee58257b4e88e1a9",
    "activated_at": "2026-08-06T00:00:24Z",
    "updated_at": "2026-08-06T13:45:55Z",
    "blocker": {
      "schema": "connlab.personal-task-blocker",
      "version": 1,
      "code": "EXTERNAL_BLOCKER",
      "reason": "Authorized lifecycle probe stopped after A handoff: operation exec-a6bf75db-4f86-49f8-83e0-e0d360998c1c succeeded and created destination thread 019fd73e-6aac-74b0-b404-70ff1be70f42, but the 84b1 worktree remained registered and the saved project checkout moved off master. Primary master was restored under separate User authority. Handoff cannot be treated as worktree retirement; no archive or B-sequence action is authorized.",
      "dirty_paths": [],
      "failed_validation": null,
      "recorded_at": "2026-08-06T13:45:54Z"
    },
    "validation": null
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION",
    "disposition": "closed after human review",
    "decision_ref": "User exact wording on 2026-08-06: 关闭",
    "closed_at": "2026-08-05T23:44:47Z"
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

- `TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION`: active in `running/blocked`.
- Revision 5 implementation-before-cutover is approved; checkpoint `88006c46` is locally committed
  and validated, while the current blocker and execution slot remain retained.
- Authorized lifecycle probing proved that `handoff_thread` does not retire its source worktree and
  temporarily moved the saved-project checkout off master; primary was explicitly restored clean.
- No closeout order is proven. Cutover, second approval, actual permission grant, production runtime
  message, pilot, push, further lifecycle probing, and alternate cleanup remain unauthorized.

## Queue

- Empty. New tasks must be submitted to the durable FIFO queue while this blocked task remains active.

## Retained History

- Four retained/cancelled lane snapshots remain location-addressable in the machine-control block.
- Task-A remains cancelled. All retained branches, worktrees, and evidence are untouched.
- `TASK_GOVERNANCE_CLASSIC_ROLE_MIGRATION` remains historical planning material only; it is not queued or executable.

## Immutable History

- Generation-1 board archive and canonical index remain unchanged under `docs/archive/task_board_history/`.
- Direct generation-1 rollback proof may return `BLOCKED_ROLLBACK_CHAIN` after later legitimate board commits; this is expected protection, not failure.
