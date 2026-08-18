# TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION

Status: `cutover_complete`

Revision: `7.4.1`

Current phase: `closed atomically under board schema v2`

Planning controller: Codex task `019fc491-21b0-77b0-bf18-53f53a366a7c`

Future runtime orchestrator: Codex task `019fb3d4-12a5-73b3-be8e-e59686fa39a9`

Revision 6.1 implementation completion commit:
`49c6df30f38ce7b7f0df95a9509e3d005914426a`

## Authority And Completion State

The Revision 7.4.1 atomic cutover commit activates the version-2 serial workflow, migrates the board,
closes this Task and releases active in one Git boundary. The version-2 board is the live authority.

The prior manifest/permission/cutover-command design is superseded by this Task and the Revision 7.4.1
Plan. Git history retains the old text for audit; it is no longer implementation authority.

## Goal

After one approved local atomic cutover, a normal complex task exposes only three User interactions:

1. submit the requirement;
2. approve the committed Planner plan;
3. inspect the integrated result and say `关闭`.

After plan approval, Developer, Reviewer, QA and Integrator run serially and automatically. Reviewer
or QA findings return automatically to Developer and repeat the required gates. Only a scope change,
destructive action, integration conflict, ambiguous authority, or another unresolved blocker returns
to the User.

WIP remains one. Submit checks occupancy before parsing or classification. While a task is active,
the new request receives a zero-write wait response and is not stored; after close, the User submits
it again against the idle board. There is never more than one active owner.

## Repository-Confirmed Problems Being Corrected

1. `plan-cutover` without `--expected-board-sha256` returns
   `BLOCKED_BOARD_HASH_MISMATCH`; adding that argument returns
   `BLOCKED_ARGUMENT_COMBINATION`.
2. `scripts/connlab_personal_task.py` unconditionally returns
   `BLOCKED_CUTOVER_NOT_AUTHORIZED` for all three cutover commands.
3. No full manifest generator, materializer, commit verifier, or rollback implementation exists.
   `apply_cutover_payload` is only a small fixture-style permission test.
4. Ordinary v1 `close` would release active before migration and is forbidden for this governance
   task.
5. Current normative rules and runtime entry still keep the complex role chain dormant.

## Planning-Revision Scope

This planning revision changes exactly two paths:

1. `tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md`
2. `docs/task_governance_serial_complex_role_chain_automation_plan.md`

It changes no runtime file, board block, permission, probe resource, worktree, thread, branch, remote,
archive, index, product code, or external repository.

## One-Time Atomic Cutover Contract

There is no manifest file, target-bytes bundle, permission-receipt framework, or public cutover
command family. The immutable candidate Git commit is the complete content bundle and approval
object.

The Controller prepares a direct-child candidate commit in a fresh isolated temporary Git repository
whose top-level and literal parent are verified before any target bytes are copied, while the primary
worktree and v1 board remain byte-unchanged. It then shows the exact parent, commit, path list and full pre-cutover diff
to the User. Only an explicit approval of that literal candidate commit and literal parent authorizes
a fast-forward of `master`; the application command must not derive either value from a mutable ref.

The candidate commit changes exactly these 16 paths:

1. `AGENTS.md`
2. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
3. `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
4. `docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`
5. `scripts/run_task.ps1`
6. `scripts/connlab_execution_gate.ps1`
7. `scripts/connlab_personal_task.py`
8. `scripts/connlab_serial_board.py`
9. `scripts/connlab_serial_complex.py`
10. `docs/task_board.md`
11. `tasks/TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION.md`
12. `docs/task_governance_serial_complex_role_chain_automation_plan.md`
13. `tests/unit/test_connlab_serial_complex_orchestrator_contract.py`
14. `tests/unit/test_connlab_execution_gate_script.py`
15. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
16. `tests/integration/test_connlab_serial_complex_recovery.py`

No other path may differ between the candidate parent and candidate commit.

The same candidate commit must:

- remove the unused cutover command family and permission/manifest fixture code;
- activate the v2 serial-complex rules, runtime skill, entry and gate;
- migrate the board from v1 human review to v2 idle;
- set `active=null`, require the compatibility queue fields to remain `queue=[]` and
  `next_enqueue_sequence=1`, preserve retained history, and record this governance task in
  `last_closed` using the fixed non-self-referential decision text
  `User approved the exact pre-reviewed local atomic cutover commit in controller task 019fc491-21b0-77b0-bf18-53f53a366a7c.`;
- mark this Task and Plan `cutover_complete`;
- contain the bounded temporary-repository end-to-end regression.

No ordinary v1 `close` runs before the candidate is applied. At the commit boundary the parent still
has the v1 active governance task and the child has v2 idle, so no committed idle authority gap exists.

## Rollback

After successful fast-forward and before any v2 task activation, the only rollback is:

```powershell
git revert --no-edit $approvedCutoverCommit
```

The revert must restore a tree equal to the candidate parent, including v1 human review with this
governance task still active. No reset, restore, stash, clean, alternate patch, force operation, or
lifecycle cleanup is authorized. If candidate application fails before HEAD changes, there is no
cutover commit to revert; stop and report the unchanged HEAD and any dirty paths.

The fixed board decision text deliberately contains neither the future candidate hash nor the later
approval wording. The User's external approval binds the exact candidate commit, parent and diff;
attempting to embed that future hash in the candidate would create a Git self-reference.

## Acceptance

- The candidate parent is the clean planning-revision HEAD and the candidate has exactly one parent.
- The candidate diff is exactly the 16-path allowlist and passes `git diff --check`.
- An occupied v2 submit returns `BLOCKED_ACTIVE_TASK_RUNNING`, `changed=false`, without parsing or
  persisting the request; a later idle submit performs the first classification and activation.
- The occupied-submit return occurs immediately after board parsing and before `resolve_primary`,
  any Git/worktree command, `writer_lock`, JSON parsing or classifier invocation.
- `run_task.ps1` exposes no `ActivateNext`; the v1-only helper token fails closed with zero writes
  against every v2 board and exists solely for exact rollback compatibility.
- The v2 `block` writer accepts only a validated `connlab.serial-task-blocker` whose stage equals the
  current complex phase, and `resume` uses its frozen `resume_phase`.
- `record-integration` verifies the committed board transition, primary merge commit/parents/tree,
  exact reviewed task-worktree HEAD/clean state and committed evidence bytes before writing human review.
- The bounded temporary-repository test proves v1 human review -> one cutover commit -> v2 idle and
  proves an exact `git revert` restores the parent tree.
- The approved regression suite passes on the candidate commit before User approval and after
  fast-forward.
- `inspect` and the execution gate accept v2 idle after cutover.
- Cutover completion is reported as `complex workflow enabled and repository-level validation
  passed`; it must not claim that the native Codex role chain has already passed end to end.
- The first ordinary complex requirement is the monitored first real run, not a pilot gate or a new
  governance task. Failure retains its active slot and typed blocker under the normal recovery rules.
- Daily complex work preserves WIP=1 and needs no User approval for role dispatch, worktree-host
  creation, Reviewer/QA retry, integration, or retained closeout.
- generation-1, canonical index, Task-A, retained/probe resources and external repositories are
  unchanged.
- Primary ends clean on local `master`; no push, lifecycle operation, pilot, or cleanup occurs.

## Approval Gate

Approval of this Revision 7.4.1 authorizes only preparation and validation of the exact candidate commit;
it does not apply it. The Controller must return the real candidate commit, parent and exact diff for
a separate explicit cutover decision. A plain `关闭` must not be interpreted as cutover approval.

The cutover decision must quote the literal 40-hex candidate and parent and explicitly authorize
`git merge --ff-only <literal-approved-candidate>` to update all 16 allowlisted paths, including
`.agents/skills/connlab-lane-orchestrator/SKILL.md`. If the sandbox still refuses that exact write,
stop without an alternate write strategy; do not restore a permission probe, receipt or manifest.

After that approval, the Controller verifies the candidate ref still equals the approved literal but
executes the literal hash, never the ref-derived value. No second routine approval, manifest approval,
permission receipt, runtime activation message or pilot is part of the cutover.

`STATUS: CUTOVER_COMPLETE`
