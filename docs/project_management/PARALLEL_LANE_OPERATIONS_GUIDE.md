# ConnLab Parallel Lane Operations Guide

Last Updated: 2026-07-31
Status: active operational policy
Scope: lane isolation, shared-file ownership, clean validation, integration, and residual closeout

Concurrency authority comes only from
`docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`: WIP=1 is the default, and a second
owner requires an explicit User-approved max-two parallel exception.

## 1. Why This Guide Exists

ConnLab spent roughly one week reconciling a worktree that contained changes from many otherwise accepted tasks. The final cleanup was not difficult because Git was unreliable. It was difficult because logical task lanes were allowed to share one physical working directory for too long.

The resulting worktree mixed:

- unique regression coverage that still needed to be retained
- coverage already accepted in another commit
- support-only edits inside oversized mixed tests
- stale task plans and evidence
- conflicting `docs/task_board.md` hunks
- harmless formatting changes
- untracked governance documents with no current owner

RELEASE_006B1/B2/B3 recovered the remaining unique test value into bounded modules before the stale mixed residuals could be discarded. That recovery was necessary, but it should not be a normal development workflow.

## 2. Root Cause

The root cause was incomplete parallel-execution isolation.

### 2.1 Logical lanes without physical isolation

Tasks were routed to different role threads, but those threads often edited the same primary worktree. A separate chat is not a separate Git workspace. The main worktree became an implicit shared staging area for unrelated lanes.

### 2.2 Declared ownership without an enforced lock

Plans named `May Touch`, `Must Not Touch`, and `Locked Paths`, but approval did not require a concrete worktree plus an exclusive shared-file owner. Several lanes therefore accumulated changes in the same large test files and governance files.

### 2.3 Oversized mixed tests became residual containers

New coverage was added to already oversized test modules. Later packages could select only some hunks, leaving useful, duplicate, and support-only edits interleaved in the same file.

### 2.4 Review and QA sometimes observed a dirty source tree

Evidence recorded exclusions, hashes, and hunk boundaries, but the underlying tree still contained unrelated changes. Every later gate had to prove which changes were real inputs and which were ambient residuals.

### 2.5 Excluded residuals had no immediate closeout owner

Integrator correctly excluded out-of-scope hunks, but the process did not require those hunks to be classified immediately as:

- retained by a named follow-up lane
- migrated into a bounded package
- or approved for discard

The residual count therefore grew after each accepted lane.

### 2.6 Governance documents drifted independently

Task, plan, evidence, and board updates were often left uncommitted after product acceptance. Later roles repeatedly reconciled stale statuses before they could review otherwise valid code.

### 2.7 Manual role prompting amplified gate count

The operator had to paste separate commands into Planner, Developer, Reviewer, QA, and Integrator threads. Small fixture or assertion corrections repeatedly returned through broad human approval gates because there was no durable Goal authorization envelope and no single closeout controller.

## 3. Non-Negotiable Operating Rules

### Rule 1: One product lane, one branch, one worktree

Before Developer implementation starts, the orchestrator must create and verify:

- branch: `lane/<lane-id>`
- sibling worktree: `<repo-name>-worktrees/<lane-id>`
- recorded base commit
- clean primary worktree
- clean lane worktree

`Branch / Worktree: TBD` is not implementation-ready.

The primary `master` worktree is an integration worktree. Product implementation must not use it as a shared scratch directory.

### Rule 2: One shared path, one active owner

The board must name one owner for every shared file or shared authority path. Two active lanes may not both own the same path, even when they intend to edit different hunks.

High-conflict shared files include:

- `docs/task_board.md`
- oversized mixed test modules
- API composition roots
- schema/database ownership modules
- Matrix, Fee, LTR, Office, and Project lifecycle authority paths

If a second lane needs the same path, serialize the lanes or create a contract/helper extraction first.

### Rule 3: New tests use bounded modules

New behavior coverage belongs in a new focused test module by default.

Adding to an oversized mixed test requires an explicit exception that proves:

- the new behavior cannot be tested through a bounded public-contract module
- the file remains within its frozen line budget
- the entire file can be packaged atomically

Support helpers needed by a bounded test belong in the bounded test or a dedicated fixture module, not in an unrelated mixed test.

### Rule 4: Developer hands off a clean lane commit

Before `ready_for_review`, Developer must:

1. run lane validation
2. stage exact lane paths only
3. create one or more local lane checkpoint commits
4. leave the lane worktree and index clean
5. record base commit, lane HEAD, changed paths, and validation in evidence

Developer must not merge or push. Local checkpoint commits make the review input immutable and reproducible.

### Rule 5: Reviewer and QA validate committed inputs

Reviewer compares the recorded base commit to the lane HEAD.

QA must use one of:

- the clean lane worktree at the reviewed commit
- a clean temporary worktree at that commit
- an exact `git archive` of that commit

QA must not use ambient dirty files from the primary worktree. If validation requires injecting an uncommitted candidate, the evidence must name every injected path and prove the source hash.

### Rule 6: Integrator closes residuals immediately

After each accepted integration, Integrator must produce a residual ledger:

| Class | Meaning | Required action |
|---|---|---|
| `retain` | unique value not yet accepted | create a named bounded follow-up lane |
| `duplicate` | value already present in accepted history | add to exact discard list |
| `stale` | obsolete status, plan, evidence, or fixture context | add to exact discard list |
| `format-only` | whitespace/line-ending-only change | add to exact discard list |
| `conflict` | possible product behavior disagreement | stop and return to Planner/User |

No accepted lane may finish with an unnamed residual.

### Rule 7: Governance follows the task

Task, plan, lane evidence, and accepted closeout metadata must be committed with the planning or implementation package that owns them.

`docs/task_board.md` remains a primary-worktree file owned only by Planner/Integrator. Lane branches must not carry unrelated board edits.

### Rule 8: Definition of Done includes repository hygiene

A lane is complete only when:

- Reviewer and required QA gates pass
- Integrator accepts the exact package
- lane worktree status and index are empty
- primary worktree status and index are empty, or every residual has a named owner and expiry
- governance documents are committed
- no temporary archive or fixture remains without an explicit retention reason
- remote push status is stated

`Tests passed` alone is not lane completion.

### Rule 9: One Goal owns a multi-lane closeout

When the user authorizes a series, the orchestrator creates one durable Goal authorization envelope. Inside that envelope, normal Planner/Developer/Reviewer/QA/Integrator handoffs, bounded fix passes, tests-only migrations, evidence updates, and local commits continue automatically.

Pause only for:

- product contract or scope expansion
- a repeated or ambiguous test failure
- cross-lane ownership conflict
- destructive discard
- merge/push not already authorized

Do not request a new human approval for every small hunk when it remains inside the approved Goal envelope.

### Rule 10: Permanent roles, task-scoped evidence

Normal work reuses permanent Planner, Developer, Reviewer, QA, Integrator, Quick Fixer, and
Orchestrator conversations by exact ID from `ROLE_THREAD_REGISTRY.md`. A task owns its branch,
worktree, capsule/plan, and evidence—not a temporary role bundle. Callbacks return to permanent
Orchestrator. Permanent roles are not archived at task closeout.

## 4. Automated Lifecycle

The operator should not need to run Git worktree or branch commands.

Default user command:

```text
执行 TASK_XXX
```

The operator does not need to append "create a worktree", "check other tasks", or "continue to Integrator". For an explicit execute/start/implement command, those are default orchestration semantics.

Codex must then:

1. re-read the board, task, plan, evidence, registered role threads, and `git worktree list`
2. resume the existing task worktree when the task is already active; never create a duplicate
3. run the execution gate and obey the sole token/queue/paused state
4. queue every ordinary second task; only a recorded explicit exception can permit a secondary owner
5. run Planner Discovery and required approval gates when the task is not implementation-ready
6. commit approved planning/governance state in the primary worktree
7. create the lane branch/worktree with `scripts/connlab_lane_worktree.ps1 -TaskId <TASK_ID>`
8. route Developer to the exact worktree
9. require a clean local lane checkpoint commit
10. route Reviewer and QA against that commit
11. integrate only the reviewed commit
12. record and resolve the residual ledger
13. retire the clean integrated worktree
14. report local/remote commit status

The operator may ask for status or change direction, but does not need to remember Git syntax.

The equivalent local CLI entry is:

```powershell
.\scripts\run_task.ps1 -Task TASK_XXX
```

`run_task.ps1` starts orchestration. It does not implement directly in the primary worktree. The legacy `dev_cycle.ps1` delegates to the same entry and no longer runs broad auto-fix passes in `master`.

This default applies to product and tests-only implementation lanes even when no other task is currently active. Always isolating implementation avoids relying on potentially stale thread-presence detection. Planner-only discovery may remain in the clean primary worktree until implementation is approved.

Automatic continuation stops only for:

- missing user approval required by the frozen task contract
- shared-path/authority ownership conflict that requires serialization or re-scope
- ambiguous product behavior or unexplained test failure
- destructive discard
- merge or remote push outside the existing authorization

## 5. Agent-Only Worktree Commands

These commands are implementation details for Codex/Integrator. They are documented for auditability, not as required operator steps.

Create an isolated lane:

```powershell
.\scripts\connlab_lane_worktree.ps1 -Action Create -TaskId TASK_XXX -Lane task-xxx-short-name -BaseRef master
```

Inspect it:

```powershell
.\scripts\connlab_lane_worktree.ps1 -Action Inspect -Lane task-xxx-short-name
```

List managed worktrees:

```powershell
.\scripts\connlab_lane_worktree.ps1 -Action List
```

Retire it after its HEAD is integrated and the worktree is clean:

```powershell
.\scripts\connlab_lane_worktree.ps1 -Action Retire -Lane task-xxx-short-name -IntegrationRef master
```

The script never force-removes a worktree, discards changes, or pushes a remote branch.

## 6. Safe Commit Contract

Lane checkpoint commits use:

```powershell
.\scripts\task_complete_commit.ps1 `
  -TaskId TASK_XXX `
  -Summary "bounded implementation" `
  -Paths @("path/one", "path/two")
```

The script:

- requires a `lane/*` branch
- requires an initially empty index
- rejects ambient paths outside the exact list
- stages only explicit paths
- runs cached diff checks
- creates a local commit
- never runs `git add -A`
- never pushes

Mixed files such as `docs/task_board.md` require Integrator-owned exact hunk staging and are not valid lane checkpoint inputs.

## 7. Operator Safety Controls

These remain explicit human gates:

- `discard` for permanent restoration/deletion of audited residuals
- exact remote push authorization
- product contract changes
- conflict resolution that changes accepted behavior

Everything else in an approved Goal should be automated and reported, not delegated back to the operator as Git homework.

## 8. RELEASE_006 Lesson

RELEASE_006B1/B2/B3 did not add three unrelated features. It recovered three pieces of unique regression value from large mixed residuals:

- manual-required Fee preview blocker coverage
- multi-Group Base Fee fallback coverage
- real Damp Heat `extract_row_details()` integration coverage

Once those were moved into bounded modules, the remaining stale, duplicate, and formatting residuals could be safely discarded. The lasting lesson is to prevent unique value and disposable residue from sharing a file or worktree in the first place.

## 9. Controlled Lane V2 Operations Hook

The v2 helper is frozen legacy. Keep its production registry read-only and heartbeat `PAUSED`.
Only historical disposable roots and zero-write tests remain allowed without a separately approved
reactivation task.

The exact mutation order is:

```text
prepare-dispatch
mark-invocation-started
one external action
record-action-result
ack-dispatch
advance-state
stop
```

Worktree create/adopt and Developer-task create/adopt remain separate scans. JSON/dry-run/adopt
support in `connlab_lane_worktree.ps1` does not permit real topology mutation without the task's
explicit gate. Possible-start ambiguity, dirty state, path/branch/base mismatch, or shared-owner
conflict always stops without resend, force, cleanup, or fallback.

For classic permanent-role handoff and Integrator closeout maintenance, use
`ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`. Transition apply preserves
all queue/parallel/lock facts; board maintenance cannot run with a non-null parallel exception.
