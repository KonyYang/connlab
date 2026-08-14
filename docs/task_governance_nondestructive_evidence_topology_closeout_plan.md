# TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT Plan

Status: `bounded_scope_amendment_pending_user_approval`

## 1. Outcome And Chosen Model

Choose exactly one ownership model: **primary sequential evidence-only commits**. Every execution
callback evidence commit advances primary, never the task branch/worktree. Existing board-only
authority commits remain board-only and the task worktree remains clean at the exact reviewed
subject. Planner evidence is the existing committed planning prefix; bounded fix loops may append
additional Developer/Reviewer/QA evidence without changing this model.

Rejected alternatives:

- Evidence on the task branch is the defect being removed.
- A separate retained evidence ref/worktree adds a second ref owner and recovery lifecycle and would
  require normal ref mutation.
- Combining evidence with the callback board commit is circular because callback validation requires
  an already committed evidence ref and would also break board-only durability commits.

No new writer command, schema, state, role, approval, registry, manifest, lane or lifecycle is added.

## 2. Discovery Gate

### User-confirmed

- The task branch must stay at the Developer subject after that subject exists.
- Evidence must remain committed, independently recoverable and exact-path/commit/raw-SHA bound.
- Normal execution must not use destructive branch-pointer recovery or add User interactions.
- The task is limited to evidence persistence and integration topology.

### Repository-confirmed

- `validate_integration_transition` requires `branch_head == subject_commit`; this is retained.
- `verify_integration_repository` already checks registered task worktree branch/HEAD/clean state,
  merge parents/tree and committed evidence hashes.
- `consume-callback` stores ordered evidence refs and exact reviewed subjects.
- The existing real temporary-repository helper commits evidence on primary, showing the minimal
  topology is already compatible with the state machine; production instructions and repository
  verification are the missing seam.
- `scripts/connlab_serial_complex.py` needs no modification because no state or callback schema
  changes.

No unresolved discovery question changes scope, behavior, authority or validation.

## 3. Exact Git Topology And Commit Order

Let `S` be the final Developer implementation subject in the task branch. The task branch is:

```text
T0 -> one or more approved implementation commits -> S
```

After `S`, its branch and registered worktree remain clean and fixed at `S`. For each role `r` in
Developer, Reviewer, QA and Integrator, primary is:

```text
B_r  begin-role board-only commit
-> A_r  record-invocation board-only commit
-> E_r  single-parent evidence-only commit, exactly the fixed role evidence path
-> C_r  consume-callback board-only commit
```

`A_r` and `E_r` contain byte-identical `docs/task_board.md`. `E_r` is current primary HEAD when the
callback writer validates it. The ordered board evidence list is **not** a fixed four-item list: it
starts with committed Planner evidence `E_P`, then contains exactly one evidence ref for every
successfully consumed execution callback in durable invocation order. Reviewer/QA fix loops append
their actual Developer/Reviewer/QA callback evidence and require no route-length or evidence-count
constant. After the final Integrator callback commit `C_I` is integration-ready, the local merge has
parents `[C_I, S]`; `record-integration` binds `subject_commit=branch_head=S` and the complete dynamic
evidence list. No execution `E_r` is in `S` ancestry.

## 4. File-Level Implementation

### `scripts/connlab_personal_task.py`

Keep this 434-line writer as a thin orchestration seam. It may only add bounded imports and calls and
must remain at or below the 500-line Python hard limit. Before applying an execution-role
`consume-callback`, it calls the dedicated verifier described below; before `record-integration`, it
revalidates the complete accepted evidence topology.

### `scripts/connlab_serial_evidence_topology.py`

Add one focused repository-verification module, target at most 300 lines and hard limit 500. It is not
a writer, command, framework or second authority source. It receives the existing active/callback or
integration facts and verifies:

- primary clean and current HEAD exactly equals the supplied evidence commit;
- evidence commit is single-parent and its parent is the immediately preceding committed
  record-invocation authority state;
- parent-to-evidence diff is exactly the Task-derived fixed evidence path;
- parent/evidence/current raw board bytes are identical;
- task worktree registration, branch, clean state and HEAD equal callback subject, with existing
  Reviewer/QA/Integrator subject binding retained;
- evidence commit is not an ancestor of the task subject;
- committed raw bytes match the evidence SHA-256;
- evidence contains one exact TASK_ID, ROLE, STATUS, SUBJECT, MODEL, REASONING_EFFORT,
  MODEL_ROUTE_REASON, ACTION_ID and ATTEMPT binding;
- ACTION_ID, ROLE and ATTEMPT match the corresponding durable board invocation;
- MODEL, REASONING_EFFORT and MODEL_ROUTE_REASON match the frozen route in the exact committed Plan.

Any mismatch raises a typed `BLOCKED_CALLBACK_INVALID`, `BLOCKED_SUBJECT_MISMATCH`,
`BLOCKED_WORKTREE_FACTS` or `BLOCKED_EVIDENCE_INVALID` before board mutation. Planner evidence keeps
its existing pre-host planning behavior; the strict topology applies to Developer/Reviewer/QA/
Integrator.

At integration, treat Planner evidence as the pre-host prefix, then dynamically pair every remaining
board evidence ref with its corresponding durable execution invocation. Revalidate every execution
evidence commit as an ordered primary ancestor before the merge parent and retain its one-path
evidence-only identity. Equality is derived from the actual board lists, not a fixed role sequence,
route length or evidence count.

### Orchestrator skill and normative protocol

Update `.agents/skills/connlab-lane-orchestrator/SKILL.md` and
`docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md` to name primary as the sole execution
evidence owner and freeze the exact `B_r -> A_r -> E_r -> C_r` sequence. Roles run and review the
task worktree but write/commit only their fixed evidence path on clean primary after invocation.
These two texts are required so a restart does not fall back to the defective task-worktree commit
habit; no broader policy document changes.

### Integration regression

Add `tests/integration/test_connlab_nondestructive_evidence_topology.py`, bounded to at most 500 lines,
for the real disposable-repository end-to-end and topology negatives.

The bounded scope amendment adds two fixture-only paths after the strict verifier exposed stale test
assumptions:

- In `tests/integration/test_connlab_serial_complex_recovery.py`, replace the existing uncommitted
  `docs/plan.md@aaaa...#bbbb...` sentinel with a real committed Plan and its raw SHA-256. Keep the
  existing recovery cases and assertions; do not add a sentinel exception to production. Avoid net
  line growth in this already oversized historical module where mechanically possible.
- In `tests/unit/test_connlab_serial_complex_orchestrator_contract.py`, make
  `test_public_writer_rejects_role_transition_without_active_v2_task` resolve the actual primary
  repository instead of passing the linked task worktree as primary. Retain its zero-write task
  mismatch assertion and do not weaken primary verification.

These are the only newly authorized changes. They do not alter verifier semantics, runtime behavior,
state schema or authority.

## 5. Durable And Independent Model-Routing Proof Boundary

`connlab.serial-invocation` does not persist model, reasoning effort or route reason. The verifier
must not claim those fields are recoverable from board invocation data.

The proof is intentionally layered:

1. **Durable board identity:** ACTION_ID, ROLE and ATTEMPT in evidence match the corresponding board
   invocation exactly.
2. **Committed Plan binding:** evidence MODEL, REASONING_EFFORT and MODEL_ROUTE_REASON equal this
   Plan's frozen route: Developer, Reviewer, QA and Integrator are all
   `gpt-5.6-sol / medium / risk:authority`.
3. **Independent execution audit:** Reviewer checks actual Developer and Reviewer dispatch capsule/
   agent identity; QA checks the complete actual dispatch set and forbidden-Luna rule; their evidence
   records that audit. Integrator summarizes `ACTUAL_MODEL_ROUTING` from committed audited evidence.

This proves committed evidence identity and independent dispatch reconciliation, not an unavailable
board-only reconstruction of actual spawn parameters.

## 6. Crash Recovery

- After `A_r` and before evidence: board is callback-pending and primary is `A_r`; resume the same
  recorded role invocation to produce `E_r`, without a new action or attempt.
- After `E_r` and before callback: board remains callback-pending and primary is the uniquely valid
  `E_r`; reuse its exact ref and consume the callback once.
- After writer replacement and before commit: only the board is dirty; exact-stage/commit that board
  transition before continuing.
- After `C_r`: board and primary identify the next phase and ordered evidence refs.
- Any other primary commit between `A_r` and `E_r`, extra evidence commit, task HEAD movement,
  multiparent evidence, dirty state or unprovable identity fails closed. Recovery never moves a
  branch pointer or discards content.

## 7. Real Temporary-Git End-To-End And Negatives

The formal-entry test executes:

```text
run_task.ps1 Submit
-> Planner ready
-> run_task.ps1 Approve
-> host
-> Developer subject S
-> Developer/Reviewer/QA/Integrator evidence and callbacks
-> local merge [primary_parent, S]
-> record-integration
-> human review
```

It proves `E_P` plus every dynamically produced execution/fix-loop evidence ref is readable at exact
commit/path/raw SHA and maps one-to-one, in order, to the actual durable invocations; task
branch/worktree HEAD stays `S` after every evidence/callback; execution evidence is absent from `S`
ancestry; merge and `record-integration` pass; and a captured Git command ledger contains no reset,
restore, stash, rebase, cherry-pick, force update, deletion or recreation.

Zero-write negatives cover evidence mixed with code, wrong path/blob/hash/header/model/status/subject/
action/attempt, multiparent or unknown parent, evidence order drift, task branch/worktree/subject drift,
dirty primary/task worktree and an extra commit. Every negative snapshots board bytes, primary/task
HEAD and worktree content before the writer and proves they remain unchanged.

## 8. Exact Scope And Non-Goals

Implementation/protocol/test allowlist is exactly seven paths:

1. `scripts/connlab_personal_task.py`
2. `scripts/connlab_serial_evidence_topology.py`
3. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
4. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
5. `tests/integration/test_connlab_nondestructive_evidence_topology.py`
6. `tests/integration/test_connlab_serial_complex_recovery.py`
7. `tests/unit/test_connlab_serial_complex_orchestrator_contract.py`

The Task, Plan, fixed Planner/Developer/Reviewer/QA/Integrator evidence paths and
`docs/task_board.md` are the only additional governance paths, for fifteen total. No change is
needed to `scripts/connlab_serial_complex.py`, product code,
backend/frontend/API/database/schema/
persistence/business rules, model routing, host creation, digest autocorrection, test consolidation,
Close performance or board history.

All forbidden categories remain false except governance `persistence=true` and `authority=true`.
Destructive actions, external mutation and push/release remain false.

## 9. Validation

```text
py -m pytest tests/integration/test_connlab_nondestructive_evidence_topology.py -q
py -m pytest tests/integration/test_connlab_serial_complex_recovery.py -q
py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m py_compile scripts/connlab_personal_task.py scripts/connlab_serial_complex.py scripts/connlab_serial_evidence_topology.py
python line-budget check: connlab_personal_task.py <= 500, connlab_serial_evidence_topology.py <= 500, new integration test <= 500
git diff --check
```

The integration suite must specifically prove zero-, one- and restart-resumed normal role flows,
correct digest autocorrection, blocker writer/resume, Planner approval, complex Close and retained
closeout remain green. All implementation paths and Git/evidence topology are inspected exactly.

Rollback is a local revert of the bounded implementation commit; there is no data migration, ref
movement or cleanup.

## 10. Exact Approved Request

The following code fence is the canonical single-line UTF-8 approved request for `Approve`:

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT","summary":"Persist every complex execution callback evidence as a sequential primary evidence-only commit so the task branch remains at the exact reviewed subject and verified integration needs no destructive topology recovery.","kind":"planned","may_touch":["scripts/connlab_personal_task.py","scripts/connlab_serial_evidence_topology.py",".agents/skills/connlab-lane-orchestrator/SKILL.md","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","tests/integration/test_connlab_nondestructive_evidence_topology.py","tests/integration/test_connlab_serial_complex_recovery.py","tests/unit/test_connlab_serial_complex_orchestrator_contract.py","tasks/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT.md","docs/task_governance_nondestructive_evidence_topology_closeout_plan.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md","docs/task_board.md"],"expected_file_count":15,"classification_reason":"Complex governance persistence and integration-authority correction with independent Reviewer, mandatory QA and Integrator gates; the bounded amendment only repairs two stale test fixtures and changes no product, API, database, schema, business-rule, external or destructive behavior.","targeted_validation":["py -m pytest tests/integration/test_connlab_nondestructive_evidence_topology.py -q","py -m pytest tests/integration/test_connlab_serial_complex_recovery.py -q","py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m py_compile scripts/connlab_personal_task.py scripts/connlab_serial_complex.py scripts/connlab_serial_evidence_topology.py","python line-budget check: connlab_personal_task.py <= 500, connlab_serial_evidence_topology.py <= 500, test_connlab_nondestructive_evidence_topology.py <= 500","git diff --check","real temporary-Git end-to-end: canonical Submit through human review with Planner prefix plus dynamic execution/fix-loop primary evidence-only commits, stable task subject HEAD, successful record-integration, frozen Plan route audit, forbidden-operation absence and zero-write drift negatives"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":true,"authority":true,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 11. Stop Point

Wait for explicit User approval of the committed amended Plan ref and approved-request SHA-256. Keep
the existing host, `DEVELOPER_BLOCKED` state and five-path dirty patch unchanged. Do not resume the
Developer or modify runtime/protocol/tests before approval.
