# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING

Status: `integration_reconciliation_authority_revision_pending_user_approval`

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Activation commit: `6227acb7cfccaab276194d2a7cbda96bc1f09a89`

## Goal

Reduce avoidable retries, orchestration latency, and model cost in Personal Serial Workflow V2 without
adding a governance framework, changing product behavior, or changing the board/runtime schema.

The permanent Orchestrator and direct simple tasks remain on `gpt-5.6-sol` with
`reasoning_effort=medium`. The automatic complex chain uses explicit role-level routing, with
`gpt-5.6-terra` as the default and narrowly defined risk-based escalation to `gpt-5.6-sol`.

## Approved-Plan Boundary

Implementation is forbidden until the User approves the exact committed Plan and its
`connlab.personal-task-approved-request` contract.

Implementation may touch exactly:

1. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
2. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
3. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
4. `docs/task_board.md`

Planning changed only:

1. `docs/task_board.md` through `scripts/run_task.ps1` Submit and the activation commit;
2. `tasks/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING.md`;
3. `docs/task_governance_orchestrator_latency_and_model_routing_plan.md`;
4. `docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_planner.md` plus
   writer-generated/committed Planner-ready board transitions.

## Must Not Touch

- `scripts/run_task.ps1`, `scripts/connlab_personal_task.py`, `scripts/connlab_serial_board.py`, or the
  board JSON schema;
- product/backend/frontend code, API/database/schema/migration/persistence/authority/public-drive or
  business semantics;
- browser plugin, retained/frozen/cancelled lane resources, legacy V1/V2 audit resources, lifecycle
  cleanup, remotes, or push.

## Acceptance

- Submit, Approve, and Close guidance uses only `scripts/run_task.ps1`; no direct Python request-JSON
  construction or legacy schema probing is prescribed.
- The exact Submit key set excludes `kind` and uses the classifier's ten forbidden-category keys;
  the exact Approve JSON includes `kind=planned` and uses the approved-scope validator's nine keys
  (no `push_or_release`); Close has no JSON payload and requires one non-empty `DecisionRef`.
  Contract, cross-schema-copy negative, and entry negatives freeze all three shapes.
- Simple work keeps the direct two-interaction path: submit requirement, then inspect and close.
- Recovery reconstructs the active task/host from board, Git, and evidence without duplicate activation.
- Every complex role dispatch explicitly passes `model` and `reasoning_effort`; role evidence records
  `MODEL`, `REASONING_EFFORT`, and `MODEL_ROUTE_REASON`, and Integrator/final summaries reconcile those
  fields with the actual dispatch action. Luna is not used.
- UI smoke is required only for user-visible UI changes and uses documented load state or deterministic
  selectors; unsupported `networkidle` probing is forbidden.
- Reviewer, mandatory QA, and Integrator remain required after approval.

Historical Revision 3 status before implementation: `REVISION_3_PLANNED_PENDING_USER_APPROVAL`.

## Integration Reconciliation Amendment

The original implementation is locally merged but is not accepted. The precise state is:
`Integrator pre-integration audit completed; acceptance blocked.` The accepted implementation subject
remains `ad7dac819268ae77781709b626aea4f624a7a740`; the immutable clean lane now ends at
`f7770b6a6a82a36f946d16145a2124f6330961e1` after the required Reviewer, QA, and Integrator evidence
commits. The existing two-parent merge is
`093d48966b15c536b7411b3cc4cdca1e1e0d4faf`, and the exact blocker-board baseline is clean primary
`82370aeb1690f1a6e1ebda7d37048f5f926d7570` with `INTEGRATION_BLOCKED`.

This amendment authorizes no implementation until the User approves its exact committed Plan ref. A
later approval may authorize one reviewed, task-specific executor artifact that leaves the original
lane and existing merge immutable and performs one hash-bound compare-and-swap board transition. It
must verify the exact commits, trees, topology, evidence bytes/status, clean Git facts, blocker board
lineage, amendment Plan ref, pre-implementation machine-authority chain, durable host relocation, and
reconciliation role evidence before it can atomically record:

- `complex_context.head_sha=f7770b6a6a82a36f946d16145a2124f6330961e1`;
- `complex_context.integrated_commit=093d48966b15c536b7411b3cc4cdca1e1e0d4faf`;
- `active.phase=human_review`;
- `control.state=implemented_pending_human_review`;
- `complex_context.worktree_lifecycle=integrated`;
- complete hash-verified evidence refs; and
- `active.blocker=null`.

For that unmerged executor artifact only, the executor code/test delta supersedes the earlier runtime
prohibition and is exactly:

1. `scripts/connlab_personal_task.py`
2. `scripts/connlab_model_routing_integration_reconciliation.py` (new)
3. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py` (new)
4. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py` (new)

The four fixed reconciliation role-evidence paths are evidence refs, not implementation scope. The
only primary write is the final atomic `docs/task_board.md` transition and its exact board-only commit.
All other original Must Not Touch paths remain locked.

Before any executor path or reconciliation worktree is created, the machine authority must be updated
through existing reviewed commands only. The required sequence is: record the truthful
`SCOPE_EXPANDED` blocker; approve the exact strict-superset eight-path request; resume to planning;
record a real Planner ready callback using this committed amendment evidence; and approve the same
request normally from `awaiting_user_approval`. The last approval must prove both
`active.scope_contract.may_touch` and `complex_context.approved_code_paths` equal the eight-path
request, and must bind the exact Plan ref and User approval ref. The approved-request SHA-256 is
`5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34`.

Only after that committed authority checkpoint may the existing durable host begin and record a real
Developer invocation. That invocation owns one exact host relocation to the approved reconciliation
branch/worktree. The relocation must atomically replace the host Git facts while preserving the live
Developer action, scope, locks, Plan/approval refs, and original-lane evidence. No broader executor
implementation may occur until the new host facts are committed and verified. Final reconciliation
returns the primary task resource to the original integrated lane and records the clean executor
branch/worktree as a retained same-task resource with a permanent residual owner.

No second merge, resume prewrite, manual board edit, history rollback, generic validation relaxation,
push, cleanup, product change, or mutation of the existing lane is permitted. Any mismatch is a
zero-write blocker.

`STATUS: INTEGRATION_RECONCILIATION_AUTHORITY_REVISION_PENDING_USER_APPROVAL`
