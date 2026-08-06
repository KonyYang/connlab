# ConnLab Task Board

> Status: Revision 6.1 pre-cutover retained-closeout implementation is validated and awaits human review.
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
  "state": "implemented_pending_human_review",
  "active": {
    "task_id": "TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION",
    "summary": "Implement and verify dormant serial complex role-chain support without cutover.",
    "kind": "planned",
    "phase": "human_review",
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
    "plan_ref": "docs/task_governance_serial_complex_role_chain_automation_plan.md@3308c0e3aeabe0d76b3535c5e33a8c4e079f187e#82467e5e1c5328f8b2e248bb09213e11526316ca73906e24ca79c21a4c49e3ca",
    "approval_ref": "批准 Revision 6.1 的最小 pre-cutover 收口实施，并明确授权将当前 EXTERNAL_BLOCKER 恢复到 implementation。",
    "activation_parent_sha": "17207db931cbe75d31c05fa1ee58257b4e88e1a9",
    "activated_at": "2026-08-06T00:00:24Z",
    "updated_at": "2026-08-06T16:03:26Z",
    "blocker": null,
    "validation": {
      "schema": "connlab.personal-task-validation",
      "version": 1,
      "status": "passed",
      "checks": [
        {
          "command": "py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_classifier.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_worktree.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_connlab_execution_gate_script.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/integration/test_connlab_serial_complex_recovery.py -q",
          "exit_code": 0,
          "summary": "85 passed in 21.15s"
        },
        {
          "command": "py scripts/connlab_personal_task.py inspect --repo-root D:\\PythonProject\\connlab --json",
          "exit_code": 0,
          "summary": "ALLOW_INSPECT; active task running/implementation before review transition"
        },
        {
          "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/connlab_execution_gate.ps1 -RepositoryRoot D:\\PythonProject\\connlab -Intent Inspect -Json",
          "exit_code": 0,
          "summary": "ALLOW_INSPECT"
        },
        {
          "command": "git diff --check",
          "exit_code": 0,
          "summary": "No whitespace errors"
        },
        {
          "command": "Verify changed paths are a subset of the approved 18-path allowlist",
          "exit_code": 0,
          "summary": "11 observed paths, all approved; scope digest b6a5a50818a40f25a4a56d1868448319cae16a7ab7e791f3d43de7cc93605b67"
        },
        {
          "command": "Verify immutable archive/index, retained history, and Task-A exact evidence",
          "exit_code": 0,
          "summary": "generation-1/index bytes, SHA-256 and blobs unchanged; retained-history digest 76f7887e30bc319223fb1f465ec57a5a216e75d58e2a5fe1a0728955762dfcab; Task-A committed evidence SHA-256 f1ca9341149d567958d837c18932e25ddee1ad47189266d0de73a03540e6de3a"
        },
        {
          "command": "Verify already committed lifecycle failure evidence and retained probe resources without lifecycle mutation",
          "exit_code": 0,
          "summary": "Both probe threads remain readable/notLoaded; both detached worktrees remain clean at ead61ccd2143c304a2b82aff0e3bfecdd5a6ad11; retained branch unchanged"
        }
      ],
      "observed_paths": [
        "docs/lane_evidence/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION_capability_probe.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "docs/task_board.md",
        "docs/task_governance_serial_complex_role_chain_automation_plan.md",
        "scripts/connlab_personal_task.py",
        "scripts/connlab_serial_board.py",
        "scripts/connlab_serial_complex.py",
        "tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md",
        "tests/integration/test_connlab_serial_complex_recovery.py",
        "tests/unit/test_connlab_serial_complex_orchestrator_contract.py",
        "tests/unit/test_connlab_serial_complex_state.py"
      ],
      "manual_checks": [
        "No lifecycle probe, handoff, archive, unarchive, retire, remove, prune, branch deletion, cutover, permission grant, runtime message, pilot, push, or cleanup was executed.",
        "scripts/connlab_personal_task.py is 271 lines; connlab_serial_board.py is 490; connlab_serial_complex.py is 489."
      ],
      "recorded_at": "2026-08-07T00:03:25+08:00"
    }
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

- `TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION`: active in
  `implemented_pending_human_review/human_review`.
- Revision 6.1 implements a legal `retained` closeout for exact, clean integrated resources; normal
  closeout and cutover no longer depend on retirement, archive, or `CLOSEOUT_ORDER`.
- The prior lifecycle failure remains preserved as completed discovery evidence. Both probe threads,
  detached worktrees, and the retained branch remain unchanged and location-addressable.
- Cutover, second approval, actual permission grant, production runtime message, pilot, push,
  lifecycle mutation, and cleanup remain unauthorized and were not executed.

## Queue

- Empty. New tasks must enter durable FIFO while this task awaits explicit User `关闭`.

## Retained History

- Four retained/cancelled lane snapshots remain location-addressable in the machine-control block.
- Task-A remains cancelled. All retained branches, worktrees, and evidence are untouched.
- `TASK_GOVERNANCE_CLASSIC_ROLE_MIGRATION` remains historical planning material only; it is not queued or executable.

## Immutable History

- Generation-1 board archive and canonical index remain unchanged under `docs/archive/task_board_history/`.
- Direct generation-1 rollback proof may return `BLOCKED_ROLLBACK_CHAIN` after later legitimate board commits; this is expected protection, not failure.
