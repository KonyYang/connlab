# ConnLab Personal Serial Workflow Simplification Plan

Status: `DRAFT_FOR_USER_REVIEW`
Task: `TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION`
Date: 2026-08-05
Planning base: `ae33faa38894c26245397226d8e4357512c77b91`

## 1. Outcome

ConnLab will use one personal task queue instead of a permanent-role orchestration system. Natural
task commands in the current conversation will update one active record or append one FIFO record.
The active task is implemented directly in the primary worktree, locally committed after bounded
validation, and held at `implemented_pending_human_review` until the User says `关闭`.

The implementation simplifies the existing system; it does not add another automation framework.

## 2. Discovery Gate

### Confirmed by the User

- There is one developer and no valid need for concurrent implementation.
- New tasks must wait in FIFO order while one task is active.
- A simple task has a clear root cause, changes one to three implementation files, and does not
  change API/database/persistence/business semantics.
- Simple tasks require neither a prior plan nor plan approval.
- After implementation they become `implemented_pending_human_review`; `关闭` performs closeout.
- Implementation may occur directly in the primary worktree; lane branches and sibling worktrees
  are no longer required.
- Former roles must not be dispatched and Task-A must remain retained and cancelled.

### Confirmed by Repository Evidence

- Primary was clean at `master@ae33faa38894c26245397226d8e4357512c77b91` during planning.
- The board passed active-context inspection and execution-gate inspection in valid `cancelled`
  state with `active=null` and no token owner.
- Existing policy already enforces WIP=1 and FIFO, but also retains parallel exceptions,
  preemption/reconciliation, lane/worktree isolation, seven permanent roles, and mandatory
  Reviewer/QA/Integrator closeout.
- `scripts/run_task.ps1` hard-codes continuation through local Integrator acceptance.
- `scripts/connlab_execution_gate.ps1` validates the obsolete multi-role state model.

### Planner Decision

Evidence is sufficient to plan one governance-only change. No product or data behavior is in
scope. The FIFO successor becomes eligible after close but does not auto-start; this prevents a
close command from implicitly authorizing new writes.

## 3. Target Contract

### 3.1 Minimal Board Authority

Keep one marker-delimited machine-readable block in `docs/task_board.md`, reduced to:

- `schema` and `version`;
- `mode: personal_serial`;
- `wip_limit: 1`;
- `state: idle | running | implemented_pending_human_review`;
- one nullable `active` record;
- an ordered `queue` containing task ID, summary, kind, enqueue sequence, and timestamp;
- one short retained-history section preserving pointers for every current residual, including the
  cancelled Task-A evidence and retained lane.

Remove active-context fields that exist only for multi-role execution: secondary owner,
`parallel_exception`, paused/preemption state, reconciliation state, role, lane, worktree,
handoff/transition metadata, gate chain, and Integrator residual closeout.

Task-A's lane, evidence, task/plan files, commits, and archived history remain untouched. Other
currently retained residuals likewise keep their existing owner and artifact pointers. The
pre-change board remains recoverable from Git commit `ae33faa3`; no new archive generation is
required for this governance migration.

### 3.2 Command Semantics

| Command situation | Required result |
|---|---|
| no active task + qualifying simple request | record active `running/simple`, implement directly |
| no active task + ordinary/high-risk request | create short plan, wait for explicit approval |
| active task exists | append idempotently to FIFO; no implementation |
| implementation validation and commit pass | set `implemented_pending_human_review`; retain active slot |
| User says `关闭` | close current task, release slot, expose FIFO head as next eligible |
| User says `关闭` with no active task | no-op with a clear response |
| simple task becomes ambiguous/high-risk | stop; convert to planned flow only with User direction |

### 3.3 Minimal Safety Invariants

- Never write implementation when another active task exists.
- Never auto-start the queue head merely because the previous task closed.
- Refuse a new task when the primary worktree/index is unexpectedly dirty, except for files
  explicitly owned by the current task.
- Require targeted validation or an explicitly reported unavailable/manual check before commit.
- Use exact-path staging; never `git add -A`.
- Local commit only. Push, destructive cleanup, external publication, and service restart require
  separate explicit authorization.
- Human review replaces Reviewer/QA/Integrator routing; it does not remove implementation self-checks.

## 4. Implementation Scope

### May Touch

Core authority and daily rules:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

Legacy routing references, changed only to mark them frozen/non-daily and point to the personal
serial policy:

- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/connlab-planner/SKILL.md`

Entry points and validation:

- `scripts/run_task.ps1`
- `scripts/connlab_execution_gate.ps1`
- `scripts/connlab_active_context.py`
- `tests/unit/test_connlab_personal_serial_workflow.py` (new bounded contract tests)
- `tests/unit/test_connlab_execution_gate_script.py`
- `tests/integration/test_connlab_execution_gate_recovery.py`
- `tests/unit/test_execution_wip_and_quick_fix_governance.py`
- `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
- `tests/unit/test_connlab_lane_worktree_script.py`
- `tests/unit/test_connlab_active_context.py`
- `tests/unit/test_connlab_active_context_governance.py`
- this task and plan file for implementation status/validation results

### Must Not Touch

- all product, backend, frontend, API, domain, database, migration, Office, LTR, Matrix, Fee, report,
  release, or runtime feature code and tests;
- `docs/archive/task_board_history/**` and its canonical index;
- every Task-A task/plan/evidence/transition/attestation file, its retained lane/worktree, commits,
  and branch;
- the external `connlab-governance-migration` repository;
- Controlled Lane V2 helper, registry, heartbeat, pilot/corrective packages, and tests;
- other tasks, plans, evidence, retained worktrees, generated artifacts, real data, remotes, and
  services;
- deletion or retirement of legacy scripts/documents in this task. They are frozen in place.

## 5. File-Level Steps After Approval

1. Add failing governance tests for the three-state personal schema, single active item, idempotent
   FIFO queue, simple-task eligibility, pending-human-review lock, and explicit close behavior.
2. Replace the multi-role sections of `AGENTS.md` and the normative WIP policy with the personal
   serial contract. Keep product/architecture/testing rules intact.
3. Compact the live board control block from the current cancelled state into the personal schema,
   retaining a short immutable pointer to Task-A without changing any Task-A artifact.
4. Simplify `connlab_execution_gate.ps1` to read-only personal decisions such as inspect,
   start-or-queue, implementation-allowed, and close-allowed. Remove active support for parallel,
   preemption, reconciliation, worktree, and role-gate intents.
5. Simplify `run_task.ps1` so it no longer builds an Orchestrator capsule or promises execution to
   Integrator. It must surface start/queue decisions without dispatching another conversation.
6. Align planning/execution/checklist documents: simple tasks skip plans; non-simple tasks use one
   short plan and User approval; all tasks use proportional self-validation and exact local commit.
7. Mark former orchestration/handoff/registry documents and skills as frozen historical references;
   do not delete them or invoke their roles.
8. Update only directly affected governance tests, run the validation matrix, inspect the exact
   diff, and make one local implementation commit on primary.
9. Set this task to `implemented_pending_human_review`. Do not close it, start the FIFO successor,
   or push until the User reviews and says `关闭`.

## 6. Validation

Minimum behavioral coverage:

- clean idle primary permits one task;
- a second task queues once and keeps FIFO order;
- pending human review continues to block/queue new work;
- simple-task classification rejects API/database/schema/migration/persistence/authority/business
  semantics and changes exceeding three implementation files;
- ordinary/high-risk task requires a plan approval marker;
- no decision emits Planner/Developer/Reviewer/QA/Integrator dispatch or lane/worktree creation;
- `关闭` is the only normal release path and does not auto-start the queue head;
- Task-A retained references remain present while its artifacts and lane remain byte/Git unchanged;
- malformed board state fails closed without writes.

Planned commands:

```powershell
py -m pytest tests\unit\test_connlab_execution_gate_script.py -q
py -m pytest tests\unit\test_connlab_personal_serial_workflow.py -q
py -m pytest tests\unit\test_execution_wip_and_quick_fix_governance.py -q
py -m pytest tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests\unit\test_connlab_lane_worktree_script.py -q
py -m pytest tests\unit\test_connlab_active_context.py tests\unit\test_connlab_active_context_governance.py -q
py -m pytest tests\integration\test_connlab_execution_gate_recovery.py -q
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\connlab_execution_gate.ps1' -Raw -Encoding UTF8))"
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\run_task.ps1' -Raw -Encoding UTF8))"
py scripts\connlab_active_context.py inspect --repo-root . --json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\connlab_execution_gate.ps1 -Intent Inspect -Json
git diff --check
git status --short
```

The exact test list may be narrowed or extended only to cover directly affected governance code;
product test scope must not expand.

## 7. Risks And Controls

| Risk | Control |
|---|---|
| direct primary edit leaves partial work | preflight clean check, exact-path staging, bounded validation, one local commit |
| a small task is misclassified | all simple predicates are mandatory; ambiguity or one forbidden category forces planned flow |
| human review is confused with no validation | validation remains required and is recorded before `implemented_pending_human_review` |
| queued work starts accidentally | close only releases the slot; queue head requires a later explicit execute/continue command |
| legacy automation reactivates | old roles, lane helpers, transitions, and V2 remain frozen and are removed from daily references |
| Task-A history is lost | retain its short board pointer and leave all lane/evidence/archive/Git objects untouched |
| old tests encode obsolete behavior | replace only directly conflicting assertions; retain fail-closed and frozen-history coverage |

## 8. Rollback

Before the first implementation edit, require clean `master` at the approved planning commit.
Because implementation is one local governance commit, rollback before any later task depends on
the new schema is an exact `git revert <implementation-commit>` after User authorization. Once a
later task has used the personal schema, rollback requires a new explicit migration decision.

No reset, restore, archive rewrite, Task-A mutation, lane cleanup, or remote operation is part of
rollback.

## 9. Acceptance And Stop Point

Implementation acceptance requires:

- only the approved governance paths changed;
- personal serial tests and PowerShell parsing pass;
- active-context and execution-gate inspect pass under the new schema;
- product paths, Task-A artifacts/lane, archives, remotes, and external repository are unchanged;
- primary contains one local implementation commit and is clean;
- board records this task as `implemented_pending_human_review` with no role dispatch;
- no queued task has started.

After these conditions are met, stop for User inspection. Only the User command `关闭` closes the
task. No implementation begins before explicit approval of this plan.
