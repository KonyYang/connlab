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
    "summary": "Complete the already-reviewed model-routing task through an exact, one-time integration reconciliation without relaxing normal workflow contracts.",
    "kind": "planned",
    "classification": "complex",
    "phase": "review",
    "scope_contract": {
      "may_touch": [
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
        "docs/task_board.md",
        "scripts/connlab_personal_task.py",
        "scripts/connlab_model_routing_integration_reconciliation.py",
        "tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py",
        "tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py"
      ],
      "expected_file_count": 8,
      "classification_reason": "Strict superset of the already-approved four paths, adding only the task-specific unmerged reconciliation writer/helper and bounded proof tests; product behavior and normal workflow contracts remain unchanged.",
      "targeted_validation": [
        "py -m pytest tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q",
        "py -m pytest tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py -q",
        "py -m pytest tests/unit/test_connlab_serial_complex_state.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q",
        "py -m py_compile scripts/connlab_personal_task.py scripts/connlab_model_routing_integration_reconciliation.py",
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
    "plan_ref": "docs/task_governance_orchestrator_latency_and_model_routing_plan.md@6eab428fce885fd62bf31f291e2cc5e42bc40596#e94f147c4d75f83a75980ae058e65dc6d682b9055572e0f6da7846e2c5663585",
    "approval_ref": "User approved TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING bounded integration reconciliation authority revision 6eab428fce885fd62bf31f291e2cc5e42bc40596, Plan SHA-256 e94f147c4d75f83a75980ae058e65dc6d682b9055572e0f6da7846e2c5663585, approved-request SHA-256 5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34, and manifest SHA-256 a882f4a9eb89b342c27ade4d01db0c03b53db11a7ccc878c75abb7d8f4eab0c0 on 2026-08-09.",
    "activation_parent_sha": "38372b9351a5ab84007bcde4728a07fefa2dae43",
    "activated_at": "2026-08-08T00:31:25Z",
    "updated_at": "2026-08-09T00:58:40Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-governance-orchestrator-latency-and-model-routing",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-orchestrator-latency-and-model-routing",
      "base_sha": "3d0884e12cc39e7b416da75ab01aaffd36c6418c",
      "head_sha": "3d0884e12cc39e7b416da75ab01aaffd36c6418c",
      "integration_target": "master",
      "worktree_lifecycle": "integration_ready",
      "current_role": null,
      "current_attempt": 5,
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
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "2962f4bd190bc6cbcdaf147baf4859d402c1c5cb430c77fe86ae4a96ad374e88",
          "role": "Integrator",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/model_routing_integrator",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-08T05:48:54Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "0b031b7c20fd357c90ab3927b5a905359ec410c8d933203addd71159ee339ed0",
          "role": "Planner",
          "attempt": 2,
          "thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
          "agent_id": null,
          "host_id": null,
          "status": "completed",
          "recorded_at": "2026-08-09T00:54:08Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "1bfbfbce486864c016cb52dd039301f990d93dbdefffdf1fe1ae36038d363299",
          "role": "Developer",
          "attempt": 2,
          "thread_id": null,
          "agent_id": "/root/model_routing_reconciliation_developer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-09T01:01:16Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "1cc9d4839f96f1d41c4c1b667fc3ec2997d0d83bc75ef867231abae393e92903",
          "role": "Reviewer",
          "attempt": 2,
          "thread_id": null,
          "agent_id": "/root/model_routing_reconciliation_reviewer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-09T01:19:17Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "6ff47b59e98f6a41e69a1dfd51bf2db770b9ea5cce21707252bb67fcbe7ff26a",
          "role": "Developer",
          "attempt": 3,
          "thread_id": null,
          "agent_id": "/root/model_routing_b1_b3_fix_developer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-09T04:08:51Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "46e0babddfecda8d0408c05a26f94257336650ce039bc049008b7ba88b476b28",
          "role": "Reviewer",
          "attempt": 3,
          "thread_id": null,
          "agent_id": "/root/model_routing_b1_b3_fix_reviewer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-09T04:27:59Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "21310c03bccfa75291a62dd18f2af34d698fc01605c4d5fae8af006745a85acb",
          "role": "Developer",
          "attempt": 4,
          "thread_id": null,
          "agent_id": "/root/model_routing_b1_b3_fix_developer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-09T06:21:35Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "0f98a0d42373575832df6a3141ca360372c363692739d4013050a013db5fe182",
          "role": "Reviewer",
          "attempt": 4,
          "thread_id": null,
          "agent_id": "/root/model_routing_b1_b3_fix_reviewer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-09T06:50:50Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "1dc846bf7b51a2843c9807ab9bb5615223b2de41f87ec8b1d23d971d9c9f5dab",
          "role": "Developer",
          "attempt": 5,
          "thread_id": null,
          "agent_id": "/root/model_routing_b1_b3_fix_developer",
          "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
          "status": "started",
          "recorded_at": "2026-08-09T07:21:22Z"
        }
      ],
      "host_thread_id": "019fb3d4-12a5-73b3-be8e-e59686fa39a9",
      "host_id": "host-task-governance-orchestrator-latency-and-model-routing",
      "approved_code_paths": [
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/unit/test_task_scoped_role_thread_lifecycle_governance.py",
        "docs/task_board.md",
        "scripts/connlab_personal_task.py",
        "scripts/connlab_model_routing_integration_reconciliation.py",
        "tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py",
        "tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py"
      ],
      "required_gates": [
        "Reviewer",
        "QA",
        "Integrator"
      ],
      "developer_subject_commit": "df5ee4e1e48f8a813430ae7facbcde1af3ecbd3e",
      "reviewer_subject_commit": "ad7dac819268ae77781709b626aea4f624a7a740",
      "qa_subject_commit": "ad7dac819268ae77781709b626aea4f624a7a740",
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md@ec7af84879a8ddd300f310af62ed46480341bee1#c1d85c2dfbb5fcb0bc39e76cf0b23e97efab9ab2c300f669495526608ff64f10",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_developer.md@ad7dac819268ae77781709b626aea4f624a7a740#0985f2ed69d88f58962b2ab3e29d100b45596647b6c9ab9423146332fb3bed7c",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_reviewer.md@d5e82f2ea6ab18c979540c226811c2a20978f48e#27488e4d5001edff3a45770d0140fe694fc43c867f7f109274b76d0291161c96",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_qa.md@d6c7eba5b7cfe8dfb41e82575dc94404e8e2f5ae#5c22e90893a4e87d3609d03f4e2c910069c53640c35b4d6f09cc02292c96915a",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integrator.md@f7770b6a6a82a36f946d16145a2124f6330961e1#8c15467010e3693ada5247ed3dd011c5334d736012dee7a94d1a8f9664cd05f0",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md@6eab428fce885fd62bf31f291e2cc5e42bc40596#4734ae3e6a4ae67e640443e0ba49ddb7fb75a6fd6e995c3b874e5a50c7369414",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md@673a9a276209c497fbda186ac347950a7cb56abf#bf528b6803ed0cbc3f60dbccb3389d978cd0630b5196917a213a0115c00c4abe",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@cfa5a5b5e765046283c60daf889e8c5586871fbb#8c5a45d1cb0299835d934ee649cbb539465ee5b2628ad3e0fd3a7ab55f72e8c7",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md@2e25ace1bb0600fd9c9e8fae502687734cc71574#0a9dc1ae8f80c789fcaecb276eb10d5ba8543c9a8bb0ba9a4fc1467e375f5e40",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@e58e8235e24fc5a3e0a49a879f7223008b0a5933#c093d4c6e66032faa495230f2f3b241d14cc39d530b0c066f02d405b17ac3fce",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md@cd1dfb160ff2b00542002999ff890b6284886cd5#24f66006569714e612d82f3d59152515e1f6c15dc2f27e13f867818421baa219",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md@7231d4cc6ad03d2723c614955b8ae1c97f7e86c1#a7d23ad68bae7ce943ebcad981bca704d2f28573a106cd3cbdd311d309bc4844",
        "docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md@03d49ffc92470c47feb4b8856efaf4bf26366209#4d2ac58ee4ca8ba414b6ca5ac0520db9b0d4faafb2fd94c300c6119821836cb1"
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
