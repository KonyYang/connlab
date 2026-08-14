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
    "phase": "development",
    "scope_contract": {
      "may_touch": [
        "scripts/connlab_personal_task.py",
        "scripts/connlab_serial_evidence_topology.py",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/integration/test_connlab_nondestructive_evidence_topology.py",
        "tasks/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT.md",
        "docs/task_governance_nondestructive_evidence_topology_closeout_plan.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md",
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md",
        "docs/task_board.md"
      ],
      "expected_file_count": 13,
      "classification_reason": "Complex governance persistence and integration-authority correction with independent Reviewer, mandatory QA and Integrator gates; no product, API, database, schema, business-rule, external or destructive change.",
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
    "plan_ref": "docs/task_governance_nondestructive_evidence_topology_closeout_plan.md@7ee08a659172bde11f4bb1b87e1e9bac2630eaeb#c6ceda8c42a7e91c784eac98628eda8d6cd5b528883df5266fe8d9ecb23d1446",
    "approval_ref": "User explicitly approved implementation of Plan ref 7ee08a659172bde11f4bb1b87e1e9bac2630eaeb and approved-request SHA-256 0b36fc339ba7cc7dfa412a2608833fc403a8c41fd19051efef05a289e8851298 by saying 批准实施.",
    "activation_parent_sha": "dd88e7fab9494985502236a32a46e81c3c79e0fe",
    "activated_at": "2026-08-14T14:59:46Z",
    "updated_at": "2026-08-14T15:26:45Z",
    "blocker": null,
    "validation": null,
    "complex_context": {
      "workflow_version": 1,
      "task_branch": null,
      "task_worktree": null,
      "base_sha": "dd88e7fab9494985502236a32a46e81c3c79e0fe",
      "head_sha": "dd88e7fab9494985502236a32a46e81c3c79e0fe",
      "integration_target": "master",
      "worktree_lifecycle": "absent",
      "current_role": null,
      "current_attempt": 1,
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
        }
      ],
      "host_thread_id": null,
      "host_id": null,
      "approved_code_paths": [
        "scripts/connlab_personal_task.py",
        "scripts/connlab_serial_evidence_topology.py",
        ".agents/skills/connlab-lane-orchestrator/SKILL.md",
        "docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md",
        "tests/integration/test_connlab_nondestructive_evidence_topology.py",
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
      "developer_subject_commit": null,
      "reviewer_subject_commit": null,
      "qa_subject_commit": null,
      "integrated_commit": null,
      "evidence_refs": [
        "docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md@72a135b3e891a1c3b2c97bb78d55163f09ffda31#9e393adb8d7df9c485bfc2367c4d87f818543f13d94e15d87a8f6be625dce4b9"
      ],
      "pending_callback": {
        "state": "host_creation_pending",
        "action_id": "91b93e012b32ded8faf448cc6ab278aae86ee61888a4bd4c6f303a0971e41afe",
        "role": "Host",
        "attempt": 1
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
