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
    "task_id": "TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT",
    "summary": "Persist every complex execution callback evidence as a sequential primary evidence-only commit so the task branch remains at the exact reviewed subject and verified integration needs no destructive topology recovery.",
    "kind": "planned",
    "classification": "complex",
    "phase": "qa",
    "scope_contract": {
      "may_touch": [
        "scripts/connlab_personal_task.py",
        "scripts/connlab_serial_evidence_topology.py",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/integration/test_connlab_nondestructive_evidence_topology.py",
        "tests/integration/test_connlab_serial_complex_recovery.py",
        "tests/unit/test_connlab_serial_complex_orchestrator_contract.py",
        "tasks/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT.md",
        "docs/task_governance_nondestructive_evidence_topology_closeout_plan.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md",
        "docs/task_board.md"
      ],
      "expected_file_count": 15,
      "classification_reason": "Complex governance persistence and integration-authority correction with independent Reviewer, mandatory QA and Integrator gates; the bounded amendment only repairs two stale test fixtures and changes no product, API, database, schema, business-rule, external or destructive behavior.",
      "targeted_validation": [
        "py -m pytest tests/integration/test_connlab_nondestructive_evidence_topology.py -q",
        "py -m pytest tests/integration/test_connlab_serial_complex_recovery.py -q",
        "py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q",
        "py -m py_compile scripts/connlab_personal_task.py scripts/connlab_serial_complex.py scripts/connlab_serial_evidence_topology.py",
        "python line-budget check: connlab_personal_task.py <= 500, connlab_serial_evidence_topology.py <= 500, test_connlab_nondestructive_evidence_topology.py <= 500",
        "git diff --check",
        "real temporary-Git end-to-end: canonical Submit through human review with Planner prefix plus dynamic execution/fix-loop primary evidence-only commits, stable task subject HEAD, successful record-integration, frozen Plan route audit, forbidden-operation absence and zero-write drift negatives"
      ],
      "forbidden_categories": {
        "api_contract": false,
        "database": false,
        "schema_or_migration": false,
        "persistence": true,
        "authority": true,
        "public_drive_workflow": false,
        "business_rule_semantics": false,
        "destructive_action": false,
        "external_mutation": false
      }
    },
    "plan_ref": "docs/task_governance_nondestructive_evidence_topology_closeout_plan.md@9d7966d53896d032e3bfe546bbd0ea38659a9fbb#0892bcf16008c2be90bd6de84a065f650fb6bb5dfecff8f2fba905f4162cf57d",
    "approval_ref": "User approval in current message: authorize same-scope PLANNER_REVISION_BUNDLE_TOPOLOGY_FIX using this exact committed Plan and byte-identical approved-request SHA-256 9910790e5d12df746f4c1fc3680eccbe249b6fec7762e76cd7deb340a106ee51.",
    "activation_parent_sha": "dd88e7fab9494985502236a32a46e81c3c79e0fe",
    "activated_at": "2026-08-14T14:59:46Z",
    "updated_at": "2026-08-15T04:11:04Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": "codex/task-governance-nondestructive-evidence-topology-closeout",
      "task_worktree": "D:\\PythonProject\\connlab-worktrees\\task-governance-nondestructive-evidence-topology-closeout",
      "base_sha": "56f1fe51a29d5449f1b3178257d62e90ce363601",
      "head_sha": "56f1fe51a29d5449f1b3178257d62e90ce363601",
      "integration_target": "master",
      "worktree_lifecycle": "ready",
      "current_role": "QA",
      "current_attempt": 2,
      "role_invocations": [
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "d9ebd4935e7cc614dd855844078e624ac28e14e6f5b0f340f53235be8cf69f77",
          "role": "Planner",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_planner",
          "host_id": null,
          "status": "started",
          "recorded_at": "2026-08-14T15:01:11Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "e9eafbf4c20a56b507686e9059c2e1208214456a9e854301593e9e6bdcf2de34",
          "role": "Developer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_developer",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-14T22:30:32Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "12b005e6ab8abb039ff46af5ab8d78c4e176d1079d736b039ed9a66177a2c128",
          "role": "Planner",
          "attempt": 2,
          "thread_id": null,
          "agent_id": "/root",
          "host_id": null,
          "status": "completed",
          "recorded_at": "2026-08-14T23:02:52Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "028e220d99d575c1ed8e570f423c9068c09fb6df527d35358c90503e6a71c636",
          "role": "Developer",
          "attempt": 2,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_developer",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-14T23:04:49Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "fdaeb60f70e5101965831d5bf3792bc3e5d77d0fb533619a09c0eca756d9201d",
          "role": "Reviewer",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_reviewer",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-14T23:21:16Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "a572503df59e606f3fe4a158e85ee28222967636ae767d692ec05091cb8c68ed",
          "role": "Developer",
          "attempt": 3,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_developer",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-14T23:33:14Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "46c55df298ebbfd1d9b18b344623d80e7d90e16701f6f58122a7ea3d53964d0f",
          "role": "Reviewer",
          "attempt": 2,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_reviewer",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-14T23:50:42Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "b0dabb69a7c4dd384cd52075b07b613b5380ab7984cdb61945c528c76ffc51fb",
          "role": "QA",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_qa",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-14T23:58:56Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "154bf446c2ea9174c36cad1c16163d71aee58078a17817c0d59238cb73533c47",
          "role": "Integrator",
          "attempt": 1,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_integrator",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-15T00:09:59Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "cef992a7eb2245504ec2a389b4bae7ff305f8fe06731880049210889543edb43",
          "role": "Developer",
          "attempt": 4,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_developer4",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-15T04:13:06Z"
        },
        {
          "schema": "connlab.serial-invocation",
          "version": 1,
          "action_id": "f7b2fae2674d85395db74d176b3a192336d0fe3be624fba95f1332b41272fe06",
          "role": "Reviewer",
          "attempt": 3,
          "thread_id": null,
          "agent_id": "/root/nondestructive_evidence_topology_reviewer3",
          "host_id": "/root/nondestructive_evidence_topology_host",
          "status": "started",
          "recorded_at": "2026-08-15T04:38:22Z"
        }
      ],
      "host_thread_id": "/root/nondestructive_evidence_topology_host",
      "host_id": "/root/nondestructive_evidence_topology_host",
      "approved_code_paths": [
        "scripts/connlab_personal_task.py",
        "scripts/connlab_serial_evidence_topology.py",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/integration/test_connlab_nondestructive_evidence_topology.py",
        "tests/integration/test_connlab_serial_complex_recovery.py",
        "tests/unit/test_connlab_serial_complex_orchestrator_contract.py",
        "tasks/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT.md",
        "docs/task_governance_nondestructive_evidence_topology_closeout_plan.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md",
        "docs/task_board.md"
      ],
      "required_gates": [
        "Reviewer",
        "QA",
        "Integrator"
      ],
      "developer_subject_commit": "59e0cc7b7fa4b53b1a5a21719647aa47f9491fcb",
      "reviewer_subject_commit": "59e0cc7b7fa4b53b1a5a21719647aa47f9491fcb",
      "qa_subject_commit": "2e6f16322c93fc1a83188658476191d2a032b959",
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md@72a135b3e891a1c3b2c97bb78d55163f09ffda31#9e393adb8d7df9c485bfc2367c4d87f818543f13d94e15d87a8f6be625dce4b9",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md@109a3b58fa29ab8bc51710687cfb163add977ddb#05f5f78c54cc52dae9b0446f17819784840ef2ad44d9205e36bb2d825031fe23",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md@9d7966d53896d032e3bfe546bbd0ea38659a9fbb#c14b81b0bd97048ba0e5487d151dd92d3e1cf8cf712c149768ce79e917109a2e",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md@700d26e7b3953e92162086a96dbd8604f45bee29#7ded3a425bd16c4405a2c9510e8e1479dc17020cc0c5d600f7ca2ce67c4df858",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md@9b496e5c9afd7a3ff29055ca3fe8636ff4711e00#5d6b143b0455116f75be06ea8ba780f3d8960016a2a2b5f9fa7b07f753d4ae6f",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md@d7a331a1c9e6336a71c36278029d5c5779d74a41#1a66295ba0ffe753965f579b5a92189e96027199def11854c039700800906fe0",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md@d582be59a2509fd6f828097cc0bb44d9afd42093#27b5949e0abcfcc184f34a0b7f5544f941bbbb4565576feaf5c71848d3502a5d",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md@5c91ea8e48d936e742d5ad706207b4089979468b#641a0184e6c673a9cc3c11423004c69fa59c0ed62148389d4e5f7113dfe9e713",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md@0729144924df7bf4417efdee1edba687c103b17f#fd90c34c35e9cd9537a9df2f54bfabc189fadafa28bd672a18b4f5dcca46e2f3",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md@5bb3a708c23b57a23d6d4a247caceab717792bab#48072b6c04a8ecea993a4ec22b13a89a12dde7684f3fe8ddf49ae572cf29ee16",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md@ac1202368f4941206b9fe0828b79f1e5df46e00d#7b4b399086246b22db8cb488bbad879bfe2f341f14eecfe099c154bb4d940e25"
      ],
      "pending_callback": {
        "state": "dispatch_pending",
        "action_id": "4ac9bd99336a70caf3ce5b9a727a51e231119907221117c5220209e00d4bcdd7",
        "role": "QA",
        "attempt": 2
      },
      "closeout_disposition": null,
      "retained_resource_refs": [],
      "close_decision_ref": null
    }
  },
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_GOVERNANCE_EVIDENCE_DIGEST_AUTOCORRECTION",
    "disposition": "closed after human review",
    "decision_ref": "User explicitly sent 关闭 after reviewing the corrected implementation.",
    "closed_at": "2026-08-14T14:06:37Z"
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
