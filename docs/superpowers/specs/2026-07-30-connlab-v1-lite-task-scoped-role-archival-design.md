# ConnLab V1-Lite Task-Scoped Role Archival Design

Status: proposed design for User review; not implementation-authorized

Date: 2026-07-30

## 1. Goal

Restore the familiar ConnLab role chain while preventing Planner, Developer, Reviewer, QA,
Integrator, and Orchestrator conversations from growing without bound.

The target operating rule is:

```text
one product TASK -> one temporary role bundle -> one accepted/cancelled closeout -> archive bundle
```

Archived Codex tasks remain recoverable history. Archival removes them from the active task list
and gives the next product TASK fresh context; it does not delete repository evidence or Git
history.

## 2. Discovery Gate

### Current phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

### Current active task

`CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE`

### Current role and why planning is allowed

This pass acts as Planner. The User explicitly approved producing a reviewable migration design.
No implementation, registry mutation, task archival, branch/worktree creation, commit, merge,
fetch, or push is authorized by that approval.

### Confirmed by the User

- The previous fixed-role flow was familiar and productive.
- Reusing the same role tasks indefinitely made their histories too large.
- Controlled Lane V2 is more complex than the desired daily workflow.
- Role separation among Planner, Developer, Reviewer, QA, and Integrator must remain.
- A product TASK should end with its role conversations archived and the next TASK starting fresh.
- The recommended direction is V1-Lite: preserve governance gates and Git isolation while removing
  V2 runtime machinery from normal product work.

### Confirmed by repository and runtime evidence

- `docs/task_board.md` still names the V2 Developer-planning-binding corrective as active.
- `docs/project_management/ROLE_THREAD_REGISTRY.md` still binds permanent v1 role thread IDs.
- The same registry document says the V2 Controller is not created and has no assigned ID, while
  native task inventory proves that Controller task
  `019faaf2-f172-7523-b70f-2c4952acd59f` exists.
- Controlled V2 introduces a production registry, generation CAS, a six-command journal,
  39 typed codes, heartbeat control, recovery rules, and one-external-action scans.
- The current corrective worktree is
  `D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective` on branch
  `lane/connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`.
- That worktree is dirty at `ce3b729d5d66362499fbcb3334a16afb8cfc1e3e` with exactly two modified
  integration test files and 24 inserted lines:
  - `tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py`
  - `tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py`
- Primary `master` is clean at `cd4c31532fc8f079cba4a393768265ad099c3634`, locally ahead of
  `origin/master` by 18 commits.
- Existing project governance already treats task/plan/evidence, Git commits, and
  `docs/task_board.md` as durable authority rather than chat memory.

### Planner inference

- The scalability problem is task lifetime, not the Planner/Developer/Reviewer/QA/Integrator
  separation itself.
- A small stable entry task can remain convenient if it never receives detailed role callbacks.
- Every task-specific Controller and role task should be temporary and archived at closeout.
- Controlled V2 should be frozen as a recoverable legacy experiment rather than deleted or
  silently repurposed.

### Not yet authorized

- Creating or renaming any Codex task.
- Archiving any existing task.
- Committing the dirty V2 corrective snapshot.
- Updating `AGENTS.md`, skills, project-management documents, task files, evidence, or the board.
- Activating a replacement workflow.
- Selecting the first product TASK to run through V1-Lite.

### Planning risk

Archiving the current permanent roles immediately would orphan the dirty corrective worktree and
leave the board, role registry, actual task inventory, and V2 runtime facts inconsistent. Reusing
the V2 Controller for V1-Lite would also carry its legacy registry/pilot/corrective context into
the replacement workflow.

### Discovery decision

Continue with this proposed design because the operating goal and non-goals are clear. Keep the
migration lane non-executable until the User approves a later implementation plan and the current
V2 snapshot has an explicit preservation closeout.

## 3. Considered Approaches

### A. V1-Lite with a stable entry and temporary task bundles — recommended

Keep one lightweight pinned task named `ConnLab｜任务入口`. It accepts commands such as
`执行 TASK_XXX`, creates one temporary task Controller, and later reports the closeout result.
It does not receive role evidence or callbacks.

Each product TASK gets temporary Planner, Developer, Reviewer, QA, Integrator, and Controller
tasks. The whole bundle is archived after accepted or cancelled closeout.

Benefits:

- familiar role chain;
- fresh context for every product TASK;
- a stable place for the operator to start;
- no production registry or heartbeat;
- repository evidence remains authoritative.

Cost:

- six task-specific role tasks plus one task-specific Controller may exist during a complex TASK;
- the stable entry task should be rotated after 20 product TASKs or six months, whichever comes
  first.

### B. Keep permanent roles and rotate them periodically

Continue using the existing permanent Planner, Developer, Reviewer, QA, and Integrator, but archive
and recreate them after a fixed number of tasks.

Benefit: fewer tasks are created.

Cost: task boundaries remain mixed, reviewers inherit irrelevant context, and rotation timing is
arbitrary. This does not meet the strict one-product-TASK/one-context requirement.

### C. Continue V2-Lite on top of Controlled V2

Keep the V2 Controller, production registry, heartbeat, CAS journal, and typed recovery state while
creating temporary roles.

Benefit: strongest exactly-once and crash-recovery bookkeeping.

Cost: preserves the complexity the User wants to remove and requires more corrective tasks before
ordinary product development can proceed.

### Decision

Use approach A. Preserve V2 artifacts read-only for audit and possible future study, but remove V2
from the default product-task path.

## 4. Authority Model

V1-Lite uses the following authority order:

1. `AGENTS.md`;
2. `docs/task_board.md`;
3. current formal task, approved plan, and role evidence;
4. Git branch, worktree, index, and commits;
5. the active task-bundle manifest;
6. attributed native task read-back;
7. chat summaries and callbacks.

The bundle manifest is a routing index, not an approval source. It cannot approve a planned lane,
widen `May Touch`, bypass Reviewer/QA, authorize destructive cleanup, or authorize remote push.

## 5. Task Topology

### 5.1 Stable entry

Canonical title:

```text
ConnLab｜任务入口
```

Responsibilities:

- accept the operator's new-task command;
- verify no unfinished active bundle already owns the requested paths;
- create a task-scoped Controller after task readiness is established;
- display the final accepted/cancelled result;
- remain free of detailed role prompts, diffs, test output, and callbacks.

### 5.2 Temporary bundle

Canonical titles use the formal task ID:

```text
TASK_XXX｜Controller
TASK_XXX｜Planner
TASK_XXX｜Developer
TASK_XXX｜Reviewer
TASK_XXX｜QA
TASK_XXX｜Integrator
```

Roles are created lazily:

1. Controller and Planner first.
2. Developer only after formal plan approval and worktree readiness.
3. Reviewer when an immutable Developer checkpoint exists.
4. QA after Reviewer pass when the task requires QA.
5. Integrator after all declared gates pass.

The same task-specific Reviewer is reused for review re-gates. The same task-specific Developer is
reused for bounded Reviewer/QA fixes in the same worktree. No role task is reused by the next
product TASK.

## 6. Active Bundle Manifest

The active routing file is:

```text
docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md
```

It contains one active bundle or an explicit empty state. The active form records:

```yaml
schema_version: 1
task_id: TASK_XXX
lane_id: task-xxx
state: planned
approval_state: planned_not_approved
closeout_archive_authorized: true
entry_thread_id: <native ID>
controller_thread_id: <native ID>
role_threads:
  planner: <native ID or null>
  developer: <native ID or null>
  reviewer: <native ID or null>
  qa: <native ID or null>
  integrator: <native ID or null>
base_commit: <full SHA or null before implementation approval>
branch: <lane branch or null before implementation approval>
worktree: <absolute path or null before implementation approval>
reviewed_commit: <full SHA or null>
accepted_commit: <full SHA or null>
task_file: <repository path>
plan_file: <repository path>
evidence_files: []
last_handoff:
  from_role: <role or null>
  to_role: <role or null>
  gate: <gate or null>
  evidence_path: <path or null>
residual_status: none_recorded
archive_status: not_started
```

Angle-bracket values above describe field content in this design; the live manifest must contain
real values or explicit YAML `null`, never invented IDs or SHAs.

At accepted or cancelled closeout, the manifest is copied into:

```text
docs/archive/thread_bundles/<TASK_ID>.md
```

The active file is then reset to:

```yaml
schema_version: 1
state: empty
active_task_id: null
```

Historical manifests are append-free: one bounded file per product TASK.

## 7. Role Handoff Contract

Normal callbacks are deliberately small:

```text
TASK_ID: TASK_XXX
ROLE: Developer
STATUS: ready_for_review
EVIDENCE: docs/lane_evidence/TASK_XXX_task-xxx_developer.md
COMMIT: <full SHA>
NEXT: Reviewer
BLOCKER: none
```

The callback does not repeat:

- full diffs;
- full test logs;
- task scope;
- all authority hashes;
- registry generations;
- route/operation/idempotency identifiers.

Before routing the next role, Controller rereads the named evidence, board, task, plan, Git state,
and exact target task. Duplicate callbacks are harmless because `last_handoff` and evidence status
already show whether the handoff was performed.

## 8. Lifecycle

```text
requested
-> discovery
-> planned
-> user_plan_approved
-> developer_active
-> review
-> developer_fix (optional, bounded)
-> review_pass
-> qa (when required)
-> integration
-> accepted | cancelled
-> closeout_ready
-> archived
```

Rules:

- `planned` is not executable.
- Developer requires a formal task, approved plan, exact branch/worktree, clean recorded base, and
  exclusive path ownership.
- Reviewer reads the recorded base-to-HEAD committed diff.
- QA uses the reviewed clean commit, a clean temporary worktree, or an exact archive.
- Integrator alone updates global completion state.
- A task may close as `cancelled` only with a preservation record for every dirty or unintegrated
  artifact.
- Archival occurs only from `closeout_ready`.

## 9. Closeout And Archive Gate

Integrator must prove:

1. Board status is `complete/accepted` or explicitly `cancelled/frozen`.
2. Task, plan, evidence, and closeout manifest are committed with their owning package.
3. Reviewer and required QA blockers are closed.
4. Accepted and reviewed commits are recorded.
5. Lane worktree/index are clean.
6. Primary worktree/index are clean, or every residual has owner and expiry.
7. Worktree is safely retired or explicitly retained with a named owner and reason.
8. No role task is active and no unconsumed callback remains.
9. Remote push status is stated.
10. `closeout_archive_authorized` is true.

Archive order:

1. Planner;
2. Developer;
3. Reviewer;
4. QA;
5. Integrator;
6. task-specific Controller.

The stable entry is not archived as part of a normal product TASK. After every successful archive
operation, native read-back must confirm the archived state and the archived bundle manifest must
record the result. A failed archive leaves the bundle in `closeout_ready` with the exact failed
task ID; it does not mark the bundle archived.

## 10. Failure And Recovery

### Dirty worktree

Stop routing. Assign a named owner and preserve the changes in a bounded local checkpoint or an
explicit retained residual. Never archive the last responsible Developer/Controller first.

### Missing or stale evidence

Stop before role handoff. The producing role must reconcile the evidence; chat output alone is
insufficient.

### Ambiguous role task

Stop and require exact native task ID read-back. Do not search by title and guess.

### Callback after closeout

Read the archived bundle manifest. If the callback matches an already consumed gate, record no
action. If it describes new state, restore the task bundle for Planner reconciliation before any
new routing.

### Archive failure

Keep the active manifest and repository state unchanged except for recording the failed archive
attempt. Retry only the exact failed task after native read-back.

### Interrupted Controller

A fresh Controller may be created only after reading the active manifest, board, evidence, Git
state, and existing native task IDs. It adopts the same bundle; it does not create a second lane or
worktree.

## 11. Controlled V2 Freeze Strategy

Controlled V2 is retained as historical, inactive infrastructure:

- heartbeat remains `PAUSED`;
- production registry remains read-only;
- pilot remains frozen;
- no further corrective, bootstrap, migration, or product task is routed through V2;
- V2 scripts and tests are not deleted by this migration;
- `CONTROLLED_LANE_ORCHESTRATION_V2.md` is marked legacy/frozen after closeout;
- the old fixed-role registry is preserved in the V2 closeout archive, then removed from active
  routing authority.

### Current dirty corrective preservation

Before archiving its Controller or Developer:

1. verify the two-path, 24-insertion diff still matches the current snapshot;
2. create one local preservation checkpoint on the existing corrective branch only;
3. do not merge that checkpoint into `master`;
4. write a cancelled/frozen closeout record naming the checkpoint, dirty-history reason, registry
   generation/hash, paused heartbeat, and retained branch;
5. leave the preserved worktree clean;
6. archive the old task-specific V2 conversations only after closeout read-back.

The suggested preservation commit message is:

```text
test(orchestration): preserve paused v2 corrective snapshot
```

This action requires separate explicit User approval in the implementation task.

### Existing V2-Lite test-status planning tasks

The temporary Planner and Reviewer for `TASK_V2_LITE_TEST_STATUS_TABLE` are not implementation
authority. Their product findings may be copied into a future formal task/plan after User review.
They must not be silently adopted as a V1-Lite approved lane. The V2-Lite manifest should close as
`cancelled_before_implementation`, after which those temporary role tasks may be archived.

## 12. Proposed Repository Changes

The later implementation plan should restrict governance changes to:

- modify `AGENTS.md` to make V1-Lite the default normal-task orchestration and freeze V2;
- modify `.agents/skills/connlab-lane-orchestrator/SKILL.md` to use task-scoped bundles and compact
  callbacks;
- modify `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`;
- modify `docs/project_management/ROLE_THREAD_REGISTRY.md` into a stable-entry plus active-bundle
  pointer;
- modify `docs/project_management/PARALLEL_EXECUTION_MODEL.md` thread-lifecycle section;
- modify `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md` closeout/archive section;
- modify `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md` to legacy/frozen status;
- create `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`;
- create a formal migration task, plan, and Planner evidence;
- update `docs/task_board.md` through Planner/Integrator-owned exact hunks;
- create one V2 frozen closeout manifest under `docs/archive/thread_bundles/`.

No backend, frontend, API, schema, database, Office, Matrix, Fee, LTR, or product test path belongs
to this governance migration.

## 13. Validation

### Static governance validation

- UTF-8 and trailing-whitespace checks for every changed document.
- `git diff --check`.
- Exact path whitelist.
- Search proving normal task instructions no longer require registry generation, heartbeat,
  route/operation/idempotency, or one-external-action scans.
- Search proving V2 remains documented as frozen and recoverable rather than deleted.
- Search proving `AGENTS.md`, skill, protocol, bundle schema, and closeout gate use the same role
  names and lifecycle.

### Disposable workflow validation

Use a fake formal task and temporary native role tasks without product edits:

1. create Controller and Planner;
2. record a planned-not-approved gate;
3. simulate approval and create a disposable clean worktree;
4. route fake Developer, Reviewer, QA, and Integrator evidence;
5. create a closeout manifest;
6. archive the temporary role tasks in the required order;
7. confirm native archived state;
8. reset the active manifest to empty;
9. confirm the stable entry remains active;
10. confirm no registry/heartbeat/V2 mutation occurred.

The disposable workflow must use a repository-independent fake task or a separately approved
docs-only pilot. It must not modify product code or business data.

### First real-task acceptance

After governance validation, one separately approved product TASK may serve as the V1-Lite pilot.
Acceptance requires:

- fresh task-scoped roles;
- normal Planner -> User -> Developer -> Reviewer -> QA -> Integrator chain;
- compact callbacks;
- clean worktree lifecycle;
- committed evidence;
- successful bundle archival;
- no reuse of its role tasks by the next product TASK.

## 14. Rollback

Before first real-task activation, rollback is omission of the V1-Lite governance package.

After activation but before a product implementation begins:

- unarchive the most recent stable entry or role bundle if necessary;
- restore the previous active routing documents from the accepted pre-migration commit;
- keep V2 heartbeat paused and registry read-only;
- do not delete archived bundle manifests.

After a product implementation begins, rollback is a separate Planner reconciliation. It must not
switch Controllers or role tasks while a Developer worktree is dirty or a Reviewer/QA gate is
pending.

## 15. Non-Goals

- No deletion of V2 code, tests, registry, or archived conversations.
- No migration of V2 state into a new runtime database.
- No automatic remote push.
- No destructive worktree cleanup.
- No product behavior, API, schema, database, frontend, Matrix, Fee, LTR, or Office change.
- No permanent reuse of task-specific role tasks.
- No replacement of task/plan/evidence/Git authority with a chat manifest.
- No archival of the current V2 corrective roles before its dirty snapshot is preserved.

## 16. Approval Gates

This design is not executable.

After User review, the next allowed output is a detailed implementation plan for one governance
migration task. That plan must freeze exact `May Touch`, `Must Not Touch`, locked paths, base
commit, branch/worktree, validation, V2 preservation checkpoint, task archival inventory, and
rollback.

Implementation, local commits, V2 closeout, native task creation, and archival require a later
explicit User approval of that implementation plan.
