# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE Planner Evidence

Status: implementation_tests_authorized / pending isolated corrective worktree creation and Developer implementation

## Discovery Gate

Current phase:
controlled v2 bootstrap corrective planning.

Current task/lane:
`CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE` /
`connlab-controlled-lane-orchestration-v2-thread-title-corrective`.

Why allowed:
the User authorized docs-only discovery after bootstrap failed closed before registry genesis.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- Planner Discovery and task execution protocols
- accepted automation/bootstrap task, plan, skill, role registry, and v2 protocol
- `bootstrap.py`, `state_machine.py`, `registry.py`, `contracts.py`, and focused tests
- native tool schemas for `set_thread_title`, `read_thread`, and `list_threads`
- actual read-only `list_threads` and `read_thread` outputs
- Git refs, status, worktree topology, file counts, and CTL code catalog

## Native Capability Findings

- `create_thread` cannot set an exact title.
- `set_thread_title` accepts exact `threadId` and `title` only.
- Its return is opaque and cannot be acknowledgement authority.
- `read_thread` directly returns the target thread ID and title.
- `list_threads` returns title and project facts, and its current callable schema declares optional
  `query`; filtered or unfiltered output remains discovery-only, unavailable or rejected query use
  fails closed, and exact filtering must still be local and by frozen thread ID.
- No native mutation call was made.

## Repository Findings

- discovery base is `62ded4291822e84512afcaf2e3b536b0b22fd230`;
- primary/index were clean before this governance pass;
- accepted bootstrap worktree is clean at `91c6b425`;
- TASK_367A worktree is clean at `53840b42`;
- production registry/controller/heartbeat/pilot do not exist;
- `bootstrap.py` is 300 lines, `state_machine.py` 280, registry test 485;
- current state/action path has no title-pending state and create ack requires `title_verified`;
- existing 39 codes cover every required title failure and recovery condition.

## Planner Decision

Create an independent planned-only corrective. Insert a separately journaled title action after
thread adoption and before heartbeat. Title mutation and exact read-back are separate scans, each
with at most one native tool call. Reuse the existing six commands and 39 codes. Extract title
logic to a new bounded module instead of expanding the 300-line bootstrap module.

The future implementation uses a new branch/worktree from an approved governance checkpoint.
The accepted bootstrap worktree remains retained and read-only.

## Scope Freeze

Future May Touch is exactly nine implementation/test/skill/protocol paths listed in the task.
`contracts.py`, `registry.py`, `cli.py`, PowerShell wrapper, AGENTS, products, existing mixed tests,
real runtime state, and retained worktrees are locked.

New coverage is bounded in two new test modules. The 485-line registry test permits only exact
line-neutral controller-ack expectation migration.

## Readiness

User intent, native capability, state flow, errors, recovery, May Touch, locks, test commands,
budgets, worktree strategy, rollback, and runtime boundary are explicit. Reviewer plan/readiness
re-gate passed after B1-B3 closure.

The User explicitly authorized implementation and tests within the Reviewer-approved exact
nine-path scope. A controlled local governance checkpoint and clean primary/index are required
before the Orchestrator creates the new isolated corrective worktree; the accepted bootstrap
worktree remains read-only and cannot be reused.

Runtime bootstrap/pilot, real registry/controller/heartbeat creation, fetch, push, migration,
archive, and cleanup remain unauthorized. Corrective acceptance must be followed by a separate
User runtime gate and a restart from verified registry absence.

Recommended next action: Orchestrator creates the isolated corrective worktree, then routes
Developer implementation.
