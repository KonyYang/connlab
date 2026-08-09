# TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING

Status: `integration_ancestry_reconciliation_amendment_pending_user_approval`

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
`Integrator pre-integration audit completed; local merge exists; acceptance remains blocked.` The accepted implementation subject
remains `ad7dac819268ae77781709b626aea4f624a7a740`; the immutable clean lane now ends at
`f7770b6a6a82a36f946d16145a2124f6330961e1` after the required Reviewer, QA, and Integrator evidence
commits. The existing two-parent merge is
`093d48966b15c536b7411b3cc4cdca1e1e0d4faf`, and the exact blocker-board baseline is clean primary
`82370aeb1690f1a6e1ebda7d37048f5f926d7570` with `INTEGRATION_BLOCKED`.

The frozen planning-start state for this final revision is:

- primary was clean at `5ce3ca0eca760314e7b26a385f681cb5c2b314e0`;
- board authority remains `state=running`, `phase=blocked`, `blocker=INTEGRATION_BLOCKED`, and
  `resume_phase=integration`;
- `active.scope_contract.may_touch` and `complex_context.approved_code_paths` each remain the original
  four paths;
- board `head_sha=3d0884e12cc39e7b416da75ab01aaffd36c6418c`,
  `integrated_commit=null`, and `worktree_lifecycle=integration_ready`;
- QA subject remains `ad7dac819268ae77781709b626aea4f624a7a740`, and the original lane remains clean at
  `f7770b6a6a82a36f946d16145a2124f6330961e1`;
- merge `093d48966b15c536b7411b3cc4cdca1e1e0d4faf` exists in primary ancestry but is not recorded by
  the board as accepted;
- no reconciliation branch/worktree exists; the eight-path authority chain has not run; no
  reconciliation Developer, Reviewer, QA, or Integrator has begun; and final CAS, human review, and
  closeout have not run.

These are blocked planning facts, not completion evidence. This Task must not be described as
`integrator_accepted`, complete, integration recorded, or ready for close.

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
only task-specific primary writes after independent review are the atomic host rebind and the final
atomic `docs/task_board.md` transition, each followed by its exact board-only durability commit. All
other original Must Not Touch paths remain locked.

Before any executor path or reconciliation worktree is created, the machine authority must be updated
through existing reviewed commands only. The required sequence is: record the truthful
`SCOPE_EXPANDED` blocker; approve the exact strict-superset eight-path request; resume to planning;
record a real Planner ready callback using this committed amendment evidence; and approve the same
request normally from `awaiting_user_approval`. The last approval must prove both
`active.scope_contract.may_touch` and `complex_context.approved_code_paths` equal the eight-path
request, and must bind the exact Plan ref and User approval ref. The approved-request SHA-256 is
`5eb00a105d1e0b5a047423c46b84436d854bf9c4ee85a54546c23932cedb2d34`.

Only after that committed authority checkpoint may the existing durable host begin and record a real
Developer invocation. The Plan-bound new worktree is initially a candidate review resource, not the
active host. Developer must finish the complete bridge/final-reconciliation implementation and tests
at immutable subject `B`; Developer evidence `D`, independent Reviewer evidence `R`, and mandatory QA
evidence `Q` must all be committed and their normal callbacks accepted before live host relocation.
Only the subsequently dispatched Integrator may use those reviewed bytes to perform the atomic rebind,
preserving its pending invocation until final CAS. Thus no unreviewed Developer writer can change the
primary board.

The fixed pre-rebind evidence contracts are task-derived paths with exact committed byte hashes:
`docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_developer.md` has `STATUS: ready_for_review`,
`docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_reviewer.md` has `STATUS: reviewer_pass`,
`docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_qa.md` has `STATUS: qa_pass`, and
`docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md` has `STATUS: pre_rebind_attestation_ready`. Their
topology is `approval-authority-base -> B -> D -> R -> Q -> I`; only Integrator may run live rebind at
`I`. These are genuine normal role events owned by the existing durable host, not fabricated history.
If the existing V2 role commands cannot express this sequence exactly, execution stops before rebind
with a new authority blocker.

Final reconciliation returns the primary task resource to the original integrated lane and records the
clean executor branch/worktree as a retained same-task resource with a frozen record schema, exact
duplicate/conflict rule, closeout reconciliation rule, and permanent residual owner.

No second merge, resume prewrite, manual board edit, history rollback, generic validation relaxation,
push, cleanup, product change, or mutation of the existing lane is permitted. Any mismatch is a
zero-write blocker.

`STATUS: INTEGRATION_RECONCILIATION_AUTHORITY_REVISION_PENDING_USER_APPROVAL`

## Bounded Integration Ancestry Reconciliation Amendment

The latest exact state is not acceptance. Primary is clean at
`d2b9b3a3b68970d261678989b249b3a6477bfde6`; the physical board SHA-256 is
`b5c132c16762e6a1f5545a2ffc4c9af7219776067b0a254a6221c1c2817e389d` and the sole
machine authority is `running/blocked/INTEGRATION_BLOCKED`. The final reviewed reconciliation
subject is `8c9f3a31ac44e03df8087684a038602e5532fefb`. The clean candidate is retained at
`11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69`; its exact blocker evidence is
`docs/lane_evidence/TASK_GOVERNANCE_ORCHESTRATOR_LATENCY_AND_MODEL_ROUTING_integration-reconciliation_integrator.md@11cf2532e0275d07c3fb9ba8d7a85d7d710a6e69#ea23c4cc2a0ad7a819e1c83fba78c954c50216de09108074f879a9d93904e477`.

The blocker is a contract defect, not Git drift: the reviewed repository verifier treats
`approval-authority-base -> B` as one direct-parent edge, while the legitimate same-task history
contains four Reviewer-blocked/Developer-fix rounds before final subject `8c9f3a31...`. The approval
checkpoint remains an immutable ancestor and must never be replaced by an arbitrary ancestor test.

After a new exact User approval, one bounded continuation may replace only that single-pass ancestry
assumption with a deterministic commit grammar. Every commit from approval checkpoint
`666a20d745fd72f6cbfd280d6ed1e29c0b023dda` to the future final implementation must be classified and
verified. Implementation commits may touch only the four approved executor paths; role-evidence
commits may touch only the task-derived evidence path for that role and must bind the exact task,
role, status, subject, model tuple, committed bytes and SHA-256. Reviewer/QA blockers may be followed
only by another implementation commit for this same approved task. The successful terminal chain is
always the direct-parent sequence `final B -> Developer ready -> Reviewer pass -> QA pass ->
Integrator ready`.

Because the current board blocker resumes only to `integration`, the amendment also requires one
task-specific, one-use adoption transition. It may run only after the ancestry implementation has an
independent Developer evidence commit, Reviewer pass and mandatory QA pass. It atomically adopts the
reviewed final subject/evidence and clears the exact current blocker into `running/integration` with
no role pending; only then may the normal writer begin a real Integrator invocation. This is not a
normal-state-machine change, fabricated callback history, or generic blocked-to-development bypass.
It must bind the exact source primary/board/blocker/candidate/Plan/approval and return zero writes on
any mismatch or replay conflict.

The already machine-approved eight-path scope remains unchanged. The future implementation delta is
limited to:

1. `scripts/connlab_personal_task.py` — register only the task-specific adoption command if required;
2. `scripts/connlab_model_routing_integration_reconciliation.py` — implement the grammar and atomic
   adoption proof;
3. `tests/unit/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`;
4. `tests/integration/test_task_governance_orchestrator_latency_model_routing_reconciliation.py`.

Task-derived Developer, Reviewer, QA and Integrator evidence files remain governance evidence, not
implementation scope. `docs/task_board.md` remains writer-only. Product code, normal workflow schema,
the original lane, existing merge, remote state and retained resources are locked. No rebase,
cherry-pick, manual board edit, remerge, rebind, Final CAS, push or cleanup is authorized before the
new committed Plan is explicitly approved and all required gates pass.

`STATUS: INTEGRATION_ANCESTRY_RECONCILIATION_AMENDMENT_PENDING_USER_APPROVAL`
