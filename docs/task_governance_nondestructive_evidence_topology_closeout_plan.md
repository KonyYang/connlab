# TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT Plan

Status: `ready_for_user_approval`

## 1. Outcome And Chosen Model

Choose exactly one ownership model: **primary sequential evidence-only commits**. Each Developer,
Reviewer, QA and Integrator evidence commit advances primary, never the task branch/worktree. Existing
board-only authority commits remain board-only and the task worktree remains clean at the exact
reviewed subject.

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
callback writer validates it. Ordered board evidence refs are `E_D, E_R, E_Q, E_I`. After committed
`C_I` is integration-ready, the local merge has parents `[C_I, S]`; `record-integration` binds
`subject_commit=branch_head=S` and those exact evidence refs. No `E_r` is in `S` ancestry.

## 4. File-Level Implementation

### `scripts/connlab_personal_task.py`

Before applying an execution-role `consume-callback`, extend repository verification at the existing
callback-evidence seam to require:

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
  MODEL_ROUTE_REASON, ACTION_ID and ATTEMPT binding matching durable invocation/callback facts.

Any mismatch raises a typed `BLOCKED_CALLBACK_INVALID`, `BLOCKED_SUBJECT_MISMATCH`,
`BLOCKED_WORKTREE_FACTS` or `BLOCKED_EVIDENCE_INVALID` before board mutation. Planner evidence keeps
its existing pre-host planning behavior; the strict topology applies to Developer/Reviewer/QA/
Integrator.

At integration, revalidate that accepted execution-role evidence commits are ordered primary
ancestors before the merge parent and retain their one-path evidence-only identity.

### Orchestrator skill and normative protocol

Update `.agents/skills/connlab-lane-orchestrator/SKILL.md` and
`docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md` to name primary as the sole execution
evidence owner and freeze the exact `B_r -> A_r -> E_r -> C_r` sequence. Roles run and review the
task worktree but write/commit only their fixed evidence path on clean primary after invocation.
These two texts are required so a restart does not fall back to the defective task-worktree commit
habit; no broader policy document changes.

### Integration regression

Extend `tests/integration/test_connlab_serial_complex_recovery.py`; do not add another test module.
The existing file already owns the disposable repository and complex recovery fixtures, so keeping
the end-to-end there avoids a second fixture/contract implementation.

## 5. Crash Recovery

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

## 6. Real Temporary-Git End-To-End And Negatives

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

It proves all four evidence refs are readable at exact commit/path/raw SHA; task branch/worktree HEAD
stays `S` after every evidence/callback; evidence is absent from `S` ancestry; merge and
`record-integration` pass; and a captured Git command ledger contains no reset, restore, stash,
rebase, cherry-pick, force update, deletion or recreation.

Zero-write negatives cover evidence mixed with code, wrong path/blob/hash/header/model/status/subject/
action/attempt, multiparent or unknown parent, evidence order drift, task branch/worktree/subject drift,
dirty primary/task worktree and an extra commit. Every negative snapshots board bytes, primary/task
HEAD and worktree content before the writer and proves they remain unchanged.

## 7. Exact Scope And Non-Goals

Implementation/protocol/test allowlist is exactly four paths:

1. `scripts/connlab_personal_task.py`
2. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
3. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
4. `tests/integration/test_connlab_serial_complex_recovery.py`

The Task, Plan, fixed Planner/Developer/Reviewer/QA/Integrator evidence paths and
`docs/task_board.md` are the only additional governance paths, for twelve total. No change is needed
to `scripts/connlab_serial_complex.py`, product code, backend/frontend/API/database/schema/
persistence/business rules, model routing, host creation, digest autocorrection, test consolidation,
Close performance or board history.

All forbidden categories remain false except governance `persistence=true` and `authority=true`.
Destructive actions, external mutation and push/release remain false.

## 8. Validation

```text
py -m pytest tests/integration/test_connlab_serial_complex_recovery.py -q
py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
py -m py_compile scripts/connlab_personal_task.py scripts/connlab_serial_complex.py
git diff --check
```

The integration suite must specifically prove zero-, one- and restart-resumed normal role flows,
correct digest autocorrection, blocker writer/resume, Planner approval, complex Close and retained
closeout remain green. All implementation paths and Git/evidence topology are inspected exactly.

Rollback is a local revert of the bounded implementation commit; there is no data migration, ref
movement or cleanup.

## 9. Exact Approved Request

The following code fence is the canonical single-line UTF-8 approved request for `Approve`:

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT","summary":"Persist Developer, Reviewer, QA and Integrator evidence as sequential primary evidence-only commits so the task branch remains at the exact reviewed subject and verified integration needs no destructive topology recovery.","kind":"planned","may_touch":["scripts/connlab_personal_task.py",".agents/skills/connlab-lane-orchestrator/SKILL.md","docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md","tests/integration/test_connlab_serial_complex_recovery.py","tasks/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT.md","docs/task_governance_nondestructive_evidence_topology_closeout_plan.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_planner.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_developer.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_reviewer.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_qa.md","docs/lane_evidence/TASK_GOVERNANCE_NONDESTRUCTIVE_EVIDENCE_TOPOLOGY_CLOSEOUT_integrator.md","docs/task_board.md"],"expected_file_count":12,"classification_reason":"Complex governance persistence and integration-authority correction with independent Reviewer, mandatory QA and Integrator gates; no product, API, database, schema, business-rule, external or destructive change.","targeted_validation":["py -m pytest tests/integration/test_connlab_serial_complex_recovery.py -q","py -m pytest tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m py_compile scripts/connlab_personal_task.py scripts/connlab_serial_complex.py","git diff --check","real temporary-Git end-to-end: canonical Submit through human review with four primary evidence-only commits, stable task subject HEAD, successful record-integration, forbidden-operation absence and zero-write drift negatives"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":true,"authority":true,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 10. Stop Point

Wait for explicit User approval of the committed Plan ref and approved-request SHA-256. Do not create
the task host or modify runtime/protocol/tests before approval.

