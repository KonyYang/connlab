# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF — Reviewer Evidence

Date: 2026-08-01

ROLE: Reviewer

STATUS: reviewer_blocked

NEXT: Developer

## Authority And Inspected Package

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Why allowed: primary `docs/task_board.md` records Task A as the sole WIP=`1` token owner in
  `gate_running/Reviewer`, with queue empty and paused/Quick Fix/parallel records null.
- Primary authority inspected read-only at
  `e5de0c4f2ecb0d01a33dabcacdcbd4549f186d8f`.
- Exact lane:
  `D:\PythonProject\connlab-worktrees\task-governance-active-context-deterministic-transition-and-event-handoff`.
- Branch: `lane/task-governance-active-context-deterministic-transition-and-event-handoff`.
- Review base: `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Prior reviewed implementation HEAD:
  `28d15b71dcd66d2befbb292e049446d11da0ec26`; prior Reviewer evidence commit:
  `1e4d080fb0b17a520aa5afb924fd62ffe4bf2203`.
- Full immutable fix/evidence HEAD independently re-gated:
  `6d449262473e628cdf239c5d9b54ae3a2ff2c4c8`.
- Exact branch/HEAD, base ancestry, clean lane/index, clean primary, and `git diff --check` passed.
- Base..HEAD contains the exact 23 approved implementation paths plus Developer and Reviewer
  evidence (`25` paths total). Focused prior-Reviewer..HEAD contains only the three helpers, four
  bounded tests, and Developer evidence (`8` paths). It has
  no product path, primary board/history, role registry/bundle, execution gate, worktree helper,
  V1/V2, Task B, package/lock, runtime, release, or real-data path.
- Read independently: `AGENTS.md`, primary board, approved Task/Plan, Planner and Developer
  evidence, review checklist, normative Task A contract, affected governance protocols/skills,
  all three helpers, `run_task.ps1`, and all new bounded tests. Candidate compact-read evidence
  was not used to reduce this full review.

## Final Re-gate Findings First

The bounded Developer pass closes the exact B1-B5 counterexamples recorded below: rollback output
is restricted to an existing independently proven temp tree with exclusive creation; dispatch
capsules are authority-bound or return `FULL_READ_REQUIRED`; frozen transition metadata and one
machine evidence record are required; complete maintenance records/current compact state are
checked; and the first heartbeat is measured from the preceding material event. Independent
reproductions for all five now fail closed and preserve their source repositories.

Three adjacent safety bypasses remain blocking despite all committed tests passing.

### Blocking R1 — stale actual primary state can be accepted as an exact duplicate transition

`scripts/connlab_execution_transition.py:299-304` calls `already_applied` before the current primary
HEAD, lane HEAD/status, evidence, ancestry, and scope checks at lines 322-345. The duplicate helper
compares the caller's old `expected_primary_head` with the historical entry, but never compares it
with the repository's actual current HEAD.

Independent disposable reproduction applied a legal transition, committed the board transition,
then committed an unrelated primary change and replayed the original request:

```text
actual_head       e6cb60965f64dd7e3071c35ff226b884bbcc0d1a
recorded_preapply 3076cc7c3db76b7dff6be1291f120027de95f46c
exit              0
decision          ALREADY_APPLIED
```

This is not an exact duplicate under the frozen current-Git facts and violates the stale-facts
fail-closed contract. Require idempotency to revalidate the actual primary/lane/evidence/clean/
scope facts and prove the current primary is exactly the committed transition result, with no
later unrelated commit. Add at least later-primary-commit and dirty-lane duplicate negatives.

### Blocking R2 — maintenance accepts forged transition states and an unreviewed helper checkpoint

`scripts/connlab_active_context.py:307-320` requires `from_state`, `from_role`, `to_state`, and
`to_role`, but never checks their values against each event. A disposable Task A history with
`REVIEWER_PASS` changed to `from_role=Quick Fixer` and `to_role=Developer` still returned
`APPLIED_MAINTENANCE` and wrote archive/index/board.

The same block only proves that each historical entry's `helper_blob_sha` matches the helper at
that entry's own lane head. It never binds Reviewer/QA acceptance to the helper blob currently
being migrated. After valid Developer/Reviewer/QA evidence, an additional unreviewed commit changed
`scripts/connlab_active_context.py`; production-like apply again returned `APPLIED_MAINTENANCE`.

Validate exact legal transition tuples (and their transition IDs), require Reviewer/QA evidence to
attest the accepted current helper checkpoint, and reject any helper change after the last required
gate. Add state-tuple tampering and post-QA helper-drift zero-write regressions.

### Blocking R3 — a canonical forged incremental archive can remove active authority detail

`scripts/connlab_active_context.py:189-193` checks each incremental archive item's line number and
exact source text, but does not call `is_terminal_line` for that item. The remaining hashes, counts,
plan digest, compact bytes, and canonical JSONL can therefore be recomputed around an ineligible
line.

Independent two-generation reproduction replaced one terminal archive item with the exact current
active line and recomputed all stored facts:

```text
chosen_text          - `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF`:
                     gate_running/Integrator; current evidence retained.
is_terminal          false
validation_exit      0
decision             MAINTENANCE_REQUIRED
board_contains_line  false
```

The helper accepted the forged chain and planned generation three, even though active/current
evidence had moved out of the board. Require every incremental item to be terminal-eligible under
the exact source snapshot and prove active/queue/paused/QF/parallel/residual/current/proposed lines
cannot be removed by a recomputed canonical archive/index.

## Historical First-gate Findings — Closed By The Bounded Fix

### Blocking B1 — `prove-rollback` can overwrite live authority or an arbitrary existing file

`scripts/connlab_active_context.py:340-350` resolves the caller-provided `--output`, creates its
parents, and calls `write_bytes` without requiring a new safe temp destination or excluding the
repository, board, index, archive, links, or existing files. `prove-rollback` is available outside
Integrator apply authority, so its advertised read-only proof path is a general overwrite path.

Independent disposable-repository reproduction:

```text
apply APPLIED_MAINTENANCE
prove-rollback --output <repo>/docs/task_board.md
prove_exit 0
prove_decision ROLLBACK_PROVEN
live_board_overwritten True True
```

The command replaced the compact live board with the archived pre-maintenance bytes. This violates
the approved rule that rollback is reconstructed only into a safe temp path and never silently
restores live authority.

Required bounded fix and regression:

1. Accept only a new, non-link destination in an explicitly proven temporary root; fail closed for
   every repository path, existing target, path escape, link/junction traversal, board/index/archive,
   or parent creation outside that root. Use exclusive creation.
2. Prove safe temp output still reconstructs byte-exactly.
3. Prove attempts targeting the live board and other existing files return stable `BLOCKED_*` and
   leave every byte/status unchanged.

### Blocking B2 — dispatch capsules are not bound to durable task/lane/gate authority

`scripts/connlab_handoff_contract.py:17-20` omits the frozen lane, branch, worktree, base/head,
scope/lock/gate digests, named action, and stop-condition fields. Lines 106-131 prove that refs
exist and that `board_ref` points to current primary HEAD, but never parse the referenced board or
bind capsule `task_id`, role/status/next, task/plan/evidence refs, lane Git facts, required gates,
scope, or locks to it.

Independent reproduction changed a valid capsule from `TASK_X` to `TASK_OTHER`, changed its
role/status/next, and retained all `TASK_X` refs. The helper still returned:

```text
exit 0
decision ALLOW_DISPATCH_CAPSULE
capsule_bytes 1031
transition_count 1
dispatch_count 1
```

This allows a reference-valid but authority-contradictory dispatch, contrary to the callback-is-
only-a-wakeup rule and the frozen complete-capsule contract.

Required bounded fix and regression:

1. Require the complete approved capsule fields and exact types/budgets.
2. Parse the referenced primary board and bind task/token/state/role/lane/branch/worktree/base/head,
   required gates, scope/locks digests, evidence path/status, next legal action, and stop conditions
   to the task/plan/evidence refs and current Git facts.
3. Return `FULL_READ_REQUIRED` or stable blocking output for cross-task refs, wrong role/status/next,
   stale/unrelated commits, lane/head/lock/gate drift, incomplete capsule, or contradictory board.

### Blocking B3 — transition metadata and evidence status are not fail-closed

The approved plan freezes `scope_contract_ref`, `may_touch_digest`, `locked_paths_digest`, and
`last_transition_id` as required active metadata. `scripts/connlab_execution_transition.py:121-128`
does not require any of them. A disposable active record missing all four returned
`ALLOW_TRANSITION` for `DEVELOPER_READY`.

In addition, lines 269-272 validate evidence using unrestricted substring searches. A Reviewer
evidence blob whose current status was `reviewer_blocked` but which contained historical text
`STATUS: reviewer_pass` was accepted for `REVIEWER_PASS`:

```text
exit 0
decision ALLOW_TRANSITION
next_role QA
```

This can advance a blocked review and does not provide the required immutable task/scope/lock/gate
binding.

Required bounded fix and regression:

1. Require and cryptographically validate all frozen active metadata against the exact approved
   task/plan commit; legacy records must return `BLOCKED_TRANSITION_METADATA` and stay manual.
2. Parse one unambiguous current evidence status/role/task machine record or exact callback block;
   do not accept historical prose substrings or multiple contradictory records.
3. Add the complete task-listed mismatch matrix: state/role/owner/task/lane/primary/lane HEAD,
   evidence path/commit/blob/hash/status, ancestry, dirty worktree/index, scope/lock/gate digests,
   queue/pause/QF/parallel/residual drift, marker/summary mismatch, exact duplicate, and divergent
   duplicate. Each negative must prove zero writes.

### Blocking B4 — maintenance gate history and idempotency can approve corrupt state

`scripts/connlab_active_context.py:251-257` treats the presence of three event names as complete
Developer/Reviewer/QA evidence and treats `HEAD:scripts/connlab_active_context.py` existence as
accepted helper ancestry. It does not validate role evidence refs, commits, blob hashes, statuses,
reviewed/QA ancestry, or the accepted helper checkpoint. The shipped maintenance fixture contains
only `{"event": ...}` records and production apply succeeds.

Lines 351-355 also return `ALREADY_APPLIED` from the last index source commit/hash before checking
the current compact board, clean status, expected plan digest, or complete chain. After a successful
disposable migration, extra corrupt bytes were appended to the board; the repeated command still
returned:

```text
decision ALREADY_APPLIED
zero_write True
```

This violates exact idempotency and the requirement that corrupt/conflicting state fail closed.
The index validator also lacks the frozen index schema/version and does not recompute every stored
byte/record/rollback/source-blob fact.

Required bounded fix and regression:

1. Validate complete Reviewer/QA transition entries and immutable evidence refs/statuses/ancestry;
   require the accepted reviewed/QA helper checkpoint, not merely file existence.
2. Permit `ALREADY_APPLIED` only when current board hash, complete canonical index/hash chain,
   archive bytes/counts, expected plan digest, and clean state exactly match the recorded result.
3. Add negative cases for event-name-only history, altered compact board, schema/version/count/
   rollback/source-blob tampering, non-contiguous generations, path/link escape, archive conflict,
   and second/third-generation rollback. All failures must preserve board/index/archive bytes.

### Blocking B5 — the first heartbeat can occur before 60 seconds

`scripts/connlab_handoff_contract.py:179-184` compares only adjacent heartbeat events. A single
heartbeat is never compared with `role_start` or the preceding material event. This disposable
sequence was accepted:

```text
role_start  00:00:00Z
heartbeat   00:00:01Z state=unchanged
decision    ALLOW_CADENCE
```

The approved contract requires a heartbeat only after at least 60 seconds of active silence and
suppresses unchanged waits. This is a quantitative acceptance miss and therefore blocking.

Required bounded fix and regression:

1. Compare every heartbeat, including the first, with the previous permitted commentary/material
   event and require at least 60 seconds of silence.
2. Reject unchanged heartbeat state relative to the preceding state, invalid event order, and
   mixed/negative timestamp timelines; retain the <=90-second callback-to-dispatch rule.

## Independent Final Re-gate Validation

Passing evidence, which does not waive R1-R3:

- Exact B1-B5 adversarial replays now fail closed: live-board/existing/link/escape rollback output,
  cross-task dispatch capsule, missing transition metadata/historical status text, event-name-only
  maintenance history/corrupt repeat, and one-second first heartbeat.
- Focused four-module fix matrix: `49 passed in 131.61s`.
- Complete twelve-module Task A matrix: `129 passed in 191.33s`.
- `py -m py_compile` for the three helpers and six bounded test modules: passed.
- PowerShell AST parse: `run_task.ps1`, `connlab_execution_gate.ps1`, and
  `connlab_lane_worktree.ps1`: `AST_PARSE_OK_3`.
- Helper limits: transition `452` lines / `26477` bytes; active context `494` / `31902`;
  handoff `334` / `22884`; each remains below the hard 500-line limit. Core budgets remain:
  Orchestrator skill `6092` bytes, Planner skill `4341`, orchestration protocol `6881`, and
  `run_task.ps1` `3980`.
- Production read-only checks at primary `e5de0c4f...`: transition inspect correctly returned
  `BLOCKED_TRANSITION_METADATA` for the legacy active record; active-context inspect returned
  `ALLOW_INSPECT` at `2514` lines / `786540` bytes / `153` terminal records; plan returned
  `MAINTENANCE_REQUIRED` with a `111`-line / `18657`-byte compact preview. Primary HEAD, board
  SHA-256 `68c1b00610471bf344a52df5b2ce8d452270d5d9e269a2acb214fde1ed4e9f8c`, and final clean status
  were unchanged; no production archive/index was created.
- `git diff --check`, final `show --check`, exact full/focused allowlists, both ancestry checks,
  staged-empty, and final lane/primary clean checks passed. Protected base/head blobs are identical;
  Task B is untouched. All `12` other registered worktrees were independently read as clean.

Historical first-gate passing evidence retained for audit:

- Complete Developer-listed governance matrix: `105 passed in 92.53s`.
- `py -m py_compile` for all three helpers and six new bounded test modules: passed.
- PowerShell AST parse: `run_task.ps1`, `connlab_execution_gate.ps1`, and
  `connlab_lane_worktree.ps1`: passed.
- Core budgets: Orchestrator skill `6092` bytes; Planner skill `4341`; active orchestration
  protocol `6881`; all below limits.
- Helper line limits: transition `375`, active context `385`, handoff `220`; all below 500.
- Independently generated nominal capsule `1017` bytes, template `75`, read set `701`, callback
  `162`, and simulated callback-to-dispatch `45` seconds; these nominal positives pass their hard
  budgets but do not cover B2/B5.
- Read-only primary inspection/maintenance plan: `ALLOW_INSPECT`, board `2514` lines / `786374`
  bytes / `153` terminal records, planned compact board `111` lines / `18440` bytes. Primary HEAD,
  board SHA-256 `a1cff8b089e4bd420bedf601dd510064e558fb7ff408fb3a125bbb5cc3fd2357`,
  and clean status were identical before/after; no archive/index was created.
- Full/focused `git diff --check`, final commit `show --check`, exact 24-path package, staged-empty,
  and lane/primary clean checks passed. An intermediate Developer evidence commit had whitespace
  reported by `show --check`, and final HEAD correctly normalizes it.
- Ten protected retained/frozen worktrees were independently read as clean. Base/head Git blobs
  are equal for board, ROLE_THREAD_REGISTRY, Controlled Lane V2 contract/skill/helper, execution
  gate/worktree/task-complete helpers, active bundle, and Task B task/plan/Planner evidence.

All adversarial reproductions used disposable temporary Git repositories and were removed. No
production apply/migration, real Create/Retire, product/API/schema/data/file-resource access,
merge, push, restart, reset, restore, clean, rebase, stash, or destructive repository action ran.

## Final Re-gate Conclusion And Handoff

`reviewer_blocked`.

The bounded fix closes B1-B5 and the package meets its nominal regression, parse, scope, size, and
protected-state gates. However, R1-R3 are independently executable safety counterexamples: stale
primary facts are accepted as an exact duplicate, maintenance accepts forged gate/helper authority,
and a canonical incremental archive can remove active authority detail. Return these exact bounded
helper/test fixes to Developer. Mandatory QA must not start until a full Reviewer re-gate closes all
three findings.
