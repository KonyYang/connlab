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
  "state": "idle",
  "active": null,
  "queue": [],
  "next_enqueue_sequence": 1,
  "last_closed": {
    "task_id": "TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN",
    "disposition": "retained",
    "decision_ref": "关闭",
    "integration_commit": "e56f3ef78168d9541f7e21b402e0feac3d041aaf",
    "integrator_evidence_ref": "docs/lane_evidence/TASK_LTR_WORKBOOK_ADMIN_RUNTIME_CONFIG_CORRECTED_PLAN_integrator.md@b3507acc2cc444f6ec7e6c1a71900bcbd9a83e0c#edfc81750dc5dad81b68906e4e01c745a53d7d93b37ffe6e79a1903ad7d52cf8",
    "retained_resources": {
      "thread_id": "/root/ltr_admin_runtime_config_host",
      "worktree": "D:\\PythonProject\\connlab-worktrees\\task-ltr-workbook-admin-runtime-config",
      "branch": "codex/task-ltr-workbook-admin-runtime-config",
      "head_sha": "ff01fb1d725c98fb58a3e343cf241076853e8cfa"
    },
    "closed_at": "2026-08-16T01:13:03Z"
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
