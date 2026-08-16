# TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION Planner Evidence

TASK_ID: TASK_GOVERNANCE_PERSONAL_SERIAL_V2_WRITER_RECOVERY_CORRECTION
ROLE: Planner
STATUS: ready_for_user_approval
SUBJECT: 3d0a2fec2d31ade9e448233226f0aa3e00fd8a84
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:authority
ACTION_ID: 7e76a4d28ccb2f07e72a4c95667ca21c0c34215cf60944a532ffcdf448be5ce5
ATTEMPT: 1
NEXT: User
BLOCKER: none

## Read-only authority facts

- Active board state was `running / planning / Planner / attempt 1 / callback_pending`.
- Durable pending callback identity matched this Planner action ID and attempt.
- Primary was clean; HEAD at inspection was `3d0a2fec2d31ade9e448233226f0aa3e00fd8a84`.
- The Planner read the governing rules, complete active board, active orchestrator skill, relevant
  protocol, and actual implementation/tests.
- No Task/Plan for this active task existed before this callback and no implementation test was run.

## Root-cause findings

- Native attempts are allocated from cross-role `current_attempt`.
- bounded Developer reentry repeats that cross-role allocation.
- durable invocation/timing identities lack continuous per-role reconciliation.
- complete board validation occurs after `os.replace`.
- blocked v2 approval bypasses exact committed Plan/manifest validation.
- scope amendment synchronizes paths but not the exact committed validation manifest.
- controlled `connlab_serial_phase2.py` and `connlab_personal_task.py` exceed 500 lines.

## Planning decision

Authorize exactly one new mechanical module: `scripts/connlab_serial_native_action.py`.

It owns native-action construction and shared role-local attempt-history validation. The existing
phase2 module re-exports the builder and uses the same derived Developer attempt for bounded fixes.
The board validates complete role history and complete rendered/temporary bytes before replacement.
The writer validates every blocked v2 reapproval against the exact committed Plan and atomically stores
its manifest with scope and paths.

The approved implementation/test scope is exactly six paths; fixed Task, Plan, five evidence paths,
and board make the complete 14-path governance scope. Any additional path requires User direction.

## Safety

The Planner made no repository, board, index, ref, branch, worktree, temporary fixture, external
resource, or Git write and performed no cleanup, push, reset, restore, stash, rebase, cherry-pick,
archive, retirement, deletion, or movement.

STATUS: ready_for_user_approval

NEXT: User

BLOCKER: none
