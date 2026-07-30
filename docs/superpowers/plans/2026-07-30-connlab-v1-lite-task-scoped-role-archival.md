# ConnLab V1-Lite Task-Scoped Role Archival Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. ConnLab does not permit automatic progression from one formal TASK to the next; stop at each Integrator closeout unless the User's later execution approval explicitly names the whole three-task series.

**Goal:** Freeze the unfinished Controlled Lane V2 runtime safely, replace permanent role reuse with a V1-Lite task-scoped role bundle, validate one disposable bundle, and archive the legacy ConnLab role tasks without losing repository or Git evidence.

**Architecture:** The repository remains the durable authority through `AGENTS.md`, `docs/task_board.md`, formal task/plan/evidence files, and Git. One lightweight stable entry task creates a temporary Controller and temporary Planner/Developer/Reviewer/QA/Integrator tasks for each product TASK. A bounded active-bundle manifest indexes native task IDs during execution; Integrator writes an immutable closeout manifest and archives the task-specific bundle after accepted or cancelled closeout.

**Tech Stack:** Markdown governance files, Python 3.11+/pytest for static contract tests, PowerShell Git/worktree helpers, Git local branches/worktrees, and native Codex task read/create/archive operations.

## Global Constraints

- Current product phase remains `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The implementation is governance-only: no backend, frontend, API, schema, database, Matrix, Fee, LTR, Office, business fixture, or real-data change.
- `docs/task_board.md` is modified only by Planner or Integrator in the primary worktree.
- Every formal implementation TASK uses one `lane/*` branch and one isolated worktree.
- Never use `git add -A`, force-remove, reset, restore, clean, branch `-D`, remote push, or destructive discard.
- V2 registry and heartbeat remain read-only; heartbeat stays `PAUSED`.
- Existing V2 scripts/tests are frozen, not deleted.
- Archive is recoverable and is allowed only after the exact closeout gate passes.
- No native task ID or Git SHA is invented. Dynamic IDs and SHAs come from exact native/Git read-back and are persisted immediately.
- Every role callback is compact and points to repository evidence instead of reproducing diffs or test logs.

---

## Execution Map

This plan contains three serialized formal TASKs:

1. `CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT`
   - preserve the current two-file dirty corrective snapshot;
   - close the active V2 corrective as cancelled/frozen;
   - leave legacy tasks unarchived until the replacement entry exists.
2. `CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE`
   - implement and test V1-Lite repository governance in an isolated lane;
   - integrate the docs/skill/test package locally.
3. `CONNLAB_V1_LITE_NATIVE_BOOTSTRAP_AND_LEGACY_ARCHIVE`
   - create the stable entry;
   - execute a disposable native task-bundle lifecycle;
   - record exact native IDs;
   - archive disposable and legacy tasks after read-back.

TASK 2 depends on TASK 1 accepted closeout. TASK 3 depends on TASK 2 accepted integration.
They must not run in parallel because all three own orchestration authority and board state.

---

### Task 1: Freeze And Close The Current Controlled V2 Corrective

**Formal TASK:** `CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT`

**Files:**

- Preserve in existing branch only:
  - `tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py`
  - `tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py`
- Create in primary governance package:
  - `tasks/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT.md`
  - `docs/connlab_controlled_lane_v2_freeze_closeout_plan.md`
  - `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT_planner.md`
  - `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT_integrator.md`
- Modify in primary governance package:
  - `tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE.md`
  - `docs/task_board.md`

**Interfaces:**

- Consumes:
  - corrective branch
    `lane/connlab-controlled-lane-orchestration-v2-developer-planning-binding-corrective`;
  - corrective worktree `D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective`;
  - expected committed HEAD `ce3b729d5d66362499fbcb3334a16afb8cfc1e3e`;
  - current primary baseline `cd4c31532fc8f079cba4a393768265ad099c3634`;
  - exact two-path dirty snapshot with 24 inserted lines;
  - production registry generation `34` and heartbeat `PAUSED`.
- Produces:
  - one local preservation commit on the existing corrective branch;
  - a clean corrective worktree;
  - a primary closeout commit marking the corrective `cancelled/frozen`;
  - `docs/task_board.md` with no active V2 implementation task;
  - no task archive and no V2 runtime mutation.

- [ ] **Step 1: Re-read and freeze the exact precondition**

Run:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
git status --short --branch
git worktree list --porcelain
git -C 'D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective' status --short --branch
git -C 'D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective' diff --stat
git -C 'D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective' diff --name-only
```

Expected:

- primary/index clean except User-approved planning documents awaiting their own review/commit;
- corrective HEAD remains `ce3b729d...`;
- only the two declared integration tests are modified;
- diff remains 24 insertions and no deletion;
- no second worktree owns the corrective branch.

If any fact differs, stop and return to Planner reconciliation. Do not stage or archive.

- [ ] **Step 2: Write the formal freeze task, plan, and Planner evidence**

The task contract must state:

```text
Status: approved_for_freeze_closeout
Outcome: preserve current incomplete RED coverage on its existing lane branch; do not integrate it
Runtime: registry generation 34 read-only; heartbeat PAUSED
Archive: forbidden in this task
Remote: no fetch or push
```

The closeout plan must list the two exact test paths and require a failing-test preservation note.
The Planner evidence must record current primary SHA, corrective HEAD, two-path diff stat, runtime
generation/hash, paused heartbeat, and native task inventory read-back.

- [ ] **Step 3: Update the board to make the freeze task the only approved governance action**

Modify only the active-task header and exact V2 lane rows in `docs/task_board.md`.

Expected board semantics:

```text
Current Active Task: CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT
V2 Developer-planning-binding corrective: freeze closeout in progress
Pilot: frozen; no continuation authority
V1-Lite migration: proposed; not executable
```

Run:

```powershell
git diff --check -- tasks/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT.md docs/connlab_controlled_lane_v2_freeze_closeout_plan.md docs/lane_evidence/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT_planner.md docs/task_board.md
git status --short
```

Expected: only the authorized governance paths are present; index is empty.

- [ ] **Step 4: Obtain the Task 1 governance checkpoint approval and commit it**

Stop and ask the User to approve the exact governance-path list and numstat. After approval, stage
only those exact paths:

```powershell
git add -- tasks/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT.md docs/connlab_controlled_lane_v2_freeze_closeout_plan.md docs/lane_evidence/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT_planner.md docs/task_board.md
git diff --cached --check
git commit -m "docs(orchestration): authorize controlled v2 freeze closeout"
```

Record the resulting full SHA as the Task 1 governance checkpoint.

- [ ] **Step 5: Run the preservation tests and record the expected incomplete state**

In the corrective worktree run:

```powershell
py -m pytest tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py -q
```

Expected: the preserved RED tests fail on the unresolved P1 lifecycle/recovery contracts. Record
the exact failing node IDs and assertion summaries in Integrator evidence. A different failure,
collection error, import error, or product-test failure is a blocker.

- [ ] **Step 6: Create the exact local preservation commit**

Verify an empty index, then stage only the two tests:

```powershell
git -C 'D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective' add -- tests/integration/test_connlab_controlled_lane_full_pilot_lifecycle.py tests/integration/test_connlab_controlled_lane_full_pilot_recovery.py
git -C 'D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective' diff --cached --check
git -C 'D:\PythonProject\connlab\tmp\wt\dev-plan-bind-corrective' commit -m "test(orchestration): preserve paused v2 corrective snapshot"
```

Expected:

- commit contains exactly two paths and 24 insertions;
- worktree/index are clean;
- commit is not merged into `master`;
- registry, heartbeat, task inventory, and remote refs are unchanged.

- [ ] **Step 7: Write frozen closeout evidence and update source-of-truth status**

Create Integrator evidence containing:

- governance checkpoint SHA;
- preservation commit SHA;
- exact two paths and test-failure snapshot;
- explicit statement that the preservation commit is unaccepted and unmerged;
- registry generation/hash and heartbeat `PAUSED`;
- retained branch/worktree owner: `CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT`;
- remote status;
- residual classification `retain/frozen-history`.

Update the old corrective task status to:

```text
cancelled/frozen; incomplete RED snapshot preserved on retained lane branch; not integrated
```

Update `docs/task_board.md` so no V2 implementation is active and TASK 2 is the next recommended
governance task, still awaiting its own approval.

- [ ] **Step 8: Reviewer and Integrator validate and commit the closeout package**

Reviewer verifies:

- preservation commit exactness;
- no product diff;
- no V2 runtime mutation;
- closeout facts match Git and native read-back.

Integrator stages only:

```text
tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_DEVELOPER_PLANNING_BINDING_CORRECTIVE.md
docs/lane_evidence/CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT_integrator.md
docs/task_board.md
```

Then run:

```powershell
git diff --cached --check
git commit -m "docs(orchestration): freeze controlled v2 corrective"
git show --check --stat --oneline HEAD
git status --short --branch
```

Expected: primary clean, no active V2 implementation task, corrective branch retained and clean,
no archive action. Stop after Task 1.

---

### Task 2: Implement V1-Lite Task-Scoped Role Governance

**Formal TASK:** `CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE`

**Branch:** `lane/connlab-task-scoped-role-thread-lifecycle`

**Worktree:** `D:\PythonProject\connlab-worktrees\connlab-task-scoped-role-thread-lifecycle`

**Files:**

- Create:
  - `tasks/CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE.md`
  - `docs/connlab_task_scoped_role_thread_lifecycle_plan.md`
  - `docs/lane_evidence/CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE_planner.md`
  - `docs/lane_evidence/CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE_developer.md`
  - `docs/lane_evidence/CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE_reviewer.md`
  - `docs/lane_evidence/CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE_qa.md`
  - `docs/lane_evidence/CONNLAB_TASK_SCOPED_ROLE_THREAD_LIFECYCLE_integrator.md`
  - `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`
  - `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
- Modify:
  - `AGENTS.md`
  - `.agents/skills/connlab-lane-orchestrator/SKILL.md`
  - `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
  - `docs/project_management/ROLE_THREAD_REGISTRY.md`
  - `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
  - `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
  - `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`
  - `tests/unit/test_connlab_lane_worktree_script.py`
  - `docs/task_board.md` through Planner/Integrator-owned exact hunks only

**Interfaces:**

- Consumes:
  - accepted Task 1 frozen-closeout commit;
  - clean primary worktree;
  - design specification
    `docs/superpowers/specs/2026-07-30-connlab-v1-lite-task-scoped-role-archival-design.md`;
  - current role/task inventory as read-only migration input.
- Produces:
  - repository-wide V1-Lite default contract;
  - empty active-bundle manifest;
  - compact callback contract;
  - V2 frozen-legacy contract;
  - static pytest coverage;
  - no native task creation or archive action.

- [ ] **Step 1: Create and approve the Task 2 governance checkpoint**

Planner creates the formal task, task-specific plan, Planner evidence, and exact board row.
The task must freeze:

```text
May Touch: only the Task 2 files listed above
Must Not Touch: product/backend/frontend/API/schema/database/business tests/V2 runtime/real data
Locked Paths: AGENTS.md, orchestrator skill, orchestration protocols, role registry, active bundle
Validation: static governance pytest + existing orchestration governance pytest + UTF-8/diff checks
Merge Gate: Reviewer pass + QA pass + Integrator exact package
```

After User approval, commit these planning files in primary, record the full checkpoint SHA, create
the declared branch/worktree from that SHA with `scripts/connlab_lane_worktree.ps1`, and verify
both primary and lane clean.

- [ ] **Step 2: Write the failing governance tests**

Create `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` with:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v1_lite_is_the_default_task_orchestration_contract() -> None:
    agents = read("AGENTS.md")
    skill = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md")

    assert "V1-Lite Task-Scoped Role Lifecycle" in agents
    assert "ACTIVE_TASK_THREAD_BUNDLE.md" in agents
    assert "TASK_XXX｜Controller" in skill
    assert "TASK_XXX｜Developer" in skill
    assert "closeout_archive_authorized" in protocol


def test_active_bundle_starts_empty_and_v2_is_frozen() -> None:
    bundle = read("docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md")
    registry = read("docs/project_management/ROLE_THREAD_REGISTRY.md")
    v2 = read("docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md")

    assert "state: empty" in bundle
    assert "active_task_id: null" in bundle
    assert "ConnLab｜任务入口" in registry
    assert "Status: frozen legacy" in v2
    assert "heartbeat remains `PAUSED`" in v2


def test_compact_callback_and_archive_order_are_frozen() -> None:
    skill = read(".agents/skills/connlab-lane-orchestrator/SKILL.md")
    protocol = read("docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md")

    for field in ("TASK_ID:", "ROLE:", "STATUS:", "EVIDENCE:", "COMMIT:", "NEXT:"):
        assert field in skill
    archive_order = (
        "Planner -> Developer -> Reviewer -> QA -> Integrator -> task-specific Controller"
    )
    assert archive_order in protocol
```

- [ ] **Step 3: Run the focused test and confirm RED**

Run:

```powershell
py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
```

Expected: failures because `ACTIVE_TASK_THREAD_BUNDLE.md` and V1-Lite normative strings do not yet
exist. A collection/import failure is not the expected RED.

- [ ] **Step 4: Update `AGENTS.md`**

Replace Section 19 with:

```text
## 19. V1-Lite Task-Scoped Role Lifecycle
```

It must state:

- one product TASK owns one temporary Controller/Planner/Developer/Reviewer/QA/Integrator bundle;
- the stable entry never receives detailed callbacks;
- roles are created lazily and never reused by the next product TASK;
- bundle archive is automatic only after Integrator closeout and explicit manifest authorization;
- board/task/plan/evidence/Git outrank bundle/chat state;
- V2 is frozen legacy and not the normal execution path.

Add:

```text
## 20. Controlled Lane V2 Frozen Legacy
```

It must preserve the read-only registry, paused heartbeat, retained code/tests, and prohibition on
new runtime/pilot/corrective actions without a separate User-approved reactivation task.

- [ ] **Step 5: Rewrite the Orchestrator skill around task-scoped bundles**

In `.agents/skills/connlab-lane-orchestrator/SKILL.md`:

- replace fixed permanent-role preference with the active-bundle manifest;
- keep board/evidence/Git preflight and worktree safety;
- create roles lazily;
- reuse same task-specific Developer/Reviewer only inside the same TASK;
- use the compact callback fields from the test;
- remove heartbeat as the normal continuation mechanism;
- archive only after the declared gate;
- retain a read-only V2 legacy section that never routes ordinary product work.

The skill must explicitly say:

```text
TASK_XXX｜Controller
TASK_XXX｜Planner
TASK_XXX｜Developer
TASK_XXX｜Reviewer
TASK_XXX｜QA
TASK_XXX｜Integrator
```

- [ ] **Step 6: Update protocols and create the empty active manifest**

Update `LANE_ORCHESTRATION_PROTOCOL.md` with:

- authority order;
- lazy role creation;
- compact callback;
- duplicate-callback read-back behavior;
- closeout requirements;
- exact archive order:
  `Planner -> Developer -> Reviewer -> QA -> Integrator -> task-specific Controller`;
- archive failure recovery;
- stable-entry rotation after 20 product TASKs or six months.

Update `ROLE_THREAD_REGISTRY.md` so it contains:

- stable entry canonical title `ConnLab｜任务入口`;
- native ID status `unassigned until Task 3 exact read-back`;
- pointer to `ACTIVE_TASK_THREAD_BUNDLE.md`;
- legacy task inventory moved to frozen-history notes rather than active authority.

Create `ACTIVE_TASK_THREAD_BUNDLE.md` with normative schema documentation and exact empty live
state:

```yaml
schema_version: 1
state: empty
active_task_id: null
```

- [ ] **Step 7: Align parallel-execution and operations documents**

In `PARALLEL_EXECUTION_MODEL.md`:

- state that role tasks are task-scoped coordination identities;
- preserve one lane/branch/worktree ownership;
- add archive as a Definition-of-Done requirement when authorized.

In `PARALLEL_LANE_OPERATIONS_GUIDE.md`:

- add native task-bundle closeout after worktree/residual closeout;
- require exact task IDs and native archived read-back;
- keep remote push and destructive discard as separate gates.

In `CONTROLLED_LANE_ORCHESTRATION_V2.md`:

```text
Status: frozen legacy
```

Keep its historical contracts, but add a leading freeze notice stating that registry, heartbeat,
pilot, bootstrap, corrective, migration, and normal task routing are inactive. Retain the sentence
`Bootstrap is not activated` so existing safety coverage remains true.

- [ ] **Step 8: Update existing governance test expectations**

Modify `tests/unit/test_connlab_lane_worktree_script.py` so
`test_v2_governance_hooks_are_present_without_bootstrap_activation` additionally asserts:

```python
assert "V1-Lite Task-Scoped Role Lifecycle" in agents
assert "Status: frozen legacy" in v2
assert "Bootstrap is not activated" in v2
```

Do not remove its PowerShell dry-run, credential, force-removal, 39-code, or six-command safety
coverage.

- [ ] **Step 9: Run GREEN validation**

Run:

```powershell
py -m pytest tests/unit/test_task_scoped_role_thread_lifecycle_governance.py tests/unit/test_connlab_lane_worktree_script.py -q
```

Expected: all tests pass.

Then run:

```powershell
py -m pytest tests/unit/test_connlab_controlled_lane_bootstrap.py tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py -q
```

Expected: historical V2 disposable/dry-run coverage still passes; no production registry or native
task mutation occurs.

Run:

```powershell
git diff --check
git status --short
```

Also perform strict UTF-8, trailing-whitespace, exact whitelist, forbidden product-path, and
physical-line checks.

- [ ] **Step 10: Create the clean Developer checkpoint**

Stage exact Task 2 lane paths only using `scripts/task_complete_commit.ps1` or explicit
`git add -- <exact paths>`. Suggested commit:

```text
docs(orchestration): add task-scoped role lifecycle
```

Developer evidence records:

- planning checkpoint SHA;
- lane HEAD;
- exact changed paths and numstat;
- tests and static checks;
- V2 runtime unchanged;
- lane worktree/index clean.

- [ ] **Step 11: Reviewer and QA gate the immutable checkpoint**

Reviewer compares the Task 2 planning checkpoint to lane HEAD and validates:

- permanent roles are no longer active authority;
- ordinary tasks do not route through V2;
- archive cannot occur before closeout;
- active manifest cannot approve scope;
- no product path changed.

QA runs the Task 2 focused and historical V2 safety suites from the reviewed clean commit, writes
QA evidence, and confirms no native task was created or archived.

- [ ] **Step 12: Integrate Task 2 and stop**

Integrator:

- verifies Reviewer/QA pass;
- fast-forwards or stages the exact reviewed package according to current topology;
- updates `docs/task_board.md`;
- writes residual ledger;
- confirms primary/lane clean;
- records remote status;
- does not create/archive native tasks yet.

Suggested governance closeout commit:

```text
docs(orchestration): accept task-scoped role lifecycle
```

Stop after Task 2 accepted integration.

---

### Task 3: Bootstrap The Stable Entry, Validate A Disposable Bundle, And Archive Legacy Tasks

**Formal TASK:** `CONNLAB_V1_LITE_NATIVE_BOOTSTRAP_AND_LEGACY_ARCHIVE`

**Files:**

- Create:
  - `tasks/CONNLAB_V1_LITE_NATIVE_BOOTSTRAP_AND_LEGACY_ARCHIVE.md`
  - `docs/connlab_v1_lite_native_bootstrap_and_legacy_archive_plan.md`
  - `docs/lane_evidence/CONNLAB_V1_LITE_NATIVE_BOOTSTRAP_AND_LEGACY_ARCHIVE_planner.md`
  - `docs/lane_evidence/CONNLAB_V1_LITE_NATIVE_BOOTSTRAP_AND_LEGACY_ARCHIVE_qa.md`
  - `docs/lane_evidence/CONNLAB_V1_LITE_NATIVE_BOOTSTRAP_AND_LEGACY_ARCHIVE_integrator.md`
  - `docs/archive/thread_bundles/CONNLAB_V1_LITE_DISPOSABLE_VALIDATION.md`
  - `docs/archive/thread_bundles/CONNLAB_LEGACY_ROLE_THREADS_2026-07-30.md`
- Modify:
  - `docs/project_management/ROLE_THREAD_REGISTRY.md`
  - `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`
  - `docs/task_board.md`

**Interfaces:**

- Consumes:
  - Task 2 accepted V1-Lite governance;
  - explicit User authority to create and archive the exact native tasks named by this task;
  - native `create_thread`, `read_thread`, and `set_thread_archived` operations;
  - clean primary and no active product lane.
- Produces:
  - one exact native stable-entry task ID;
  - one successfully archived disposable bundle;
  - archived legacy ConnLab orchestration tasks;
  - immutable closeout manifests;
  - empty active-bundle state.

- [ ] **Step 1: Create and approve the Task 3 plan**

The task must enumerate the exact legacy archive candidates:

```text
019eb3b8-8624-74b2-a4a7-a6856399deac  old Orchestrator
019eff12-a71a-7861-b3d2-908b204bdf73  permanent Planner
019eff12-f314-79f3-ae9e-3d1af76868d6  permanent Developer
019eff13-27d3-75a2-b654-d8ac28937614  permanent Reviewer
019eff13-7311-7ba1-9594-c0f7dc6a3d75  permanent QA
019eff13-bcb5-74c3-bb20-3c704038f4b3  permanent Integrator
019faaf2-f172-7523-b70f-2c4952acd59f  V2 Controller
019fb05b-8425-7443-9e9d-12da88c677db  V2-Lite temporary Planner
019fb166-08cf-7963-ae9e-3d1af76868d6  V2-Lite temporary Reviewer
019f9c46-d3be-7c72-bafd-5412a054cfa8  TASK_367A Developer worktree task
019f0bc9-c88d-7262-a8ed-47e5472a3bdc  legacy Quick Fixer
```

This current design/plan-review conversation is not part of automatic legacy archival.

Before approval, exact native read-back must confirm each candidate exists, is idle/notLoaded, and
has no running or approval-waiting turn.

Planner writes the formal task, task-specific plan, Planner evidence, and exact board row in the
primary worktree. After the User approves that exact governance package, stage only those paths,
run cached diff checks, and create:

```text
docs(orchestration): authorize v1-lite native bootstrap
```

Record the full governance checkpoint SHA and confirm primary/index clean before creating or
archiving any native task.

- [ ] **Step 2: Create the stable entry and persist its exact ID**

After explicit User authorization, create one local project task with canonical title:

```text
ConnLab｜任务入口
```

Its initial prompt permits only:

- receiving `执行 TASK_XXX`;
- reading board/task readiness;
- creating a task-scoped Controller;
- reporting closeout;
- no detailed callback, product edit, merge, registry, heartbeat, archive, or push.

Persist the returned native task ID, set that exact task's title to `ConnLab｜任务入口`, and read
back the exact ID/title pair. Update `ROLE_THREAD_REGISTRY.md` with that real ID. Do not infer the
ID from title search or treat an automatically generated title as canonical.

- [ ] **Step 3: Start the disposable bundle**

Use formal fake task ID:

```text
CONNLAB_V1_LITE_DISPOSABLE_THREAD_BUNDLE_VALIDATION
```

Create a task-specific Controller and Planner, set their exact titles to
`CONNLAB_V1_LITE_DISPOSABLE_THREAD_BUNDLE_VALIDATION｜Controller` and
`CONNLAB_V1_LITE_DISPOSABLE_THREAD_BUNDLE_VALIDATION｜Planner`, and read back each exact ID/title.
Persist their real IDs immediately in `ACTIVE_TASK_THREAD_BUNDLE.md` with:

```yaml
schema_version: 1
task_id: CONNLAB_V1_LITE_DISPOSABLE_THREAD_BUNDLE_VALIDATION
lane_id: connlab-v1-lite-disposable-thread-bundle-validation
state: planned
approval_state: planned_not_approved
closeout_archive_authorized: true
```

The fake task must not touch product or V2 runtime paths.

- [ ] **Step 4: Exercise the compact role chain**

Create Developer, Reviewer, QA, and Integrator lazily. Set and read back each canonical
`CONNLAB_V1_LITE_DISPOSABLE_THREAD_BUNDLE_VALIDATION｜<Role>` title against its exact returned ID.
Each role only writes or reads its bounded disposable evidence under `docs/lane_evidence/`; no
product file changes.

Every callback uses exactly:

```text
TASK_ID:
ROLE:
STATUS:
EVIDENCE:
COMMIT:
NEXT:
BLOCKER:
```

Use a disposable docs-only worktree. Developer hands off one clean local checkpoint containing only
the disposable evidence. Reviewer and QA validate that commit. Integrator records a no-product-diff
residual ledger and safely retires the clean disposable worktree.

- [ ] **Step 5: Close and archive the disposable bundle**

Write `CONNLAB_V1_LITE_DISPOSABLE_VALIDATION.md` with all real role IDs, branch/worktree, base,
reviewed commit, accepted commit, evidence, residuals, archive authorization, and remote status.

Archive in exact order:

```text
Planner -> Developer -> Reviewer -> QA -> Integrator -> task-specific Controller
```

After each archive, read back exact native state. If one fails, stop with the active manifest at
`closeout_ready`; do not continue to the next role.

After all six pass, reset active manifest to:

```yaml
schema_version: 1
state: empty
active_task_id: null
```

Confirm the stable entry remains active.

- [ ] **Step 6: Re-read every legacy archive candidate**

For each exact ID from Step 1, record:

- title;
- host/project/cwd;
- native status;
- latest final state;
- associated branch/worktree/evidence;
- archive blocker or `none`.

Required gates:

- V2 corrective preservation branch is clean and recorded;
- TASK_367A retained worktree has a named retained owner in board/evidence;
- no candidate is active or awaiting User approval;
- no unconsumed callback exists;
- V2 registry/heartbeat remain unchanged.

Any mismatch returns to Planner; do not archive a partial subset unless the User approves the
revised exact inventory.

- [ ] **Step 7: Write and commit the legacy closeout manifest**

Create `CONNLAB_LEGACY_ROLE_THREADS_2026-07-30.md` containing the exact read-back facts and planned
archive order. Update board and registry frozen-history notes. Commit the manifest and governance
hunks before native archival:

```text
docs(orchestration): record legacy role thread closeout
```

Verify primary/index clean.

- [ ] **Step 8: Archive legacy role tasks**

Archive recoverably in this order:

1. permanent Planner;
2. permanent Developer;
3. permanent Reviewer;
4. permanent QA;
5. permanent Integrator;
6. legacy Quick Fixer;
7. TASK_367A Developer worktree task;
8. V2-Lite temporary Planner;
9. V2-Lite temporary Reviewer;
10. V2 Controller;
11. old Orchestrator last.

Read back every task after archival. Record success or exact failure in the closeout manifest.
Never archive the new stable entry.

- [ ] **Step 9: Run QA read-back**

QA confirms:

- stable entry active and exact title/ID;
- active bundle empty;
- disposable role bundle archived;
- every authorized legacy candidate archived;
- no unlisted ConnLab task archived;
- repository primary clean;
- retained V2/TASK_367A branches/worktrees unchanged;
- V2 heartbeat `PAUSED`;
- no registry generation/hash change;
- no fetch/push.

- [ ] **Step 10: Integrator closeout**

Integrator updates Task 3 evidence and `docs/task_board.md`, commits exact governance hunks, and
records:

- stable entry ID;
- disposable archive manifest;
- legacy archive manifest;
- recoverability statement;
- residual ledger;
- remote status;
- next recommended action: select one new formal product TASK for the first real V1-Lite run.

Run:

```powershell
git diff --cached --check
git commit -m "docs(orchestration): activate v1-lite task entry"
git show --check --stat --oneline HEAD
git status --short --branch
```

Expected: Task 3 complete/accepted, active bundle empty, stable entry active, legacy tasks archived,
primary clean. Stop; do not start the first product TASK automatically.

---

## Plan Self-Review

### Spec coverage

- Familiar Planner -> Developer -> Reviewer -> QA -> Integrator flow: Task 2 Steps 4-7.
- One product TASK per temporary role bundle: Task 2 governance and Task 3 disposable validation.
- Stable lightweight entry: Task 3 Step 2.
- Compact callbacks: Task 2 tests/skill and Task 3 Step 4.
- Closeout then archive: Task 2 protocol and Task 3 Steps 5-8.
- V2 freeze without deletion: Task 1 and Task 2 Step 7.
- Dirty corrective preservation: Task 1 Steps 5-8.
- Exact legacy inventory and recoverable archive: Task 3 Steps 1, 6-8.
- No product changes or remote action: global constraints and each task gate.

### Placeholder scan

Dynamic native task IDs and commit SHAs are defined as outputs of exact read-back steps. The plan
does not invent them. No executable path, role, branch, worktree, validation command, archive
candidate, or stop gate is left unspecified.

### Type and naming consistency

- Stable entry: `ConnLab｜任务入口`.
- Active manifest: `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`.
- Task bundle roles: Controller, Planner, Developer, Reviewer, QA, Integrator.
- Archive order is identical in design, test, protocol, and native validation.
- V2 terminal status is consistently `frozen legacy`.

## Execution Approval Boundary

This plan is reviewable but not executable until the User explicitly approves it.

The recommended approval text is:

```text
批准按该实施计划执行三个串行任务；每个任务完成 Integrator closeout 后停止，不自动进入下一个任务。先执行 CONNLAB_CONTROLLED_LANE_V2_FREEZE_CLOSEOUT。
```
