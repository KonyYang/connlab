# ConnLab Serial Complex Role-Chain Automation — Cutover Simplification Plan

> **For the current controller:** execute inline only after explicit User approval. Do not create
> agents, threads, lanes, branches or worktrees while preparing or implementing this governance
> correction.

**Goal:** Replace the uncallable manifest-based cutover with one reviewable, content-addressed local
Git commit that simultaneously activates the v2 serial workflow, migrates the board, closes this
governance task and releases active.

**Architecture:** Keep the live primary worktree on v1 human review while a direct-child candidate
commit is assembled through a temporary Git index and validated in a bounded temporary repository.
The candidate commit itself is the exact target-content bundle. The User approves its real commit ID
and diff, after which `master` fast-forwards to it.

**Tech Stack:** Python 3.11+, PowerShell, pytest, Git plumbing and ordinary local Git commits.

## Global Constraints

- Status: `CUTOVER_COMPLETE`.
- Task: `TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION`.
- Current live authority remains board v1 `implemented_pending_human_review/human_review`.
- WIP is one; occupied submissions wait with zero writes; no concurrent task or implementation owner exists.
- No product/backend/frontend/API/database/persistence/business-rule change.
- No manifest file, base64 target bundle, permission receipt, cutover CLI family or lifecycle cleanup.
- No push, remote mutation, pilot, archive, retirement, handoff, branch deletion, reset, restore,
  stash, clean, agent creation or worktree creation.
- This planning revision changes only the existing Task and Plan.

---

## 1. Discovery Gate And Verified Facts

### Confirmed by the User

- The steady-state User contract is requirement -> plan approval -> result inspection and `关闭`.
- Developer -> Reviewer -> QA -> Integrator is automatic after plan approval.
- Only scope changes, destructive actions or unresolved blockers return to the User.
- The current task must remain active in human review while this correction is planned.
- One exact local atomic cutover commit is preferred over a repository manifest/permission framework.

### Confirmed by the repository

- Planning base before this revision: `49c6df30f38ce7b7f0df95a9509e3d005914426a`, clean local
  `master`.
- Board state: `implemented_pending_human_review`, active Task ID matches, phase `human_review`,
  blocker null and the compatibility queue fields empty/inert.
- Calling `plan-cutover` without `--expected-board-sha256` returns
  `BLOCKED_BOARD_HASH_MISMATCH` with zero board writes.
- Supplying `--expected-board-sha256` is rejected as `BLOCKED_ARGUMENT_COMBINATION` before board
  loading.
- The writer unconditionally returns `BLOCKED_CUTOVER_NOT_AUTHORIZED` for `plan-cutover`,
  `apply-cutover` and `verify-cutover-commit`.
- `apply_cutover_payload` accepts only `task_id, source_head, paths, permission_proof`, reruns a
  handle probe and invokes a supplied callback. It is not the planned generator/materializer/verifier.
- `migrate_v1_to_v2` already performs the required pure board transition from validated v1 human
  review to v2 idle while preserving retained history and requiring inert empty queue fields.

### Planning inference

The current human-review state cannot be legally reopened by the v1 helper. Therefore a separate
pre-cutover runtime-code correction would create another authority-transition problem. The minimal
safe solution is to place the correction, activation, migration and close in the same candidate
commit, built outside the live worktree and approved by exact Git identity.

No discovery question remains open.

## 2. Superseded Revision 6.1 Design

Revision 7.4.1 supersedes every Revision 6.1 requirement for:

- `plan-cutover`, `apply-cutover`, `verify-cutover-commit`;
- a cutover manifest or `TARGET_SET_SHA256`;
- `target_bytes_base64`, source/target byte bundles or manifest rollback records;
- intrinsic permission probing, permission receipts or permission-drift approval loops;
- a runtime activation message or mandatory pilot;
- retirement, archive or any lifecycle ordering.

Those concepts remain visible only in Git history. They must not be implemented, generated or
required by the Revision 7.4.1 candidate.

## 3. Exact Candidate-Cutover Allowlist

The direct-child candidate commit changes exactly 16 paths:

| Path | Exact cutover responsibility |
|---|---|
| `AGENTS.md` | Make the personal serial v2 complex workflow normative and freeze the three-interaction contract. |
| `.agents/skills/connlab-lane-orchestrator/SKILL.md` | Activate the automatic state-driven Planner/Developer/Reviewer/QA/Integrator loop. |
| `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md` | Define v2 WIP=1, zero-write waiting and automatic post-approval routing. |
| `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md` | Remove manifest/permission commands and document the final runtime contract. |
| `scripts/run_task.ps1` | Route submit, approval and close intents into the v2 personal writer/orchestrator path. |
| `scripts/connlab_execution_gate.ps1` | Accept and gate v2 idle/active/human-review states without legacy role routing. |
| `scripts/connlab_personal_task.py` | Remove the unused public cutover command family and obsolete arguments while retaining v1/v2 daily commands. |
| `scripts/connlab_serial_board.py` | Check occupancy before classification and keep v2 queue compatibility fields inert. |
| `scripts/connlab_serial_complex.py` | Remove permission/manifest fixture functions; retain classifier, role transitions and retained closeout. |
| `docs/task_board.md` | Atomically migrate v1 human review to v2 idle, close this governance task and release active. |
| `tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md` | Record Revision 7.4.1 `cutover_complete`. |
| `docs/task_governance_serial_complex_role_chain_automation_plan.md` | Record Revision 7.4.1 `cutover_complete`. |
| `tests/unit/test_connlab_serial_complex_orchestrator_contract.py` | Delete obsolete permission/manifest tests and assert the reduced public contract. |
| `tests/unit/test_connlab_execution_gate_script.py` | Prove v2 gate routing and legacy fail-closed behavior. |
| `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` | Prove normative files expose only the intended automatic serial role contract. |
| `tests/integration/test_connlab_serial_complex_recovery.py` | Add the one bounded temporary-repository atomic-cutover/revert test. |

No file is created or deleted. The previously proposed cutover-manifest path remains nonexistent.

## 4. Atomic Authority Transition

The candidate parent must contain:

- clean primary `master`;
- board v1 `implemented_pending_human_review/human_review`;
- this active governance Task ID, blocker null and passed validation;
- compatibility queue fields exactly `queue=[]` and `next_enqueue_sequence=1`;
- unchanged retained history, generation-1, canonical index, Task-A and probe resources.

The candidate board target is produced by the existing pure `migrate_v1_to_v2` behavior and must
contain in the same commit:

- schema version `2`;
- state `idle`;
- `active=null`;
- exact inert queue values `queue=[]`, `next_enqueue_sequence=1` and the retained-history JSON value;
- `last_closed.task_id=TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION`;
- `last_closed.disposition=closed atomically by approved v2 cutover`;
- `last_closed.decision_ref=User approved the exact pre-reviewed local atomic cutover commit in
  controller task 019fc491-21b0-77b0-bf18-53f53a366a7c.` and one recorded close timestamp.

The fixed decision text contains no candidate hash or future approval quotation, avoiding Git commit
self-reference. The external User approval in section 6 binds the real candidate commit, parent and
diff before the candidate becomes live authority.

The other 15 targets activate the new rules and remove the dead cutover framework. Therefore the
candidate parent remains v1 active, while the candidate child is v2 idle with active rules. There is
no ordinary v1 close and no committed authority gap.

## 5. Candidate Construction Without Live-Worktree Activation

After the User approves this Revision 7.4.1 plan, the Controller performs these bounded preparation
steps. They do not move `master`, edit the primary worktree, or change the board.

- [ ] Record the clean planning-revision HEAD as `$cutoverParent` and require it remain unchanged.
- [ ] Create a new isolated temporary Git repository, prove `git rev-parse --show-toplevel` points to
      that exact directory, check out the literal `$cutoverParent`, and require a clean baseline.
- [ ] Copy only the 16 reviewed target files into that repository; never copy or reuse another
      candidate's `.git` metadata.
- [ ] Create one ordinary direct-child commit with message
      `governance: activate personal serial complex workflow v2`, and retain it at
      `refs/codex/cutover-candidates/serial-complex-v2`.
- [ ] Check out that exact candidate into a bounded temporary repository under `tmp/` and run all
      section 9 validation there.
- [ ] Leave the primary board and worktree byte-unchanged while returning the exact candidate facts
      and diff to the User.

The candidate Git object is the content-addressed target bundle. No repository manifest, encoded
bytes file, target-hash schema or permission receipt is created.

## 6. Exact Pre-Cutover Review And Approval

The Controller derives real values from the candidate ref:

```powershell
$cutoverRef = 'refs/codex/cutover-candidates/serial-complex-v2'
$cutoverCommit = (git rev-parse $cutoverRef).Trim()
$cutoverParent = (git rev-parse "$cutoverCommit^").Trim()
git status --short --branch
git diff --check $cutoverParent $cutoverCommit
git diff --name-only $cutoverParent $cutoverCommit
git show --format=fuller --stat $cutoverCommit
git diff --binary $cutoverParent $cutoverCommit -- `
  AGENTS.md `
  .agents/skills/connlab-lane-orchestrator/SKILL.md `
  docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md `
  docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md `
  scripts/run_task.ps1 `
  scripts/connlab_execution_gate.ps1 `
  scripts/connlab_personal_task.py `
  scripts/connlab_serial_board.py `
  scripts/connlab_serial_complex.py `
  docs/task_board.md `
  tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md `
  docs/task_governance_serial_complex_role_chain_automation_plan.md `
  tests/unit/test_connlab_serial_complex_orchestrator_contract.py `
  tests/unit/test_connlab_execution_gate_script.py `
  tests/unit/test_task_scoped_role_thread_lifecycle_governance.py `
  tests/integration/test_connlab_serial_complex_recovery.py
```

The Controller must show the full real output and stop. Cutover authorization is valid only when the
User explicitly approves the exact `$cutoverCommit`, exact `$cutoverParent` and exact 16-path diff.
A plain `关闭`, approval of this planning revision, path-only approval or conversational summary is
not cutover authorization.

No separate manifest approval, permission proof, target hash, runtime message or pilot approval is
required. If the execution environment cannot write an exact target during the approved fast-forward,
that is an unresolved blocker: stop without trying an alternate permission or write strategy.

The exact cutover approval must additionally authorize the one-time Git write across all 16 named
paths, explicitly including `.agents/skills/connlab-lane-orchestrator/SKILL.md`. This is an execution
condition, not a permission-receipt schema or additional approval system. If the sandbox refuses the
approved operation, the Controller stops and reports the denial.

## 7. Apply And Rollback

After exact candidate approval, apply only the two literal hashes quoted by the User. The Controller
must render the final execution capsule after approval with the real 40-hex values directly inside the
two single-quoted assignments. The metavariables below describe that required shape and are not an
executable pre-approval command; ref-derived assignments, environment substitutions and abbreviated
hashes are invalid.

```powershell
$approvedCutoverCommit = '<user-approved-literal-40-hex-candidate>'
$approvedCutoverParent = '<user-approved-literal-40-hex-parent>'

if ((git rev-parse HEAD).Trim() -ne $approvedCutoverParent) {
    throw 'Cutover parent drift.'
}
if ((git rev-parse "$approvedCutoverCommit^").Trim() -ne $approvedCutoverParent) {
    throw 'Candidate parent mismatch.'
}
if ((git rev-parse 'refs/codex/cutover-candidates/serial-complex-v2').Trim() -ne $approvedCutoverCommit) {
    throw 'Candidate ref drift.'
}
if (git status --porcelain) { throw 'Primary is dirty.' }
git merge --ff-only $approvedCutoverCommit
if ((git rev-parse HEAD).Trim() -ne $approvedCutoverCommit) {
    throw 'Cutover HEAD mismatch.'
}
```

The exact User approval also authorizes that one `git merge --ff-only` operation to update the full
16-path allowlist, including the currently restricted `.agents` skill path. If the sandbox rejects
the write, stop. Do not retry through a ref, edit files individually, request a repository permission
receipt, regenerate a candidate or use another Git strategy.

Run section 9 immediately. No v2 request may activate until validation passes.

If post-cutover validation fails while HEAD still equals the candidate and no v2 task has activated,
the User's exact candidate approval also authorizes only this rollback:

```powershell
git revert --no-edit $approvedCutoverCommit
git diff --exit-code $approvedCutoverParent HEAD
py scripts/connlab_personal_task.py inspect --repo-root D:\PythonProject\connlab --json
git status --short --branch
```

The revert result must be clean and restore v1 human review with this governance Task ID active. No
`reset`, `restore`, `checkout`, stash, clean, amend, alternate patch or force operation is allowed.
If fast-forward fails before HEAD changes, there is no applied cutover to revert; report HEAD/status
and stop.

## 8. Steady-State Daily Complex Flow

```text
User submits requirement
  -> runtime orchestrator classifies and occupies WIP
  -> fresh read-only Planner produces committed Task/Plan
User approves Planner plan
  -> approval transition/commit
  -> one task worktree host
  -> Developer commit
  -> fresh Reviewer
  -> fresh QA
  -> fresh Integrator
  -> verified primary integration
  -> implemented_pending_human_review
User inspects and says 关闭
  -> retained closeout verification/commits
  -> idle
Next requirement is submitted again against idle and only then classified
```

After plan approval, no User approval is required for host creation, Developer dispatch, Reviewer/QA
dispatch, bounded Reviewer/QA fix loops, Integrator dispatch, the approved non-conflicting integration
transaction or retained closeout.

The runtime orchestrator continues automatically while transitions are provable. It returns to the
User only for:

- a path/scope/API/data/authority change outside the approved plan;
- a destructive action;
- dirty or divergent Git state that cannot be resolved by the already approved transaction;
- an integration conflict;
- an ambiguous callback/evidence/identity;
- a repeated or otherwise unresolved blocker.

WIP remains one from submit through final close. A submit against an occupied board returns
`BLOCKED_ACTIVE_TASK_RUNNING`, `changed=false`, immediately after the raw board is parsed and before
`resolve_primary`, any Git/worktree operation, writer-lock acquisition, JSON parsing or classifier
invocation. It stores nothing and creates no task resource. After close, the User submits the
requirement again; the idle transition then performs normal repository verification, classification
and activation.

The daily PowerShell entry exposes only `Submit`, `Approve` and `Close`. The Python parser retains
the version-1 `activate-next` token solely so the exact Git revert restores and can validate the
parent workflow; under version 2 that token returns `BLOCKED_LEGACY_MODE_FROZEN` with zero writes.

Repository-level cutover validation does not execute the native Codex Planner/Developer/Reviewer/QA/
Integrator chain. After cutover the completion statement is limited to: `complex workflow enabled and
repository-level validation passed`. It must not claim that real role handoff has passed end to end.

The first ordinary complex requirement submitted under the three-interaction contract is also the
monitored first real run. It is not a pilot, does not need a separate approval, and does not create a
new governance task. The runtime orchestrator records each normal durable transition. Any failure
keeps that requirement active with its typed blocker; only an unresolved blocker returns to the User.

## 9. Validation

The candidate and applied commit must run:

```powershell
py -m pytest `
  tests/unit/test_connlab_personal_serial_workflow.py `
  tests/unit/test_connlab_serial_classifier.py `
  tests/unit/test_connlab_serial_complex_state.py `
  tests/unit/test_connlab_serial_complex_worktree.py `
  tests/unit/test_connlab_serial_complex_orchestrator_contract.py `
  tests/unit/test_connlab_execution_gate_script.py `
  tests/unit/test_task_scoped_role_thread_lifecycle_governance.py `
  tests/integration/test_connlab_serial_complex_recovery.py -q

py scripts/connlab_personal_task.py inspect --repo-root D:\PythonProject\connlab --json
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/connlab_execution_gate.ps1 -RepositoryRoot D:\PythonProject\connlab -Intent Inspect -Json
git diff --check $approvedCutoverParent $approvedCutoverCommit
git diff --name-only $approvedCutoverParent $approvedCutoverCommit
git status --short --branch
```

Also verify generation-1 and canonical-index bytes/SHA-256/Git blobs, retained-history canonical
digest, Task-A evidence, both probe worktrees/threads and retained probe branch remain unchanged.

The bounded recovery integration suite must also use the real PowerShell/helper entry points, never
direct board mutation, to prove:

- active simple and active complex submissions both return the same zero-write wait result before
  request parsing; a real `GIT_TRACE` probe and pre-existing lock prove that this path invokes neither
  Git nor the writer lock; after close, a resubmitted requirement is classified and activated;
- `DEVELOPER_BLOCKED -> development` and `INTEGRATION_BLOCKED -> integration` each pass through the
  legal complex `block` writer and explicit `resume`;
- submit -> Planner ready -> Approve -> host -> Developer -> Reviewer -> QA -> Integrator -> verified
  `record-integration` -> Close -> retained closeout -> idle;
- dirty task worktree, forged merge/evidence facts, or an uncommitted integration-ready board is
  rejected before any board write.

The bounded atomic-cutover regression is
`test_atomic_cutover_commit_migrates_v1_human_review_to_v2_idle_and_reverts` in
`tests/integration/test_connlab_serial_complex_recovery.py`. It must:

1. initialize a temporary Git repository containing fixture versions of the exact 16 paths;
2. commit a v1 board in human review with inert empty queue fields and retained-history sentinels;
3. create one direct-child commit changing exactly the 16 paths;
4. fast-forward to that commit and prove v2 idle, `active=null`, exact close record, inert empty queue
   fields, preserved retained history, active runtime markers and clean Git status;
5. run `git revert --no-edit` for that exact commit and prove the final tree equals the v1 parent,
   including the active human-review board.

## 10. Implementation Checklist After Plan Approval

- [ ] Reconfirm primary clean and board unchanged at v1 human review.
- [ ] Prepare the 16 target files outside the primary worktree.
- [ ] Remove the public cutover command family and permission/manifest fixture code.
- [ ] Implement the bounded temporary-repository red/green regression.
- [ ] Update the four runtime rule/entry files for the three-interaction automatic chain.
- [ ] Produce the v2 idle board target and cutover-complete Task/Plan targets.
- [ ] Create the one direct-child candidate commit through a temporary index.
- [ ] Validate the candidate in the temporary repository.
- [ ] Show the exact commit, parent, 16 paths and full diff; stop for explicit User cutover approval.
- [ ] Render a final command containing the approved candidate and parent as literal 40-hex strings.
- [ ] Verify the mutable candidate ref still equals the approved literal, then fast-forward only the
      literal candidate and rerun repository-level validation.
- [ ] Stop on v2 idle; do not pilot, push, clean up, or activate another task.

## 11. Completion State

Revision 7.4.1 is applied as one direct-child commit: the runtime rules are active, the board is v2
idle, this governance Task is atomically closed, and no pilot, push, lifecycle cleanup or next-task
activation occurred. Repository-level validation does not claim a native role-chain end-to-end run.

`STATUS: CUTOVER_COMPLETE`
