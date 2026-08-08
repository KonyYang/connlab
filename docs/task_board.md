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
    "task_id": "TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING",
    "summary": "Reduce Personal Serial Workflow V2 retry latency and execution cost through explicit role model routing and deterministic daily orchestration guidance.",
    "kind": "planned",
    "classification": "complex",
    "phase": "integration",
    "scope_contract": {
      "may_touch": [
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
        "docs/task_board.md"
      ],
      "expected_file_count": 4,
      "classification_reason": "Governance-only four-path change with mandatory independent Reviewer, QA, and Integrator gates; no runtime, schema, product, authority, or persistence changes.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q",
        "py -m pytest tests/integration/test_connlab_execution_gate_recovery.py tests/integration/test_connlab_serial_complex_recovery.py -q",
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
    "plan_ref": "docs/task_governance_orchestrator_latency_and_model_routing_plan.md@ceb7607b854038142ff50896cccfb8907b1ef2c7#f6f3041eaed7acd390ec21f787102aaad452eaa652750d9068b39c0c0df34241",
    "approval_ref": "User explicitly approved Revision 3 for TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING in the permanent Orchestrator conversation on 2026-08-08, binding Plan ceb7607b854038142ff50896cccfb8907b1ef2c7 and approved-request SHA-256 43d110d8f7a3e87859f59b72c62cd295d214fa86e3bb60e5d091587587a74d3a.",
    "activation_parent_sha": "38372b9351a5ab84007bcde4728a07fefa2dae43",
    "activated_at": "2026-08-08T00:31:25Z",
    "updated_at": "2026-08-08T05:17:49Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-governance-orchestrator-latency-and-model-routing",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-and-model-routing",
      "base_sha": "3d0884e12cc39e7b416da75ab01aaffd36c6418c",
      "head_sha": "3d0884e12cc39e7b416da75ab01aaffd36c6418c",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": null,
      "current_attempt": 1,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "f30780aee498354fd871384b0195458dbc52e925df42e504a68d3fc5f398dca7",
          "role": "Planner",
          "attempt": 1,
          "thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
          "agent_id": null,
          "host_id": null,
          "status": "completed",
          "recorded_at": "2026-08-08T04:26:37Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "206e249d076405df948b0c5f775d35b4f7ff0049115328f11f238b822fe543d9",
          "role": "Developer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/model_routing_developer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-08T05:22:31Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "78079ae12bf6a392463c4a21e4a270571fe45d978c25a012fae7a3ac1a75f5c6",
          "role": "Reviewer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/model_routing_reviewer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-08T05:34:32Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "3e06d2504671a1bc9428ad0248881a6f398cbc03fa6603ec8012323ba538300b",
          "role": "QA",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/model_routing_qa",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-08T05:41:40Z"
        }
      ],
      "host_thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
      "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
      "approved_code_paths": [
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
        "docs/task_board.md"
      ],
      "required_gates": [
        "Reviewer",
        "QA",
        "Integrator"
      ],
      "developer_subject_commit": "ad7dac819268ae77781709b626aea4f624a7a740",
      "reviewer_subject_commit": "ad7dac819268ae77781709b626aea4f624a7a740",
      "qa_subject_commit": "ad7dac819268ae77781709b626aea4f624a7a740",
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md@ec7af84879a8ddd300f310af62ed46480341bee1#c1d85c2dfbb5fcb0bc39e76cf0b23e97efab9ab2c300f669495526608ff64f10",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_developer.md@ad7dac819268ae77781709b626aea4f624a7a740#0985f2ed69d88f58962b2ab3e29d100b45596647b6c9ab9423146332fb3bed7c",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_reviewer.md@d5e82f2ea6ab18c979540c226811c2a20978f48e#27488e4d5001edff3a45770d0140fe694fc43c867f7f109274b76d0291161c96",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_qa.md@d6c7eba5b7cfe8dfb41e82575dc94404e8e2f5ae#5c22e90893a4e87d3609d03f4e2c910069c53640c35b4d6f09cc02292c96915a"
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
    "task_id": "TASK_MATRIX_EDITOR_REMOVE_UNUSED_TEMPLATES_PLACEHOLDER",
    "disposition": "closed after human review",
    "decision_ref": "user://explicit-close/2026-08-08/TASK_MATRIX_EDITOR_REMOVE_UNUSED_TEMPLATES_PLACEHOLDER",
    "closed_at": "2026-08-08T00:00:28Z"
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

## Immutable History

- Generation-1 board archive and canonical index remain unchanged under `docs/archive/task_board_history/`.
- Direct generation-1 rollback proof may return `BLOCKED_ROLLBACK_CHAIN` after later legitimate board commits; this is expected protection, not failure.
