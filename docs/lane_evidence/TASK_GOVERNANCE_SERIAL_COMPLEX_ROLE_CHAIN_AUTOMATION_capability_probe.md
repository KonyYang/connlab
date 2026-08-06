# Serial Complex Native Capability Probe Evidence

Status: `PARTIAL_BLOCKED_NO_CLEANUP_AUTHORITY`

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

## Unproven capability and blocker

The required exact closeout order (`retire_then_archive` or `archive_then_retire`) is not proven.
Testing either order would mutate native task/worktree lifecycle state and constitutes cleanup, which
the current User approval explicitly withholds. Therefore no closeout order may be frozen, no cutover
manifest may be generated, and no second approval may be requested from this evidence alone.

Both probe tasks and worktrees remain clean and retained. The next authorized action, if the User
wants to continue, is a separate exact approval to test retirement/archive lifecycle for these two
named probe tasks only. Until then the governance task remains active in pre-cutover implementation;
it must not be marked human-review complete or cut over.
