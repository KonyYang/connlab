# Serial Complex Native Capability Probe Evidence

Status: `COMPLETE_RETAINED_NO_FURTHER_LIFECYCLE_ACTION`

Date: 2026-08-06

Authority: Revision 5 first implementation approval. The User explicitly withheld cutover, actual
permission grant, production runtime message, pilot, push, and cleanup authority.

## Safe facts proven

The full read-only probe task was created from exact commit
`ead61ccd2143c304a2b82aff0e3bfecdd5a6ad11`:

- thread: `019fd6d8-7d13-7011-bc09-77ebc790919e`
- host: `local` (the task itself reported that host ID was not visible inside its context)
- cwd: `C:\Users\White\.codex\worktrees\84b1\connlab`
- Git state: detached HEAD at the exact source commit; porcelain status empty
- native isolation: registered linked worktree distinct from primary
- stateless role-agent probe: a temporary agent named `/root/stateless_capability_probe` was created
  with `fork_turns="none"`, reported the same cwd, and confirmed no inherited conversation context
- repository writes, commits, pushes, archive, retirement, production-role dispatch, and production
  activation messages: none
- task result: `STATUS: PROBE_FACTS_READY`

The first create request initially exposed no usable task/client identifier to the controller. A
bounded retry was made before task enumeration showed that the first request had succeeded. This
created a second read-only probe task:

- thread: `019fd6d8-e5e1-7961-9423-8e205e9e02c5`
- host: `local`
- cwd: `C:\Users\White\.codex\worktrees\fc39\connlab`
- Git state: detached HEAD at the same exact source commit; porcelain status empty
- repository changes: none
- task result: `STATUS: PROBE_FACTS_READY`

The duplicate is retained and disclosed. It must not be silently archived, retired, deleted, or
treated as production authority.

## Unproven capability and retained disposition

The required exact closeout order (`retire_then_archive` or `archive_then_retire`) is not proven.
Testing either order would mutate native task/worktree lifecycle state and constitutes cleanup, which
the original probe approval explicitly withheld. Revision 6 later removed lifecycle order from normal
closeout and cutover. This evidence therefore remains a completed discovery record, not a normal
closeout blocker.

## Authorized lifecycle attempt and fail-closed stop

The User later authorized exactly these two sequences:

1. thread `019fd6d8-7d13-7011-bc09-77ebc790919e`: handoff/retire, verify, archive, verify;
2. thread `019fd6d8-e5e1-7961-9423-8e205e9e02c5`: archive, verify, handoff/retire, verify.

The authorization required immediate stop on any failure or unverifiable state, with no force,
branch deletion, alternate cleanup strategy, or continuation of the other sequence. Preflight proved
primary `master@b0701d443110a5947bdffc8d01840abdea76ac1e` and both detached probe worktrees clean.

Sequence 1 stopped after its first operation:

- `handoff_thread` operation: `exec-a6bf75db-4f86-49f8-83e0-e0d360998c1c`
- final operation revision/status: `12` / `success`
- destination thread: `019fd73e-6aac-74b0-b404-70ff1be70f42`
- destination cwd: `D:\PythonProject\connlab`
- operation steps reported done: stash-source-changes, detach-worktree-branch,
  checkout-local-branch, apply-changes-to-local, switching-thread

Post-operation verification disproved the assumed retirement semantics:

- `C:\Users\White\.codex\worktrees\84b1\connlab` still existed, remained registered by
  `git worktree list`, stayed detached at `ead61ccd2143c304a2b82aff0e3bfecdd5a6ad11`, and was clean;
- the source task remained readable with its original worktree cwd;
- the saved-project checkout moved from `master@b0701d44` to
  `codex/connlabserial-complex-capability-p@ead61ccd`;
- no archive operation ran, and sequence 2 never started.

Under a separate exact User recovery authorization, only `git switch master` was executed after
rechecking the unexpected branch/HEAD, the preserved master ref, and clean status. Recovery proved:

- primary restored to `master@b0701d443110a5947bdffc8d01840abdea76ac1e` and clean;
- personal helper returned `ALLOW_INSPECT`;
- both `84b1` and `fc39` worktrees remained present and clean;
- destination thread remained idle; no additional handoff, archive, force, branch deletion, push, or
  lifecycle action occurred.

Conclusion: Codex `handoff_thread` is a checkout migration/toggle, not a proven worktree-retirement
primitive. Neither closeout order is validly proven, and the protocol must not treat handoff success
as retirement.

## Revision 6 disposition

The recorded failure completes lifecycle discovery. Both probe tasks and detached worktrees remain
retained, clean, and location-addressable at the exact identities above. Revision 6 closeout verifies
and records those resources without handoff, archive, unarchive, retirement, removal, pruning, branch
deletion, or another lifecycle experiment. Any later cleanup is a separate maintenance request and is
not part of implementation, human review, or cutover readiness.
