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
    "task_id": "TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP",
    "summary": "Freeze legacy Controlled Lane entry under Personal Serial V2, remove stale ActivateNext/last_closed assumptions, and clarify the sole Submit/Approve/Close daily workflow without creating a new governance framework.",
    "kind": "planned",
    "classification": "complex",
    "phase": "development",
    "scope_contract": {
      "may_touch": [
        "AGENTS.md",
        ".agents/skills/connlab-controlled-lane/SKILL.md",
        "scripts/connlab_controlled_lane.ps1",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "docs/project_management/TASK_EXECUTION_SKILL.md",
        "tests/unit/test_connlab_lane_worktree_script.py",
        "tests/integration/test_connlab_execution_gate_recovery.py",
        "tests/integration/test_connlab_serial_complex_recovery.py",
        "docs/task_board.md"
      ],
      "expected_file_count": 9,
      "classification_reason": "Complex governance cleanup with independent review; exact nine-path scope freezes retained legacy entry behavior and corrects only confirmed stale workflow assumptions.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q",
        "py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q",
        "py -m pytest tests/unit/test_connlab_personal_serial_workflow.py -q",
        "git diff --check"
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
    "plan_ref": "docs/task_governance_personal_serial_v2_legacy_entry_freeze_and_stale_test_cleanup_plan.md@ca3858a8a8eafe59a3322a17a98c6e5d8684b5a7#67db77e0db767b3967235e9fccc185adad723619bfab8b904e991d93f3041bf5",
    "approval_ref": "User approved exact Plan ca3858a8a8eafe59a3322a17a98c6e5d8684b5a7#67db77e0db767b3967235e9fccc185adad723619bfab8b904e991d93f3041bf5 and approved-request cef186b0e0251ffb668e5cb3360eba54af547b83f4130333fa377c5ddb8320ba; exact nine-path implementation; one gpt-5.6-terra/medium/default_complex Developer-Reviewer-QA-Integrator chain; no push, cleanup, archive, retire, or scope expansion.",
    "activation_parent_sha": "f2e3c3c13ec4c29f156cec5d245291290a237bff",
    "activated_at": "2026-08-12T23:42:04Z",
    "updated_at": "2026-08-12T23:51:52Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-governance-personal-serial-v2-legacy-entry-freeze-and-stale-test-cleanup",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-personal-serial-v2-legacy-entry-freeze-and-stale-test-cleanup",
      "base_sha": "0e662928c5c57de927af75af2e56aa6883523a7a",
      "head_sha": "0e662928c5c57de927af75af2e56aa6883523a7a",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": null,
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "b70970522e0ce37dfe37404a4798b932341b801dd6efee1a3f485ea80018fba2",
          "role": "Planner",
          "attempt": 1,
          "thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
          "agent_id": null,
          "host_id": null,
          "status": "completed",
          "recorded_at": "2026-08-12T23:43:45Z"
        }
      ],
      "host_thread_id": "019ff81a-157d-7780-8efd-a115887a8997",
      "host_id": "host-task-governance-personal-serial-v2-legacy-entry-freeze-and-stale-test-cleanup",
      "approved_code_paths": [
        "AGENTS.md",
        ".agents/skills/connlab-controlled-lane/SKILL.md",
        "scripts/connlab_controlled_lane.ps1",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "docs/project_management/TASK_EXECUTION_SKILL.md",
        "tests/unit/test_connlab_lane_worktree_script.py",
        "tests/integration/test_connlab_execution_gate_recovery.py",
        "tests/integration/test_connlab_serial_complex_recovery.py",
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
        "docs/lane_evidence/TASK_GOVERNANCE_PERSONAL_SERIAL_V2_LEGACY_ENTRY_FREEZE_AND_STALE_TEST_CLEANUP_planner.md@ca3858a8a8eafe59a3322a17a98c6e5d8684b5a7#e5e4a4291620a15554b4cb94dac62aabb9583eb406693feaefc1ac97a54e6783"
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
    "task_id": "TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING",
    "disposition": "core model-routing goal accepted as completed; auxiliary reconciliation/proof expansion terminated and retained; cleanup deferred until the first successful post-close real task, then report CLEANUP_READY",
    "decision_ref": "User accepts the four core model-routing goals as completed, terminates auxiliary proof/reconciliation experiments, retains all related resources, and authorizes production cancellation to release WIP.",
    "closed_at": "2026-08-12T23:12:29Z"
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
